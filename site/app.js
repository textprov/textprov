import textprov from "textprov";

(function () {
  "use strict";

  var selectors = {
    human: String.fromCodePoint(0xe0100),
    ai: String.fromCodePoint(0xe0101),
  };
  var markedText = "";
  // Exact Unicode White_Space set from SPEC.md, not JavaScript's \s.
  var whitespace =
    /^[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/u;

  function mark(text, state) {
    if (!Object.prototype.hasOwnProperty.call(selectors, state)) {
      throw new RangeError("Unsupported provenance state: " + state);
    }
    var selector = selectors[state];
    return textprov
      .segments(text)
      .map(function (segment) {
        var points = Array.from(segment);
        var first = points[0].codePointAt(0);
        var pua =
          points.length === 1 &&
          textprov.mapping.puaRanges.some(function (range) {
            return first >= range[0] && first <= range[1];
          });
        if (
          segment.endsWith(selectors.human) ||
          segment.endsWith(selectors.ai) ||
          pua ||
          whitespace.test(segment)
        ) {
          return segment;
        }
        var marked = segment + selector;
        // GB4 makes a selector after a control-break cluster an orphan, not a mark.
        return textprov.segments(marked).length === 1 ? marked : segment;
      })
      .join("");
  }

  function renderDemo() {
    var input = document.getElementById("demo-input");
    var state = document.querySelector('input[name="state"]:checked').value;
    var output = document.getElementById("demo-output");
    var preview = document.getElementById("demo-preview") || output;
    // The demo explicitly relabels pasted text; the producer itself is idempotent.
    var text = textprov
      .runs(input.value, { strip: true })
      .map(function (run) {
        return run.text;
      })
      .join("");
    markedText = mark(text, state);
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

  var clipTabs = document.getElementById("clip-tabs");
  if (clipTabs) {
    var platforms = ["macos", "windows", "wayland", "x11"];
    var agent = navigator.userAgent || "";
    // iPadOS reports itself as a Mac; touch points tell them apart.
    var mobile =
      /Android|iPhone|iPad|iPod/.test(agent) ||
      (/Macintosh/.test(agent) && navigator.maxTouchPoints > 1);

    var selectPlatform = function (selected) {
      platforms.forEach(function (platform) {
        var tab = document.getElementById("clip-tab-" + platform);
        var active = platform === selected;
        tab.setAttribute("aria-selected", String(active));
        tab.setAttribute("tabindex", active ? "0" : "-1");
        document.getElementById("clip-panel-" + platform).hidden = !active;
      });
    };

    if (mobile) {
      // No terminal to run a command in: point at the file instead.
      document.getElementById("clip-desktop").hidden = true;
      document.getElementById("clip-mobile").hidden = false;
    } else {
      platforms.forEach(function (platform, index) {
        var tab = document.getElementById("clip-tab-" + platform);
        var panel = document.getElementById("clip-panel-" + platform);
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", "clip-tab-" + platform);
        tab.addEventListener("click", function () {
          selectPlatform(platform);
        });
        tab.addEventListener("keydown", function (event) {
          var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
          if (!step) return;
          event.preventDefault();
          var next = platforms[(index + step + platforms.length) % platforms.length];
          selectPlatform(next);
          document.getElementById("clip-tab-" + next).focus();
        });
      });
      clipTabs.hidden = false;
      // The browser cannot see the display server; Wayland is the Linux default.
      selectPlatform(
        /Windows/.test(agent) ? "windows" : /Linux|X11|CrOS/.test(agent) ? "wayland" : "macos",
      );
    }
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
