// js/check_fixtures.mjs

// Runs textprov.js against ../fixtures.json and ../ucd/GraphemeBreakTest.txt,
// and checks the tables it embeds (textprov.mapping) against ../mapping.json,
// which it never loads at runtime.
// Usage: node check_fixtures.mjs [path/to/textprov.js]
// Exits non-zero on any failing case, version mismatch, or table drift.
import fs from "fs";
import path from "path";
import { createRequire } from "module";
import { fileURLToPath } from "url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "..");
const target = path.resolve(process.argv[2] || path.join(here, "textprov.js"));
const textprov = createRequire(import.meta.url)(target);
const fx = JSON.parse(fs.readFileSync(path.join(root, "fixtures.json"), "utf8"));

let fail = 0;

// The embedded tables must match the canonical registry.
const map = JSON.parse(fs.readFileSync(path.join(root, "mapping.json"), "utf8"));
const cp = (s) => parseInt(s.slice(2), 16);
const selectors = {};
for (const [name, value] of Object.entries(map.variation_selectors)) selectors[name] = cp(value);
const ranges = [];
for (const [key, entry] of Object.entries(map.pua).sort((a, b) => cp(a[0]) - cp(b[0]))) {
  const point = cp(key);
  if (point - 0x100000 !== cp(entry.base) || (entry.provenance || "ai") !== "ai") {
    fail++;
    console.log(`FAIL mapping.json ${key}: textprov.js assumes PUA = 0x100000 + base and state ai`);
  }
  const last = ranges[ranges.length - 1];
  if (last && last[1] === point - 1) last[1] = point;
  else ranges.push([point, point]);
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
if (!same(textprov.mapping.selectors, selectors)) {
  fail++;
  console.log(
    "FAIL selectors: textprov.js",
    JSON.stringify(textprov.mapping.selectors),
    "mapping.json",
    JSON.stringify(selectors),
  );
}
if (!same(textprov.mapping.puaRanges, ranges)) {
  fail++;
  console.log(
    "FAIL puaRanges: textprov.js",
    JSON.stringify(textprov.mapping.puaRanges),
    "mapping.json",
    JSON.stringify(ranges),
  );
}
if (textprov.mapping.version !== map.version) {
  fail++;
  console.log(
    `FAIL registry version: textprov.js ${textprov.mapping.version}, mapping.json ${map.version}`,
  );
}

if (textprov.specVersion !== fx.spec_version) {
  fail++;
  console.log(
    `FAIL specification version: implementation ${textprov.specVersion}, fixture ${fx.spec_version}`,
  );
}
if (textprov.registryVersion !== fx.registry_version) {
  fail++;
  console.log(
    `FAIL registry version: implementation ${textprov.registryVersion}, fixture ${fx.registry_version}`,
  );
}
for (const c of fx.cases) {
  const got = textprov.runs(c.input, c.options);
  if (JSON.stringify(got) !== JSON.stringify(c.runs)) {
    fail++;
    console.log("FAIL", c.name, "\n got", JSON.stringify(got), "\n exp", JSON.stringify(c.runs));
  }
}
console.log(`${path.relative(process.cwd(), target)}: ${fx.cases.length - fail}/${fx.cases.length} pass`);

// Segmentation: every line of Unicode's GraphemeBreakTest.txt for the pinned
// version. "÷" marks a boundary, "×" its absence; the text after "#" is a
// comment.
const testFile = path.join(root, "ucd", "GraphemeBreakTest.txt");
const lines = fs.readFileSync(testFile, "utf8").split("\n");
const declared = /GraphemeBreakTest-(\d+\.\d+\.\d+)\.txt/.exec(lines[0])[1];
let segmentFail = 0;
if (declared !== textprov.unicodeVersion) {
  fail++;
  segmentFail++;
  console.log(`FAIL Unicode version: textprov.js ${textprov.unicodeVersion}, test file ${declared}`);
}
let segmentTotal = 0;
for (const line of lines) {
  const body = line.split("#")[0].trim();
  if (!body) continue;
  const expected = [];
  let current = "";
  for (const token of body.split(/\s+/).slice(1)) {
    if (token === "÷") {
      expected.push(current);
      current = "";
    } else if (token !== "×") current += String.fromCodePoint(parseInt(token, 16));
  }
  segmentTotal++;
  const got = textprov.segments(expected.join(""));
  if (!same(got, expected)) {
    fail++;
    segmentFail++;
    console.log("FAIL segments", body, "\n got", JSON.stringify(got));
  }
}
console.log(`GraphemeBreakTest-${declared}: ${segmentTotal - segmentFail}/${segmentTotal} pass`);
process.exit(fail ? 1 : 0);
