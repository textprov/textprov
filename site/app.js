import textprov from "textprov";

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

  var passage = document.getElementById("sample-passage");
  if (passage) {
    // Keep the original character sequence: revealing and copying never add marks.
    var sampleText = passage.textContent;
    var revealed = false;
    var revealButton = document.getElementById("reveal-button");
    var sampleCopyButton = document.getElementById("sample-copy-button");
    revealButton.hidden = false;
    sampleCopyButton.hidden = false;

    revealButton.addEventListener("click", function () {
      revealed = !revealed;
      passage.textContent = sampleText;
      if (revealed) textprov.render(passage);
      revealButton.setAttribute("aria-pressed", String(revealed));
      revealButton.textContent = revealed ? "Hide labels" : "Reveal labels";
      document.getElementById("sample-legend").hidden = !revealed;
      document.getElementById("sample-reveal-status").textContent = revealed
        ? "Labels revealed. The opening is labelled human; the completion is labelled AI."
        : "Labels hidden. The text still contains its marks.";
    });

    sampleCopyButton.addEventListener("click", function () {
      var status = document.getElementById("sample-copy-status");
      copyText(sampleText).then(
        function () {
          status.textContent = "Copied with marks. Paste it into the reader below.";
          document.getElementById("reader").open = true;
        },
        function () {
          status.textContent = "Select the passage and copy it with your keyboard.";
        },
      );
    });
  }
})();
