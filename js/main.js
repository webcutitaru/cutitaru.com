(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var docEl = document.documentElement;
  var header = document.querySelector(".site-header");
  var backTop = document.querySelector(".back-top");
  var progressPath = document.getElementById("scroll-progress-path");
  var progressSvg = progressPath ? progressPath.closest(".scroll-progress-ring") : null;
  var navInner = document.querySelector(".site-header .nav-inner");
  var RING_STROKE = 2.5;
  /** Reflow ring when only `border-radius` media rule changes (width/height may stay equal). */
  var navRadiusMedia = window.matchMedia("(max-width: 1024px)");

  function parseRadiusPx(el) {
    if (!el) return 0;
    var b = getComputedStyle(el).borderTopLeftRadius;
    var first = b.split(/\s+/)[0];
    var px = parseFloat(first);
    return isNaN(px) ? 0 : px;
  }

  /**
   * Scroll ring = same outline as `.nav-inner` border-box (CSS `border-radius` on that box).
   * Path sits on the outer edge of the box in layout px (offsetWidth/offsetHeight include 1px border
   * with box-sizing: border-box). SVG stroke is centered on the path (half stroke in/out).
   * Arc sweep-flag 0 (not 1): with y-down coords, sweep=1 drew corners concave vs CSS border-radius.
   */
  function buildRoundedRectOutlinePath(w, h, r) {
    var rEff = Math.min(r, w / 2, h / 2);
    var x0 = 0;
    var y0 = 0;
    var x1 = w;
    var y1 = h;
    var rw = w;
    var rh = h;
    if (rEff < 0.5) {
      return (
        "M" +
        x0 +
        "," +
        rh / 2 +
        "L" +
        x0 +
        "," +
        y1 +
        "L" +
        x1 +
        "," +
        y1 +
        "L" +
        x1 +
        "," +
        y0 +
        "L" +
        x0 +
        "," +
        y0 +
        "L" +
        x0 +
        "," +
        rh / 2
      );
    }
    return (
      "M" +
      x0 +
      "," +
      (y0 + rh / 2) +
      "L" +
      x0 +
      "," +
      (y1 - rEff) +
      "A" +
      rEff +
      "," +
      rEff +
      " 0 0 0 " +
      (x0 + rEff) +
      "," +
      y1 +
      "L" +
      (x1 - rEff) +
      "," +
      y1 +
      "A" +
      rEff +
      "," +
      rEff +
      " 0 0 0 " +
      x1 +
      "," +
      (y1 - rEff) +
      "L" +
      x1 +
      "," +
      (y0 + rEff) +
      "A" +
      rEff +
      "," +
      rEff +
      " 0 0 0 " +
      (x1 - rEff) +
      "," +
      y0 +
      "L" +
      (x0 + rEff) +
      "," +
      y0 +
      "A" +
      rEff +
      "," +
      rEff +
      " 0 0 0 " +
      x0 +
      "," +
      (y0 + rEff) +
      "L" +
      x0 +
      "," +
      (y0 + rh / 2)
    );
  }

  function updateScrollRingPath() {
    if (!progressPath || !progressSvg || !navInner) return;
    var w = navInner.offsetWidth;
    var h = navInner.offsetHeight;
    if (w < 4 || h < 4) return;

    navInner.style.clipPath = "";
    navInner.style.webkitClipPath = "";

    var rCss = parseRadiusPx(navInner);
    var d = buildRoundedRectOutlinePath(w, h, rCss);
    progressPath.setAttribute("d", d);
    var pad = Math.ceil(RING_STROKE / 2 + 2);
    progressSvg.setAttribute(
      "viewBox",
      -pad + " " + -pad + " " + (w + 2 * pad) + " " + (h + 2 * pad)
    );
    progressSvg.setAttribute("preserveAspectRatio", "none");
  }

  function onScroll() {
    if (header) {
      if (window.scrollY > 40) {
        header.classList.add("is-scrolled");
      } else {
        header.classList.remove("is-scrolled");
      }
    }

    if (progressPath) {
      var scrollable = docEl.scrollHeight - window.innerHeight;
      var pct = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
      pct = Math.min(100, Math.max(0, pct));
      docEl.style.setProperty("--scroll-n", String(pct));
    }
  }

  if (navInner && progressPath && progressSvg) {
    var ringResize = new ResizeObserver(function () {
      updateScrollRingPath();
    });
    ringResize.observe(navInner);
    window.addEventListener("load", updateScrollRingPath);
    updateScrollRingPath();
    requestAnimationFrame(updateScrollRingPath);
    if (navRadiusMedia.addEventListener) {
      navRadiusMedia.addEventListener("change", updateScrollRingPath);
    } else if (navRadiusMedia.addListener) {
      navRadiusMedia.addListener(updateScrollRingPath);
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (backTop) {
    backTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      var id = anchor.getAttribute("href");
      if (!id || id === "#") return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({
        behavior: reduceMotion ? "auto" : "smooth",
        block: "start",
      });
      history.pushState(null, "", id);
    });
  });

  var params = new URLSearchParams(window.location.search);
  var sentParam = params.get("sent");
  var contactToast = document.querySelector("[data-contact-toast]");
  var contactToastTitle = contactToast ? contactToast.querySelector("#contact-toast-title") : null;
  var contactToastClose = contactToast ? contactToast.querySelector("[data-contact-toast-close]") : null;
  var contactToastBackdrop = contactToast ? contactToast.querySelector("[data-contact-toast-dismiss]") : null;
  var contactToastPrevFocus = null;

  function stripSentFromUrl() {
    try {
      var u = new URL(window.location.href);
      if (u.searchParams.has("sent")) {
        u.searchParams.delete("sent");
        var next = u.pathname + (u.search || "") + (u.hash || "");
        window.history.replaceState({}, document.title, next);
      }
    } catch (err1) {
      try {
        var path = window.location.pathname || "/";
        var hash = window.location.hash || "";
        window.history.replaceState({}, document.title, path + hash);
      } catch (err2) {}
    }
  }

  function closeContactToast() {
    if (!contactToast) return;
    contactToast.classList.remove("is-open", "contact-toast--ok", "contact-toast--err");
    contactToast.hidden = true;
    contactToast.setAttribute("hidden", "");
    contactToast.setAttribute("aria-hidden", "true");
    if (contactToastPrevFocus && typeof contactToastPrevFocus.focus === "function") {
      contactToastPrevFocus.focus();
    }
    contactToastPrevFocus = null;
  }

  function openContactToast(kind, message) {
    if (!contactToast || !contactToastTitle) return;
    contactToastPrevFocus = document.activeElement;
    contactToast.removeAttribute("hidden");
    contactToast.hidden = false;
    contactToast.setAttribute("aria-hidden", "false");
    contactToast.classList.remove("contact-toast--ok", "contact-toast--err");
    contactToast.classList.add("is-open", kind === "err" ? "contact-toast--err" : "contact-toast--ok");
    contactToastTitle.textContent = message;
    requestAnimationFrame(function () {
      try {
        if (contactToastClose) {
          contactToastClose.focus();
        }
      } catch (focusErr) {}
    });
  }

  function maybeOpenSentToast(sentVal) {
    var s = sentVal !== undefined && sentVal !== null ? sentVal : sentParam;
    if (!contactToast || (s !== "1" && s !== "0")) return;
    var toastMsg =
      s === "1"
        ? contactToast.getAttribute("data-ok-message") ||
          contactToast.dataset.okMessage ||
          "Your message was sent.\nThank you!"
        : contactToast.getAttribute("data-err-message") ||
          contactToast.dataset.errMessage ||
          "We couldn’t send your message. Please try again or email me directly.";
    openContactToast(s === "0" ? "err" : "ok", toastMsg);
    if (contactToast.classList.contains("is-open")) {
      stripSentFromUrl();
    }
  }

  maybeOpenSentToast();
  window.addEventListener("load", function () {
    var p2 = new URLSearchParams(window.location.search);
    var s2 = p2.get("sent");
    if (contactToast && (s2 === "1" || s2 === "0") && !contactToast.classList.contains("is-open")) {
      maybeOpenSentToast(s2);
    }
  });

  if (contactToast && contactToastClose) {
    contactToastClose.addEventListener("click", closeContactToast);
  }
  if (contactToast && contactToastBackdrop) {
    contactToastBackdrop.addEventListener("click", closeContactToast);
  }
  if (contactToast) {
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && contactToast.classList.contains("is-open")) {
        closeContactToast();
      }
    });
  }

  var revealSelector =
    "main > section:not(#home), .service-card, .portfolio-card, .feature-mini, .partners-mosaic__item";
  var revealNodes = document.querySelectorAll(revealSelector);

  if (revealNodes.length) {
    if (reduceMotion) {
      revealNodes.forEach(function (el) {
        el.classList.add("reveal", "is-visible");
      });
    } else {
      revealNodes.forEach(function (el) {
        el.classList.add("reveal");
      });
      var revealObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          });
        },
        { root: null, rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
      );
      revealNodes.forEach(function (el) {
        revealObserver.observe(el);
      });
    }
  }

  var form = document.querySelector("[data-contact-form]");
  if (form) {
    var fields = {
      name: { el: form.querySelector("#name"), err: form.querySelector("[data-err-for='name']") },
      email: { el: form.querySelector("#email"), err: form.querySelector("[data-err-for='email']") },
      phone: { el: form.querySelector("#phone"), err: form.querySelector("[data-err-for='phone']") },
      message: { el: form.querySelector("#message"), err: form.querySelector("[data-err-for='message']") },
    };

    function clearErrors() {
      Object.keys(fields).forEach(function (key) {
        if (fields[key].err) fields[key].err.textContent = "";
      });
    }

    function validate() {
      clearErrors();
      var ok = true;
      if (!fields.name.el.value.trim()) {
        fields.name.err.textContent = "Please enter your name.";
        ok = false;
      }
      var email = fields.email.el.value.trim();
      if (!email) {
        fields.email.err.textContent = "Please enter your email.";
        ok = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        fields.email.err.textContent = "That email doesn’t look valid.";
        ok = false;
      }
      if (!fields.message.el.value.trim()) {
        fields.message.err.textContent = "Please enter a short message.";
        ok = false;
      }
      return ok;
    }

    form.addEventListener("submit", function (e) {
      if (!validate()) {
        e.preventDefault();
      }
    });
  }

  var servicesCarousel = document.querySelector("[data-services-carousel]");
  if (servicesCarousel) {
    var servicesViewport = servicesCarousel.querySelector(".services-carousel__viewport");
    var servicesPrev = servicesCarousel.querySelector('[data-services-scroll="prev"]');
    var servicesNext = servicesCarousel.querySelector('[data-services-scroll="next"]');

    function servicesScrollStep() {
      if (!servicesViewport) return 0;
      var grid = servicesViewport.querySelector(".services-grid");
      var card = servicesViewport.querySelector(".service-card");
      if (!card) return Math.round(servicesViewport.clientWidth * 0.75);
      var gap = 0;
      if (grid) {
        var g = getComputedStyle(grid).gap || getComputedStyle(grid).columnGap;
        gap = parseFloat(g) || 0;
      }
      return Math.round(card.getBoundingClientRect().width + gap);
    }

    function servicesUpdateNav() {
      if (!servicesViewport || !servicesPrev || !servicesNext) return;
      if (window.matchMedia("(min-width: 720px)").matches) {
        servicesPrev.disabled = false;
        servicesNext.disabled = false;
        return;
      }
      var max = servicesViewport.scrollWidth - servicesViewport.clientWidth;
      var left = servicesViewport.scrollLeft;
      if (max <= 1) {
        servicesPrev.disabled = true;
        servicesNext.disabled = true;
        return;
      }
      servicesPrev.disabled = left <= 1;
      servicesNext.disabled = left >= max - 1;
    }

    function servicesScrollBy(dir) {
      if (!servicesViewport) return;
      servicesViewport.scrollBy({
        left: servicesScrollStep() * dir,
        behavior: reduceMotion ? "auto" : "smooth",
      });
    }

    if (servicesPrev) {
      servicesPrev.addEventListener("click", function () {
        servicesScrollBy(-1);
      });
    }
    if (servicesNext) {
      servicesNext.addEventListener("click", function () {
        servicesScrollBy(1);
      });
    }

    if (servicesViewport) {
      servicesViewport.addEventListener("scroll", servicesUpdateNav, { passive: true });
    }
    window.addEventListener("resize", servicesUpdateNav);
    window.addEventListener("load", servicesUpdateNav);
    servicesUpdateNav();

    var mq720 = window.matchMedia("(min-width: 720px)");
    if (mq720.addEventListener) {
      mq720.addEventListener("change", servicesUpdateNav);
    } else if (mq720.addListener) {
      mq720.addListener(servicesUpdateNav);
    }

    if (window.ResizeObserver && servicesViewport) {
      new ResizeObserver(servicesUpdateNav).observe(servicesViewport);
    }
  }

  var cookieBanner = document.getElementById("cookie-banner");
  if (cookieBanner) {
    var cookieAccept = cookieBanner.querySelector(".cookie-banner__accept");
    var cookieStorageKey = "cutitaru_cookie_ack";

    function hideCookieBanner() {
      cookieBanner.hidden = true;
      cookieBanner.setAttribute("aria-hidden", "true");
    }

    function showCookieBanner() {
      cookieBanner.hidden = false;
      cookieBanner.removeAttribute("aria-hidden");
    }

    try {
      if (window.localStorage && localStorage.getItem(cookieStorageKey)) {
        hideCookieBanner();
      } else {
        showCookieBanner();
      }
    } catch (e) {
      showCookieBanner();
    }

    if (cookieAccept) {
      cookieAccept.addEventListener("click", function () {
        try {
          if (window.localStorage) {
            localStorage.setItem(cookieStorageKey, "1");
          }
        } catch (err) {}
        hideCookieBanner();
      });
    }
  }

  (function sendVisitPingOncePerSession() {
    try {
      if (window.localStorage && localStorage.getItem("cutitaru_skip_visit_ping") === "1") {
        return;
      }
    } catch (e0) {}

    try {
      var visitKey = "cutitaru_visit_ping_v1";
      if (!window.sessionStorage || sessionStorage.getItem(visitKey)) {
        return;
      }
      sessionStorage.setItem(visitKey, "1");
    } catch (e) {
      return;
    }

    var tz = "";
    try {
      if (window.Intl && Intl.DateTimeFormat) {
        tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
      }
    } catch (err2) {}

    var screenLine = "";
    if (window.screen && window.screen.width && window.screen.height) {
      screenLine =
        window.screen.width +
        "x" +
        window.screen.height +
        "@" +
        (window.devicePixelRatio || 1);
    }

    var payload = {
      path: window.location.pathname + window.location.search,
      referrer: document.referrer || "",
      lang: navigator.language || "",
      tz: tz,
      screen: screenLine,
    };

    fetch("visit_ping.php", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).catch(function () {});
  })();
})();
