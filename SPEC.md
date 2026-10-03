# SPEC.md

---

# TextProv protocol specification

> **Status: Draft — experimental.** Specification version: 0.2. Registry version: 0.1.
> Updated: 2026-10-02.
> Specification behavior may change incompatibly before Stable. Implementers should
> pin an immutable revision. Published registry allocations remain reserved and
> will not be reassigned or removed. Stable specification compatibility guarantees
> have not yet taken effect. See the [maturity lifecycle](docs/MATURITY.md).

TextProv is a protocol for attaching origin labels to passages of p󠄁r󠄁o󠄁s󠄁e󠄁. A label
states that a passage is human-written, AI-generated, mixed, edited, or of
unknown origin. Cooperating tools can preserve, interpret, and display these
labels as text moves between them. For example, a writing integration can
label a generated passage so an editor can identify it during review or an
agent integration can distinguish it from the operator's surrounding input.

TextProv stores labels as Unicode code points within the character sequence,
not in a separate metadata field or document wrapper. The labels can therefore
survive copying, pasting, and plain-text storage, provided every tool in the
path preserves those code points. A tool that removes the marks also removes
the labels.

TextProv provides a shared foundation: a common structure, encoding, and
vocabulary for exchanging provenance information. Applications can agree on
what a label means while choosing how to use it.

This document defines the text encodings, label registry, producer and decoder
behavior, and renderer markup. How a producer assigns labels, how a consumer
uses them in decisions, and how a renderer presents them are integration
choices.

A TextProv label is a claim, not proof. Decoding identifies the claim attached
to a passage; it does not establish who made the claim or whether the claim is
true. Any text processor can add, change, or remove a mark, and unmarked text
makes no claim about its origin. A label also says nothing about the text's
quality, accuracy, or trustworthiness. Authentication, signatures, tamper
evidence, and verification of producer claims are outside this protocol.

This draft has two independent compatibility versions:

- **Specification version 0.2** covers the encodings, decoding algorithm, and
  conformance rules defined in this document.
- **Registry version 0.1** covers `mapping.json`, including the available states
  and the base characters assigned Private Use Area (PUA) slots.

Both versions are Draft. Specification behavior remains experimental, while
published registry allocations remain reserved. Fixtures and reference APIs
expose the versions as `spec_version` and `registry_version`, or with the
language-appropriate camel-case equivalents.

## Marking scope

T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 a󠄁d󠄁d󠄁r󠄁e󠄁s󠄁s󠄁e󠄁s󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁u󠄁n󠄁i󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 p󠄁e󠄁o󠄁p󠄁l󠄁e󠄁,󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 l󠄁a󠄁b󠄁e󠄁l󠄁s󠄁
n󠄁e󠄁e󠄁d󠄁 t󠄁o󠄁 t󠄁r󠄁a󠄁v󠄁e󠄁l󠄁 w󠄁i󠄁t󠄁h󠄁 t󠄁h󠄁e󠄁 w󠄁o󠄁r󠄁d󠄁s󠄁.󠄁

S󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁 o󠄁u󠄁t󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁s󠄁,󠄁
d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 s󠄁t󠄁r󠄁i󠄁n󠄁g󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁e󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 t󠄁h󠄁o󠄁s󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁s󠄁.󠄁 P󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁
f󠄁o󠄁r󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁s󠄁 t󠄁o󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁o󠄁l󠄁 a󠄁n󠄁d󠄁 d󠄁e󠄁v󠄁e󠄁l󠄁o󠄁p󠄁m󠄁e󠄁n󠄁t󠄁 w󠄁o󠄁r󠄁k󠄁f󠄁l󠄁o󠄁w󠄁s󠄁.󠄁

