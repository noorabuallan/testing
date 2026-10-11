/* MKN Arabia — main script */
(function () {
  // ===== إعدادات التواصل — عدّلها هنا =====
  var WHATSAPP_NUMBER = "201140552627"; // رقم واتساب بالصيغة الدولية بدون + أو 00
  var EMAIL = "contact@mknarabia.com";

  var html = document.documentElement, body = document.body;
  var mqMobile = window.matchMedia ? window.matchMedia("(max-width: 640px)") : { matches: false, addEventListener: function () {} };
  function onMQ(mq, fn) { if (mq.addEventListener) mq.addEventListener("change", fn); else if (mq.addListener) mq.addListener(fn); }

  // Header on scroll
  var header = document.querySelector(".header");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 30);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile nav: a real dialog-like overlay (focus moves in, Escape closes, page behind is inert)
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  var behind = [document.querySelector("main"), document.querySelector(".footer"), document.querySelector(".wa-float"), document.querySelector(".skip-link")];
  function setNav(open) {
    body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "إغلاق القائمة" : "فتح القائمة");
    html.style.overflow = open ? "hidden" : "";
    behind.forEach(function (el) { if (el) el.inert = open; });
    if (open) setTimeout(function () { var first = nav.querySelector("a"); if (first) first.focus(); }, 60); // after the overlay becomes visible
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = !body.classList.contains("nav-open");
      setNav(open);
      if (!open) toggle.focus();
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { if (body.classList.contains("nav-open")) setNav(false); });
    });
    nav.addEventListener("click", function (e) { if (e.target === nav) { setNav(false); toggle.focus(); } });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("nav-open")) { setNav(false); toggle.focus(); }
    });
  }

  // Reveal on scroll
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("in"); });
  }

  // Glass spotlight: light follows the pointer on glass cards (desktop only, at most once per frame)
  if (window.matchMedia && window.matchMedia("(hover: hover)").matches) {
    var spotEv = null;
    document.addEventListener("pointermove", function (ev) {
      if (spotEv) { spotEv = ev; return; }
      spotEv = ev;
      requestAnimationFrame(function () {
        var e = spotEv; spotEv = null;
        var el = e.target.closest && e.target.closest(".spot");
        if (!el) return;
        var r = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - r.left) + "px");
        el.style.setProperty("--my", (e.clientY - r.top) + "px");
      });
    }, { passive: true });
  }

  // Current year
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // WhatsApp / email links — campaign visits carry a short source code so the lead can be attributed
  function srcRef() { var r = window.MKN ? window.MKN.ref() : ""; return r ? "\n\n— رمز المصدر: " + r : ""; }
  function waUrl(msg) { return "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(msg + srcRef()); }
  document.querySelectorAll("[data-wa]").forEach(function (el) {
    var msg = el.getAttribute("data-wa") || "مرحباً MKN ARABIA، أرغب بالاستفسار عن خدماتكم";
    el.setAttribute("href", waUrl(msg));
    el.setAttribute("target", "_blank");
    el.setAttribute("rel", "noopener");
  });
  document.querySelectorAll("[data-email]").forEach(function (el) {
    el.setAttribute("href", "mailto:" + EMAIL);
    if (!el.textContent.trim()) el.textContent = EMAIL;
  });

  // Horizontal carousels (mobile): focusable, named regions only while they actually scroll
  function swipes() {
    document.querySelectorAll(".swipe").forEach(function (s) {
      var on = mqMobile.matches && s.scrollWidth > s.clientWidth + 4;
      if (on) {
        s.tabIndex = 0; s.setAttribute("role", "region");
        if (s.dataset.lb) s.setAttribute("aria-labelledby", s.dataset.lb);
      } else {
        s.removeAttribute("tabindex"); s.removeAttribute("role"); s.removeAttribute("aria-labelledby");
      }
    });
  }
  swipes(); onMQ(mqMobile, swipes); window.addEventListener("load", swipes);

  // Pricing tabs (WAI-ARIA tabs: arrows / Home / End, RTL-aware)
  var tabs = [].slice.call(document.querySelectorAll("[role=tab]"));
  function selectTab(t) {
    tabs.forEach(function (x) {
      var on = x === t;
      x.setAttribute("aria-selected", on ? "true" : "false");
      x.tabIndex = on ? 0 : -1;
      var p = document.getElementById(x.getAttribute("aria-controls"));
      if (p) p.hidden = !on;
    });
    swipes(); // the newly shown panel may scroll horizontally on phones
    var strip = t.parentNode;
    if (strip.scrollWidth > strip.clientWidth + 4) {
      strip.scrollTo({ left: t.offsetLeft - (strip.clientWidth - t.offsetWidth) / 2, behavior: "smooth" });
    }
  }
  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      selectTab(t);
      if (history.replaceState) history.replaceState(null, "", "#" + t.dataset.key);
    });
  });
  var tablist = document.querySelector("[role=tablist]");
  if (tablist) {
    tablist.addEventListener("keydown", function (e) {
      var i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      var rtl = getComputedStyle(tablist).direction === "rtl", n = null;
      if (e.key === (rtl ? "ArrowLeft" : "ArrowRight")) n = (i + 1) % tabs.length;
      else if (e.key === (rtl ? "ArrowRight" : "ArrowLeft")) n = (i - 1 + tabs.length) % tabs.length;
      else if (e.key === "Home") n = 0;
      else if (e.key === "End") n = tabs.length - 1;
      if (n === null) return;
      e.preventDefault();
      tabs[n].focus();
      tabs[n].click();
    });
  }
  function tabFromHash() {
    var target = location.hash && document.querySelector('[role=tab][data-key="' + location.hash.slice(1) + '"]');
    if (!target) return;
    selectTab(target);
    requestAnimationFrame(function () { tablist.scrollIntoView({ block: "start" }); });
  }
  if (tabs.length) { tabFromHash(); window.addEventListener("hashchange", tabFromHash); }

  // Sticky jump navs: highlight the section in view and keep its chip visible
  document.querySelectorAll(".jump").forEach(function (jump) {
    if (!("IntersectionObserver" in window)) return;
    var links = [].slice.call(jump.querySelectorAll('a[href^="#"]'));
    var map = {};
    links.forEach(function (a) { var el = document.getElementById(a.getAttribute("href").slice(1)); if (el) map[el.id] = a; });
    var current = null;
    var jio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var a = map[e.target.id];
        if (!a || a === current) return;
        if (current) { current.classList.remove("is-active"); current.removeAttribute("aria-current"); }
        current = a; a.classList.add("is-active"); a.setAttribute("aria-current", "location");
        if (jump.scrollWidth > jump.clientWidth + 4) {
          jump.scrollTo({ left: a.offsetLeft - (jump.clientWidth - a.offsetWidth) / 2, behavior: "smooth" });
        }
      });
    }, { rootMargin: "-35% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { jio.observe(document.getElementById(id)); });
  });

  // Testimonials: "show all" per country on phones
  document.querySelectorAll("[data-more]").forEach(function (b) {
    b.addEventListener("click", function () {
      var g = b.closest(".tgroup");
      if (g) g.classList.add("is-open");
      b.remove();
    });
  });

  // Footer service list: open on desktop, collapsible on phones
  function footerDepts() {
    document.querySelectorAll(".fdepts").forEach(function (d) { d.open = !mqMobile.matches; });
  }
  footerDepts(); onMQ(mqMobile, footerDepts);

  // Pause / play the moving logo rails and marquee (WCAG 2.2.2)
  var mt = document.querySelectorAll(".motion-toggle");
  function setMotion(paused) {
    html.classList.toggle("motion-paused", paused);
    mt.forEach(function (b) {
      b.setAttribute("aria-pressed", paused ? "true" : "false");
      b.textContent = paused ? "تشغيل الحركة" : "إيقاف الحركة";
    });
  }
  var paused0 = false;
  try { paused0 = localStorage.getItem("mkn_motion") === "paused"; } catch (e) {}
  setMotion(paused0);
  mt.forEach(function (b) {
    b.addEventListener("click", function () {
      var p = !html.classList.contains("motion-paused");
      setMotion(p);
      try { localStorage.setItem("mkn_motion", p ? "paused" : "on"); } catch (e) {}
    });
  });

  // Floating WhatsApp button steps aside where a WhatsApp action is already on screen
  if ("IntersectionObserver" in window) {
    var visible = 0;
    var fio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && !e.target.__in) { e.target.__in = true; visible++; }
        else if (!e.isIntersecting && e.target.__in) { e.target.__in = false; visible--; }
      });
      body.classList.toggle("wa-hide", visible > 0);
    });
    document.querySelectorAll("#contact-form, .cta, .prose-cta, .footer").forEach(function (el) { fio.observe(el); });
  }

  // Contact form → WhatsApp message (data stays in the form; inline Arabic validation)
  var form = document.getElementById("contact-form");
  if (form) {
    var RULES = {
      name: function (v) { return v.trim().length >= 2 ? "" : "يرجى كتابة اسمك الكامل"; },
      phone: function (v) {
        var n = v.replace(/[٠-٩]/g, function (d) { return d.charCodeAt(0) - 1632; }).replace(/[۰-۹]/g, function (d) { return d.charCodeAt(0) - 1776; });
        return /^\+?[0-9\s\-()]{8,18}$/.test(n.trim()) ? "" : "يرجى إدخال رقم هاتف صحيح مع رمز الدولة، مثل ‎+966 5X XXX XXXX";
      },
      country: function (v) { return v ? "" : "يرجى اختيار السوق المستهدف"; },
      service: function (v) { return v ? "" : "يرجى اختيار الخدمة المطلوبة"; },
      email: function (v) { return !v.trim() || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? "" : "يرجى إدخال بريد إلكتروني صحيح مثل name@company.com"; }
    };
    function check(name) {
      var input = form.elements[name], err = document.getElementById("e-" + name);
      if (!input || !err) return true;
      var msg = RULES[name](input.value || "");
      if (msg) {
        input.setAttribute("aria-invalid", "true"); input.setAttribute("aria-describedby", err.id);
        err.textContent = msg; err.hidden = false;
      } else {
        input.removeAttribute("aria-invalid"); input.removeAttribute("aria-describedby");
        err.textContent = ""; err.hidden = true;
      }
      return !msg;
    }
    Object.keys(RULES).forEach(function (n) {
      var input = form.elements[n];
      if (input) input.addEventListener(input.tagName === "SELECT" ? "change" : "input", function () {
        if (input.getAttribute("aria-invalid")) check(n);
      });
    });
    var ok = form.querySelector(".form-success"), alt = form.querySelector(".form-alt");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var bad = Object.keys(RULES).filter(function (n) { return !check(n); });
      if (bad.length) { form.elements[bad[0]].focus(); return; }
      var d = new FormData(form);
      var lines = [
        "طلب جديد من موقع MKN ARABIA",
        "الاسم: " + (d.get("name") || ""),
        "الشركة: " + (d.get("company") || "-"),
        "الهاتف: " + (d.get("phone") || ""),
        "البريد: " + (d.get("email") || "-"),
        "الدولة: " + (d.get("country") || ""),
        "الخدمة المطلوبة: " + (d.get("service") || ""),
        "الموعد المتوقع: " + (d.get("timing") || "-"),
        "الميزانية: " + (d.get("budget") || "-"),
        "الهدف والأصول المتاحة: " + (d.get("message") || "-")
      ];
      var r = window.MKN ? window.MKN.ref() : "";
      if (r) lines.push("", "— رمز المصدر: " + r, "— صفحة الدخول: " + (window.MKN.attribution().landing_page || location.pathname));
      var text = lines.join("\n");
      if (window.MKN) window.MKN.track("generate_lead", {
        form_id: "contact", method: "whatsapp", department: d.get("service") || "", market: d.get("country") || "",
        budget_range: d.get("budget") || "", timing: d.get("timing") || "", content_name: d.get("service") || ""
      });
      var url = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(text);
      window.open(url, "_blank", "noopener");
      if (ok) {
        ok.textContent = "فتحنا واتساب برسالتك الجاهزة — اضغط «إرسال» هناك لإتمام الطلب. إن لم يفتح واتساب، استخدم أحد الخيارات أدناه.";
        ok.classList.add("show");
      }
      if (alt) {
        alt.hidden = false;
        document.getElementById("wa-retry").setAttribute("href", url);
        document.getElementById("mail-alt").setAttribute("href", "mailto:" + EMAIL + "?subject=" + encodeURIComponent("طلب من الموقع — " + (d.get("name") || "")) + "&body=" + encodeURIComponent(text));
        var copy = document.getElementById("copy-brief");
        copy.onclick = function () {
          try { navigator.clipboard.writeText(text).then(function () { copy.textContent = "تم النسخ ✓"; }); } catch (e) {}
        };
      }
    });
  }
})();
