// Display preference for the VS-marked draft documents and example.
// Regions marked [data-prov-document] are decorated once with textprov.render();
// the preference only switches their styling, so the text and its marks never
// change and copied text keeps its labels either way.

export const STORAGE_KEY = "textprov:provenance";
export const SHOWN = "shown";
export const HIDDEN = "hidden";

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
  regions.forEach(function (region) { textprov.render(region); });

  toggles.forEach(function (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      var next = root.dataset.provenance === SHOWN ? HIDDEN : SHOWN;
      apply(next);
      writePreference(storage, next);
    });
  });

  var legend = document.getElementById("prov-legend");
  if (legend) legend.hidden = false;
  return true;
}
