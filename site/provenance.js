// Display preference for the bounded historical VS demonstration.
// Regions marked [data-prov-document] are decorated once with textprov.render();
// the preference only switches their styling, so the text and its marks never
// change and copied text keeps its labels either way.

export const STORAGE_KEY = "textprov:provenance";
export const SHOWN = "shown";
export const HIDDEN = "hidden";

// Unicode White_Space set used by the retained experimental decoder.
var whitespace =
  /^[\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/u;

export function readPreference(storage) {
  try {
    return storage && storage.getItem(STORAGE_KEY) === HIDDEN ? HIDDEN : SHOWN;
  } catch (error) {
    return SHOWN;
  }
}

function writePreference(storage, value) {
  try {
    if (storage) storage.setItem(STORAGE_KEY, value);
  } catch (error) {
    // The preference still applies to this page view.
  }
}

// Counts non-whitespace grapheme clusters per label; unmarked text has no claim.
export function summarize(textprov, text) {
  var counts = { ai: 0, human: 0, unmarked: 0 };
  textprov.runs(text, { mergeWhitespace: false }).forEach(function (run) {
    var clusters = textprov.segments(run.text).filter(function (cluster) {
      return !whitespace.test(cluster);
    }).length;
    counts[run.state || "unmarked"] += clusters;
  });
  return counts;
}

function percent(part, total) {
  if (!part) return "0%";
  var value = (part / total) * 100;
  return value < 1 ? "<1%" : Math.round(value) + "%";
}

export function describe(counts) {
  var total = counts.ai + counts.human + counts.unmarked;
  if (!total) return "No text to label.";
  return (
    "AI " +
    percent(counts.ai, total) +
    " · human " +
    percent(counts.human, total) +
    " · unmarked " +
    percent(counts.unmarked, total)
  );
}

export function initProvenanceDisplay(options) {
  var document = options.document;
  var textprov = options.textprov;
  var storage = options.storage;
  var regions = Array.from(document.querySelectorAll("[data-prov-document]"));
  if (regions.length === 0) return null;

  var root = document.documentElement;
  var toggles = Array.from(document.querySelectorAll("[data-prov-toggle]"));
  function apply(value) {
    root.dataset.provenance = value;
    toggles.forEach(function (toggle) {
      toggle.setAttribute("aria-checked", String(value === SHOWN));
    });
  }

  // Set the preference before the spans exist so a hidden preference never flashes.
  apply(readPreference(storage));
  var counts = { ai: 0, human: 0, unmarked: 0 };
  regions.forEach(function (region) {
    var regionCounts = summarize(textprov, region.textContent);
    Object.keys(counts).forEach(function (state) {
      counts[state] += regionCounts[state];
    });
    textprov.render(region);
  });

  toggles.forEach(function (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      var next = root.dataset.provenance === SHOWN ? HIDDEN : SHOWN;
      apply(next);
      writePreference(storage, next);
    });
  });

  var summary = document.getElementById("prov-summary");
  if (summary) summary.textContent = describe(counts);
  var legend = document.getElementById("prov-legend");
  if (legend) legend.hidden = false;
  return counts;
}
