// Runs textprov.js against ../fixtures.json and checks the tables it embeds
// (textprov.mapping) against ../mapping.json, which it never loads at runtime.
// Usage: node check_fixtures.mjs [path/to/textprov.js]
// Exits non-zero on any failing case, version mismatch, or table drift.
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
const target = path.resolve(process.argv[2] || path.join(here, 'textprov.js'));
const textprov = createRequire(import.meta.url)(target);
const fx = JSON.parse(fs.readFileSync(path.join(root, 'fixtures.json'), 'utf8'));

let fail = 0;

// The embedded tables must match the canonical registry.
const map = JSON.parse(fs.readFileSync(path.join(root, 'mapping.json'), 'utf8'));
const cp = s => parseInt(s.slice(2), 16);
const selectors = {};
for (const [name, value] of Object.entries(map.variation_selectors)) selectors[name] = cp(value);
const ranges = [];
for (const [key, entry] of Object.entries(map.pua).sort((a, b) => cp(a[0]) - cp(b[0]))) {
  const point = cp(key);
  if (point - 0x100000 !== cp(entry.base) || (entry.provenance || 'ai') !== 'ai') {
    fail++;
    console.log(`FAIL mapping.json ${key}: textprov.js assumes PUA = 0x100000 + base and state ai`);
  }
  const last = ranges[ranges.length - 1];
  if (last && last[1] === point - 1) last[1] = point; else ranges.push([point, point]);
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
if (!same(textprov.mapping.selectors, selectors)) {
  fail++;
  console.log('FAIL selectors: textprov.js', JSON.stringify(textprov.mapping.selectors), 'mapping.json', JSON.stringify(selectors));
}
if (!same(textprov.mapping.puaRanges, ranges)) {
  fail++;
  console.log('FAIL puaRanges: textprov.js', JSON.stringify(textprov.mapping.puaRanges), 'mapping.json', JSON.stringify(ranges));
}
if (textprov.mapping.version !== map.version) {
  fail++;
  console.log(`FAIL mapping version: textprov.js ${textprov.mapping.version}, mapping.json ${map.version}`);
}

if (textprov.contractVersion !== fx.contract_version) {
  fail++;
  console.log(`FAIL contract version: implementation ${textprov.contractVersion}, fixture ${fx.contract_version}`);
}
if (textprov.mappingVersion !== fx.mapping_version) {
  fail++;
  console.log(`FAIL mapping version: implementation ${textprov.mappingVersion}, fixture ${fx.mapping_version}`);
}
for (const c of fx.cases) {
  const got = textprov.runs(c.input, c.options);
  if (JSON.stringify(got) !== JSON.stringify(c.runs)) {
    fail++;
    console.log('FAIL', c.name, '\n got', JSON.stringify(got), '\n exp', JSON.stringify(c.runs));
  }
}
console.log(`${path.relative(process.cwd(), target)}: ${fx.cases.length - fail}/${fx.cases.length} pass`);
process.exit(fail ? 1 : 0);
