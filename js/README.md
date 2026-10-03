# textprov

Client-side decorator for the [TextProv](https://github.com/textprov/textprov) protocol. Turns in-band provenance marks (Unicode variation selectors and a PUA block) into HTML `<span>` elements with a class and a `data-prov` attribute — so provenance is visible without installing any font.

The Python package of the same name (`pip install textprov`) is the full SDK — producer, decoder, and CLI. This npm package ships the browser decoder only.

- ~37 KB (unminified, including vendored Unicode segmentation tables), no dependencies, browser-first (IIFE + `window.textprov`), also usable from Node (CJS) and via ESM default import.
- Implements draft specification version 0.2 and registry version 0󠄁.󠄁2󠄁 (see [SPEC.md](https://github.com/textprov/textprov/blob/main/SPEC.md) and [mapping.json](https://github.com/textprov/textprov/blob/main/mapping.json)).
- Optional companion stylesheet (`textprov.css`) uses a wavy underline for `ai` and a faint tint for `human`.

States: `human`, `ai`. Other variation selectors are ordinary non-TextProv text and are preserved, including with `strip: true`.

## Install

```sh
npm install textprov
```

## Usage

### Browser (script tag)

```html
<link rel="stylesheet" href="node_modules/textprov/textprov.css" />
<script src="node_modules/textprov/textprov.js"></script>
<script>
  textprov.render(document.body);
</script>
```

### Node (CommonJS)

```js
const textprov = require("textprov");

textprov.runs("Hello\u{E0101} world\u{E0100}");
// [
//   { state: null,    text: "Hell" },
//   { state: "ai",    text: "o\u{E0101}" },
//   { state: null,    text: " worl" },
//   { state: "human", text: "d\u{E0100}" }
// ]
```

### ESM

```js
import textprov from "textprov";

textprov.render(document.body, { strip: true, prefix: "prov" });
```

## API

- `textprov.render(root?, options?)` — walks text nodes under `root` (default `document.body`), replaces marked runs with `<span>` elements. Skips `<script>`, `<style>`, `<textarea>`, and anything already inside a `.<prefix>` element. Returns the number of spans created. Browser only.
- `textprov.runs(text, options?)` — returns `[{ state, text }]`. Environment-agnostic; use this in Node or for custom rendering.
- `textprov.segments(text)` — splits `text` into e󠄁x󠄁t󠄁e󠄁n󠄁d󠄁e󠄁d󠄁 g󠄁r󠄁a󠄁p󠄁h󠄁e󠄁m󠄁e󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁s󠄁 (󠄁U󠄁A󠄁X󠄁 #󠄁2󠄁9󠄁)󠄁,󠄁 t󠄁h󠄁e󠄁 u󠄁n󠄁i󠄁t󠄁s󠄁 a󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁,󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁s󠄁 v󠄁e󠄁n󠄁d󠄁o󠄁r󠄁e󠄁d󠄁 a󠄁t󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 1󠄁7󠄁.󠄁0󠄁.󠄁0󠄁.󠄁 D󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 u󠄁s󠄁e󠄁 `Intl.Segmenter`,󠄁 s󠄁o󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 e󠄁n󠄁v󠄁i󠄁r󠄁o󠄁n󠄁m󠄁e󠄁n󠄁t󠄁 a󠄁n󠄁d󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 p󠄁o󠄁r󠄁t󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 a󠄁l󠄁i󠄁k󠄁e󠄁.󠄁
- `textprov.unicodeVersion` —󠄁 `"17.0.0"`,󠄁 t󠄁h󠄁e󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 v󠄁e󠄁n󠄁d󠄁o󠄁r󠄁e󠄁d󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁s󠄁.󠄁
- `textprov.specVersion` — `"0.2"`
- `textprov.registryVersion` — `"0.2"`
- `textprov.mapping` — `{ version, selectors, puaRanges }`, the embedded tables (checked against the canonical `mapping.json` in CI).

### Options

| Option | Default | Description |
| --- | --- | --- |
| `strip` | `false` | Remove the selector code point from run text. State is still reported via `data-prov` / the returned `state`. |
| `merge_whitespace` | `true` | Whitespace between two runs of the same state joins them into a single run. `mergeWhitespace` is an accepted alias. |
| `prefix` | `"prov"` | Class prefix. `render()` emits `class="<prefix> <prefix>-<state>"` and skips descendants of `.<prefix>` on re-render. |

## Output shape

```html
Hell<span class="prov prov-ai" data-prov="ai">o&#xE0101;</span>
```

For input `Hello\u{E0101}`, only the final `o` is marked. The HTML character
reference `&#xE0101;` above represents the retained selector; `render()` keeps
the actual code point in the text node. To mark a whole word, a producer adds a
selector after each eligible grapheme cluster.

With `strip: true` the selector is removed from the span text; the class and `data-prov` remain.

## Styles

`textprov.css` is optional and not part of the decorator specification. It ships CSS custom properties on `:root` (with a `prefers-color-scheme: dark` override) and never affects layout — only `background` and `text-decoration` are set.

```html
<link rel="stylesheet" href="node_modules/textprov/textprov.css" />
```

## Links

- Protocol spec: <https://github.com/textprov/textprov/blob/main/SPEC.md>
- Mapping registry: <https://github.com/textprov/textprov/blob/main/mapping.json>
- Issues: <https://github.com/textprov/textprov/issues>

## License

A󠄁p󠄁a󠄁c󠄁h󠄁e󠄁-󠄁2󠄁.󠄁0󠄁
