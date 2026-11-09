/* Kobon — tiny progressive enhancements (no framework) */
(function () {
  "use strict";
  // Formspree forms: POST via fetch, inline status; native POST still works without JS
  document.querySelectorAll("form.js-formspree").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (f.reportValidity && !f.reportValidity()) return;
      var btn = f.querySelector('button[type="submit"], button:not([type])');
      var status = f.querySelector(".form-status");
      if (!status) {
        status = document.createElement("p");
        status.className = "form-status";
        status.setAttribute("role", "status");
        status.setAttribute("aria-live", "polite");
        f.appendChild(status);
      }
      var okMsg = f.getAttribute("data-ok") || "OK";
      var errMsg = f.getAttribute("data-err") || "Error";
      if (btn) btn.disabled = true;
      status.textContent = "";
      fetch(f.action, {
        method: "POST",
        body: new FormData(f),
        headers: { Accept: "application/json" }
      }).then(function (r) {
        if (r.ok) {
          status.textContent = okMsg;
          f.reset();
        } else {
          status.textContent = errMsg;
        }
      }).catch(function () {
        status.textContent = errMsg;
      }).finally(function () {
        if (btn) btn.disabled = false;
      });
    });
  });
  // stores page filter (?q=)
  var q = document.getElementById("site-q");
  if (q) {
    var items = Array.prototype.slice.call(document.querySelectorAll("[data-search]"));
    var empty = document.getElementById("search-empty");
    var apply = function (v) {
      var term = (v || "").trim().toLowerCase(), shown = 0;
      items.forEach(function (el) {
        var ok = !term || el.getAttribute("data-search").indexOf(term) !== -1;
        el.hidden = !ok; if (ok) shown++;
      });
      if (empty) { empty.hidden = !(term && shown === 0); empty.textContent = empty.getAttribute("data-msg"); }
    };
    var init = new URLSearchParams(location.search).get("q") || "";
    q.value = init; apply(init);
    q.addEventListener("input", function () { apply(q.value); });
  }
  // filter forms never navigate (replaces inline onsubmit, CSP-safe)
  document.querySelectorAll("form.js-filter").forEach(function (f) {
    f.addEventListener("submit", function (e) { e.preventDefault(); });
  });
  // season tags: re-evaluate soon / live / past against today's date
  var today = new Date(), pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var ymd = today.getFullYear() + "-" + pad(today.getMonth() + 1) + "-" + pad(today.getDate());
  document.querySelectorAll("[data-season-start]").forEach(function (el) {
    var s = el.getAttribute("data-season-start"), en = el.getAttribute("data-season-end");
    var st = ymd < s ? "soon" : (ymd < en ? "live" : "past");
    var label = el.getAttribute("data-l-" + st), cls = el.getAttribute("data-c-" + st);
    if (label) el.textContent = label;
    if (cls) el.className = cls;
  });
  // copy code buttons
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b) return;
    var code = b.getAttribute("data-code");
    if (navigator.clipboard) navigator.clipboard.writeText(code).then(function () {
      var o = b.textContent; b.textContent = b.getAttribute("data-done") || "✓";
      setTimeout(function () { b.textContent = o; }, 1600);
    });
  });
  // close mobile menu after choosing a link
  document.querySelectorAll(".menu .panel a").forEach(function (a) {
    a.addEventListener("click", function () { var d = a.closest("details"); if (d) d.removeAttribute("open"); });
  });
})();