C󠄁o󠄁d󠄁e󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁s󠄁 e󠄁m󠄁b󠄁e󠄁d󠄁d󠄁e󠄁d󠄁 i󠄁n󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 m󠄁a󠄁y󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 a󠄁s󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁
s󠄁u󠄁r󠄁r󠄁o󠄁u󠄁n󠄁d󠄁i󠄁n󠄁g󠄁 c󠄁o󠄁m󠄁m󠄁u󠄁n󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 f󠄁e󠄁n󠄁c󠄁e󠄁d󠄁 e󠄁x󠄁a󠄁m󠄁p󠄁l󠄁e󠄁s󠄁 a󠄁n󠄁d󠄁 i󠄁n󠄁l󠄁i󠄁n󠄁e󠄁 e󠄁x󠄁p󠄁r󠄁e󠄁s󠄁s󠄁i󠄁o󠄁n󠄁s󠄁.󠄁
I󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 m󠄁a󠄁y󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁s󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁.󠄁 M󠄁a󠄁r󠄁k󠄁s󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁d󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁;󠄁 t󠄁h󠄁e󠄁y󠄁
d󠄁o󠄁 n󠄁o󠄁t󠄁 e󠄁s󠄁t󠄁a󠄁b󠄁l󠄁i󠄁s󠄁h󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁 i󠄁s󠄁 s󠄁u󠄁i󠄁t󠄁a󠄁b󠄁l󠄁e󠄁 f󠄁o󠄁r󠄁 d󠄁i󠄁r󠄁e󠄁c󠄁t󠄁 e󠄁x󠄁e󠄁c󠄁u󠄁t󠄁i󠄁o󠄁n󠄁.󠄁

A󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁s󠄁 e󠄁l󠄁i󠄁g󠄁i󠄁b󠄁l󠄁e󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 b󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 p󠄁a󠄁s󠄁s󠄁i󠄁n󠄁g󠄁 i󠄁t󠄁 t󠄁o󠄁 a󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁.󠄁 E󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁
a󠄁n󠄁d󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁 o󠄁p󠄁e󠄁r󠄁a󠄁t󠄁e󠄁 o󠄁n󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 s󠄁e󠄁q󠄁u󠄁e󠄁n󠄁c󠄁e󠄁s󠄁;󠄁 t󠄁h󠄁e󠄁y󠄁 d󠄁o󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁c󠄁o󠄁g󠄁n󠄁i󠄁z󠄁e󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁
l󠄁a󠄁n󠄁g󠄁u󠄁a󠄁g󠄁e󠄁s󠄁,󠄁 f󠄁i󠄁l󠄁e󠄁 r󠄁o󠄁l󠄁e󠄁s󠄁,󠄁 o󠄁r󠄁 s󠄁y󠄁n󠄁t󠄁a󠄁x󠄁.󠄁 T󠄁h󠄁e󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁-󠄁c󠄁o󠄁d󠄁e󠄁 e󠄁x󠄁e󠄁m󠄁p󠄁t󠄁i󠄁o󠄁n󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁 h󠄁o󠄁w󠄁
a󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 h󠄁a󠄁n󠄁d󠄁l󠄁e󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 i󠄁t󠄁 r󠄁e󠄁c󠄁e󠄁i󠄁v󠄁e󠄁s󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁s󠄁 n󠄁o󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁
o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 e󠄁x󠄁e󠄁m󠄁p󠄁t󠄁i󠄁o󠄁n󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁y󠄁 h󠄁u󠄁m󠄁a󠄁n󠄁 a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁s󠄁h󠄁i󠄁p󠄁.󠄁

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

A **consumer** is whatever acts on decoded runs. It may be a renderer showing
states to a person, or a program that reads the states itself, such as an audit
tool or a model harness separating pasted model output from the operator's own
text. The protocol gives consumers a shared structure and vocabulary, and
leaves how they use it open
([ADR 0014](docs/adr/0014-the-protocol-defines-structure-not-use.md)).

Consumers can use decoded states without displaying them. P9E utility fonts primarily
support development, debugging, and demonstrations: a compatible font and text
shaper can reveal supported marks without a separate inspection tool. Their
glyph designs, including sawtooth underlines, are presentation choices.
Applications can expose provenance on demand or use it internally
([ADR 0015](docs/adr/0015-fonts-are-for-inspection-and-demonstration.md)).

