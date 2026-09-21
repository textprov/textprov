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
})();
