import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { renderSpec, specMeta } from "./build-spec.js";

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

test("spec keeps provenance marks in prose and out of anchors and links", () => {
  const ai = (text) => Array.from(text, (c) => c + "\u{E0101}").join("");
  const source = [
    "## States",
    `${ai("Labels")} are **${ai("claims")}**, see [${ai("Discussion")} #13](https://example.com/13).`,
  ].join("\n\n");
  const html = renderSpec(source, template);

  assert.ok(html.includes('id="states"'));
  assert.ok(html.includes(`${ai("Labels")} are <strong>${ai("claims")}</strong>`));
  assert.ok(html.includes(`<a href="https://example.com/13">${ai("Discussion")} #13</a>`));
});

test("the spec template decorates only the specification body", () => {
  const shipped = readFileSync(new URL("./spec.template.html", import.meta.url), "utf8");
  assert.equal(shipped.match(/data-prov-document/g).length, 1);
  assert.match(shipped, /<article class="spec-body" data-prov-document>\s*<!-- SPEC -->/);
  assert.match(shipped, /<script type="module" src="spec\.js"><\/script>/);
  // Without JavaScript the toggle and legend stay hidden; the marks remain in the text.
  assert.match(shipped, /<button [^>]*data-prov-toggle hidden>/);
  assert.match(shipped, /<div class="prov-legend" id="prov-legend" hidden>/);
});

test("page chrome takes its versions and date from the marked SPEC.md status block", () => {
  const ai = (text) => Array.from(text, (c) => (c === " " ? c : c + "\u{E0101}")).join("");
  const source = [
    `> **${ai("Status: Draft")}** ${ai("Specification version: 0.3. Registry version: 0.2.")}`,
    `> ${ai("Updated: 2026-10-03.")}`,
  ].join("\n");
  assert.deepEqual(specMeta(source), {
    SPEC_VERSION: "0.3",
    REGISTRY_VERSION: "0.2",
    UPDATED: "2026-10-03",
  });

  const chrome = "<p><!-- SPEC_VERSION --> <!-- REGISTRY_VERSION --> <!-- UPDATED --></p><!-- SPEC -->";
  assert.ok(renderSpec(source, chrome).startsWith("<p>0.3 0.2 2026-10-03</p>"));
  assert.throws(() => renderSpec("## States", chrome), /no SPEC_VERSION/);

  // The shipped template states no version or date of its own.
  const shipped = readFileSync(new URL("./spec.template.html", import.meta.url), "utf8");
  assert.doesNotMatch(shipped, /version(?:&nbsp;| )\d|\d{4}-\d{2}-\d{2}/);
});
