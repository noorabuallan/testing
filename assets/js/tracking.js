/* =========================================================
   MKN ARABIA — Tracking & attribution
   ---------------------------------------------------------
   1) ضع المعرّفات في CONFIG (اترك أي حقل فارغًا لتعطيله).
   2) الوضع المفضّل: GTM_ID فقط — كل الأحداث تُدفع إلى dataLayer
      وتُدار وسوم GA4 و Meta و TikTok و Google Ads من داخل GTM.
   3) بدون GTM: يُحمَّل GA4 والبكسلات مباشرة وتُرسل لها الأحداث.
   تفاصيل الأحداث والمعاملات: TRACKING.md
   ========================================================= */
(function () {
  var CONFIG = {
    GTM_ID: "",               // مثال: "GTM-XXXXXXX"
    GA4_ID: "",               // مثال: "G-XXXXXXXXXX"  (يُستخدم فقط إذا كان GTM_ID فارغًا)
    GOOGLE_ADS_ID: "",        // مثال: "AW-123456789"
    GOOGLE_ADS_LEAD_LABEL: "",     // تسمية تحويل "طلب/نموذج"
    GOOGLE_ADS_WHATSAPP_LABEL: "", // تسمية تحويل "نقرة واتساب"
    META_PIXEL_ID: "",        // مثال: "123456789012345"
    TIKTOK_PIXEL_ID: "",      // مثال: "CXXXXXXXXXXXXXXX"
    ATTRIBUTION_DAYS: 90      // مدة الاحتفاظ بمصدر الزيارة
  };

  var w = window, d = document;
  w.dataLayer = w.dataLayer || [];
  var DIRECT = !CONFIG.GTM_ID;

  /* ---------- safe storage ---------- */
  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function load(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } }

  /* ---------- attribution (first & last touch) ---------- */
  var KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
              "gclid", "gbraid", "wbraid", "fbclid", "ttclid", "msclkid", "li_fat_id"];
  var CLICK_IDS = { gclid: ["google", "cpc"], gbraid: ["google", "cpc"], wbraid: ["google", "cpc"],
                    fbclid: ["facebook", "paid_social"], ttclid: ["tiktok", "paid_social"],
                    msclkid: ["bing", "cpc"], li_fat_id: ["linkedin", "paid_social"] };
  var SEARCH = /(^|\.)(google|bing|yahoo|duckduckgo|yandex|baidu|ecosia)\./i;
  var SOCIAL = /(facebook|instagram|fb\.|t\.co|twitter|x\.com|linkedin|lnkd|tiktok|snapchat|youtube|pinterest|whatsapp)/i;

  function now() { return Date.now(); }
  function fresh(t) { return t && (now() - t.ts) < CONFIG.ATTRIBUTION_DAYS * 864e5; }

  function readTouch() {
    var q = new URLSearchParams(location.search), t = {}, has = false;
    KEYS.forEach(function (k) { var v = q.get(k); if (v) { t[k] = v.trim().slice(0, 150); has = true; } });
    if (has) {
      // click id without utm → infer source/medium
      if (!t.utm_source) {
        for (var id in CLICK_IDS) if (t[id]) { t.utm_source = CLICK_IDS[id][0]; t.utm_medium = t.utm_medium || CLICK_IDS[id][1]; break; }
      }
      return t;
    }
    var ref = d.referrer, host = "";
    try { host = ref ? new URL(ref).hostname : ""; } catch (e) {}
    if (host && host !== location.hostname) {
      if (SEARCH.test(host)) return { utm_source: host.match(SEARCH)[2].toLowerCase(), utm_medium: "organic" };
      if (SOCIAL.test(host)) return { utm_source: host.replace(/^www\.|^l\.|^lm\.|^m\./, ""), utm_medium: "social" };
      return { utm_source: host.replace(/^www\./, ""), utm_medium: "referral" };
    }
    return null;
  }

  var touch = readTouch();
  var first = load("mkn_first_touch"), last = load("mkn_last_touch");
  if (touch) {
    touch.landing_page = location.pathname;
    touch.ts = now();
    last = touch; store("mkn_last_touch", last);
    if (!fresh(first)) { first = touch; store("mkn_first_touch", first); }
  }
  if (!fresh(last)) last = null;
  if (!fresh(first)) first = null;

  function attribution() {
    var l = last || {}, f = first || {};
    return {
      utm_source: l.utm_source || "(direct)", utm_medium: l.utm_medium || "(none)",
      utm_campaign: l.utm_campaign || "", utm_term: l.utm_term || "", utm_content: l.utm_content || "",
      gclid: l.gclid || "", fbclid: l.fbclid || "", ttclid: l.ttclid || "",
      landing_page: l.landing_page || location.pathname,
      first_source: f.utm_source || l.utm_source || "(direct)", first_medium: f.utm_medium || l.utm_medium || "(none)",
      first_campaign: f.utm_campaign || ""
    };
  }

  /* short source code appended to WhatsApp messages — only for tracked visits (campaign, search, social, referral);
     direct visits add nothing, so the visitor never sees technical text like "(direct) / (none)" */
  function ref() {
    if (!last) return "";
    var a = attribution();
    var parts = [a.utm_source, a.utm_medium];
    if (a.utm_campaign) parts.push(a.utm_campaign);
    if (a.utm_content) parts.push(a.utm_content);
    return parts.join("/");
  }

  /* ---------- loaders ---------- */
  function script(src) { var s = d.createElement("script"); s.async = true; s.src = src; d.head.appendChild(s); }

  if (CONFIG.GTM_ID) {
    w.dataLayer.push({ "gtm.start": now(), event: "gtm.js" });
    script("https://www.googletagmanager.com/gtm.js?id=" + CONFIG.GTM_ID);
  }

  function gtag() { w.dataLayer.push(arguments); }
  if (DIRECT && (CONFIG.GA4_ID || CONFIG.GOOGLE_ADS_ID)) {
    script("https://www.googletagmanager.com/gtag/js?id=" + (CONFIG.GA4_ID || CONFIG.GOOGLE_ADS_ID));
    gtag("js", new Date());
    var a0 = attribution();
    if (CONFIG.GA4_ID) gtag("config", CONFIG.GA4_ID, {
      user_properties: { first_source: a0.first_source, first_medium: a0.first_medium, first_campaign: a0.first_campaign }
    });
    if (CONFIG.GOOGLE_ADS_ID) gtag("config", CONFIG.GOOGLE_ADS_ID);
  }

  if (DIRECT && CONFIG.META_PIXEL_ID) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(w, d, "script", "https://connect.facebook.net/en_US/fbevents.js");
    w.fbq("init", CONFIG.META_PIXEL_ID); w.fbq("track", "PageView");
  }

  if (DIRECT && CONFIG.TIKTOK_PIXEL_ID) {
    !function (w2, d2, t) { w2.TiktokAnalyticsObject = t; var ttq = w2[t] = w2[t] || [];
      ttq.methods = ["page", "track", "identify", "instances", "debug", "on", "off", "once", "ready", "alias", "group", "enableCookie", "disableCookie"];
      ttq.setAndDefer = function (o, m) { o[m] = function () { o.push([m].concat(Array.prototype.slice.call(arguments, 0))); }; };
      for (var i = 0; i < ttq.methods.length; i++) ttq.setAndDefer(ttq, ttq.methods[i]);
      ttq.load = function (id) { var s = d2.createElement("script"); s.async = true; s.src = "https://analytics.tiktok.com/i18n/pixel/events.js?sdkid=" + id + "&lib=" + t;
        var x = d2.getElementsByTagName("script")[0]; x.parentNode.insertBefore(s, x); };
      ttq.load(CONFIG.TIKTOK_PIXEL_ID); ttq.page(); }(w, d, "ttq");
  }

  /* ---------- event API ---------- */
  var PIXEL_MAP = {
    generate_lead:  { meta: "Lead",    tiktok: "SubmitForm", ads: "GOOGLE_ADS_LEAD_LABEL" },
    quote_request:  { meta: "Lead",    tiktok: "SubmitForm", ads: "GOOGLE_ADS_LEAD_LABEL" },
    whatsapp_click: { meta: "Contact", tiktok: "Contact",    ads: "GOOGLE_ADS_WHATSAPP_LABEL" },
    email_click:    { meta: "Contact", tiktok: "Contact" },
    phone_click:    { meta: "Contact", tiktok: "Contact" }
  };

  function track(event, params) {
    var p = Object.assign({}, params || {}, attribution(), { page_path: location.pathname });
    w.dataLayer.push(Object.assign({ event: event }, p));
    if (!DIRECT) return;
    if (CONFIG.GA4_ID) gtag("event", event, p);
    var m = PIXEL_MAP[event];
    if (!m) return;
    if (w.fbq && m.meta) w.fbq("track", m.meta, { content_name: p.content_name || event, content_category: p.department || p.link_location || "" });
    if (w.ttq && m.tiktok) w.ttq.track(m.tiktok, { content_name: p.content_name || event });
    if (CONFIG.GOOGLE_ADS_ID && m.ads && CONFIG[m.ads]) gtag("event", "conversion", { send_to: CONFIG.GOOGLE_ADS_ID + "/" + CONFIG[m.ads] });
  }

  w.MKN = { track: track, attribution: attribution, ref: ref, config: CONFIG };

  /* ---------- automatic interaction tracking ---------- */
  function locationOf(el) {
    if (el.closest(".wa-float")) return "floating_button";
    if (el.closest(".header")) return "header";
    if (el.closest(".footer")) return "footer";
    var sec = el.closest("section");
    if (sec) {
      if (sec.id) return sec.id;
      var lab = sec.querySelector(".label");
      if (lab) return lab.textContent.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 40);
    }
    return "body";
  }
  function txt(el) { return (el.getAttribute("aria-label") || el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80); }

  d.addEventListener("click", function (ev) {
    var sm = ev.target.closest("summary");
    if (sm && sm.parentElement && !sm.parentElement.open) track("faq_open", { question: txt(sm) });
    var a = ev.target.closest("a, button");
    if (!a) return;
    var href = a.getAttribute("href") || "", loc = locationOf(a);
    if (a.hasAttribute("data-quote")) {
      track("quote_request", { package_id: a.getAttribute("data-quote"), content_name: a.getAttribute("data-quote-name") || "",
                               department: a.getAttribute("data-dept") || "", method: "whatsapp", link_location: loc });
    }
    // booking link clicks (a click is NOT a confirmed booking — the booking itself happens on Google Calendar)
    if (a.hasAttribute("data-book") || /calendar\.app\.google|calendar\.google\.com\/calendar\/appointments/i.test(href)) {
      track("booking_click", { link_location: loc, link_text: txt(a) });
      return;
    }
    if (a.hasAttribute("data-wa") || /wa\.me|whatsapp/i.test(href)) {
      track("whatsapp_click", { link_location: loc, link_text: txt(a), content_name: a.getAttribute("data-quote-name") || "" });
    } else if (/^mailto:/i.test(href) || a.hasAttribute("data-email")) {
      track("email_click", { link_location: loc });
    } else if (/^tel:/i.test(href)) {
      track("phone_click", { link_location: loc });
    } else if (/instagram|linkedin|facebook|tiktok|x\.com|twitter|youtube|snapchat/i.test(href)) {
      track("social_click", { platform: (href.match(/instagram|linkedin|facebook|tiktok|x\.com|twitter|youtube|snapchat/i) || [""])[0].toLowerCase(), link_location: loc });
    } else if (a.getAttribute("role") === "tab") {
      track("select_content", { content_type: "package_department", item_id: a.getAttribute("data-key") || "" });
    } else if (a.type !== "submit" && (a.classList.contains("btn") || a.classList.contains("cell"))) {
      track("cta_click", { link_text: txt(a), link_url: href, link_location: loc });
    }
  }, true);

  // form start (first interaction)
  d.addEventListener("focusin", function (ev) {
    var f = ev.target.closest && ev.target.closest("form");
    if (f && !f.__started) { f.__started = true; track("form_start", { form_id: f.id || "form" }); }
  });

  // scroll depth 25/50/75/90
  var marks = [25, 50, 75, 90], hit = {};
  function onScroll() {
    var h = d.documentElement, max = h.scrollHeight - h.clientHeight;
    if (max <= 0) return;
    var pct = Math.round((w.scrollY / max) * 100);
    marks.forEach(function (m) { if (pct >= m && !hit[m]) { hit[m] = true; track("scroll_depth", { percent_scrolled: m }); } });
  }
  w.addEventListener("scroll", onScroll, { passive: true });

  // case study views
  d.addEventListener("DOMContentLoaded", function () {
    if (!("IntersectionObserver" in w)) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { io.unobserve(e.target); track("view_case", { case_id: e.target.id, content_name: (e.target.querySelector("h2") || {}).textContent || "" }); }
      });
    }, { threshold: 0.4 });
    d.querySelectorAll("article.case[id]").forEach(function (el) { io.observe(el); });
  });
})();