## States

| State | Selector | Producer support |
| --- | --- | --- |
| _unmarked_ | — | No state; the consumer decides what that means |
| `human` | `U+E0100` | Required |
| `ai` | `U+E0101` | Required |
| `mixed` | `U+E0102` | Required |
| `edited` | `U+E0103` | Proposed |
| `unknown` | `U+E0104` | Proposed |

A specification-version-0.2 decoder recognizes `human`, `ai`, and `mixed`, and
a conforming producer must support them. `edited` and `unknown` are proposed
allocations reserved for future stabilization; producers must not emit them and
decoders may ignore them until they are promoted.

Selectors are drawn from Unicode's Variation Selectors Supplement block,
`U+E0100`–`U+E01EF`, giving 240 code points total. Registry 0.1 uses five,
leaving 235 unallocated. Future selectors reserved by a later registry version
must fall inside this block; the adjacent Tags block
(`U+E0000`–`U+E007F`) is out of scope.

Unmarked text is deliberately distinct from `human`: there is no code point for
"assumed human." A decoder reports no state on unmarked text and the consumer
decides what that means ([ADR 0010](docs/adr/0010-contributor-identity-is-out-of-band.md)).

The state vocabulary is deliberately small and says nothing about *who*. Author
identity, model names, and timestamps are out-of-band data; see
[ADR 0010](docs/adr/0010-contributor-identity-is-out-of-band.md).

## Application use (non-normative)

An agent prompt can combine an operator's own instructions with passages
copied from model output. When that output carries TextProv marks and the
copying path preserves them, an integration can recover a distinction that
plain, unlabelled text would lose. The decoded provenance gives the application
additional context for interpreting the combined prompt.

For example, an integration could experiment with giving operator-written
input a weight of `1.2` and AI-labelled passages a weight of `0.9` in its
decision process. This use requires further integration to decode the marks,
apply a policy, and evaluate its effect. The numbers illustrate one possible
application; the protocol supplies shared provenance states, and applications
choose how to use them. A selector retains the same meaning across consumers
with different policies. TextProv does not implement model weighting.

A workflow may treat unmarked input as operator-written based on how it was
collected. That is a local assumption: decoding still reports no state, as
specified above. Provenance alone does not establish instruction authority or
verify authorship. These distinctions let integrations experiment with the
same encoded information while retaining its shared meaning.

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

Registry version 0.1 covers `U+0021`–`U+00FF`, excluding characters in the
Unicode general categories `Zs` (space separators), `Cc` (control characters),
and `Cf` (format characters): 188 entries, every one state `ai`. The formula reserves
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

