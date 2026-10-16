#!/usr/bin/env python3
"""
Deploy the MKN ARABIA WordPress theme to a Hostinger website through the Hostinger API.

    HOSTINGER_API_TOKEN=… python3 tools/deploy/hostinger_deploy.py [--domain mknarabia.com] [--dry-run]

Steps (each one is skipped when it is already done, so the script is safe to run again):
  1. find the website and its hosting username;
  2. install WordPress in Arabic if the domain has none (admin password is random and written to
     .hostinger/wp-admin.txt, which is git-ignored — the owner signs in from hPanel and can reset it);
  3. upload the theme (wordpress/mkn-arabia) file by file and deploy + activate it;
  4. make sure SSL is installed and HTTPS is forced;
  5. open the site once so the theme imports its content, then check every page;
  6. clear the caches and record the target in .hostinger/site.json.

--dry-run only reads (steps 1, 2-check, 4-check) and prints what would happen.
Only the Python standard library is used.
"""
import argparse
import json
import os
import secrets
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("HOSTINGER_API_BASE", "https://developers.hostinger.com")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
THEME_DIR = os.path.join(ROOT, "wordpress", "mkn-arabia")
SLUG = "mkn-arabia"


def say(msg):
    print(msg, flush=True)


def fail(msg):
    say("✗ " + msg)
    sys.exit(1)


class Api:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, params=None, body=None, ok=(200, 201, 202, 204)):
        url = API + path
        if params:
            url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": "Bearer " + self.token, "Accept": "application/json",
            "Content-Type": "application/json", "User-Agent": "mkn-deploy/1.0"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    raw = r.read().decode() or "{}"
                    return r.status, json.loads(raw) if raw.strip()[:1] in "[{" else raw
            except urllib.error.HTTPError as e:
                raw = e.read().decode(errors="replace")
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 ** (attempt + 1))
                    continue
                if e.code in ok:
                    return e.code, raw
                fail(f"{method} {path} → HTTP {e.code}: {raw[:400]}")
            except urllib.error.URLError:
                time.sleep(2 ** (attempt + 1))
        fail(f"{method} {path} failed after retries")


def items(payload):
    if isinstance(payload, dict):
        for k in ("data", "items", "websites", "installations"):
            if isinstance(payload.get(k), list):
                return payload[k]
    return payload if isinstance(payload, list) else []


