# Rendering provenance marks in HTML without a special font

A TextProv decorator reads provenance marks already present in text and wraps
marked runs in HTML spans. CSS then displays the states without requiring a
provenance font or support for its variant glyphs. This is for page authors
and integrators who control the HTML or DOM; it does not determine whether a
provenance claim is true.

The decorator is implemented in this repository. Start with the
[JavaScript guide](../js/README.md) for browser integration or the
[Python guide](../python/README.md) for rendering text as HTML on the server.
This page explains the approach and records the original prototype measurements;
[SPEC.md](../SPEC.md#decoder) defines the current decoding rules.

## Why use spans instead of a font?

Font-based rendering needs both a matching provenance font (called a **P+
font**) and a text shaper that selects its decorated glyphs. Installing or
serving the font alone is not enough. In the recorded CoreText tests, selectors
remained in the text but did not select those glyphs. See the
[font and interchange guide](SELECTORS-PUA-AND-INTERCHANGE.md#known-limitation-selector-glyphs-on-macos-coretext)
for the evidence and limits.

A span decorator avoids that font-substitution dependency. Readers need no
special font installation. The page author must supply the decorator output
and CSS; client-side decoration also requires JavaScript and `Intl.Segmenter`.

## How decoration works

The input is marked Unicode text. A decoder splits it into runs, each with a
state or no state. A renderer emits marked runs as:

```html
<span class="prov prov-STATE" data-prov="STATE">TEXT</span>
```

`STATE` is a recognized label such as `ai`; `TEXT` is the run's text, escaped
when serialized as HTML. Unmarked runs remain text. The `data-prov` attribute
carries the state, while the classes let CSS style it.

This requires a text-processing pass, not CSS alone: CSS cannot select a code
point inside a text node. The decorator preserves selector-encoded text by
default and converts registered Private Use Area (PUA) characters to ordinary
base characters plus their selectors. It does not change the producer's role
of adding marks.

### Decoding rules

The [normative algorithm](../SPEC.md#algorithm) defines classification order,
including whitespace and lone selectors. In summary:

1. Identify grapheme clusters: a base character and the code points that belong
   with it, such as combining marks. JavaScript uses `Intl.Segmenter`; Python
   uses the package's `cluster_end` helper. Their segmentation is not guaranteed
   to agree for every Unicode sequence; see the
   [specification's limits](../SPEC.md#not-specified).
2. Read recognized selectors (`U+E0100`–`U+E0104`) or registered PUA entries
   using the [registry](../mapping.json). A lone selector or a selector after
   whitespace is not a mark under the contract.
3. Coalesce adjacent clusters with the same state. By default, absorb
   whitespace between two runs of the same non-null state, then coalesce again.
4. Emit spans for marked runs and text for the rest.

### Where to apply the pass

**In the browser**, `textprov.render(root)` walks text nodes and replaces
matching nodes with text and spans. It skips `script`, `style`, `textarea`,
and nodes already inside `.prov` (or the configured prefix class). Runs are
detected within each text node, not across element boundaries.

**On the server**, Python's `to_html(text)` accepts text, not an HTML document.
It escapes the input and returns an HTML fragment. To decorate existing HTML,
your integration must parse that HTML and apply the pass to eligible text
nodes. Passing a whole HTML document to `to_html` escapes its tags rather than
preserving its structure. For Markdown, render to HTML first and then decorate
the text nodes; do not wrap Markdown source in spans before parsing it.

## Text preservation and display options

- **Retain selectors by default.** Keeping selectors in span text lets a
  selection retain the encoding. Clipboard and destination behavior still need
  testing in the target workflow; the prototype measured selection strings, not
  physical clipboard round-trips.
- **Use `strip` only when losing plain-text copy provenance is acceptable.**
  It removes recognized mark selectors from run text while leaving the state on
  the span. This may help text matching, but find-in-page was not measured.
- **Merge whitespace by default.** Whitespace between equal-state runs joins
  the span for display. Producers do not mark whitespace. Set
  `merge_whitespace` to `false` to disable the merge.
- **Decode PUA to base plus selector.** The current implementations and
  [specification](../SPEC.md#encodings) use this form so the ordinary text and
  its state remain available without a P+ font. With `strip`, only the base
  character remains.

The markup and decoder options are part of the contract. The visual style is
not. The optional [stylesheet](../js/textprov.css) uses a wavy underline for
`ai`, a solid underline for `unknown`, and other styles for the remaining states.

## Original prototype measurements

Measured 2026-09-11 on macOS (Darwin 27) with Playwright builds of Chromium
(1243) and WebKit 26.5 (2358), using a system font with no P+ font loaded.
The original prototype lived in a session scratchpad, not in this repository.
These results are historical measurements, not a fresh test of the current
packages.

Input was the Nerd Fonts producer fork's `example-marked.txt` (PUA) and its
`nfprov convert --from pua --to vs` output: two paragraphs, with 322 selectors
in the selector-encoded form.

| Check | Chromium | WebKit |
| --- | --- | --- |
| Spans produced, server-side, selector input | 7 | 7 |
| Spans produced, client-side, selector input | 7 | 7 |
| Spans produced, client-side, PUA input | 7 | 7 |
| Server-side and client-side runs identical | yes | yes |
| Marks visible with system font, no P+ font | yes | yes |
| Width of `T` + U+E0101 minus width of `T`, px | 0 | 0 |
| Selectors in a selection of the server-rendered section | 322 | 322 |
| Selectors in a selection of the client-rendered section | 322 | 322 |
| Selectors in a selection of the PUA-decoded section | 0 | 0 |

At measurement time, the prototype decoded PUA to bare base characters. That
explains the zero in the last row. It was subsequently changed to emit base
plus selector, as the current contract requires; the table does not measure
that revised behavior.

A destination that preserves the selection's selectors receives the encoding
intact. Whether it displays the provenance is a separate question: a compatible
font and shaper can show the marks, while the tested CoreText path shows plain
base glyphs without removing the selectors from the stored text.

### Not verified by the prototype

- A physical clipboard paste into a P+ editor; only the selection string was
  read.
- Find-in-page with selectors retained in the DOM.
- Firefox.
- A real iOS device; the WebKit test ran on macOS, not iOS.
- Screen reader behavior.
- Markdown source containing selectors adjacent to syntax characters. This is
  a producer and parser integration concern independent of the decorator.

## Implementations and related work

- [JavaScript](../js/README.md): `runs` detects runs; `render` decorates DOM
  text nodes. The package includes optional CSS.
- [Python](../python/README.md): `runs` detects runs; `to_html` renders text as
  an escaped HTML fragment.
- [Ruby](../ruby/README.md): another producer, decoder, and HTML renderer.

Editor decoration APIs could use the same run detection without rewriting the
buffer. [ADR 0009](adr/0009-editor-decoration-apis.md) proposes this path for
editors with suitable extension APIs; it has not been prototyped, and a usable
Zed decoration API has not been established.
