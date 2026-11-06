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
})();