A producer marks text s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 b󠄁y󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 t󠄁h󠄁e󠄁
[m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](#marking-scope). It must hold the following.

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
model wrote a paragraph, a marker run over a p󠄁r󠄁o󠄁s󠄁e󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 by hand.

### Producer conformance

`fixtures.json` carries `producer_cases` and `convert_cases` beside the decoder
`cases`. Each producer case records an input, the state and mode, and the exact
output. An implementation conforms when it reproduces every output, and when
the four properties above hold for text of its own choosing — the reference
suite tests them as properties, not only as recorded cases, because the cases
cannot cover every input.

Producer conformance is defined at specification version 0.2. It documents what the
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
{ "spec_version": "0.2",
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
| Specification (`SPEC.md`, decoder, producer rules, `fixtures.json`) | 0.2 | Draft | S󠄁c󠄁o󠄁p󠄁e󠄁,󠄁 a󠄁lgorithm, markup, or conformance-rule changes |
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
- How a consumer uses provenance in decisions, including weighting passages in
  agent prompts. See [application use](#application-use-non-normative) and
  [ADR 0014](docs/adr/0014-the-protocol-defines-structure-not-use.md).
- Visual style. The specification defines classes and an attribute; CSS is an
  integration choice. `js/textprov.css` is one such choice, not part of this
  document.
- Inferring provenance from text that has no marks.
- Behaviour on text nodes inside `pre` or `code`. Implementations may skip
  them; the fixture does not cover it.
- Unicode-version differences in grapheme segmentation beyond the fixture.
  Implementations must use extended grapheme clusters, but specification version 0.2
  does not pin a Unicode version. T󠄁h󠄁e󠄁 r󠄁e󠄁f󠄁e󠄁r󠄁e󠄁n󠄁c󠄁e󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁
  t󠄁a󠄁b󠄁l󠄁e󠄁s󠄁 v󠄁e󠄁n󠄁d󠄁o󠄁r󠄁e󠄁d󠄁 a󠄁t󠄁 o󠄁n󠄁e󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁s󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁'󠄁s󠄁
  `GraphemeBreakTest.txt` (󠄁[A󠄁D󠄁R󠄁 0󠄁0󠄁1󠄁7󠄁](docs/adr/0017-vendor-grapheme-segmentation.md))󠄁;󠄁
  a󠄁n󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁n󠄁 a󠄁 d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁e󠄁n󠄁t󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 m󠄁a󠄁y󠄁 p󠄁l󠄁a󠄁c󠄁e󠄁 a󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁
  b󠄁o󠄁u󠄁n󠄁d󠄁a󠄁r󠄁y󠄁 d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁e󠄁n󠄁t󠄁l󠄁y󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁 t󠄁h󠄁e󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁s󠄁.󠄁

## Open questions

T󠄁h󠄁e󠄁s󠄁e󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁r󠄁e󠄁 u󠄁n󠄁r󠄁e󠄁s󠄁o󠄁l󠄁v󠄁e󠄁d󠄁 a󠄁t󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 0󠄁.󠄁2󠄁.󠄁 E󠄁a󠄁c󠄁h󠄁 h󠄁a󠄁s󠄁 a󠄁
d󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 t󠄁h󠄁r󠄁e󠄁a󠄁d󠄁.󠄁 A󠄁 r󠄁e󠄁s󠄁o󠄁l󠄁u󠄁t󠄁i󠄁o󠄁n󠄁 u󠄁p󠄁d󠄁a󠄁t󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 a󠄁f󠄁f󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 s󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁m󠄁o󠄁v󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁
q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁i󠄁s󠄁 l󠄁i󠄁s󠄁t󠄁.󠄁

### Marking and states

T󠄁h󠄁e󠄁s󠄁e󠄁 c󠄁a󠄁m󠄁e󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁p󠄁o󠄁s󠄁i󠄁t󠄁o󠄁r󠄁y󠄁'󠄁s󠄁 o󠄁w󠄁n󠄁 u󠄁s󠄁e󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁c󠄁o󠄁l󠄁
(󠄁[d󠄁o󠄁g󠄁f󠄁o󠄁o󠄁d󠄁i󠄁n󠄁g󠄁](docs/development/dogfooding.md))󠄁.󠄁

1. **C󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁 a󠄁n󠄁d󠄁 f󠄁o󠄁r󠄁g󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁** A󠄁r󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁,󠄁 p󠄁u󠄁l󠄁l󠄁 r󠄁e󠄁q󠄁u󠄁e󠄁s󠄁t󠄁
   d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁p󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 i󠄁s󠄁s󠄁u󠄁e󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁v󠄁i󠄁e󠄁w󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 t󠄁h󠄁e󠄁
   [m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](#marking-scope)?󠄁 T󠄁h󠄁e󠄁y󠄁 a󠄁r󠄁e󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 p󠄁e󠄁o󠄁p󠄁l󠄁e󠄁,󠄁 b󠄁u󠄁t󠄁 t󠄁h󠄁e󠄁
   t󠄁o󠄁o󠄁l󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 h󠄁o󠄁l󠄁d󠄁 t󠄁h󠄁e󠄁m󠄁 s󠄁e󠄁a󠄁r󠄁c󠄁h󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁r󠄁s󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁 a󠄁s󠄁 p󠄁l󠄁a󠄁i󠄁n󠄁 t󠄁e󠄁x󠄁t󠄁:󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 b󠄁r󠄁e󠄁a󠄁k󠄁
   `git log --grep`,󠄁 C󠄁o󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 C󠄁o󠄁m󠄁m󠄁i󠄁t󠄁s󠄁 p󠄁a󠄁r󠄁s󠄁e󠄁r󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 f󠄁o󠄁r󠄁g󠄁e󠄁 s󠄁e󠄁a󠄁r󠄁c󠄁h󠄁.󠄁 A󠄁 g󠄁i󠄁t󠄁
   t󠄁r󠄁a󠄁i󠄁l󠄁e󠄁r󠄁 w󠄁o󠄁u󠄁l󠄁d󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 b󠄁a󠄁n󠄁d󠄁,󠄁 f󠄁o󠄁r󠄁 a󠄁 w󠄁h󠄁o󠄁l󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 r󠄁a󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁a󠄁n󠄁 a󠄁
   p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁.󠄁 (󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁3󠄁](https://github.com/textprov/textprov/discussions/13))󠄁
2. **W󠄁h󠄁a󠄁t󠄁 `human` a󠄁s󠄁s󠄁e󠄁r󠄁t󠄁s󠄁.󠄁** D󠄁o󠄁e󠄁s󠄁 `human` s󠄁t󠄁a󠄁t󠄁e󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 w󠄁r󠄁o󠄁t󠄁e󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁,󠄁
   o󠄁r󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁t󠄁e󠄁d󠄁 i󠄁t󠄁?󠄁 T󠄁h󠄁i󠄁s󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁s󠄁 `human` a󠄁s󠄁
   h󠄁u󠄁m󠄁a󠄁n󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁,󠄁 b󠄁u󠄁t󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 u󠄁s󠄁u󠄁a󠄁l󠄁l󠄁y󠄁 o󠄁b󠄁s󠄁e󠄁r󠄁v󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁s󠄁s󠄁i󠄁o󠄁n󠄁.󠄁 A󠄁
   p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 c󠄁a󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁d󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁,󠄁 a󠄁n󠄁d󠄁 a󠄁 s󠄁c󠄁r󠄁i󠄁p󠄁t󠄁 c󠄁a󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁 t󠄁e󠄁x󠄁t󠄁 n󠄁o󠄁
   p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 w󠄁r󠄁o󠄁t󠄁e󠄁.󠄁 (󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁4󠄁](https://github.com/textprov/textprov/discussions/14))󠄁
3. **W󠄁h󠄁e󠄁n󠄁 a󠄁 p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁 i󠄁s󠄁 `mixed`.󠄁** W󠄁h󠄁e󠄁n󠄁 a󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 r󠄁e󠄁s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁'󠄁s󠄁 w󠄁o󠄁r󠄁d󠄁s󠄁
   f󠄁a󠄁i󠄁t󠄁h󠄁f󠄁u󠄁l󠄁l󠄁y󠄁,󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁u󠄁l󠄁t󠄁 `mixed`,󠄁 `ai`,󠄁 o󠄁r󠄁 `edited`?󠄁 N󠄁e󠄁i󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁i󠄁s󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁
   n󠄁o󠄁r󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁 `mixed` o󠄁r󠄁 `edited`.󠄁 A󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 c󠄁a󠄁n󠄁 d󠄁e󠄁t󠄁e󠄁c󠄁t󠄁 a󠄁
   v󠄁e󠄁r󠄁b󠄁a󠄁t󠄁i󠄁m󠄁 q󠄁u󠄁o󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 b󠄁u󠄁t󠄁 c󠄁a󠄁n󠄁n󠄁o󠄁t󠄁 j󠄁u󠄁d󠄁g󠄁e󠄁 w󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 a󠄁 p󠄁a󠄁r󠄁a󠄁p󠄁h󠄁r󠄁a󠄁s󠄁e󠄁 i󠄁s󠄁 f󠄁a󠄁i󠄁t󠄁h󠄁f󠄁u󠄁l󠄁.󠄁
   (󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁5󠄁](https://github.com/textprov/textprov/discussions/15))󠄁
