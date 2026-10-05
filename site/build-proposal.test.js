import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { documents, renderDocument, renderProposal } from "./build-proposal.js";

test("canonical proposal pages publish every candidate without specification metadata", () => {
  const sources = Object.fromEntries(documents.map(([, , path]) => [path, readFileSync(new URL(`../${path}`, import.meta.url), "utf8")]));
  const html = renderProposal(sources);
  for (const [id] of documents) assert.ok(html.includes(`<section id="${id}">`));
  assert.ok(!html.includes("data-prov-document"), "ordinary proposal prose must not be decoded as historical VS labels");
  assert.ok(!html.includes("Registry version"));
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  assert.equal(new Set(ids).size, ids.length, "generated anchors must be unique");
  for (const [, fragment] of html.matchAll(/href="#([^"]+)"/g)) assert.ok(ids.includes(fragment), `Missing fragment ${fragment}`);
});

test("relative document links and fragments resolve to the published sections", () => {
  const entries = [["model", "Model", "docs/model.md"], ["vs", "VS", "docs/encodings/vs.md"]];
  const html = renderDocument('# Model\n\n[VS](encodings/vs.md#trade-offs) [Here](#model) [Unicode](https://unicode.org/)\n', 'docs/model.md', 'model', entries);
  assert.match(html, /href="#vs--trade-offs"/);
  assert.match(html, /href="#model--model"/);
  assert.match(html, /href="https:\/\/unicode.org\/"/);
});

test("duplicate headings receive separate anchors", () => {
  const html = renderDocument('# Model\n\n## Decision\n\n## Decision\n', 'docs/model.md', 'model');
  assert.match(html, /id="model--decision"/);
  assert.match(html, /id="model--decision-1"/);
});
