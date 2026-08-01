(function () {
  "use strict";

  function fallbackCopy(text) {
    var helper = document.createElement("textarea");
    helper.value = text;
    helper.setAttribute("readonly", "");
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.appendChild(helper);
    helper.select();
    var copied = document.execCommand("copy");
    helper.remove();
    if (!copied) throw new Error("Copy command was rejected");
  }

  function writeClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    fallbackCopy(text);
    return Promise.resolve();
  }

  document.querySelectorAll("[data-copy-target]").forEach(function (button) {
    var originalLabel = button.textContent;
    var resetTimer;

    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-copy-target"));
      var status = button.closest(".copy-card").querySelector(".copy-status");
      if (!target) return;

      window.clearTimeout(resetTimer);
      writeClipboard(target.textContent).then(function () {
        button.textContent = "Copied";
        button.classList.add("is-copied");
        status.textContent = "Copied.";
        resetTimer = window.setTimeout(function () {
          button.textContent = originalLabel;
          button.classList.remove("is-copied");
          status.textContent = "";
        }, 1800);
      }).catch(function () {
        status.textContent = "Select the text and copy it manually.";
      });
    });
  });

  document.querySelectorAll("[data-char-count-for]").forEach(function (counter) {
    var target = document.getElementById(counter.getAttribute("data-char-count-for"));
    if (target) counter.textContent = String(target.textContent.length);
  });
})();
