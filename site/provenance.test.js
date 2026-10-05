import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { test } from "node:test";
import { HIDDEN, SHOWN, STORAGE_KEY, initProvenanceDisplay } from "./provenance.js";

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

function page({ regions = [mark("Draft", AI) + " text"], storage = memoryStorage() } = {}) {
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
  const elements = { "prov-legend": { hidden: true } };
  const regionElements = regions.map((textContent) => ({ textContent }));
  const rendered = [];
  const document = {
    documentElement: root,
    querySelectorAll(selector) {
      if (selector === "[data-prov-document]") return regionElements;
      if (selector === "[data-prov-toggle]") return [toggle];
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
  const counts = initProvenanceDisplay({ document, textprov: api, storage });
  return { counts, root, toggle, elements, rendered, storage };
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
