# TextProv protocol specification

TextProv carries provenance in the text itself. A run of characters can say
whether a person wrote it, a machine generated it, or its origin is unknown.
The state travels as Unicode code points, so it survives copy, paste, and
plain-text storage, and needs no side-channel, no wrapper format, and no
metadata the transport can drop.

This document defines the in-band encodings, registry rules, producer behavior,
decoder behavior, and renderer markup. It does not define how an integration
determines which provenance state applies or how a renderer presents that state
visually.

TextProv carries provenance labels, not proof of provenance. Any text processor
can add, remove, or change a mark. Authentication, signatures, tamper evidence,
and verification of a producer's claim are outside this protocol.

Two version numbers appear in this spec. **Contract version 1** covers the
algorithms and rules below — the encodings, the decoder, and producer
conformance. **Registry version 1** covers `mapping.json`: which base
characters have PUA slots and which states exist. The registry rolls forward as
coverage grows (see [Registry](#registry)); the contract stays put until a rule
changes. The fixture and reference APIs call the registry version
`mapping_version`; "mapping version" and "registry version" refer to the same
value.

## Roles

| Role | Does |
| --- | --- |
| Producer | Adds marks to text. |
| Decoder | Splits marked text into runs, each carrying at most one state. |
| Renderer | Shows the states: markup, editor decorations, or a font's own variants. |

Producing is text processing: it requires the registry and cluster
segmentation, but no font, shaping engine, DOM, or other renderer. Rendering
depends on the target surface: a span renderer needs a DOM, while a font
renderer needs a font toolchain. A font is one renderer among three, not the
producer ([ADR 0011](docs/adr/0011-the-producer-is-text-processing.md)).

## States

| State | Selector | Producer support |
| --- | --- | --- |
| _unmarked_ | — | No state; the consumer decides what that means |
| `human` | `U+E0100` | Required |
| `ai` | `U+E0101` | Required |
| `mixed` | `U+E0102` | Required |
| `edited` | `U+E0103` | Optional |
| `unknown` | `U+E0104` | Optional |

A contract-version-1 decoder recognizes every selector in the table. A
conforming producer must support `human`, `ai`, and `mixed`; support for
producing `edited` and `unknown` is optional.

Unmarked text is deliberately distinct from `human`: there is no code point for
"assumed human." A decoder reports no state on unmarked text and the consumer
decides what that means ([ADR 0010](docs/adr/0010-contributor-identity-is-out-of-band.md)).

The state vocabulary is deliberately small and says nothing about *who*. Author
identity, model names, and timestamps are out-of-band data; see
[ADR 0010](docs/adr/0010-contributor-identity-is-out-of-band.md).

## Encodings

Two encodings may appear, together or alone. In the examples below,
`A + U+E0101` means the two-code-point sequence `U+0041 U+E0101`. It normally
displays as the base glyph `A`; the provenance selector may be invisible.

**Selector encoding.** A marked grapheme cluster ends with one of the code
points in `mapping.json` under `variation_selectors`. Because these selectors
have the Unicode `Grapheme_Extend` property, segmentation treats the selector
as part of the cluster it marks. The selectors are a private convention shared
by producers, decoders, and provenance-aware fonts; they are not registered
Unicode variation sequences. A font that lacks the variants renders the plain
base glyph, so unmarked-looking text is the fallback.

For example, decoding `A + U+E0101` with the default options produces one run,
`(state="ai", text="A + U+E0101")`. With `strip=true`, the run is
`(state="ai", text="A")`.

**PUA encoding.** One code point listed in `mapping.json` `pua`, standing for
the base character and state recorded there. Supplementary PUA-B (plane 16) is
used, with a fixed allocation:

```text
PUA_AI(cp) = 0x100000 + cp
```

A font that lacks the glyph shows a missing-glyph box, and a decoder-less
consumer cannot read the text at all. PUA is therefore a font-workflow
encoding, not a web or interchange one: do not publish PUA-encoded text
([ADR 0008](docs/adr/0008-do-not-publish-pua-to-the-web.md)). A decoder decodes
PUA input to base plus selector
([ADR 0003](docs/adr/0003-decode-pua-to-base-plus-selector.md)).

Whitespace is never marked by a conforming producer. A selector after
whitespace, or with no preceding cluster, is not a mark.

## Registry

`mapping.json` is the canonical registry.

```json
{
  "version": 1,
  "variation_selectors": {
    "human": "U+E0100",
    "ai": "U+E0101",
    "mixed": "U+E0102",
    "edited": "U+E0103",
    "unknown": "U+E0104"
  },
  "pua": {
    "U+100041": { "base": "U+0041", "provenance": "ai" }
  }
}
```

Version 1 covers `U+0021`–`U+00FF` minus the general categories `Zs`, `Cc`, and
`Cf`: 188 entries, every one state `ai`. The formula reserves the rest of the
range; a later version must not give those code points a different meaning.

Although the PUA formula is fixed, a consumer must read the `pua` table rather
than compute it. A future version may restrict an entry or attach metadata.

### Stability rules

- Published code points are never reassigned or removed.
- A version that adds base characters or states increments `version` and
  appends entries only.

### Vendoring

An implementation may embed the tables the registry reduces to rather than
reading the file at runtime; a browser script cannot load JSON synchronously.
An implementation that embeds must check its copy against `mapping.json` in its
test suite, so drift fails the build rather than shipping. Both reference
implementations here do that ([ADR 0006](docs/adr/0006-decorator-packages-and-repository.md)).

## Producer

A producer marks text. It must hold the following.

1. **One mark per cluster.** Split the text into clusters the same way a
   decoder does, and mark each one once, after the whole cluster: after
   combining marks, emoji variation selectors, skin-tone modifiers, ZWJ joins,
   and the second half of a regional-indicator pair.
2. **Never mark whitespace.** A decoder relies on this: whitespace is what it
   is allowed to absorb between two runs of the same state.
3. **Be idempotent.** Marking text that is already marked returns it
   unchanged. A cluster that already carries a selector keeps the state it has,
   and a PUA character is left alone; a producer does not overwrite a state it
   did not set.
4. **Be reversible.** Removing TextProv marks from marked output must reproduce
   the producer's input exactly. Mark removal deletes recognized provenance
   selectors and replaces every registered PUA code point with its registered
   base character.

In the PUA encoding, a producer replaces a base character with its PUA
counterpart only when the cluster is exactly one code point and the registry
allocates it for that state. Registry version 1 allocates `U+0021`-`U+00FF` and
the `ai` state only, so every other cluster keeps the selector encoding. The
two encodings therefore mix freely in one document, and converting between
them changes only the clusters that have a counterpart.

### Conversion

Conversion changes only representations that have an allocated equivalent in
the registry.

- When the source and target encodings are the same, the output equals the
  input.
- Converting from selector to PUA encoding replaces a selector-encoded `ai`
  cluster only when the cluster contains exactly one base code point and the
  registry contains the corresponding `ai` PUA entry.
- Converting from PUA to selector encoding replaces each registered PUA code
  point with its registered base followed by the selector for its registered
  state.
- Unmarked text, lone selectors, unallocated bases, and states without a PUA
  allocation remain unchanged.

Registry version 1 provides PUA allocations only for `ai`.

### Non-normative edit helper

The reference Python implementation provides a `mark_added` convenience
operation. It finds the longest common prefix and suffix by Unicode code point,
then marks the intervening portion of the new text. This operation is not
required for producer conformance and does not try to infer authorship of
unchanged text.

Nothing here says *how* a producer decides which state applies. That is the
integration's problem: an editor watching who typed, a pipeline that knows a
model wrote a paragraph, a marker run over a file by hand.

### Producer conformance

`fixtures.json` carries `producer_cases` and `convert_cases` beside the decoder
`cases`. Each producer case records an input, the state and mode, and the exact
output. An implementation conforms when it reproduces every output, and when
the four properties above hold for text of its own choosing — the reference
suite tests them as properties, not only as recorded cases, because the cases
cannot cover every input.

Producer conformance is defined at contract version 1. It documents what the
reference producer already did; no behaviour changed when it was written down.

## Decoder

### Options

| Option | Default | Effect |
| --- | --- | --- |
| `strip` | false | Remove selectors from run text. State is still reported. |
| `merge_whitespace` | true | Whitespace between two runs of the same state joins them. |

`merge_whitespace` is the contract spelling. An implementation in a language
whose convention is camel case may accept `mergeWhitespace` as an alias, but
must accept the contract spelling, because the fixture uses it.

### Algorithm

1. Split the input into grapheme clusters (Unicode extended grapheme
   clusters). A selector is `Grapheme_Extend`, so it belongs to the cluster of
   its base.
2. Classify each cluster in the following order:
   - A cluster ending in a recognized selector whose preceding code points are
     all whitespace has no state. Text is unchanged. This rule takes precedence
     over selector classification because whitespace cannot carry a mark.
   - Last code point is a selector and the cluster has more than one code
     point: state from `variation_selectors`. Text is the cluster, minus the
     selector when `strip`.
   - The cluster is exactly one code point in `pua`: state from that entry.
     Text is the base character followed by the selector for that state, or
     the base character alone when `strip`.
   - Whitespace only: provisional state `ws`.
   - Anything else, including a lone selector: no state. Text unchanged.
3. Concatenate adjacent clusters of equal state into runs.
4. If `merge_whitespace`, a `ws` run whose neighbours both have the same
   non-null state takes that state. Every remaining `ws` run becomes no state.
5. Concatenate adjacent runs of equal state again.

Output: an ordered list of `(state, text)`. Concatenating every `text`
reproduces the input exactly unless `strip` is set or PUA input was present.

## Markup

For each run with a state, emit

```html
<span class="prov prov-STATE" data-prov="STATE">TEXT</span>
```

with `TEXT` HTML-escaped. Runs with no state are emitted as escaped text.
`data-prov` is the machine-readable contract; the classes exist for CSS. An
implementation may accept a class prefix option, and `prov` is the default.
A custom prefix changes the classes only; `data-prov` does not move.

The selectors stay inside the span text, so selecting and copying rendered text
round-trips the marks ([ADR 0002](docs/adr/0002-retain-selectors-in-span-text.md)).

In a DOM, apply the pass to text nodes only. Skip `script`, `style`,
`textarea`, and any node already inside an element with the prefix class. Run
server-side passes on rendered HTML text nodes, not on markdown source.

Spans are the baseline because they need no font
([ADR 0001](docs/adr/0001-render-marks-as-html-spans.md)). Editors cannot have
their buffers rewritten, so the same run detection feeds decoration APIs
instead ([ADR 0009](docs/adr/0009-editor-decoration-apis.md)).

## Conformance

`fixtures.json` defines conformance
([ADR 0004](docs/adr/0004-shared-fixture-for-conformance.md)):

```json
{ "contract_version": 1,
  "mapping_version": 1,
  "cases":          [ { "name": "...", "input": "...", "options": {}, "runs": [ { "state": "ai", "text": "..." } ] } ],
  "producer_cases": [ { "name": "...", "input": "...", "options": { "state": "ai", "mode": "vs" }, "output": "..." } ],
  "convert_cases":  [ { "name": "...", "input": "...", "options": { "from": "vs", "to": "pua" }, "output": "..." } ] }
```

`cases` is the decoder suite: `state` is a string from `variation_selectors` or
`null`, and `options` uses the option names in this document. An implementation
claiming conformance to a fixture pair must advertise the fixture's
`contract_version` and `mapping_version` and reproduce every applicable case.
A decoder-only implementation runs `cases`; an implementation that also
produces or converts marks additionally runs `producer_cases` and
`convert_cases`. A `note` on a case is prose for a human and carries no
requirement. Strings are stored with ASCII escapes; compare code points, not
bytes.

## Versioning

The contract version changes when the algorithm or markup changes. The registry
version changes independently, under the stability rules above. An
implementation states both versions it implements.

## Not specified

- How a producer decides which state applies to a given run of text.
- Visual style. The contract defines classes and an attribute; CSS is an
  integration choice. `js/textprov.css` is one such choice, not part of this
  document.
- Inferring provenance from text that has no marks.
- Behaviour on text nodes inside `pre` or `code`. Implementations may skip
  them; the fixture does not cover it.
- Unicode-version differences in grapheme segmentation beyond the fixture.
  Implementations must use extended grapheme clusters, but contract version 1
  does not pin a Unicode version. Clients using `Intl.Segmenter` and servers
  using this repository's `cluster_end` agreed on every case tested; they may
  differ where Unicode versions or segmentation coverage differ.
