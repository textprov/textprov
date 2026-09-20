(function () {
  "use strict";

  var selectors = {
    human: String.fromCodePoint(0xE0100),
    ai: String.fromCodePoint(0xE0101),
    unknown: String.fromCodePoint(0xE0102)
  };
  var segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  var markedText = "";

  function mark(text, state) {
    var selector = selectors[state];
    return Array.from(segmenter.segment(text), function (item) {
      return /^\s+$/u.test(item.segment) ? item.segment : item.segment + selector;
    }).join("");
  }

  function renderHero() {
    var node = document.getElementById("hero-demo");
    var parts = [
      ["A sentence ", "human"],
      ["can carry its history ", "ai"],
      ["without changing what it says.", "unknown"]
    ];
    node.textContent = parts.map(function (part) { return mark(part[0], part[1]); }).join("");
    textprov.render(node);
  }

  function renderDemo() {
    var input = document.getElementById("demo-input");
    var state = document.querySelector('input[name="state"]:checked').value;
    var output = document.getElementById("demo-output");
    markedText = mark(input.value, state);
    output.textContent = markedText;
    var count = textprov.render(output);
    document.getElementById("run-count").textContent = count + (count === 1 ? " marked run" : " marked runs");
    document.getElementById("copy-status").textContent = "";
  }

  function copyMarkedText() {
    var status = document.getElementById("copy-status");
    if (!navigator.clipboard) {
      status.textContent = "Clipboard unavailable";
      return;
    }
    navigator.clipboard.writeText(markedText).then(function () {
      status.textContent = "Copied with marks";
    }, function () {
      status.textContent = "Could not copy";
    });
  }

  renderHero();
  renderDemo();
  document.getElementById("demo-input").addEventListener("input", renderDemo);
  document.querySelectorAll('input[name="state"]').forEach(function (input) {
    input.addEventListener("change", renderDemo);
  });
  document.getElementById("copy-button").addEventListener("click", copyMarkedText);
}());
