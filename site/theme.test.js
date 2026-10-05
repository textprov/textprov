import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { runInNewContext } from "node:vm";

const script = readFileSync(new URL("./public/theme.js", import.meta.url), "utf8");
const STORAGE_KEY = "textprov:theme";

// Execute the same classic script served to readers, including its pre-DOM initialization.
function page({ dark = false, saved = null, blocked = null } = {}) {
  const root = { dataset: {} };
  const documentEvents = new Map();
  const buttonEvents = new Map();
  const systemEvents = new Map();
  const writes = [];
  const button = {
    hidden: true,
    attributes: {},
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, callback) { buttonEvents.set(name, callback); },
  };
  const system = {
    matches: dark,
    addEventListener(name, callback) { systemEvents.set(name, callback); },
  };
  const storage = {
    getItem(key) {
      assert.equal(key, STORAGE_KEY);
      if (blocked === "read") throw new Error("Storage reads blocked");
      return saved;
    },
    setItem(key, value) {
      if (blocked === "write" || blocked === "read") throw new Error("Storage writes blocked");
      writes.push([key, value]);
    },
  };
  const window = {
    matchMedia(query) {
      assert.equal(query, "(prefers-color-scheme: dark)");
      return system;
    },
    get localStorage() {
      if (blocked === "access") throw new Error("Storage access blocked");
      return storage;
    },
  };
  const document = {
    documentElement: root,
    addEventListener(name, callback) { documentEvents.set(name, callback); },
    querySelector(selector) {
      assert.equal(selector, "[data-theme-toggle]");
      return button;
    },
  };
  runInNewContext(script, { window, document });
  return {
    root, button, writes,
    ready: () => documentEvents.get("DOMContentLoaded")(),
    click: () => buttonEvents.get("click")(),
    systemChange(dark) {
      system.matches = dark;
      systemEvents.get("change")({ matches: dark });
    },
  };
}

function assertControl(button, mode) {
  const next = mode === "light" ? "dark" : "light";
  assert.equal(button.hidden, false);
  assert.equal(button.textContent, next === "light" ? "☀️" : "🌙");
  assert.equal(button.attributes["aria-label"], `Switch to ${next} mode`);
  assert.equal(button.title, `Switch to ${next} mode`);
}

test("system preference initializes the theme before DOM readiness and keeps following system changes", () => {
  for (const dark of [false, true]) {
    const view = page({ dark });
    assert.equal(view.root.dataset.theme, dark ? "dark" : "light");
    assert.equal(view.button.hidden, true);
    view.ready();
    assertControl(view.button, dark ? "dark" : "light");
    view.systemChange(!dark);
    assert.equal(view.root.dataset.theme, dark ? "light" : "dark");
    assertControl(view.button, dark ? "light" : "dark");
    assert.deepEqual(view.writes, []);
  }
});

test("saved light and dark overrides take precedence and ignore system changes", () => {
  for (const saved of ["light", "dark"]) {
    const view = page({ dark: saved === "light", saved });
    assert.equal(view.root.dataset.theme, saved);
    view.ready();
    view.systemChange(false);
    view.systemChange(true);
    assert.equal(view.root.dataset.theme, saved);
    assertControl(view.button, saved);
    assert.deepEqual(view.writes, []);
  }
});

test("legacy and invalid saved preferences fall back to the system", () => {
  for (const saved of ["system", "invalid", "", null]) {
    const view = page({ dark: true, saved });
    assert.equal(view.root.dataset.theme, "dark");
    view.ready();
    view.systemChange(false);
    assert.equal(view.root.dataset.theme, "light");
    assertControl(view.button, "light");
  }
});

test("clicks persist a binary override and stop following the system", () => {
  const view = page();
  view.ready();
  view.click();
  assert.equal(view.root.dataset.theme, "dark");
  assertControl(view.button, "dark");
  view.systemChange(false);
  assert.equal(view.root.dataset.theme, "dark");
  view.click();
  assert.equal(view.root.dataset.theme, "light");
  assertControl(view.button, "light");
  view.systemChange(true);
  assert.equal(view.root.dataset.theme, "light");
  assert.deepEqual(view.writes, [[STORAGE_KEY, "dark"], [STORAGE_KEY, "light"]]);
});

test("blocked storage access, reads, or writes preserve a working page-local override", () => {
  for (const blocked of ["access", "read", "write"]) {
    const view = page({ dark: true, blocked });
    assert.equal(view.root.dataset.theme, "dark");
    view.ready();
    view.systemChange(false);
    assert.equal(view.root.dataset.theme, "light");
    view.click();
    assert.equal(view.root.dataset.theme, "dark");
    assertControl(view.button, "dark");
    view.systemChange(false);
    assert.equal(view.root.dataset.theme, "dark");
    view.click();
    assert.equal(view.root.dataset.theme, "light");
    assertControl(view.button, "light");
    assert.deepEqual(view.writes, []);
  }
});