def http(method, url, data=None, headers=None, timeout=120):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def tus_upload(base, auth, rest_auth, local, dest):
    size = os.path.getsize(local)
    url = base.rstrip("/") + "/" + urllib.parse.quote(dest) + "?override=true"
    common = {"X-Auth": auth, "X-Auth-Rest": rest_auth, "Tus-Resumable": "1.0.0"}
    for attempt in range(4):
        st, body, _ = http("POST", url, b"", dict(common, **{"Upload-Length": str(size), "Upload-Offset": "0"}))
        if st == 201:
            with open(local, "rb") as f:
                st2, body2, hdr = http("PATCH", url, f.read(), dict(common, **{
                    "Content-Type": "application/offset+octet-stream", "Upload-Offset": "0"}))
            if st2 == 204 and str(hdr.get("Upload-Offset", hdr.get("upload-offset", ""))) == str(size):
                return
            body = body2
        time.sleep(2 ** (attempt + 1))
    fail(f"upload of {dest} failed: {body[:200]!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="mknarabia.com")
    ap.add_argument("--admin-email", default="contact@mknarabia.com")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("HOSTINGER_API_TOKEN", "").strip()
    if not token:
        fail("HOSTINGER_API_TOKEN is not set (add it as a secret in the environment settings).")
    api = Api(token)
    dom = a.domain.lower()

    # 1. website
    _, res = api.call("GET", "/api/hosting/v1/websites", {"domain": dom, "per_page": 100})
    site = next((w for w in items(res) if str(w.get("domain", "")).lower() == dom), None)
    if not site:
        fail(f"no website for {dom} in this Hostinger account (create it in hPanel first).")
    user = site.get("username") or (site.get("account") or {}).get("username")
    if not user:
        fail("website found but without a hosting username: " + json.dumps(site)[:300])
    say(f"✓ website {dom} · account {user}")

    # 2. WordPress
    def installation():
        _, r = api.call("GET", "/api/hosting/v1/wordpress/installations", {"username": user, "domain": dom})
        for i in items(r):
            if str(i.get("domain", "")).lower().rstrip("/") == dom and str(i.get("directory") or i.get("path") or "").strip("/") in ("", "public_html"):
                return i
        lst = items(r)
        return lst[0] if len(lst) == 1 else None

    wp = installation()
    if wp:
        say(f"✓ WordPress already installed (id {wp.get('id')})")
    elif a.dry_run:
        say("· would install WordPress (Arabic) on " + dom)
    else:
        pw = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#%^*-_") for _ in range(24))
        api.call("POST", f"/api/hosting/v1/accounts/{user}/wordpress/installations", body={
            "username": user, "domain": dom, "site_title": "MKN ARABIA", "language": "ar", "auto_updates": "minor",
            "credentials": {"email": a.admin_email, "login": "mkn-admin", "password": pw}})
        os.makedirs(os.path.join(ROOT, ".hostinger"), exist_ok=True)
        with open(os.path.join(ROOT, ".hostinger", "wp-admin.txt"), "w") as f:
            f.write(f"login: mkn-admin\npassword: {pw}\n(change it after the first sign-in)\n")
        say("… WordPress install queued; waiting (1–3 minutes)")
        for _ in range(36):
            time.sleep(10)
            wp = installation()
            if wp:
                break
        if not wp:
            fail("WordPress did not appear in the installations list after 6 minutes; check hPanel.")
        say(f"✓ WordPress installed (id {wp.get('id')}); admin login saved in .hostinger/wp-admin.txt")
    software = str(wp.get("id")) if wp else None

    # 3. theme
    files = []
    for d, _, fs in os.walk(THEME_DIR):
        for fn in fs:
            if fn.startswith(".") or fn.endswith((".md", ".py")):
                continue
            p = os.path.join(d, fn)
            files.append((p, os.path.relpath(p, THEME_DIR).replace(os.sep, "/")))
    if a.dry_run:
        say(f"· would upload {len(files)} theme files and activate «{SLUG}»")
    else:
        _, cred = api.call("POST", "/api/hosting/v1/files/upload-urls", body={"username": user, "domain": dom})
        cred = cred.get("data", cred) if isinstance(cred, dict) else {}
        url, auth, rest = cred.get("url"), cred.get("auth_key"), cred.get("rest_auth_key")
        if not (url and auth and rest):
            fail("upload credentials missing in response")
        tmp = f"{SLUG}-" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        for i, (p, rel) in enumerate(files, 1):
            tus_upload(url, auth, rest, p, f"wp-content/themes/{tmp}/{rel}")
            if i % 20 == 0 or i == len(files):
                say(f"  uploaded {i}/{len(files)}")
        api.call("POST", f"/api/hosting/v1/accounts/{user}/websites/{dom}/wordpress/themes/deploy",
                 body={"username": user, "domain": dom, "slug": SLUG, "theme_path": tmp, "is_activated": True})
        say("✓ theme deployed and activated")

    # 4. SSL
    _, ssl = api.call("GET", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/status")
    say("· SSL status: " + json.dumps(ssl)[:200])
    if not a.dry_run:
        active = isinstance(ssl, dict) and any(str(v).lower() in ("active", "installed", "true") for v in (ssl.get("data", ssl) or {}).values()) if isinstance(ssl, dict) else False
        if not active:
            api.call("POST", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/setup", ok=(200, 201, 202, 204, 409, 422))
            say("… SSL setup requested")
        api.call("PATCH", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/https-redirect/toggle",
                 body={"is_enabled": True}, ok=(200, 201, 202, 204, 409, 422))
        say("✓ HTTPS redirect on")

    if a.dry_run:
        say("dry run finished — nothing was changed.")
        return

    # 5. first visit runs the content import, then check the pages
    base = os.environ.get("MKN_SITE_BASE", f"https://{dom}").rstrip("/")  # override only for local testing
    checks = {"/": "سوّق بالعربي", "/services/": "D01", "/pricing/": "اطلب عرض سعر", "/work/": "Les Sènes Spa",
              "/testimonials/": "آراء العملاء", "/insights/": "مقالات لأصحاب الأعمال", "/about/": "د. نور الدين",
              "/contact/": "contact-form", "/privacy/": "سياسة الخصوصية", "/wp-sitemap.xml": "<sitemapindex"}
    for path in ["/"] * 3:
        st, body, _ = http("GET", base + path + "?mkn-warmup=" + secrets.token_hex(3))
        if st == 200 and "MKN" in body.decode(errors="replace"):
            break
        time.sleep(10)
    if software:
        api.call("POST", f"/api/hosting/v1/accounts/{user}/wordpress/{software}/litespeed-cache/purge", ok=(200, 201, 202, 204, 404, 422))
    api.call("DELETE", f"/api/hosting/v1/accounts/{user}/websites/{dom}/cache/clear", ok=(200, 201, 202, 204, 404, 422))
    bad = []
    for path, needle in checks.items():
        st, body, _ = http("GET", base + path)
        good = st == 200 and needle in body.decode(errors="replace")
        say(f"  {'✓' if good else '✗'} {path} ({st})")
        if not good:
            bad.append(path)
    st, body, _ = http("POST", base + "/wp-json/mkn/v1/lead", b"name=", {"Content-Type": "application/x-www-form-urlencoded", "Origin": base})
    say(f"  {'✓' if st == 422 else '✗'} lead endpoint answers ({st}, expected 422 for an empty brief)")
    st, _, hdr = http("GET", f"http://{dom}/") if "MKN_SITE_BASE" not in os.environ else (0, b"", {})
    say(f"  {'✓' if st in (301, 302) and str(hdr.get('Location', '')).startswith('https://') else '·'} http → https ({st})")

    # 6. record
    os.makedirs(os.path.join(ROOT, ".hostinger"), exist_ok=True)
    meta_path = os.path.join(ROOT, ".hostinger", "site.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    meta.update({"domain": dom, "username": user, "type": "wordpress", "theme": SLUG, "software": software})
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    if bad:
        fail("some pages did not show the expected content: " + ", ".join(bad))
    say("✓ done — https://" + dom)


if __name__ == "__main__":
    main()
