// Display preference for the VS-marked draft documents and example.
// Regions marked [data-prov-document] are decorated once with textprov.render();
// the preference only switches their styling, so the text and its marks never
// change and copied text keeps its labels either way.

export const STORAGE_KEY = "textprov:provenance";
export const DISPLAY_KEY = "textprov:display";
export const VERSION_KEY = "textprov:display-version";
export const TIER_KEY = "textprov:display-tier";
export const SHOWN = "shown";
export const HIDDEN = "hidden";
// Candidate display versions the packaged stylesheet carries behind
// data-prov-display-version, and their tiers (docs/development/display-versions.md).
// The recommendation is textprov.displayVersion and needs no entry here.
export const CANDIDATES = ["v0.3.0-bracket"];
export const TIERS = ["latent", "quiet", "loud"];

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

// An evaluation choice arrives as ?prov-display-version=<candidate> and
// ?prov-display-tier=<tier>, is remembered for this browser, and is cleared by
// an empty value. Anything not registered falls back to the recommendation.
export function readEvaluation(location, storage) {
  var choice = { version: null, tier: null };
  var params = null;
  try {
    var search = location && typeof location.search === "string" ? location.search : "";
    if (search && typeof URLSearchParams === "function") params = new URLSearchParams(search);
  } catch (error) {
    params = null;
  }
  [["prov-display-version", VERSION_KEY, CANDIDATES, "version"],
   ["prov-display-tier", TIER_KEY, TIERS, "tier"]].forEach(function (entry) {
    var value = null;
    if (params && params.has(entry[0])) {
      value = params.get(entry[0]);
      try {
        if (storage) {
          if (entry[2].indexOf(value) >= 0) storage.setItem(entry[1], value);
          else storage.removeItem(entry[1]);
        }
      } catch (error) {
        // The choice still applies to this page view.
      }
    } else {
      try { if (storage) value = storage.getItem(entry[1]); } catch (error) { value = null; }
    }
    if (entry[2].indexOf(value) >= 0) choice[entry[3]] = value;
  });
  return choice;
}

export function initProvenanceDisplay(options) {
  var document = options.document;
  var textprov = options.textprov;
  var storage = options.storage;
  var location = options.location || (document.defaultView && document.defaultView.location) || null;
  var regions = Array.from(document.querySelectorAll("[data-prov-document]"));
  if (regions.length === 0) return null;

  var root = document.documentElement;
  var toggles = Array.from(document.querySelectorAll("[data-prov-toggle]"));
  var modes = Array.from(document.querySelectorAll("[data-prov-display-control]"));
  if (!modes.length && document.createElement) {
    toggles.forEach(function (toggle) {
      var parent = toggle.closest(".provenance-controls");
      if (!parent) return;
      var label = document.createElement("label");
      label.className = "prov-display-control";
      label.appendChild(document.createTextNode("Highlight detail "));
      var select = document.createElement("select");
      select.setAttribute("data-prov-display-control", "");
      select.title = "Passages can include unmarked text. Exact characters shows recorded ranges.";
      [["passage", "Passages"], ["exact", "Exact characters"]].forEach(function (entry) {
        var option = document.createElement("option");
        option.value = entry[0]; option.textContent = entry[1]; select.appendChild(option);
      });
      label.appendChild(select); parent.appendChild(label); modes.push(select);
    });
  }
  var display = "passage";
  try { if (storage && storage.getItem(DISPLAY_KEY) === "exact") display = "exact"; } catch (error) {}
  function applyDisplay(value) {
    root.dataset.provDisplay = value;
    regions.forEach(function (region) { if (region.dataset) region.dataset.provDisplay = value; });
    modes.forEach(function (mode) { mode.value = value; });
  }
  applyDisplay(display);
  modes.forEach(function (mode) {
    mode.addEventListener("change", function () {
      var value = mode.value === "exact" ? "exact" : "passage";
      applyDisplay(value);
      try { if (storage) storage.setItem(DISPLAY_KEY, value); } catch (error) {}
    });
  });
  function apply(value) {
    root.dataset.provenance = value;
    modes.forEach(function (mode) { mode.disabled = value !== SHOWN; });
    toggles.forEach(function (toggle) {
      toggle.setAttribute("aria-checked", String(value === SHOWN));
    });
  }

  // Set the preference before the spans exist so a hidden preference never flashes.
  apply(readPreference(storage));
  regions.forEach(function (region) { textprov.render(region, { display: "passage" }); });
  applyDisplay(display);

  toggles.forEach(function (toggle) {
    toggle.hidden = false;
    toggle.addEventListener("click", function () {
      var next = root.dataset.provenance === SHOWN ? HIDDEN : SHOWN;
      apply(next);
      writePreference(storage, next);
    });
  });

  // Declare the treatment the packaged stylesheet paints (docs/development/display-versions.md).
  // The recommendation is the default; a registered candidate can be switched on
  // for evaluation (readEvaluation), and the stylesheet keys on the same attribute.
  var evaluation = readEvaluation(location, storage);
  var version = evaluation.version || textprov.displayVersion;
  if (version) root.dataset.provDisplayVersion = version;
  if (evaluation.version && evaluation.tier) root.dataset.provTier = evaluation.tier;
  else delete root.dataset.provTier;
  var legend = document.getElementById("prov-legend");
  if (legend) {
    legend.hidden = false;
    if (version && document.createElement) {
      var note = document.createElement("span");
      note.className = "prov-display-version";
      note.textContent = "Display " + version + (root.dataset.provTier ? " (" + root.dataset.provTier + " tier)" : "");
      legend.appendChild(document.createTextNode(" \u00b7 "));
      legend.appendChild(note);
    }
  }
  return true;
}
