import assert from "node:assert/strict";
import { test } from "node:test";
import { renderSpec } from "./build-spec.js";

const template = "<nav><!-- TOC --></nav><main><!-- SPEC --></main>";
const repoDocs = "https://github.com/textprov/textprov/blob/main/docs/";

function hrefs(html) {
  return [...html.matchAll(/href="([^"]*)"/g)].map((match) => match[1]);
}

test("spec rewrites repository documentation links and preserves fragments", () => {
  const html = renderSpec(
    [
      '[Maturity](docs/MATURITY.md "Lifecycle")',
      "[ADR](docs/adr/0011-the-producer-is-text-processing.md#decision)",
      "[Development](./docs/development/dogfooding.md#workflow)",
      "[Reference][maturity]",
      "",
      "[maturity]: docs/MATURITY.md#candidate",
    ].join("\n\n"),
    template,
  );

  assert.deepEqual(hrefs(html), [
    `${repoDocs}MATURITY.md`,
    `${repoDocs}adr/0011-the-producer-is-text-processing.md#decision`,
    `${repoDocs}development/dogfooding.md#workflow`,
    `${repoDocs}MATURITY.md#candidate`,
  ]);
  assert.ok(html.includes('title="Lifecycle">Maturity</a>'));
});

test("spec leaves anchors, external URLs, and other paths unchanged", () => {
  const targets = [
    "#states",
    "https://example.com/docs/guide.md#section",
    "http://example.com/docs/guide.md",
    "//example.com/docs/guide.md",
    "mailto:docs@example.com",
    "https://github.com/textprov/textprov/blob/main/docs/MATURITY.md#stable",
    "/docs/MATURITY.md",
    "README.md#development",
    "docs-other/guide.md",
  ];
  const html = renderSpec(targets.map((target) => `[Link](${target})`).join("\n\n"), template);
  assert.deepEqual(hrefs(html), targets);
});

test("spec rewrites documentation links inside headings and nested markup", () => {
  const html = renderSpec(
    [
      "## [Maturity](docs/MATURITY.md#stable)",
      "> - [**ADR**](docs/adr/0011-the-producer-is-text-processing.md#decision)",
    ].join("\n\n"),
    template,
  );

  assert.ok(html.includes(`<a href="${repoDocs}MATURITY.md#stable">Maturity</a>`));
  assert.ok(
    html.includes(
      `<a href="${repoDocs}adr/0011-the-producer-is-text-processing.md#decision"><strong>ADR</strong></a>`,
    ),
  );
  assert.ok(!html.includes('href="docs/'));
});

test("spec keeps section and ToC anchors local without rewriting code or images", () => {
  const source = [
    "# SPEC.md",
    "---",
    "# TextProv protocol specification",
    "## States",
    "[**Maturity**](docs/MATURITY.md#stable)",
    "`[Example](docs/example.md)`",
    "![Diagram](docs/diagram.png)",
  ].join("\n\n");
  const html = renderSpec(source, template);

  assert.deepEqual(hrefs(html), ["#states", "#states", `${repoDocs}MATURITY.md#stable`]);
  assert.ok(html.includes('id="states"'));
  assert.ok(html.includes("><strong>Maturity</strong></a>"));
  assert.ok(html.includes("<code>[Example](docs/example.md)</code>"));
  assert.ok(html.includes('src="docs/diagram.png"'));
  assert.ok(!html.includes("<h1"));
  assert.equal(renderSpec(source, template), html);
});
