(function () {
  "use strict";

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "absolute";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        resolve();
      } catch (err) {
        reject(err);
      } finally {
        document.body.removeChild(ta);
      }
    });
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    e.preventDefault();
    var code = btn.getAttribute("data-code") || "";
    var labelCopy = btn.getAttribute("data-label-copy") || "Copy code";
    var labelDone = btn.getAttribute("data-label-done") || "Copied!";

    copyText(code).then(function () {
      var original = btn.textContent;
      btn.textContent = labelDone;
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = original || labelCopy;
        btn.classList.remove("copied");
      }, 1800);
    }).catch(function () {
      alert(code);
    });
  });

  // Lightweight cookie / local-storage notice (no tracking cookies)
  function initCookieBanner() {
    var banner = document.getElementById("cookie-banner");
    var accept = document.getElementById("cookie-accept");
    if (!banner || !accept) return;
    try {
      if (localStorage.getItem("ye7ia_cookie_ok") === "1") return;
    } catch (err) {
      return;
    }
    banner.hidden = false;
    accept.addEventListener("click", function () {
      try {
        localStorage.setItem("ye7ia_cookie_ok", "1");
      } catch (err) {}
      banner.hidden = true;
    });
  }

  // Stores page: honor ?q= and filter cards client-side
  function initStoreSearch() {
    var input = document.getElementById("store-q");
    var grid = document.getElementById("store-grid");
    var empty = document.getElementById("store-search-empty");
    if (!input || !grid) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll("[data-store-card]"));
    if (!cards.length) return;

    function apply(q) {
      var term = (q || "").trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {
        var hay = (card.getAttribute("data-search") || "").toLowerCase();
        var ok = !term || hay.indexOf(term) !== -1;
        card.hidden = !ok;
        if (ok) shown += 1;
      });
      if (empty) empty.hidden = shown !== 0 || !term;
    }

    var params = new URLSearchParams(window.location.search);
    var initial = params.get("q") || "";
    if (initial) input.value = initial;
    apply(initial);

    input.addEventListener("input", function () {
      var q = input.value || "";
      apply(q);
      var url = new URL(window.location.href);
      if (q.trim()) url.searchParams.set("q", q.trim());
      else url.searchParams.delete("q");
      window.history.replaceState(null, "", url.pathname + url.search + url.hash);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initCookieBanner();
      initStoreSearch();
    });
  } else {
    initCookieBanner();
    initStoreSearch();
  }
})();
