# textprov — JavaScript SDK demonstration

This browser decoder makes the experimental `human`/`ai` classifications visible
using HTML spans. It also decodes the limited replacement-PUA baseline. It does
not implement the proposal's voice references, infer authorship, or certify an
encoding. Package name and version describe executable code, not a proposal
standard. No special font is required. Python and Ruby provide producers;
JavaScript provides decoding and decoration.

From this checkout:

```js
const textprov = require("./textprov.js");
textprov.runs("f\u{E0101}oo");
// [{ state: "ai", text: "f\u{E0101}" }, { state: null, text: "oo" }]
```

Installable package identity remains `textprov`. It supports CommonJS,
ESM default import, and browser scripts through `window.textprov`.

## Browser sample

```html
<link rel="stylesheet" href="textprov.css">
<script src="textprov.js"></script>
<div id="sample">f&#xE0101;oo</div>
<script>textprov.render(document.querySelector("#sample"));</script>
```

Restrict rendering to deliberately marked demonstration text. Recognizing
selectors by value collides with genuine variation sequences; stripping can
remove legitimate glyph selection. Do not run the experimental decoder over
arbitrary proposal prose. Read the [baseline limitations](../experiments/baseline/README.md),
[VS profile](../docs/encodings/vs.md), and [model](../docs/model.md).

## API

- `render(root?, options?)` decorates marked runs with `<span>` elements and
  returns the number created. It skips scripts, styles, textareas, and existing
  decorated descendants. Omitting `root` uses `document.body`; explicit sample
  scope is recommended.
- `runs(text, options?)` returns `[{ state, text }]`. Unmarked text has `null`;
  the proposal calls absence `Voice0` without adding a marker.
- `segments(text)` returns extended grapheme clusters using vendored Unicode
  17.0.0 tables, independently of the host's `Intl.Segmenter`.
- `unicodeVersion` identifies those Unicode tables.
- `mapping` exposes the embedded experimental selector and PUA tables.
- Legacy `specVersion` and `registryVersion` retain baseline identifier `0.2`;
  they do not version the proposal or reserve Unicode allocations.

| Option | Default | Implemented behavior |
| --- | --- | --- |
| `strip` | `false` | Remove recognized selectors or decode recognized PUA to bases; retain classification in returned state or `data-prov` |
| `merge_whitespace` | `true` | Join whitespace between runs with the same classification; `mergeWhitespace` is an alias |
| `prefix` | `"prov"` | Use `<prefix> <prefix>-<state>` CSS classes and skip their descendants on another render |

The default renderer preserves stored text code points. Optional `textprov.css`
adds a wavy underline for `ai` and a tint for `human`. These display choices do
not implement source identity or prescribe the proposal's presentation. The
replacement-PUA mode is distinct from the [additive-PUA candidate](../docs/encodings/additive-pua.md).

## Checks

From `js/`:

```sh
npm ci
npm test
```

Checks compare embedded tables against [baseline data](../experiments/baseline/README.md),
run shared fixtures and Unicode segmentation tests, and verify DOM decoration
preserves underlying text and avoids duplicate spans. Test dependencies are for
DOM checks; the runtime itself has none. See [UCD sources](../ucd/README.md).

MIT; see [LICENSE](LICENSE).
