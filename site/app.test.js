import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

function demo() {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        value: id === "demo-input" ? "Hello" : "",
        textContent: "",
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
    Intl,
    Blob,
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
      createElement: () => element("download-link"),
      body: { appendChild() {} },
    },
  });
  vm.runInContext(readFileSync(new URL("../js/textprov.js", import.meta.url), "utf8"), context);
  // Use real decoding; DOM styling is outside these unit tests.
  context.textprov.render = (output) =>
    context.textprov.runs(output.textContent).filter((run) => run.state).length;
  const source = readFileSync(new URL("./app.js", import.meta.url), "utf8");
  vm.runInContext(source.replace('import "../js/textprov.js";', ""), context);
  return { element, state, downloads, copied };
}

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

test("reader reports existing labels without changing the input", () => {
  const { element } = demo();
  const input = element("check-input");
  input.value = "A\u{E0100} B\u{E0101} C\u{E0102} D\u{E0103} E\u{E0104}";
  input.listeners.input();
  assert.equal(element("check-output").textContent, input.value);
  assert.match(element("check-status").textContent, /human, ai, mixed, edited, unknown/);
  input.value = "<script>ordinary text</script>";
  input.listeners.input();
  assert.equal(element("check-output").textContent, input.value);
  assert.match(element("check-status").textContent, /No TextProv labels found/);
  input.value = "";
  input.listeners.input();
  assert.equal(element("check-status").textContent, "Waiting for text.");
});

test("font examples are distinct, self-describing, and carry the expected labels", () => {
  const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
  const examples = [
    ...html.matchAll(/<p class="font-sample[^"]*" data-example="([^"]+)">([^<]+)<\/p>/g),
  ];
  assert.deepEqual(
    examples.map(([, name]) => name),
    ["ordinary", "local", "maryheather", "zilla"],
  );
  const visible = examples.map(([, , marked]) => marked.replace(/[\u{E0100}-\u{E01EF}]/gu, ""));
  assert.equal(new Set(visible).size, examples.length);
  assert.match(visible[0], /ordinary font should make it look like normal prose/);
  assert.match(visible[1], /sawtooth underline when a compatible P\+ font is installed/);
  assert.match(visible[2], /Maryheather is loaded from this page/);
  assert.match(visible[3], /Zilla Slab is the active webfont/);
  assert.doesNotMatch(examples[0][2], /\u{E0100}/u);
  for (const [, name, marked] of examples.slice(1)) {
    assert.match(marked, /\u{E0100}/u, `${name} includes Human labels`);
    assert.match(marked, /\u{E0101}/u, `${name} includes AI labels`);
  }
});

test("long static sample reveals Human and AI labels when pasted", () => {
  const file = readFileSync(new URL("./public/samples/marked-text.txt", import.meta.url), "utf8");
  assert.equal(file.codePointAt(0), 0xfeff, "UTF-8 BOM lets browsers identify the text encoding");
  const sample = file.slice(1);
  const visible = sample.replace(/[\u{E0100}-\u{E01EF}]/gu, "");
  assert.match(visible, /This paragraph declares itself Human/);
  assert.match(visible, /This paragraph declares itself AI/);
  assert.ok(visible.length > 300);
  const { element } = demo();
  element("check-input").value = sample;
  element("check-input").listeners.input();
  assert.equal(element("check-output").textContent, sample);
  assert.match(element("check-status").textContent, /Labels found: human, ai\./);
});

test("local-font example cannot download a webfont", () => {
  const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
  const rule = css.match(/@font-face\s*\{[^}]*font-family: "TextProv Local P\+"[^}]*\}/)[0];
  assert.match(rule, /local\("Maryheather TextProv Demo P\+"\)/);
  assert.doesNotMatch(rule, /url\(/);
});

test("marking pasted text replaces existing labels rather than stacking them", () => {
  const { element, state } = demo();
  element("demo-input").value = "A\u{E0101} B";
  state.value = "human";
  element("demo-input").listeners.input();
  assert.equal(element("demo-output").textContent, "A\u{E0100} B\u{E0100}");
});
