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
r󠄁e󠄁v󠄁e󠄁a󠄁l󠄁s󠄁 b󠄁o󠄁t󠄁h󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 c󠄁l󠄁a󠄁s󠄁s󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁 g󠄁r󠄁a󠄁d󠄁i󠄁e󠄁n󠄁t󠄁 m󠄁i󠄁s󠄁t󠄁 a󠄁n󠄁d󠄁 a󠄁 d󠄁o󠄁t󠄁t󠄁e󠄁d󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁
a󠄁t󠄁 6󠄁0󠄁%󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁-󠄁c󠄁o󠄁l󠄁o󠄁r󠄁 o󠄁p󠄁a󠄁c󠄁i󠄁t󠄁y󠄁.󠄁 T󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁e󠄁r󠄁 w󠄁a󠄁v󠄁y󠄁/󠄁s󠄁a󠄁w󠄁t󠄁o󠄁o󠄁t󠄁h󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁 i󠄁s󠄁
d󠄁e󠄁f󠄁u󠄁n󠄁c󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁 [d󠄁i󠄁s󠄁p󠄁l󠄁a󠄁y󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁o󠄁n󠄁](../docs/development/provenance-display.md)
d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁s󠄁,󠄁 n󠄁a󠄁t󠄁i󠄁v󠄁e󠄁 a󠄁n󠄁n󠄁o󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 h󠄁o󠄁o󠄁k󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 m󠄁o󠄁n󠄁o󠄁c󠄁h󠄁r󠄁o󠄁m󠄁e󠄁 P󠄁+󠄁 f󠄁o󠄁n󠄁t󠄁 f󠄁a󠄁l󠄁l󠄁b󠄁a󠄁c󠄁k󠄁.󠄁
T󠄁h󠄁e󠄁s󠄁e󠄁 d󠄁i󠄁s󠄁p󠄁l󠄁a󠄁y󠄁 c󠄁h󠄁o󠄁i󠄁c󠄁e󠄁s󠄁 d󠄁o󠄁 n󠄁o󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁 o󠄁r󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁 s󠄁t󠄁o󠄁r󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁
T󠄁h󠄁e󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁m󠄁e󠄁n󠄁t󠄁-󠄁P󠄁U󠄁A󠄁 m󠄁o󠄁d󠄁e󠄁 i󠄁s󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁
[additive-PUA candidate](../docs/encodings/additive-pua.md).

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

Apache-2.0; see [LICENSE](LICENSE).
