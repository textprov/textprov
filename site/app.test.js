import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

const homepage = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const inlineSample = homepage.match(/<p id="sample-passage"[^>]*>([^<]+)<\/p>/)[1];
const fixtures = JSON.parse(readFileSync(new URL("../fixtures.json", import.meta.url), "utf8"));

export function demo({ withSample = false, appSource, intl = Intl } = {}) {
  const elements = new Map();
  function element(id) {
    if (id === "sample-passage" && !withSample) return null;
    if (!elements.has(id)) {
      elements.set(id, {
        value: id === "demo-input" ? "Hello" : "",
        textContent: id === "sample-passage" ? inlineSample : "",
        hidden: true,
        attributes: {},
        setAttribute(name, value) {
          this.attributes[name] = value;
        },
        listeners: {},
        addEventListener(event, callback) {
          this.listeners[event] = callback;
        },
        click() {
          this.clicked = true;
        },
        remove() {},
      });
    }
    return elements.get(id);
  }
  const state = { value: "ai", addEventListener() {} };
  const downloads = [];
  const copied = [];
  const context = vm.createContext({
    Intl: intl,
    Blob,
    module: { exports: {} },
    window: { isSecureContext: true },
    NodeFilter: { SHOW_TEXT: 4, FILTER_ACCEPT: 1, FILTER_REJECT: 2 },
    setTimeout: (callback) => callback(),
    URL: {
      createObjectURL(blob) {
        downloads.push(blob);
        return "blob:test";
      },
      revokeObjectURL() {},
    },
    navigator: {
      clipboard: {
        writeText(text) {
          copied.push(text);
          return Promise.resolve();
        },
      },
    },
    document: {
      getElementById: element,
      querySelector: () => state,
      querySelectorAll: () => [state],
      createElement: () =>
        Object.assign(element("download-link"), { relList: { supports: () => true } }),
      createTreeWalker: () => ({ nextNode: () => null }),
      body: { appendChild() {} },
    },
  });
  vm.runInContext(readFileSync(new URL("../js/textprov.js", import.meta.url), "utf8"), context);
  const api = context.module.exports;
  // Use real decoding; DOM styling is outside these unit tests.
  api.render = (output) => api.runs(output.textContent).filter((run) => run.state).length;
  const source = appSource ?? readFileSync(new URL("./app.js", import.meta.url), "utf8");
  const script = source.replace(
    /^import(?:\s+(\w+)\s+from)?\s+"(?:textprov|\.\.\/js\/textprov\.js)";/m,
    (_, binding) => (binding ? `const ${binding} = module.exports;` : ""),
  );
  vm.runInContext(script, context);
  return { element, state, downloads, copied, context };
}

test("site consumes CommonJS exports without a browser-global API", () => {
  const { context, element } = demo({ withSample: true });
  assert.equal(context.textprov, undefined);
  assert.equal(context.window.textprov, undefined);
  assert.equal(element("demo-output").value, "H\u{E0101}e\u{E0101}l\u{E0101}l\u{E0101}o\u{E0101}");
  element("reveal-button").listeners.click();
  assert.equal(element("reveal-button").attributes["aria-pressed"], "true");
});

test("copy and UTF-8 download carry the same marked text", async () => {
  const { element, downloads, copied } = demo();
  element("copy-button").listeners.click();
  element("download-button").listeners.click();
  await Promise.resolve();
  assert.equal(copied[0], "H\u{E0101}e\u{E0101}l\u{E0101}l\u{E0101}o\u{E0101}");
  assert.equal(await downloads[0].text(), copied[0]);
  assert.equal(downloads[0].type, "text/plain;charset=utf-8");
  assert.equal(element("download-link").download, "textprov-sample.txt");
  assert.equal(element("copy-status").textContent, "Copied with marks");
});

const clusterCases = fixtures.producer_cases.filter((c) =>
  [
    "a mark goes after combining marks",
    "a flag is one cluster",
    "a ZWJ sequence is one cluster",
    "a skin-tone modifier stays with its base",
    "VS16 presentation stays with its base",
    "a Hangul syllable of conjoining jamo is one cluster",
    "a Devanagari conjunct is one cluster",
    "a tag-sequence flag is one cluster",
    "Thai sara am stays with its consonant",
  ].includes(c.name),
);

test("encoder marks each cluster once", () => {
  assert.equal(clusterCases.length, 9);
  const { element } = demo();
  const input = element("demo-input");
  for (const c of clusterCases) {
    input.value = c.input;
    input.listeners.input();
    assert.equal(element("demo-output").value, c.output, c.name);
  }
});

