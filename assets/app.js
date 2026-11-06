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
    var btn = e.target.closest("[data-copy-shop]");
    if (!btn) return;
    e.preventDefault();
    var code = btn.getAttribute("data-code") || "";
    var url = btn.getAttribute("data-url") || "#";
    var labelCopy = btn.getAttribute("data-label-copy") || "Copy & Shop";
    var labelDone = btn.getAttribute("data-label-done") || "Copied!";

    copyText(code).then(function () {
      var original = btn.textContent;
      btn.textContent = labelDone;
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = original || labelCopy;
        btn.classList.remove("copied");
      }, 1800);
      if (url && url !== "#") {
        window.open(url, "_blank", "noopener,noreferrer");
      }
    }).catch(function () {
      if (url && url !== "#") {
        window.open(url, "_blank", "noopener,noreferrer");
      }
      alert(code);
    });
  });
})();
