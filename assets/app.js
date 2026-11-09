/* Kobon — tiny progressive enhancements (no framework) */
(function () {
  "use strict";
  // mailto forms: compose a readable email from the fields
  document.querySelectorAll("form.js-mailto").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (f.reportValidity && !f.reportValidity()) return;
      var lines = [];
      f.querySelectorAll("input:not([type=hidden]),select,textarea").forEach(function (el) {
        if (!el.value) return;
        var label = el.closest("label");
        var name = label ? label.childNodes[0].textContent.trim() : (el.getAttribute("placeholder") || el.name);
        lines.push(name + ": " + el.value);
      });
      var href = "mailto:" + f.dataset.to + "?subject=" + encodeURIComponent(f.dataset.subject || "") + "&body=" + encodeURIComponent(lines.join("\n"));
      window.location.href = href;
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
