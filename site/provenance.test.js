import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { test } from "node:test";
import { CANDIDATES, DISPLAY_KEY, HIDDEN, SHOWN, STORAGE_KEY, TIER_KEY, TIERS, VERSION_KEY, initProvenanceDisplay } from "./provenance.js";

const textprov = createRequire(import.meta.url)("../js/textprov.js");
const HUMAN = "\u{E0100}";
const AI = "\u{E0101}";
// One selector per grapheme cluster, as a producer marks.
const mark = (text, selector) => textprov.segments(text).map((c) => c + selector).join("");

function memoryStorage(entries = {}) {
  const store = new Map(Object.entries(entries));
  return {
    store,
    getItem: (key) => (store.has(key) ? store.get(key) : null),
    setItem: (key, value) => store.set(key, value),
    removeItem: (key) => store.delete(key),
  };
}

const brokenStorage = {
  getItem() {
    throw new Error("blocked");
  },
  setItem() {
    throw new Error("blocked");
  },
};

function page({ regions = [mark("Draft", AI) + " text"], storage = memoryStorage(), search = "" } = {}) {
  const root = { dataset: {} };
  const toggle = {
    hidden: true,
    attributes: {},
    listeners: {},
    setAttribute(name, value) {
      this.attributes[name] = value;
    },
    addEventListener(event, callback) {
      this.listeners[event] = callback;
    },
  };
  const mode = { value: "passage", disabled: false, listeners: {}, addEventListener(event, callback) { this.listeners[event] = callback; } };
  const elements = { "prov-legend": { hidden: true } };
  const regionElements = regions.map((textContent) => ({ textContent }));
  const rendered = [];
  const document = {
    documentElement: root,
    querySelectorAll(selector) {
      if (selector === "[data-prov-document]") return regionElements;
      if (selector === "[data-prov-toggle]") return [toggle];
      if (selector === "[data-prov-display-control]") return [mode];
      return [];
    },
    getElementById: (id) => elements[id] ?? null,
  };
  // Record the preference each region was rendered under; DOM output is covered by js/check_render.mjs.
  const api = {
    ...textprov,
    render(region) {
      rendered.push({ region, provenance: root.dataset.provenance });
      return 0;
    },
  };
  const counts = initProvenanceDisplay({ document, textprov: api, storage, location: { search } });
  return { counts, root, toggle, mode, elements, rendered, storage };
}

test("pages without a document region are left alone", () => {
  const { counts, root, toggle, rendered } = page({ regions: [] });
  assert.equal(counts, null);
  assert.equal(root.dataset.provenance, undefined);
  assert.equal(toggle.hidden, true);
  assert.deepEqual(rendered, []);
});

test("labels are shown by default and the toggle persists the choice", () => {
  const { root, toggle, storage } = page();
  assert.equal(root.dataset.provenance, SHOWN);
  assert.equal(toggle.hidden, false);
  assert.equal(toggle.attributes["aria-checked"], "true");

  toggle.listeners.click();
  assert.equal(root.dataset.provenance, HIDDEN);
  assert.equal(toggle.attributes["aria-checked"], "false");
  assert.equal(storage.store.get(STORAGE_KEY), HIDDEN);

  toggle.listeners.click();
  assert.equal(root.dataset.provenance, SHOWN);
  assert.equal(storage.store.get(STORAGE_KEY), SHOWN);
});

test("a stored hidden preference applies before any region renders", () => {
  const { rendered, toggle } = page({
    regions: ["a" + AI, "b" + HUMAN],
    storage: memoryStorage({ [STORAGE_KEY]: HIDDEN }),
  });
  assert.deepEqual(
    rendered.map((entry) => entry.provenance),
    [HIDDEN, HIDDEN],
  );
  assert.equal(toggle.attributes["aria-checked"], "false");
});

