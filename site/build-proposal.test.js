import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { documents, renderDocument, renderProposal, renderPage } from "./build-proposal.js";
const sources = Object.fromEntries(documents.map(([, , path]) => [path, readFileSync(new URL(`../${path}`, import.meta.url), "utf8")]));

test("every Markdown document has a page and every local link resolves", () => {
  const pages = Object.fromEntries(documents.map(entry => [`${entry[0]}.html`, renderPage(sources[entry[2]], entry)]));
  pages['proposal.html'] = renderProposal(sources);
  const ids = {};
  for (const [filename, html] of Object.entries(pages)) {
    if (filename !== "proposal.html") {
      assert.ok(html.includes("data-prov-document"), "marked prose must render its demo labels");
      assert.ok(html.includes("data-prov-toggle"));
    }
    assert.ok(!html.includes("Registry version"));
    assert.match(html, /CC BY 4.0/);
    assert.match(html, /Apache 2.0/);
    ids[filename] = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
    assert.equal(new Set(ids[filename]).size, ids[filename].length);
  }
  for (const [filename, html] of Object.entries(pages)) {
    for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
      if (href.startsWith('#')) assert.ok(ids[filename].includes(href.slice(1)), `${filename}: ${href}`);
      if (!href.startsWith('./') || !href.includes('.html')) continue;
      const [target, fragment] = href.slice(2).split('#');
      assert.ok(pages[target], `${filename}: missing ${target}`);
      if (fragment) assert.ok(ids[target].includes(fragment), `${filename}: missing ${href}`);
    }
  }
  for (const [id] of documents) {
    assert.ok(pages[`${id}.html`].includes(`href="./${id}.html" aria-current="page"`));
    assert.ok(pages['proposal.html'].includes(`href="./${id}.html"`));
  }
});

test("relative document links and fragments resolve to individual pages", () => {
  const entries = [["model", "Model", "docs/model.md"], ["vs", "VS", "docs/encodings/vs.md"]];
  const html = renderDocument('# Model\n\n[VS](encodings/vs.md#trade-offs) [Here](#model) [Unicode](https://unicode.org/)\n', 'docs/model.md', 'model', entries);
  assert.ok(html.includes('href="./vs.html#vs--trade-offs"'));
  assert.ok(html.includes('href="./model.html#model--model"'));
  assert.ok(html.includes('href="https://unicode.org/"'));
});

test("duplicate headings receive separate anchors", () => {
  const html = renderDocument('# Model\n\n## Decision\n\n## Decision\n', 'docs/model.md', 'model');
  assert.match(html, /id="model--decision"/);
  assert.match(html, /id="model--decision-1"/);
});
