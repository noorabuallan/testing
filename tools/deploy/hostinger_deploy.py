#!/usr/bin/env python3
"""
Deploy the MKN ARABIA WordPress theme to a Hostinger website through the Hostinger API.

    HOSTINGER_API_TOKEN=… python3 tools/deploy/hostinger_deploy.py [--domain mknarabia.com] [--dry-run]

Steps (each one is skipped when it is already done, so the script is safe to run again):
  1. find the website and its hosting username; look at what public_html already holds;
  2. install WordPress in Arabic if the domain has none (admin password is random and written to
     .hostinger/wp-admin.txt, which is git-ignored — the owner signs in from hPanel and can reset it);
  3. upload the theme (wordpress/mkn-arabia) file by file, deploy and activate it;
  4. if files of the old static site are in public_html, replace its .htaccess rules with the theme's
     (old .html addresses redirect to the WordPress pages, index.php is served before index.html);
  5. make sure SSL is installed and HTTPS is forced;
  6. open the site once so the theme imports its content, clear the caches, then check every page;
  7. record the target in .hostinger/site.json.

--dry-run only reads and prints what would happen. Only the Python standard library is used.
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
THEME_MARK = "/wp-content/themes/" + SLUG + "/"
STATIC_FILES = {"index.html", "services.html", "insights.html", "work.html", "lead.php"}
WP_HTACCESS = """# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
"""


def say(msg):
    print(msg, flush=True)


def fail(msg):
    say("✗ " + msg)
    sys.exit(1)


class Api:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, params=None, body=None, ok=(200, 201, 202, 204)):
        """Returns (status, payload). Statuses outside `ok` stop the script; 429/5xx/network are retried."""
        url = API + path
        if params:
            url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": "Bearer " + self.token, "Accept": "application/json",
            "Content-Type": "application/json", "User-Agent": "mkn-deploy/1.1"})
        err = ""
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    raw = r.read().decode() or "{}"
                    return r.status, json.loads(raw) if raw.strip()[:1] in "[{" else raw
            except urllib.error.HTTPError as e:
                raw = e.read().decode(errors="replace")
                if e.code in ok:
                    return e.code, raw
                if e.code == 429 or e.code >= 500:
                    err = f"HTTP {e.code}: {raw[:300]}"
                    time.sleep(2 ** (attempt + 1))
                    continue
                fail(f"{method} {path} → HTTP {e.code}: {raw[:400]}")
            except (urllib.error.URLError, OSError) as e:
                err = str(e)
                time.sleep(2 ** (attempt + 1))
        fail(f"{method} {path} failed after retries ({err})")


def items(payload):
    if isinstance(payload, dict):
        for k in ("data", "items", "websites", "installations", "files"):
            v = payload.get(k)
            if isinstance(v, list):
                return v
            if isinstance(v, dict):
                inner = items(v)
                if inner:
                    return inner
    return payload if isinstance(payload, list) else []


def unwrap(payload):
    return payload.get("data", payload) if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def http(method, url, data=None, headers=None, timeout=120, follow=True):
    """Plain HTTP for uploads and checks. Never raises: network errors come back as status 0."""
    req = urllib.request.Request(url, data=data, method=method, headers=dict({"User-Agent": "mkn-deploy/1.1"}, **(headers or {})))
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except (urllib.error.URLError, OSError) as e:
        return 0, str(e).encode(), {}


def tus_upload(base, auth, rest_auth, local=None, dest="", content=None):
    data = content if content is not None else open(local, "rb").read()
    url = base.rstrip("/") + "/" + urllib.parse.quote(dest) + "?override=true"
    common = {"X-Auth": auth, "X-Auth-Rest": rest_auth, "Tus-Resumable": "1.0.0"}
    body = b""
    for attempt in range(4):
        st, body, _ = http("POST", url, b"", dict(common, **{"Upload-Length": str(len(data)), "Upload-Offset": "0"}))
        if st == 201:
            st2, body, hdr = http("PATCH", url, data, dict(common, **{
                "Content-Type": "application/offset+octet-stream", "Upload-Offset": "0"}))
            got = {k.lower(): v for k, v in hdr.items()}.get("upload-offset", "")
            if st2 == 204 and str(got) == str(len(data)):
                return
        time.sleep(2 ** (attempt + 1))
    fail(f"upload of {dest} failed: {body[:200]!r}")


def read_text(api, user, dom, path):
    """A text file from the website, or None when the API does not return it."""
    st, r = api.call("GET", f"/api/hosting/v1/accounts/{user}/domains/{dom}/files/content", {"path": path}, ok=(200, 403, 404, 413, 415, 422))
    if st != 200:
        return None
    r = unwrap(r) if isinstance(r, dict) else r
    if isinstance(r, str):
        return r
    if isinstance(r, dict):
        for k in ("content", "text", "body"):
            if isinstance(r.get(k), str):
                return r[k]
        if isinstance(r.get("lines"), list):
            return "\n".join(str(x.get("content", x) if isinstance(x, dict) else x) for x in r["lines"])
    return None


def clean_htaccess(current):
    """New .htaccess text, or None when nothing needs to change."""
    mkn = open(os.path.join(THEME_DIR, "data", "htaccess.txt"), encoding="utf-8").read().strip()
    if current is None:
        return mkn + "\n\n" + WP_HTACCESS
    static_sig = "RewriteRule ^insights/?$ /insights.html" in current or "ErrorDocument 404 /404.html" in current
    if not static_sig:
        return None
    blocks, keep, inside = [], [], None
    for line in current.splitlines():
        m = line.strip()
        if m.startswith("# BEGIN "):
            inside = m[len("# BEGIN "):]
        if inside and inside != "MKN ARABIA":
            keep.append(line)
        if m.startswith("# END ") and inside:
            if inside != "MKN ARABIA":
                blocks.append("\n".join(keep))
            keep, inside = [], None
    rest = "\n\n".join(b for b in blocks if b.strip())
    if "# BEGIN WordPress" not in rest:
        rest = (rest + "\n\n" if rest else "") + WP_HTACCESS
    return mkn + "\n\n" + rest.strip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="mknarabia.com")
    ap.add_argument("--admin-email", default="contact@mknarabia.com")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--disable-git-autodeploy", action="store_true",
                    help="remove a Git auto-deployment of the old static site, which would overwrite WordPress on every push")
    a = ap.parse_args()
    token = os.environ.get("HOSTINGER_API_TOKEN", "").strip()
    if not token:
        fail("HOSTINGER_API_TOKEN is not set (add it as a secret in the environment settings).")
    api = Api(token)
    dom = a.domain.lower()
    bad = []

    # 1. website and what it holds
    _, res = api.call("GET", "/api/hosting/v1/websites", {"domain": dom, "per_page": 100})
    site = next((w for w in items(res) if str(w.get("domain", "")).lower() == dom), None)
    if not site:
        fail(f"no website for {dom} in this Hostinger account (create it in hPanel first).")
    user = site.get("username") or (site.get("account") or {}).get("username")
    if not user:
        fail("website found but without a hosting username: " + json.dumps(site)[:300])
    say(f"✓ website {dom} · account {user}")

    _, listing = api.call("GET", f"/api/hosting/v1/accounts/{user}/domains/{dom}/files", {"max_depth": 1, "max_items": 500}, ok=(200, 404))
    names = {str(f.get("name") or f.get("path") or "").strip("/").split("/")[-1] for f in items(listing) if isinstance(f, dict)}
    static_left = sorted(names & STATIC_FILES)
    if static_left:
        say("! files of the old static site are in public_html: " + ", ".join(static_left)
            + " — the theme's .htaccess rules will send their addresses to the WordPress pages")

    _, git = api.call("GET", f"/api/hosting/v1/accounts/{user}/websites/{dom}/git/auto-deployments/settings", ok=(200, 404))
    git = unwrap(git) if isinstance(git, dict) else {}
    if isinstance(git, dict) and git.get("repository") and git.get("is_enabled") is not False:
        msg = f"Git auto-deployment is on ({git.get('repository')} · {git.get('branch')}): each push would overwrite WordPress with static files"
        if a.disable_git_autodeploy and not a.dry_run:
            api.call("DELETE", f"/api/hosting/v1/accounts/{user}/websites/{dom}/git/auto-deployments/settings", ok=(200, 204, 404))
            say("✓ " + msg.split(":")[0] + " — removed")
        elif a.dry_run:
            say("! " + msg + " (run with --disable-git-autodeploy to remove it)")
        else:
            fail(msg + ". Run again with --disable-git-autodeploy, or remove it in hPanel ← Advanced ← Git.")

    # 2. WordPress (exactly this domain, in its document root)
    def installation():
        _, r = api.call("GET", "/api/hosting/v1/wordpress/installations", {"username": user, "domain": dom, "ownership": "all"})
        mine = [i for i in items(r) if str(i.get("domain", "")).lower().rstrip("/") == dom]
        for i in mine:
            d = str(i.get("directory") or i.get("path") or "").strip("/")
            if d in ("", "public_html") or d.endswith("/public_html"):
                return i, mine
        return None, mine

    wp, others = installation()
    if wp:
        say(f"✓ WordPress already installed (id {wp.get('id')})")
    elif others:
        fail("WordPress exists on this domain but not in its main folder: "
             + "; ".join(str(i.get("directory") or i.get("path")) for i in others) + ". Decide which one to use in hPanel.")
    elif a.dry_run:
        say("· would install WordPress (Arabic) on " + dom)
    else:
        pw = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#%^*-_") for _ in range(24))
        os.makedirs(os.path.join(ROOT, ".hostinger"), exist_ok=True)
        with open(os.path.join(ROOT, ".hostinger", "wp-admin.txt"), "w") as f:
            f.write(f"login: mkn-admin\npassword: {pw}\n(change it after the first sign-in)\n")
        os.chmod(os.path.join(ROOT, ".hostinger", "wp-admin.txt"), 0o600)
        api.call("POST", f"/api/hosting/v1/accounts/{user}/wordpress/installations", body={
            "username": user, "domain": dom, "site_title": "MKN ARABIA", "language": "ar", "auto_updates": "minor",
            "credentials": {"email": a.admin_email, "login": "mkn-admin", "password": pw}})
        say("… WordPress install queued; waiting (1–3 minutes)")
        for _ in range(36):
            time.sleep(10)
            wp, _ = installation()
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
        cred = unwrap(cred) if isinstance(cred, dict) else {}
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

        # 4. the old static site's .htaccess rules (one sends /insights/ to insights.html) are removed;
        #    every other block (WordPress, LiteSpeed Cache) is kept
        if static_left:
            current = read_text(api, user, dom, ".htaccess")
            new = clean_htaccess(current)
            if new is not None:
                tus_upload(url, auth, rest, dest=".htaccess", content=new.encode())
                say("✓ .htaccess: old static-site rules removed" + ("" if current is not None else " (file could not be read, so it was rewritten)"))

    # 5. SSL and the HTTPS redirect
    def ssl_state():
        _, s = api.call("GET", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/status")
        return unwrap(s) if isinstance(s, dict) else {}

    s = ssl_state()
    status = str(s.get("status", "")).lower()
    say(f"· SSL status: {status or s}")
    if not a.dry_run:
        if status in ("not_installed", "failed", "expired", ""):
            api.call("POST", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/setup")
            say("… SSL installation requested")
            status = "installing"
        for _ in range(12):
            if status not in ("installing", "waiting_for_retry"):
                break
            time.sleep(15)
            s = ssl_state()
            status = str(s.get("status", "")).lower()
        if status in ("active", "expired"):
            api.call("PATCH", f"/api/hosting/v1/accounts/{user}/websites/{dom}/ssl/https-redirect/toggle",
                     body={"is_enabled": True})
            s = ssl_state()
            red = next((v for k, v in s.items() if "redirect" in k.lower()), None)
            say(f"{'✓' if red else '·'} SSL {status}; HTTPS redirect {'on' if red else 'requested'}")
            if status == "expired":
                bad.append("SSL certificate expired")
        else:
            say(f"✗ SSL not active yet ({status}: {s.get('last_error')}); run the script again later")
            bad.append("SSL " + status)

    if a.dry_run:
        say("dry run finished — nothing was changed.")
        return

    # 6. first visit runs the content import; then clear caches and check
    base = os.environ.get("MKN_SITE_BASE", f"https://{dom}").rstrip("/")  # override only for local testing
    for _ in range(4):
        st, body, _ = http("GET", base + "/?mkn-warmup=" + secrets.token_hex(3))
        if st == 200 and THEME_MARK.encode() in body:
            break
        time.sleep(10)
    if software:
        api.call("POST", f"/api/hosting/v1/accounts/{user}/wordpress/{software}/litespeed-cache/purge", ok=(200, 201, 202, 204, 404, 422))
    api.call("DELETE", f"/api/hosting/v1/accounts/{user}/websites/{dom}/cache/clear", ok=(200, 201, 202, 204, 404, 422))
    checks = {"/": "سوّق بالعربي", "/services/": "D01", "/pricing/": "اطلب عرض سعر", "/work/": "أعمال مختارة.",
              "/testimonials/": "آراء العملاء.", "/insights/": "مقالات لأصحاب الأعمال", "/about/": "د. نور الدين",
              "/contact/": "contact-form", "/privacy/": "سياسة الخصوصية"}
    for path, needle in checks.items():
        st, body, _ = http("GET", base + path)
        text = body.decode(errors="replace")
        good = st == 200 and needle in text and THEME_MARK in text
        say(f"  {'✓' if good else '✗'} {path} ({st})")
        if not good:
            bad.append(path)
    st, body, _ = http("GET", base + "/wp-sitemap.xml")
    say(f"  {'✓' if st == 200 and b'<sitemapindex' in body else '✗'} /wp-sitemap.xml ({st})")
    if not (st == 200 and b"<sitemapindex" in body):
        bad.append("/wp-sitemap.xml")
    st, _, hdr = http("GET", base + "/services.html", follow=False)
    loc = {k.lower(): v for k, v in hdr.items()}.get("location", "")
    good = st == 301 and loc.rstrip("/").endswith("/services")
    say(f"  {'✓' if good else '✗'} old address services.html → /services/ ({st} {loc})")
    if not good:
        bad.append("services.html redirect")
    st, _, _ = http("POST", base + "/wp-json/mkn/v1/lead", b"name=", {"Content-Type": "application/x-www-form-urlencoded", "Origin": base})
    say(f"  {'✓' if st == 422 else '✗'} lead endpoint answers ({st}, expected 422 for an empty brief)")
    if st != 422:
        bad.append("lead endpoint")
    if "MKN_SITE_BASE" not in os.environ:
        st, _, hdr = http("GET", f"http://{dom}/", follow=False)
        loc = {k.lower(): v for k, v in hdr.items()}.get("location", "")
        good = st in (301, 302, 307, 308) and loc.startswith("https://" + dom)
        say(f"  {'✓' if good else '✗'} http → https ({st} {loc})")
        if not good:
            bad.append("http → https redirect")

    # 7. record
    os.makedirs(os.path.join(ROOT, ".hostinger"), exist_ok=True)
    meta_path = os.path.join(ROOT, ".hostinger", "site.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    meta.update({"domain": dom, "username": user, "type": "wordpress", "theme": SLUG, "software": software})
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    if bad:
        fail("not everything is right yet: " + ", ".join(bad))
    say("✓ done — https://" + dom)


if __name__ == "__main__":
    main()
