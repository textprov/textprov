# SPEC.md

---

# TextProv protocol specification

> **Status: Draft — experimental.** Specification version: 0.1. Registry version: 0.1.
> Specification behavior may change incompatibly before Stable. Implementers should
> pin an immutable revision. Published registry allocations remain reserved and
> will not be reassigned or removed. Stable specification compatibility guarantees
> have not yet taken effect. See the [maturity lifecycle](docs/MATURITY.md).

TextProv carries origin labels in the text itself: human-written,
AI-generated, mixed, edited, or unknown. It gives cooperating producers and
consumers a shared way to preserve and display disclosures about text's origin.
For example, a writing integration can label generated passages so an editor
can see those disclosures during review.

Labels are stored as Unicode code points within the text, rather than in a
separate metadata field or wrapper. They can survive copying, pasting, and
plain-text storage when the software involved preserves those code points.
Software that removes the marks also removes the labels.

This document defines the in-band encodings, registry rules, producer behavior,
decoder behavior, and renderer markup. It does not define how an integration
determines which provenance state applies or how a renderer presents that state
visually.

TextProv carries provenance labels, not proof of provenance. A label expresses
a claim about origin, not a judgment about the text's quality, accuracy, or
trustworthiness. Any text processor can add, remove, or change a mark; unmarked
text makes no claim about its origin.

Decoding a label establishes which claim is present, not whether it is true.
Confidence in a claim depends on evidence about its source and workflow, not
on the mark alone. Decisions that depend on accurate authorship require
evidence beyond TextProv labels. Authentication, signatures, tamper evidence,
and verification of a producer's claim are outside this protocol.

Two compatibility versions appear in this draft. **Specification version 0.1**
covers the algorithms and rules below — the encodings, the decoder, and
producer conformance. **Registry version 0.1** covers `mapping.json`: which
base characters have PUA slots and which states exist. These versions are
Draft: specification behavior is experimental, but published registry allocations
remain protected. The registry and specification advance independently. Fixtures and reference
APIs expose these values as `spec_version` and `registry_version` (or the
language-appropriate camel-case equivalents).

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
| `edited` | `U+E0103` | Proposed |
| `unknown` | `U+E0104` | Proposed |

A specification-version-0.1 decoder recognizes `human`, `ai`, and `mixed`, and
a conforming producer must support them. `edited` and `unknown` are proposed
allocations reserved for future stabilization; producers must not emit them and
decoders may ignore them until they are promoted.

Selectors are drawn from Unicode's Supplemental Tag Characters block,
`U+E0100`–`U+E01EF`, giving 240 code points total. Registry 0.1 uses five,
leaving 235 unallocated. Future selectors reserved by a later registry version
must fall inside this block; the adjacent Tag Characters block
(`U+E0000`–`U+E007F`) is out of scope.

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
  "version": "0.1",
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

Registry version 0.1 covers `U+0021`–`U+00FF` minus the general categories
`Zs`, `Cc`, and `Cf`: 188 entries, every one state `ai`. The formula reserves
the rest of the range; a later version must not give those code points a
different meaning. This reservation applies during Draft and Candidate as well
as Stable.

Although the PUA formula is fixed, a consumer must read the `pua` table rather
than compute it. A future version may restrict an entry or attach metadata.

### Stability rules

These rules apply from the first publication of an allocation, including
**Draft** and **Candidate** status.

- Published selector and PUA code points are never reassigned or removed.
- Obsolete allocations remain reserved and documented with their original
  meanings.
- A version that adds base characters or states increments `version` and
  appends entries only. An addition is not automatically compatible with older
  decoders; compatibility is reviewed under the [maturity lifecycle](docs/MATURITY.md).

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
allocates it for that state. Registry version 0.1 allocates `U+0021`-`U+00FF` and
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

Registry version 0.1 provides PUA allocations only for `ai`.

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

Producer conformance is defined at specification version 0.1. It documents what the
reference producer already did; no behaviour changed when it was written down.

## Decoder

### Options

| Option | Default | Effect |
| --- | --- | --- |
| `strip` | false | Remove selectors from run text. State is still reported. |
| `merge_whitespace` | true | Whitespace between two runs of the same state joins them. |

`merge_whitespace` is the specification spelling. An implementation in a language
whose convention is camel case may accept `mergeWhitespace` as an alias, but
must accept the specification spelling, because the fixture uses it.

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
`data-prov` is the machine-readable specification; the classes exist for CSS. An
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
{ "spec_version": "0.1",
  "registry_version": "0.1",
  "cases":          [ { "name": "...", "input": "...", "options": {}, "runs": [ { "state": "ai", "text": "..." } ] } ],
  "producer_cases": [ { "name": "...", "input": "...", "options": { "state": "ai", "mode": "vs" }, "output": "..." } ],
  "convert_cases":  [ { "name": "...", "input": "...", "options": { "from": "vs", "to": "pua" }, "output": "..." } ] }
```

`cases` is the decoder suite: `state` is a string from `variation_selectors` or
`null`, and `options` uses the option names in this document. An implementation
claiming conformance to a fixture pair must advertise the fixture's
`spec_version` and `registry_version` and reproduce every applicable case.
A decoder-only implementation runs `cases`; an implementation that also
produces or converts marks additionally runs `producer_cases` and
`convert_cases`. A `note` on a case is prose for a human and carries no
requirement. Strings are stored with ASCII escapes; compare code points, not
bytes.

## Versioning

Version numbers identify the specification rules and registry contents. Maturity
status defines the change and compatibility promises; a version number or
package publication alone does not establish maturity.

| Artifact | Current version | Status | Changes with |
| --- | --- | --- | --- |
| Specification (`SPEC.md`, decoder, producer rules, `fixtures.json`) | 0.1 | Draft | Algorithm, markup, or conformance-rule changes |
| Registry (`mapping.json` and vendored copies) | 0.1 | Draft | Additions to published allocations or registry metadata changes |

The [maturity lifecycle](docs/MATURITY.md) defines entry and exit criteria for
**Draft → Candidate → Stable**, and retirement through **Deprecated**.
Promotion requires a public maintainer decision with evidence; a short release
note is sufficient. Candidate review lasts at least 30 days without changes to
required behavior. Stable requires passing applicable checks from at least one
maintained implementation and no unresolved release blockers; independent
implementation or external participation is not required. See the lifecycle for
the full criteria. No promotion is implied by this document's version numbers.

The specification and registry versions advance independently. Each promotion record
identifies the exact pair reviewed together. Registry allocation protections
apply at every stage. Stable specification behavior is immutable; incompatible
changes require a new specification version, not withdrawal of the old guarantees.

An implementation states both versions it implements. During Draft and
Candidate, it also identifies the immutable release revision used for
conformance. The live `SPEC.md` and `mapping.json` URLs describe the current
draft, not pinned release artifacts.

## Not specified

- How a producer decides which state applies to a given run of text.
- Visual style. The specification defines classes and an attribute; CSS is an
  integration choice. `js/textprov.css` is one such choice, not part of this
  document.
- Inferring provenance from text that has no marks.
- Behaviour on text nodes inside `pre` or `code`. Implementations may skip
  them; the fixture does not cover it.
- Unicode-version differences in grapheme segmentation beyond the fixture.
  Implementations must use extended grapheme clusters, but specification version 0.1
  does not pin a Unicode version. Clients using `Intl.Segmenter` and servers
  using this repository's `cluster_end` agreed on every case tested; they may
  differ where Unicode versions or segmentation coverage differ.
