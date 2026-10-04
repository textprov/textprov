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
  // Expose the private producer only in this VM; the browser API stays unchanged.
  vm.runInContext(
    script.replace("  var demoInput =", "  globalThis.mark = mark;\n  var demoInput ="),
    context,
  );
  return { element, state, downloads, copied, context, mark: context.mark };
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

const selectorCases = fixtures.producer_cases.filter((c) => c.options.mode === "vs");
const selectorStates = [
  ["human", "\u{E0100}"],
  ["ai", "\u{E0101}"],
];

for (const c of selectorCases) {
  test(`selector producer fixture: ${c.name}`, () => {
    const { mark } = demo();
    const output = mark(c.input, c.options.state);
    assert.equal(output, c.output);
    assert.equal(mark(output, c.options.state), output, "marking twice is idempotent");
  });
}

test("selector producer fixtures cover both labels on unmarked input", () => {
  const { mark, context } = demo();
  const api = context.module.exports;
  for (const c of selectorCases) {
    // Existing selectors (even inert ones) and PUA claims are not ours to substitute.
    if (
      selectorStates.some(([, selector]) => c.input.includes(selector)) ||
      api.runs(c.input).some((run) => run.state)
    )
      continue;
    const fixtureSelector = String.fromCodePoint(api.mapping.selectors[c.options.state]);
    for (const [state, selector] of selectorStates) {
      const expected = c.output.replaceAll(fixtureSelector, selector);
      assert.equal(mark(c.input, state), expected, `${c.name}: ${state}`);
      assert.equal(mark(expected, state), expected, `${c.name}: ${state} idempotence`);
    }
  }
});

test("encoder leaves whitespace and control-break clusters bare beside marked text", () => {
  const { element, state } = demo();
  const input = element("demo-input");
  const bare = "\u0085\u0000\u00ad\u200b\u2060\u180e\u001c\u001d\u001e\u001f\ufeff\r\n";
  for (const [name, selector] of selectorStates) {
    state.value = name;
    input.value = `A${bare}B`;
    input.listeners.input();
    const expected = `A${selector}${bare}B${selector}`;
    assert.equal(element("demo-output").value, expected);
    assert.equal(element("demo-preview").textContent, expected);
    input.value = expected;
    input.listeners.input();
    assert.equal(element("demo-output").value, expected);
  }
});

test("producer preserves allocated trailing selectors, including inert and stacked ones", () => {
  const { mark } = demo();
  for (const [, existing] of selectorStates) {
    for (const input of [
      existing,
      ` ${existing}`,
      `\u0085${existing}`,
      `\u0000${existing}`,
      `\u200b${existing}`,
      existing + existing,
      `A${existing}`,
      `A${existing}${existing}`,
      `A\u{E0100}\u{E0101}`,
    ]) {
      for (const [state] of selectorStates) {
        assert.equal(mark(input, state), input, `${state}: ${JSON.stringify(input)}`);
      }
    }
  }
});

test("encoder does not stack selectors retained by the strip pass", () => {
  const { element, state } = demo();
  const input = element("demo-input");
  for (const [, existing] of selectorStates) {
    const inert = `${existing} ${existing}\u0085${existing}\u0000${existing}\u200b${existing}`;
    for (const [name, selector] of selectorStates) {
      state.value = name;
      input.value = `${inert}A${existing}${existing} B`;
      input.listeners.input();
      const expected = `${inert}A${existing} B${selector}`;
      assert.equal(element("demo-output").value, expected);
      assert.equal(element("demo-preview").textContent, expected);
    }
  }
});

test("producer keeps unallocated selectors and markable format characters", () => {
  const { mark } = demo();
  for (const [state, selector] of selectorStates) {
    for (const cluster of [
      "\u{E0102}",
      "\u{E01EF}",
      "A\u{E0102}",
      "\u200c",
      "\u200d",
      "A\u200c",
      "A\u200d",
      "\u{E0067}",
      " \u0301",
      "\u{100000}",
    ]) {
      const expected = cluster + selector;
      assert.equal(mark(cluster, state), expected, `${state}: ${JSON.stringify(cluster)}`);
      assert.equal(mark(expected, state), expected);
    }
    assert.equal(mark("", state), "");
  }
});

test("producer preserves existing selector and PUA claims across label choices", () => {
  const { mark } = demo();
  const input = "A\u{E0100} B\u{E0101} \u{100048}";
  for (const [state] of selectorStates) assert.equal(mark(input, state), input);
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

test("encoder explicitly relabels registered PUA input using selectors", () => {
  const { element, state } = demo();
  const input = element("demo-input");
  for (const [name, selector] of selectorStates) {
    state.value = name;
    input.value = "\u{100048}";
    input.listeners.input();
    assert.equal(element("demo-output").value, `H${selector}`);
    assert.equal(element("demo-preview").textContent, `H${selector}`);
  }
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

test("homepage offers Unicode-safe clipboard commands and keeps the manual file links", () => {
  assert.match(homepage, /<h3>Copy the file to your clipboard<\/h3>/);
  const sampleUrl = "https://textprov.org/samples/marked-text.txt";
  const commands = Array.from(
    homepage.matchAll(/<pre><code>([^<]+)<\/code><\/pre>/g),
    (match) => match[1],
  );
  assert.deepEqual(commands, [
    `curl -fsSL ${sampleUrl} | LANG=en_US.UTF-8 pbcopy`,
    `[System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -UseBasicParsing '${sampleUrl}').RawContentStream.ToArray()) | Set-Clipboard`,
    `curl -fsSL ${sampleUrl} | wl-copy`,
    `curl -fsSL ${sampleUrl} | xclip -selection clipboard`,
  ]);
  for (const system of [
    "macOS (Terminal)",
    "Windows (PowerShell)",
    "Linux (Wayland)",
    "Linux (X11)",
  ]) {
    assert.ok(homepage.includes(`<strong>${system}</strong>`));
  }
  assert.match(homepage, /href="\.\/samples\/marked-text\.txt" target="_blank"/);
  assert.match(homepage, /href="\.\/samples\/marked-text\.txt" download/);
});

test("clipboard commands show one system at a time behind tabs", () => {
  const { element } = demo();
  const shown = () =>
    ["macos", "windows", "wayland", "x11"].filter((p) => !element(`clip-panel-${p}`).hidden);
  assert.equal(element("clip-tabs").hidden, false);
  assert.deepEqual(shown(), ["macos"]);
  element("clip-tab-windows").listeners.click();
  assert.deepEqual(shown(), ["windows"]);
  assert.equal(element("clip-tab-windows").attributes["aria-selected"], "true");
  assert.equal(element("clip-tab-macos").attributes["aria-selected"], "false");
  for (const platform of ["macos", "windows", "wayland", "x11"]) {
    assert.match(homepage, new RegExp(`id="clip-tab-${platform}"[^>]*aria-controls="clip-panel-${platform}"`));
    assert.match(homepage, new RegExp(`<div id="clip-panel-${platform}"`));
  }
  assert.match(homepage, /<p id="clip-mobile" class="note" hidden>/);
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
