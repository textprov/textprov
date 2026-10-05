import assert from "node:assert/strict";
import { test } from "node:test";
import { marked } from "marked";
import { readFileSync } from "node:fs";
import { documents } from "./build-proposal.js";
import { markMarkdown, stripDemo } from "./mark-markdown.js";
import { markHtml } from "./mark-html.js";

test("Markdown and HTML encoders preserve named entities containing digits", () => {
  const entities = ["&frac12;", "&sup2;", "&there4;", "&amp;", "&#189;", "&#xBD;"];
  const prose = `Before ${entities.join(" ")} after.`;
  for (const [source, encode] of [[prose, markMarkdown], [`<main><p>${prose}</p></main>`, markHtml]]) {
    const result = encode(source);
    assert.ok(result.includes("B\u{E0101}"), "surrounding prose must still be marked");
    for (const entity of entities) assert.ok(result.includes(entity), `entity must remain intact: ${entity}`);
    assert.equal(stripDemo(result), source);
    assert.equal(encode(result), result, "repeated encoding must preserve entities and labels");
    assert.equal(stripDemo(marked.parse(result)), marked.parse(source));
  }
});

test("encoding preserves Markdown structure, URLs, code, and existing labels", () => {
  const source = '# Heading\n\n**Bold** and [label](https://example.org/a#b "Title") &amp; `Voice1`.\n\n| Cell | Value |\n| --- | --- |\n| Test | `a+b` |\n\n1. List item\n\n```js\nconst x = "Hello";\n```\n\nAlready h\u{E0100}uman.\n';
  const result = markMarkdown(source);
  assert.equal(stripDemo(result), stripDemo(source));
  assert.equal(stripDemo(marked.parse(result)), stripDemo(marked.parse(source)));
  assert.equal(markMarkdown(result), result, "existing marks must survive repeated runs");
  assert.ok(result.includes('h\u{E0100}'));
  assert.ok(result.includes('https://example.org/a#b "Title"'));
  assert.ok(result.includes('const x = "Hello";'));
  assert.ok(result.includes('`Voice1`'));
});

test("each published Markdown source contains demo labels and remains parseable", () => {
  for (const [, , path] of documents) {
    const source = readFileSync(new URL(`../${path}`, import.meta.url), "utf8");
    assert.ok(source.includes('\u{E0101}'), path);
    assert.equal(stripDemo(marked.parse(source)), marked.parse(stripDemo(source)), path);
  }
});
