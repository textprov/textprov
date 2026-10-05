import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";
import vm from "node:vm";

const homepage = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const sample = homepage.match(/<p id="sample-passage"[^>]*>([^<]+)<\/p>/)[1];
const textprov = createRequire(import.meta.url)("../js/textprov.js");

test("only the experimental example is a decoder region and its download matches", () => {
  assert.equal((homepage.match(/data-prov-document/g) ?? []).length, 1);
  assert.match(homepage, /aria-controls="sample-passage"/);
  assert.equal(sample, readFileSync(new URL('./public/samples/marked-text.txt', import.meta.url), 'utf8').trim());
  assert.ok(sample.includes(String.fromCodePoint(0xe0100)) && sample.includes(String.fromCodePoint(0xe0101)));
  const rest = homepage.replace(sample, '');
  assert.ok(!/[\u{E0100}-\u{E01EF}]/u.test(rest), 'fresh proposal prose must not acquire historical labels');
  assert.deepEqual(textprov.runs(sample).filter(r => r.state).map(r => r.state), ['human', 'ai']);
  const nav = homepage.match(/<nav aria-label="Primary navigation">([\s\S]*?)<\/nav>/)[1];
  assert.equal((nav.match(/<a /g) ?? []).length, 1);
  assert.match(nav, /https:\/\/github.com\/textprov\/textprov/);
});

test("copy uses the original code-point sequence even after display rendering", async () => {
  const button = { hidden:true, addEventListener(event, fn) { this[event] = fn; } };
  const passage = { textContent:sample };
  const status = {};
  const copies = [];
  const source = readFileSync(new URL('./app.js', import.meta.url), 'utf8').replace(/^import .*;\n/gm, '');
  vm.runInNewContext(source, {
    textprov,
    initProvenanceDisplay() { passage.textContent = 'decorated DOM placeholder'; },
    document: { getElementById(id) { return { 'sample-passage':passage, 'sample-copy-button':button, 'sample-copy-status':status }[id]; } },
    window: { localStorage:null },
    navigator: { clipboard: { async writeText(text) { copies.push(text); } } }
  });
  assert.equal(button.hidden, false);
  await button.click();
  assert.deepEqual(copies, [sample]);
  assert.equal(status.textContent, 'Copied with experimental VS marks.');
});
