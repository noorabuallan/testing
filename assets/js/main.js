/* MKN Arabia — main script */
(function () {
  // ===== إعدادات التواصل — عدّلها هنا =====
  var WHATSAPP_NUMBER = "201140552627"; // رقم واتساب بالصيغة الدولية بدون + أو 00
  var EMAIL = "contact@mknarabia.com";

  // Header on scroll
  var header = document.querySelector(".header");
  function onScroll() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 30);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
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

  // Glass spotlight: light follows the pointer on glass cards (desktop only)
  if (window.matchMedia && window.matchMedia("(hover: hover)").matches) {
    document.addEventListener("pointermove", function (ev) {
      var el = ev.target.closest && ev.target.closest(".spot");
      if (!el) return;
      var r = el.getBoundingClientRect();
      el.style.setProperty("--mx", (ev.clientX - r.left) + "px");
      el.style.setProperty("--my", (ev.clientY - r.top) + "px");
    }, { passive: true });
  }

  // Current year
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // WhatsApp / email links — every message carries the visit source (UTM) as a reference line
  function srcRef() { return window.MKN ? "\n\n— مرجع: " + window.MKN.ref() : ""; }
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

  // Pricing tabs
  var tabs = document.querySelectorAll("[role=tab]");
  function selectTab(t) {
    tabs.forEach(function (x) {
      var on = x === t;
      x.setAttribute("aria-selected", on ? "true" : "false");
      x.tabIndex = on ? 0 : -1;
      var p = document.getElementById(x.getAttribute("aria-controls"));
      if (p) p.hidden = !on;
    });
  }
  tabs.forEach(function (t) {
    t.addEventListener("click", function () { selectTab(t); });
  });
  if (tabs.length && location.hash) {
    var target = document.querySelector('[role=tab][data-key="' + location.hash.slice(1) + '"]');
    if (target) selectTab(target);
  }

  // Contact form -> WhatsApp message
  var form = document.getElementById("contact-form");
  if (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var d = new FormData(form);
      var lines = [
        "طلب جديد من موقع MKN ARABIA",
        "الاسم: " + (d.get("name") || ""),
        "الشركة: " + (d.get("company") || "-"),
        "الهاتف: " + (d.get("phone") || ""),
        "البريد: " + (d.get("email") || "-"),
        "الدولة: " + (d.get("country") || ""),
        "القسم المطلوب: " + (d.get("service") || ""),
        "الموعد المتوقع: " + (d.get("timing") || "-"),
        "الميزانية: " + (d.get("budget") || "-"),
        "الهدف والأصول المتاحة: " + (d.get("message") || "-")
      ];
      var a = window.MKN ? window.MKN.attribution() : {};
      lines.push("", "— المصدر: " + [a.utm_source, a.utm_medium, a.utm_campaign, a.utm_content].filter(Boolean).join(" / "),
                 "— صفحة الدخول: " + (a.landing_page || location.pathname));
      if (window.MKN) window.MKN.track("generate_lead", {
        form_id: "contact", method: "whatsapp", department: d.get("service") || "", market: d.get("country") || "",
        budget_range: d.get("budget") || "", timing: d.get("timing") || "", content_name: d.get("service") || ""
      });
      var url = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
      window.open(url, "_blank", "noopener");
      var ok = document.querySelector(".form-success");
      if (ok) ok.classList.add("show");
      form.reset();
    });
  }
})();
