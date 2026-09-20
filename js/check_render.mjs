// js/check_render.mjs

// Exercises textprov.render() under jsdom: DOM structure, custom prefix,
// re-render idempotency, ancestor-skip, and script/style/textarea exclusion.
// Usage: node check_render.mjs [path/to/textprov.js]
// Exits non-zero on any failing case.
import path from "path";
import { createRequire } from "module";
import { fileURLToPath } from "url";
import { JSDOM } from "jsdom";

const here = path.dirname(fileURLToPath(import.meta.url));
const target = path.resolve(process.argv[2] || path.join(here, "textprov.js"));

const dom = new JSDOM("<!doctype html><html><body></body></html>");
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.NodeFilter = dom.window.NodeFilter;

const textprov = createRequire(import.meta.url)(target);

const AI = "\u{E0101}";
const HUMAN = "\u{E0100}";

let fail = 0;
const cases = [];
const t = (name, fn) => cases.push({ name, fn });

const setBody = (html) => {
  document.body.innerHTML = html;
  return document.body;
};

t("render wraps marked runs in spans, leaves plain text alone", () => {
  const body = setBody(`hi${AI} there`);
  const n = textprov.render(body);
  if (n !== 1) throw new Error(`span count: got ${n}, want 1`);
  const spans = body.querySelectorAll("span.prov");
  if (spans.length !== 1) throw new Error(`spans: got ${spans.length}, want 1`);
  const s = spans[0];
  if (s.className !== "prov prov-ai") throw new Error(`class: got "${s.className}"`);
  if (s.dataset.prov !== "ai") throw new Error(`data-prov: got "${s.dataset.prov}"`);
  // The VS binds to its preceding grapheme cluster ("i"), so only that
  // cluster is inside the span; the leading "h" stays as a plain text node.
  if (s.textContent !== `i${AI}`) throw new Error(`text: got ${JSON.stringify(s.textContent)}`);
  if (body.textContent !== `hi${AI} there`)
    throw new Error(`round-trip text: ${JSON.stringify(body.textContent)}`);
});

t("custom prefix rewrites class and skip marker", () => {
  const body = setBody(`x${AI}`);
  textprov.render(body, { prefix: "prov" });
  const before = body.innerHTML;
  textprov.render(body, { prefix: "prov" });
  if (body.innerHTML !== before)
    throw new Error(`default-prefix idempotency broke: ${body.innerHTML}`);

  const body2 = setBody(`x${AI}`);
  const n = textprov.render(body2, { prefix: "mark" });
  if (n !== 1) throw new Error(`custom-prefix span count: got ${n}`);
  const s = body2.querySelector("span");
  if (s.className !== "mark mark-ai")
    throw new Error(`custom-prefix class: got "${s.className}"`);
});

t("re-render is idempotent (ancestor-skip via prefix class)", () => {
  const body = setBody(`hi${AI} you${HUMAN}`);
  const first = textprov.render(body);
  const html = body.innerHTML;
  const second = textprov.render(body);
  if (second !== 0) throw new Error(`second pass created ${second} spans, want 0`);
  if (body.innerHTML !== html)
    throw new Error(`re-render mutated DOM:\n  before ${html}\n  after  ${body.innerHTML}`);
  if (first < 1) throw new Error(`first pass created no spans`);
});

t("script, style, textarea contents are not walked", () => {
  const body = setBody(
    `<script>var x = "a${AI}";</script>` +
      `<style>/* a${AI} */</style>` +
      `<textarea>a${AI}</textarea>` +
      `visible a${AI}`,
  );
  const n = textprov.render(body);
  if (n !== 1) throw new Error(`spans: got ${n}, want 1 (visible only)`);
  const scriptText = body.querySelector("script").textContent;
  if (!scriptText.includes(AI))
    throw new Error(`script content was mutated: ${JSON.stringify(scriptText)}`);
  const styleText = body.querySelector("style").textContent;
  if (!styleText.includes(AI)) throw new Error(`style content was mutated`);
  const taText = body.querySelector("textarea").textContent;
  if (!taText.includes(AI)) throw new Error(`textarea content was mutated`);
});

t("strip option removes selector from span text but keeps state", () => {
  const body = setBody(`hi${AI}`);
  textprov.render(body, { strip: true });
  const s = body.querySelector("span");
  if (s.textContent !== "i") throw new Error(`strip text: got ${JSON.stringify(s.textContent)}`);
  if (s.dataset.prov !== "ai") throw new Error(`strip state: got "${s.dataset.prov}"`);
});

t("PUA input is re-emitted as base + selector in the span", () => {
  const H_PUA = String.fromCodePoint(0x100048);
  const body = setBody(H_PUA);
  textprov.render(body);
  const s = body.querySelector("span");
  if (s.textContent !== `H${AI}`)
    throw new Error(`pua re-emit: got ${JSON.stringify(s.textContent)}, want "H${AI}"`);
  if (s.dataset.prov !== "ai") throw new Error(`pua state: got "${s.dataset.prov}"`);
});

t("nested elements: text nodes at multiple depths are walked", () => {
  const body = setBody(`<p>hi${AI}</p><div><span>you${HUMAN}</span></div>`);
  const n = textprov.render(body);
  if (n !== 2) throw new Error(`nested spans: got ${n}, want 2`);
  const provs = Array.from(body.querySelectorAll(".prov")).map((s) => s.dataset.prov);
  if (provs.join(",") !== "ai,human") throw new Error(`states: ${provs.join(",")}`);
});

for (const c of cases) {
  try {
    c.fn();
    console.log("PASS", c.name);
  } catch (e) {
    fail++;
    console.log("FAIL", c.name, "\n     ", e.message);
  }
}
console.log(`${path.relative(process.cwd(), target)}: ${cases.length - fail}/${cases.length} pass`);
process.exit(fail ? 1 : 0);
