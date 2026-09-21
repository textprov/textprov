# textprov

Client-side decorator for the [TextProv](https://github.com/textprov/textprov) protocol. Turns in-band provenance marks (Unicode variation selectors and a PUA block) into HTML `<span>` elements with a class and a `data-prov` attribute — so provenance is visible without installing any font.

The Python package of the same name (`pip install textprov`) is the full SDK — producer, decoder, and CLI. This npm package ships the browser decoder only.

- ~6 KB, no dependencies, browser-first (IIFE + `window.textprov`), also usable from Node (CJS) and via ESM default import.
- Implements draft specification version 0.1 and registry version 0.1 (see [SPEC.md](https://github.com/textprov/textprov/blob/main/SPEC.md) and [mapping.json](https://github.com/textprov/textprov/blob/main/mapping.json)).
- Optional companion stylesheet (`textprov.css`) reproduces the P+ font's mark styles (wavy for `ai`, dotted for `edited`, etc.).

States: `human`, `ai`, `mixed`, `edited`, `unknown`.

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
//   { state: "ai",    text: "Hello\u{E0101}" },
//   { state: null,    text: " " },
//   { state: "human", text: "world\u{E0100}" }
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
- `textprov.specVersion` — `"0.1"`
- `textprov.registryVersion` — `"0.1"`
- `textprov.mapping` — `{ version, selectors, puaRanges }`, the embedded tables (checked against the canonical `mapping.json` in CI).

### Options

| Option | Default | Description |
| --- | --- | --- |
| `strip` | `false` | Remove the selector code point from run text. State is still reported via `data-prov` / the returned `state`. |
| `merge_whitespace` | `true` | Whitespace between two runs of the same state joins them into a single run. `mergeWhitespace` is an accepted alias. |
| `prefix` | `"prov"` | Class prefix. `render()` emits `class="<prefix> <prefix>-<state>"` and skips descendants of `.<prefix>` on re-render. |

## Output shape

```html
Hello<span class="prov prov-ai" data-prov="ai">\u{E0101}</span>
```

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

MIT
