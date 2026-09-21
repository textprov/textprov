import "../js/textprov.js";

(function () {
  "use strict";

  var selectors = {
    human: String.fromCodePoint(0xe0100),
    ai: String.fromCodePoint(0xe0101),
    mixed: String.fromCodePoint(0xe0102),
  };
  var segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  var markedText = "";

  function mark(text, state) {
    var selector = selectors[state];
    text = textprov
      .runs(text, { strip: true })
      .map(function (run) {
        return run.text;
      })
      .join("");
    return Array.from(segmenter.segment(text), function (item) {
      return /^\s+$/u.test(item.segment) ? item.segment : item.segment + selector;
    }).join("");
  }

  function renderDemo() {
    var input = document.getElementById("demo-input");
    var state = document.querySelector('input[name="state"]:checked').value;
    var output = document.getElementById("demo-output");
    var preview = document.getElementById("demo-preview") || output;
    markedText = mark(input.value, state);
    if ("value" in output) {
      output.value = markedText;
    } else {
      output.textContent = markedText;
    }
    if (preview !== output) {
      preview.textContent = markedText;
    }
    var count = textprov.render(preview);
    document.getElementById("run-count").textContent =
      count + (count === 1 ? " marked run" : " marked runs");
    document.getElementById("copy-status").textContent = "";
  }

  function copyMarkedText() {
    var status = document.getElementById("copy-status");
    if (!navigator.clipboard) {
      status.textContent = "Clipboard unavailable";
      return;
    }
    navigator.clipboard.writeText(markedText).then(
      function () {
        status.textContent = "Copied with marks";
      },
      function () {
        status.textContent = "Could not copy";
      },
    );
  }

  function downloadMarkedText() {
    var blob = new Blob([markedText], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "textprov-sample.txt";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }

    return new Promise(function (resolve, reject) {
      var textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();

      try {
        if (!document.execCommand("copy")) throw new Error("Copy command failed");
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        textarea.remove();
      }
    });
  }

  function addSampleCopyButtons() {
    var selectorPattern = /[\u{E0100}-\u{E01EF}]/u;
    var targets = new Set(document.querySelectorAll("blockquote"));

    document.querySelectorAll("main p, main pre").forEach(function (element) {
      if (selectorPattern.test(element.textContent)) targets.add(element);
    });

    targets.forEach(function (target) {
      if (!target || !target.dataset || typeof target.insertAdjacentElement !== "function") return;
      if (target.dataset.copyButton === "true") return;
      target.dataset.copyButton = "true";

      var button = document.createElement("button");
      button.type = "button";
      button.className = "sample-copy-button";
      button.textContent = "Copy";
      button.setAttribute(
        "aria-label",
        selectorPattern.test(target.textContent) ? "Copy marked text" : "Copy sample text",
      );

      button.addEventListener("click", function () {
        copyText(target.textContent).then(
          function () {
            button.textContent = "Copied";
          },
          function () {
            button.textContent = "Copy failed";
          },
        );
        window.setTimeout(function () {
          button.textContent = "Copy";
        }, 2000);
      });

      var wrapper = document.createElement("div");
      wrapper.className = "sample-copy-wrapper";
      target.insertAdjacentElement("beforebegin", wrapper);
      wrapper.appendChild(target);
      wrapper.appendChild(button);
    });
  }

  function checkText() {
    var text = document.getElementById("check-input").value;
    var output = document.getElementById("check-output");
    var states = Array.from(
      new Set(
        textprov
          .runs(text)
          .map(function (run) {
            return run.state;
          })
          .filter(Boolean),
      ),
    );
    output.textContent = text;
    textprov.render(output);
    document.getElementById("check-status").textContent = !text
      ? "Waiting for text."
      : states.length
        ? "Labels found: " + states.join(", ") + ". These are claims, not verified origins."
        : "No TextProv labels found. This does not mean the text is human-written.";
  }

  var demoInput = document.getElementById("demo-input");
  if (demoInput) {
    renderDemo();
    demoInput.addEventListener("input", renderDemo);
    document.querySelectorAll('input[name="state"]').forEach(function (input) {
      input.addEventListener("change", renderDemo);
    });
    document.getElementById("copy-button").addEventListener("click", copyMarkedText);
    document.getElementById("download-button").addEventListener("click", downloadMarkedText);
  }

  var checkInput = document.getElementById("check-input");
  if (checkInput) {
    checkInput.addEventListener("input", checkText);
  }

  addSampleCopyButtons();

  function detectSelectorRendering() {
    try {
      if (!document.fonts || typeof document.fonts.ready === "undefined") return;
      var canvas = document.createElement("canvas");
      var ctx = canvas.getContext && canvas.getContext("2d");
      if (!ctx) return;

      var ua = navigator.userAgent || "";
      var isSafari = /Safari/.test(ua) && !/Chrome|Chromium|Android/.test(ua);
      var message = isSafari
        ? "Your browser did not render the variation-selector marks for this sample. This is a known limitation of Safari with the current demo fonts."
        : "Your browser did not render the variation-selector marks for this sample.";

      var aiSelector = String.fromCodePoint(0xe0101);
      var base = "A";
      var samples = document.querySelectorAll(".font-sample[data-example]");

      samples.forEach(function (el) {
        if (el.dataset.example === "ordinary") return;
        if (el.nextElementSibling && el.nextElementSibling.classList.contains("sample-warning"))
          return;
        var cs = window.getComputedStyle(el);
        var size = Math.max(parseFloat(cs.fontSize) || 16, 64);
        var font = cs.fontStyle + " " + cs.fontWeight + " " + size + "px " + cs.fontFamily;

        canvas.width = Math.ceil(size * 3);
        canvas.height = Math.ceil(size * 2);

        function renderTo(text) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.font = font;
          ctx.textBaseline = "top";
          ctx.fillStyle = "#000";
          ctx.fillText(text, 0, 0);
          return ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        }

        var plain = renderTo(base);
        var marked = renderTo(base + aiSelector);

        var diff = 0;
        for (var i = 0; i < plain.length; i += 4) {
          if (
            Math.abs(plain[i] - marked[i]) > 4 ||
            Math.abs(plain[i + 1] - marked[i + 1]) > 4 ||
            Math.abs(plain[i + 2] - marked[i + 2]) > 4 ||
            Math.abs(plain[i + 3] - marked[i + 3]) > 4
          ) {
            diff++;
            if (diff > 3) break;
          }
        }
        if (diff > 3) return;

        var warning = document.createElement("p");
        warning.className = "note sample-warning";
        warning.textContent = message;
        el.insertAdjacentElement("afterend", warning);
      });
    } catch (_) {
      // swallow
    }
  }

  function runDetection() {
    if (!document.fonts || !document.fonts.ready) {
      detectSelectorRendering();
      return;
    }
    document.fonts.ready.then(detectSelectorRendering, function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runDetection);
  } else {
    runDetection();
  }
})();