test("unknown stored values and blocked storage fall back to shown", () => {
  assert.equal(page({ storage: memoryStorage({ [STORAGE_KEY]: "dark" }) }).root.dataset.provenance, SHOWN);
  const { root, toggle } = page({ storage: brokenStorage });
  assert.equal(root.dataset.provenance, SHOWN);
  toggle.listeners.click();
  assert.equal(root.dataset.provenance, HIDDEN);
});

test("the simple legend is revealed after display initialization", () => {
  const { elements } = page();
  assert.equal(elements["prov-legend"].hidden, false);
});

test("the document root declares the display version the stylesheet paints", () => {
  const { root } = page();
  assert.equal(root.dataset.provDisplayVersion, textprov.displayVersion);
  assert.match(root.dataset.provDisplayVersion, /^v\d+\.\d+\.\d+-[a-z]+$/);
  assert.equal(root.dataset.provTier, undefined);
});

test("a registered candidate can be switched on for evaluation and is remembered", () => {
  const candidate = CANDIDATES[0];
  assert.notEqual(candidate, textprov.displayVersion);
  const storage = memoryStorage();
  const first = page({ storage, search: `?prov-display-version=${candidate}&prov-display-tier=quiet` });
  assert.equal(first.root.dataset.provDisplayVersion, candidate);
  assert.equal(first.root.dataset.provTier, "quiet");
  assert.equal(storage.store.get(VERSION_KEY), candidate);
  assert.equal(storage.store.get(TIER_KEY), "quiet");
  // The choice persists without the query string; the tier alone changes nothing.
  const second = page({ storage });
  assert.equal(second.root.dataset.provDisplayVersion, candidate);
  assert.equal(second.root.dataset.provTier, "quiet");
  const third = page({ storage, search: "?prov-display-tier=loud" });
  assert.equal(third.root.dataset.provTier, "loud");
  // An empty value clears the choice and the recommendation returns.
  const fourth = page({ storage, search: "?prov-display-version=" });
  assert.equal(fourth.root.dataset.provDisplayVersion, textprov.displayVersion);
  assert.equal(fourth.root.dataset.provTier, undefined);
  assert.equal(storage.store.has(VERSION_KEY), false);
  assert.equal(page({ storage: memoryStorage({ [TIER_KEY]: "loud" }) }).root.dataset.provTier, undefined);
});

test("unregistered versions and tiers fall back to the recommendation", () => {
  assert.ok(TIERS.includes("latent") && TIERS.includes("quiet") && TIERS.includes("loud"));
  const { root, storage } = page({ search: "?prov-display-version=v9.9.9-dagger&prov-display-tier=shout" });
  assert.equal(root.dataset.provDisplayVersion, textprov.displayVersion);
  assert.equal(root.dataset.provTier, undefined);
  assert.equal(storage.store.has(VERSION_KEY), false);
  assert.equal(page({ storage: memoryStorage({ [VERSION_KEY]: "v9.9.9-dagger" }) }).root.dataset.provDisplayVersion, textprov.displayVersion);
  assert.equal(page({ storage: brokenStorage, search: `?prov-display-version=${CANDIDATES[0]}` }).root.dataset.provDisplayVersion, CANDIDATES[0]);
});


test("passages are the default and exact display persists without changing source", () => {
  const source = "x" + AI + " plain";
  const { root, mode, storage, rendered, toggle } = page({ regions: [source] });
  assert.equal(root.dataset.provDisplay, "passage");
  assert.equal(mode.disabled, false);
  mode.value = "exact"; mode.listeners.change();
  assert.equal(root.dataset.provDisplay, "exact");
  assert.equal(storage.store.get(DISPLAY_KEY), "exact");
  assert.equal(rendered[0].region.textContent, source);
  toggle.listeners.click();
  assert.equal(mode.disabled, true);
  assert.equal(page({ storage }).root.dataset.provDisplay, "exact");
  assert.equal(page({ storage: memoryStorage({ [DISPLAY_KEY]: "word" }) }).root.dataset.provDisplay, "passage");
});
