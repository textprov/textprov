import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { test } from "node:test";
import vm from "node:vm";
import { markHtml } from "./mark-html.js";
import { stripDemo } from "./mark-markdown.js";

const homepage = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const sample = homepage.match(/<p id="sample-passage"[^>]*>([^<]+)<\/p>/)[1];
const textprov = createRequire(import.meta.url)("../js/textprov.js");

test("homepage prose and example have embedded labels and its download matches", () => {
  assert.equal((homepage.match(/data-prov-document/g) ?? []).length, 2);
  assert.match(homepage, /aria-controls="main homepage-footer"/);
  assert.equal(sample, readFileSync(new URL('./public/samples/marked-text.txt', import.meta.url), 'utf8').trim());
  assert.ok(sample.includes(String.fromCodePoint(0xe0100)) && sample.includes(String.fromCodePoint(0xe0101)));
  const rest = homepage.replace(sample, '');
  assert.ok(rest.includes('\u{E0101}'), 'homepage prose contains AI demo labels');
  assert.equal(markHtml(homepage), homepage, 'encoding is idempotent');
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

 test("HTML encoding preserves markup, SVG, code, and existing human labels", () => {
  const source = '<head><title>Title</title></head><main><h1 id="heading">Draft</h1><p><a href="./model.html">Model</a> &amp; h\u{E0100}uman.</p><code>Voice1</code><svg><text>Hello</text></svg><button>Copy</button></main>';
  const encoded = markHtml(source);
  assert.equal(stripDemo(encoded), stripDemo(source));
  assert.equal(markHtml(encoded), encoded);
  assert.ok(encoded.includes('h\u{E0100}'));
  assert.ok(encoded.includes('<svg><text>Hello</text></svg>'));
  assert.ok(encoded.includes('<code>Voice1</code>'));
  assert.ok(encoded.includes('href="./model.html"'));
  assert.ok(encoded.includes('D\u{E0101}'));
});