test("reader reports existing labels without changing the input", () => {
  const { element } = demo();
  const input = element("check-input");
  input.value = "A\u{E0100} B\u{E0101} C\u{E0102} D\u{E0103} E\u{E0104}";
  input.listeners.input();
  assert.equal(element("check-output").textContent, input.value);
  assert.equal(
    element("check-status").textContent,
    "Labels found: human, ai. These are claims, not verified origins.",
  );
  input.value = "C\u{E0102} D\u{E0103} E\u{E0104}";
  input.listeners.input();
  assert.equal(element("check-output").textContent, input.value);
  assert.match(element("check-status").textContent, /No TextProv labels found/);
  input.value = "<script>ordinary text</script>";
  input.listeners.input();
  assert.equal(element("check-output").textContent, input.value);
  assert.match(element("check-status").textContent, /No TextProv labels found/);
  input.value = "";
  input.listeners.input();
  assert.equal(element("check-status").textContent, "Waiting for text.");
});

test("reveal and hide preserve the exact embedded marks, including copied text", async () => {
  const { element, copied } = demo({ withSample: true });
  const passage = element("sample-passage");
  const reveal = element("reveal-button");
  assert.equal(reveal.hidden, false);
  element("sample-copy-button").listeners.click();
  await Promise.resolve();
  assert.equal(copied[0], inlineSample);
  for (const expected of ["true", "false", "true"]) {
    reveal.listeners.click();
    assert.equal(reveal.attributes["aria-pressed"], expected);
    assert.equal(element("sample-legend").hidden, expected === "false");
    assert.equal(passage.textContent, inlineSample);
    element("sample-copy-button").listeners.click();
    await Promise.resolve();
    assert.equal(copied.at(-1), inlineSample);
  }
  assert.equal(element("reader").open, true);
  assert.match(element("sample-copy-status").textContent, /Copied with marks/);
});

test("the downloadable UTF-8 sample contains the same marks as the interactive passage", () => {
  const file = readFileSync(new URL("./public/samples/marked-text.txt", import.meta.url), "utf8");
  assert.equal(file.codePointAt(0), 0xfeff, "UTF-8 BOM lets browsers identify the text encoding");
  assert.equal(file.slice(1).trimEnd(), inlineSample);
  const { element } = demo();
  element("check-input").value = file;
  element("check-input").listeners.input();
  assert.equal(element("check-output").textContent, file);
  assert.match(element("check-status").textContent, /Labels found: human, ai\./);
});

test("marking pasted text replaces existing labels rather than stacking them", () => {
  const { element, state } = demo();
  element("demo-input").value = "A\u{E0101} B";
  state.value = "human";
  element("demo-input").listeners.input();
  assert.equal(element("demo-output").value, "A\u{E0100} B\u{E0100}");
  assert.equal(element("demo-preview").textContent, "A\u{E0100} B\u{E0100}");
});

test("encoder rejects obsolete and other unsupported state names", () => {
  const { element, state } = demo();
  const output = element("demo-output").value;
  for (const name of ["mixed", "edited", "unknown", "toString", "__proto__", ""]) {
    state.value = name;
    assert.throws(() => element("demo-input").listeners.input(), {
      name: "RangeError",
      message: "Unsupported provenance state: " + name,
    });
    assert.equal(element("demo-output").value, output);
  }
});

test("encoder preserves non-TextProv selectors while replacing human/AI labels", () => {
  const { element, state } = demo();
  for (const [name, selector] of [
    ["human", "\u{E0100}"],
    ["ai", "\u{E0101}"],
  ]) {
    state.value = name;
    element("demo-input").value = "A\u{E0102} B\u{E0103} C\u{E0104} D\u{E0100} E\u{E0101}";
    element("demo-input").listeners.input();
    const expected = `A\u{E0102}${selector} B\u{E0103}${selector} C\u{E0104}${selector} D${selector} E${selector}`;
    assert.equal(element("demo-output").value, expected);
    assert.equal(element("demo-preview").textContent, expected);
  }
});

test("homepage presents the reader and links to the separate encoder", () => {
  const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
  assert.match(html, /Try a marked passage/);
  assert.match(html, /Paste text to reveal labels/);
  assert.match(html, /href="\.\/encoder\.html"/);
  assert.doesNotMatch(html, /<p><\/p>Paste text/);
  assert.doesNotMatch(html, /<p><\/p>Need to add labels/);
  assert.doesNotMatch(html, /id="demo-input"/);
  assert.doesNotMatch(html, /\b(?:mixed|edited|unknown)\b/i);
  assert.deepEqual(
    Array.from(html.matchAll(/<th scope="row"><code>(\w+)<\/code>/g), (match) => match[1]),
    ["human", "ai"],
  );
});

test("encoder provides side-by-side source and marked output", () => {
  const html = readFileSync(new URL("./encoder.html", import.meta.url), "utf8");
  assert.match(html, /class="encoder-grid"/);
  assert.match(html, /id="demo-input"/);
  assert.match(html, /id="demo-output"[^>]*readonly/);
  assert.match(html, /id="demo-preview"/);
  assert.match(html, /does not detect AI writing or verify authorship/);
  assert.deepEqual(
    Array.from(html.matchAll(/name="state" value="(\w+)"/g), (match) => match[1]),
    ["human", "ai"],
  );
});
