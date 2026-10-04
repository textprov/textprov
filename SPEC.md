# SPEC.md

---

# TextProv protocol specification

> **Status: Draft — experimental.** Specification version: 0.2. Registry version: 0󠄁.󠄁2󠄁.󠄁
> Updated: 2026-10-03.
> Specification behavior may change incompatibly before Stable. Implementers should
> pin an immutable revision. Published registry allocations remain reserved and
> will not be reassigned or removed. Stable specification compatibility guarantees
> have not yet taken effect. See the [maturity lifecycle](docs/MATURITY.md).

TextProv is a protocol for attaching origin labels to passages of p󠄁r󠄁o󠄁s󠄁e󠄁. A label
states that a passage is h󠄁u󠄁m󠄁a󠄁n󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁 o󠄁r󠄁 A󠄁I󠄁-󠄁g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁e󠄁d󠄁.󠄁 C󠄁o󠄁o󠄁p󠄁e󠄁r󠄁a󠄁t󠄁i󠄁n󠄁g󠄁 t󠄁o󠄁o󠄁l󠄁s󠄁 c󠄁a󠄁n󠄁
preserve, interpret, and display these labels as text moves between them. For example, a writing integration can
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
- **Registry version 0󠄁.󠄁2󠄁** covers `mapping.json`, including the available states
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

A specification-version-0.2 decoder recognizes o󠄁n󠄁l󠄁y󠄁 `human` a󠄁n󠄁d󠄁 `ai`,󠄁 a󠄁n󠄁d󠄁 a󠄁
c󠄁o󠄁n󠄁f󠄁o󠄁r󠄁m󠄁i󠄁n󠄁g󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 m󠄁u󠄁s󠄁t󠄁 s󠄁u󠄁p󠄁p󠄁o󠄁r󠄁t󠄁 b󠄁o󠄁t󠄁h󠄁.󠄁 N󠄁o󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁d󠄁 o󠄁r󠄁
p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁.󠄁 S󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 a󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 d󠄁o󠄁 n󠄁o󠄁t󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁 a󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁
s󠄁t󠄁a󠄁t󠄁e󠄁.󠄁

Selectors are drawn from Unicode's Variation Selectors Supplement block,
`U+E0100`–`U+E01EF`, giving 240 code points total. Registry 0󠄁.󠄁2󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁s󠄁 t󠄁w󠄁o󠄁,󠄁
k󠄁e󠄁e󠄁p󠄁s󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁 o󠄁b󠄁s󠄁o󠄁l󠄁e󠄁t󠄁e󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁s󠄁 2󠄁3󠄁5󠄁 u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁
(󠄁`U+E0105`–󠄁`U+E01EF`)󠄁.󠄁 F󠄁u󠄁t󠄁u󠄁r󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 b󠄁y󠄁 a󠄁 l󠄁a󠄁t󠄁e󠄁r󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁
m󠄁u󠄁s󠄁t󠄁 f󠄁a󠄁l󠄁l󠄁 i󠄁n󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁i󠄁s󠄁 b󠄁l󠄁o󠄁c󠄁k󠄁;󠄁 t󠄁h󠄁e󠄁 a󠄁d󠄁j󠄁a󠄁c󠄁e󠄁n󠄁t󠄁 T󠄁a󠄁g󠄁s󠄁 b󠄁l󠄁o󠄁c󠄁k󠄁 (󠄁`U+E0000`–󠄁`U+E007F`)󠄁 i󠄁s󠄁
o󠄁u󠄁t󠄁 o󠄁f󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁.󠄁

R󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 (󠄁D󠄁r󠄁a󠄁f󠄁t󠄁 0󠄁.󠄁1󠄁,󠄁 2󠄁0󠄁2󠄁6󠄁-󠄁0󠄁9󠄁-󠄁2󠄁0󠄁)󠄁 a󠄁l󠄁s󠄁o󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 `U+E0102` t󠄁o󠄁 `mixed`,󠄁
`U+E0103` t󠄁o󠄁 `edited`,󠄁 a󠄁n󠄁d󠄁 `U+E0104` t󠄁o󠄁 `unknown`.󠄁 R󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁2󠄁 m󠄁a󠄁k󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁s󠄁e󠄁
t󠄁h󠄁r󠄁e󠄁e󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 o󠄁b󠄁s󠄁o󠄁l󠄁e󠄁t󠄁e󠄁.󠄁 A󠄁n󠄁 o󠄁b󠄁s󠄁o󠄁l󠄁e󠄁t󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁s󠄁 n󠄁o󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁,󠄁
a󠄁n󠄁d󠄁 a󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 m󠄁u󠄁s󠄁t󠄁 n󠄁o󠄁t󠄁 e󠄁m󠄁i󠄁t󠄁 i󠄁t󠄁.󠄁 D󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁,󠄁 s󠄁t󠄁r󠄁i󠄁p󠄁p󠄁i󠄁n󠄁g󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁 i󠄁t󠄁
i󠄁n󠄁 p󠄁l󠄁a󠄁c󠄁e󠄁,󠄁 a󠄁s󠄁 t󠄁h󠄁e󠄁y󠄁 d󠄁o󠄁 a󠄁n󠄁 u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁.󠄁 U󠄁n󠄁d󠄁e󠄁r󠄁 t󠄁h󠄁e󠄁
[s󠄁t󠄁a󠄁b󠄁i󠄁l󠄁i󠄁t󠄁y󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁](#stability-rules) i󠄁t󠄁 s󠄁t󠄁a󠄁y󠄁s󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 i󠄁s󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 r󠄁e󠄁a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁.󠄁

Unmarked text is deliberately distinct from `human`: there is no code point for
"assumed human." A decoder reports no state on unmarked text and the consumer
decides what that means. This rule is defined here independently of the proposed
generational extension.

The state vocabulary is deliberately small and says nothing about *who*. Author
identity, model names, and timestamps are out-of-band data. For design history,
see [ADR 0010](docs/adr/0010-contributor-identity-is-out-of-band.md), whose
identity decision is unchanged but whose generational extension is proposed.

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
as part of an eligible cluster it marks. A cluster ending in a code point with
`Grapheme_Cluster_Break=Control`, `CR`, or `LF` is not eligible: Unicode grapheme
break rule GB4 forces a boundary before the selector. The selectors are a private convention shared
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
encoding, not a web or interchange one: do not publish PUA-encoded text.
This specification defines that restriction; the related
[ADR 0008](docs/adr/0008-do-not-publish-pua-to-the-web.md) remains proposed and
its expected browser-accessibility breakages have not been measured. A decoder decodes
PUA input to base plus selector
([ADR 0003](docs/adr/0003-decode-pua-to-base-plus-selector.md)).

### Whitespace

Throughout this specification, **whitespace** means a code point with the
Unicode `White_Space` property. The exact set is:

```text
U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A,
U+2028, U+2029, U+202F, U+205F, U+3000
```

A whitespace-only string or cluster is nonempty and consists entirely of
these code points. U+001C–U+001F and U+FEFF are not whitespace; U+0085 is.
Language-native whitespace predicates must not substitute a different set.
This definition applies to producers, decoder classification, and
`merge_whitespace`.

Whitespace is never marked by a conforming producer. A selector after
whitespace, or with no preceding cluster, is not a mark.

## Registry

`mapping.json` is the canonical registry.

```json
{
  "version": "0.2",
  "variation_selectors": {
    "human": "U+E0100",
    "ai": "U+E0101"
  },
  "pua": {
    "U+100041": { "base": "U+0041", "provenance": "ai" }
  }
}
```

Registry version 0󠄁.󠄁2󠄁 covers `U+0021`–`U+00FF`, excluding characters in the
Unicode general categories `Zs` (space separators), `Cc` (control characters),
and `Cf` (format characters): 188 entries, every one state `ai`. The formula
reserves the entire Supplementary Private Use Area-B (`U+100000`–`U+10FFFD`)
for `ai` base-character counterparts, not just the gaps within the current
Latin-1 allocation. A later registry version must not assign those code points
a different meaning. Reserved but unallocated code points are not TextProv
marks; consumers decode only entries in the `pua` table. This reservation
applies during Draft and Candidate as well as Stable.

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
test suite, so drift fails the build rather than shipping. All three reference
implementations here do that ([ADR 0006](docs/adr/0006-decorator-packages-and-repository.md)).

## Producer

A producer marks text s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 b󠄁y󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 t󠄁h󠄁e󠄁
[m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](#marking-scope). It must hold the following.

1. **One mark per cluster.** Split the text into clusters the same way a
   decoder does, and mark each one once, after the whole cluster: after
   combining marks, emoji variation selectors, skin-tone modifiers, ZWJ joins,
   and the second half of a regional-indicator pair.
2. **Never mark whitespace or control-break clusters.** A decoder relies on
   unmarked whitespace: it is allowed to absorb it between two runs of the same
   state. A cluster ending in a code point with `Grapheme_Cluster_Break=Control`,
   `CR`, or `LF` must also remain unchanged in either encoding. This includes
   NUL (U+0000), soft hyphen (U+00AD), zero-width space (U+200B), word joiner
   (U+2060), and byte order mark (U+FEFF). A selector appended to such a cluster
   would be a separate, orphan cluster, not a provenance mark. This rule uses
   grapheme-break properties, not general category `Cf`: format characters
   such as ZWJ, ZWNJ, and emoji tags can belong to markable clusters.
3. **Be idempotent.** Marking text that is already marked returns it
   unchanged. A cluster that already carries a selector keeps the state it has,
   and a PUA character is left alone; a producer does not overwrite a state it
   did not set.
4. **Be reversible.** A󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁,󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 t󠄁e󠄁x󠄁t󠄁:󠄁 r󠄁e󠄁m󠄁o󠄁v󠄁i󠄁n󠄁g󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁
   m󠄁a󠄁r󠄁k󠄁s󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁 y󠄁i󠄁e󠄁l󠄁d󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁 r󠄁e󠄁s󠄁u󠄁l󠄁t󠄁 a󠄁s󠄁 r󠄁e󠄁m󠄁o󠄁v󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁m󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁
   i󠄁n󠄁p󠄁u󠄁t󠄁.󠄁 F󠄁o󠄁r󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 i󠄁n󠄁p󠄁u󠄁t󠄁,󠄁 t󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 input exactly. Mark removal
   d󠄁e󠄁l󠄁e󠄁t󠄁e󠄁s󠄁 r󠄁e󠄁c󠄁o󠄁g󠄁n󠄁i󠄁z󠄁e󠄁d󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁s󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁e󠄁r󠄁e󠄁d󠄁 P󠄁U󠄁A󠄁
   c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 w󠄁i󠄁t󠄁h󠄁 i󠄁t󠄁s󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁e󠄁r󠄁e󠄁d󠄁 base character.

In the PUA encoding, a producer replaces a base character with its PUA
counterpart only when the cluster is exactly one code point and the registry
allocates it for that state. Registry version 0󠄁.󠄁2󠄁 allocates `U+0021`-`U+00FF` and
the `ai` state only, so every other cluster keeps the selector encoding. The
two encodings therefore mix freely in one document, and converting between
them changes only the clusters that have a counterpart.

### Conversion

Conversion changes only representations that have an allocated equivalent in
the registry.

- When the source and target encodings are the same, the output equals the
  input.
- Converting from selector to PUA encoding replaces a selector-encoded `ai`
  cluster only when the cluster i󠄁s󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁l󠄁y󠄁 a󠄁 b󠄁a󠄁s󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 f󠄁o󠄁l󠄁l󠄁o󠄁w󠄁e󠄁d󠄁 b󠄁y󠄁 i󠄁t󠄁s󠄁
  `ai` s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 c󠄁o󠄁r󠄁r󠄁e󠄁s󠄁p󠄁o󠄁n󠄁d󠄁i󠄁n󠄁g󠄁 `ai` P󠄁U󠄁A󠄁 e󠄁n󠄁t󠄁r󠄁y󠄁.󠄁 A󠄁
  c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁 w󠄁i󠄁t󠄁h󠄁 a󠄁n󠄁y󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 a󠄁 s󠄁e󠄁c󠄁o󠄁n󠄁d󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁,󠄁 i󠄁s󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁.󠄁
- Converting from PUA to selector encoding replaces each registered PUA code
  point with its registered base followed by the selector for its registered
  state.
- Unmarked text, lone selectors, unallocated bases, and states without a PUA
  allocation remain unchanged.

Registry version 0󠄁.󠄁2󠄁 provides PUA allocations only for `ai`.

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

Producer conformance was first defined at specification version 0.1
([ADR 0011](docs/adr/0011-the-producer-is-text-processing.md)). It documented
what the reference producer already did; no behaviour changed when it was
written down. The current specification version 0.2 includes later changes
recorded in the [changelog](CHANGELOG.md#draft-02--2026-10-02).

## Decoder

### Options

| Option | Default | Effect |
| --- | --- | --- |
| `strip` | false | Remove mark selectors from run text; inert selectors are kept. Decode PUA marks to bare bases. State is still reported. |
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
     final selector when `strip`. Earlier selectors in the cluster are kept;
     the remaining text is not classified again.
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

For example, with `V = U+E0101` (`ai`), `A V V` is one `ai` cluster
(spaces here separate code points; they are not part of the input).
With `strip=true`, its text is `A V`, not `A`. Only the final selector
supplies the state and is removed, even if earlier selectors name other states.
Decoder stripping is a single pass and is not necessarily idempotent.

### Mark removal

Mark removal is a separate text-cleanup operation, not a shortcut for
concatenating decoder runs with `strip=true`. Where provided, `strip_marks`:

- Removes every code point listed in the registry's `variation_selectors`,
  including lone selectors, selectors after whitespace, and repeated selectors.
- Replaces each registered PUA code point with its registered base character.
- Preserves all other code points, including unrecognized variation selectors
  and unallocated PUA code points.

This operation does not classify grapheme clusters or report states. It is
lossy: recognized selectors are removed even where the decoder treats them as
ordinary text. For example, `V A`, `A V V`, and `A` all become `A`.
Providing this helper is not required for decoder conformance.

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
  "registry_version": "0.2",
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
d󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 t󠄁h󠄁r󠄁e󠄁a󠄁d󠄁.󠄁

U󠄁s󠄁e󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁b󠄁l󠄁e󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁 I󠄁D󠄁s󠄁 b󠄁e󠄁l󠄁o󠄁w󠄁 i󠄁n󠄁 d󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 e󠄁x󠄁t󠄁e󠄁r󠄁n󠄁a󠄁l󠄁 r󠄁e󠄁f󠄁e󠄁r󠄁e󠄁n󠄁c󠄁e󠄁s󠄁,󠄁 s󠄁u󠄁c󠄁h󠄁 a󠄁s󠄁
`OQ-001` o󠄁r󠄁 `SPEC.md#oq-001`.󠄁 I󠄁D󠄁s󠄁 a󠄁r󠄁e󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 r󠄁e󠄁n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁e󠄁d󠄁 o󠄁r󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁d󠄁.󠄁 A󠄁s󠄁s󠄁i󠄁g󠄁n󠄁
n󠄁e󠄁w󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 n󠄁e󠄁x󠄁t󠄁 u󠄁n󠄁u󠄁s󠄁e󠄁d󠄁 n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁,󠄁 r󠄁e󠄁g󠄁a󠄁r󠄁d󠄁l󠄁e󠄁s󠄁s󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁i󠄁r󠄁 p󠄁o󠄁s󠄁i󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁r󠄁 t󠄁o󠄁p󠄁i󠄁c󠄁.󠄁

A󠄁 r󠄁e󠄁s󠄁o󠄁l󠄁u󠄁t󠄁i󠄁o󠄁n󠄁 u󠄁p󠄁d󠄁a󠄁t󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 a󠄁f󠄁f󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 s󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 a󠄁 l󠄁i󠄁n󠄁k󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁o󠄁l󠄁u󠄁t󠄁i󠄁o󠄁n󠄁
i󠄁n󠄁 t󠄁h󠄁e󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁 e󠄁n󠄁t󠄁r󠄁y󠄁.󠄁 K󠄁e󠄁e󠄁p󠄁 i󠄁t󠄁s󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁 r󠄁o󠄁w󠄁 a󠄁n󠄁d󠄁 I󠄁D󠄁 h󠄁e󠄁a󠄁d󠄁i󠄁n󠄁g󠄁 s󠄁o󠄁 e󠄁x󠄁i󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 r󠄁e󠄁f󠄁e󠄁r󠄁e󠄁n󠄁c󠄁e󠄁s󠄁
r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁 v󠄁a󠄁l󠄁i󠄁d󠄁.󠄁

| I󠄁D󠄁 | Q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁 | D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 |
| --- | --- | --- |
| [`OQ-001`](#oq-001) | C󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁 a󠄁n󠄁d󠄁 f󠄁o󠄁r󠄁g󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁 | [#󠄁1󠄁3󠄁](https://github.com/textprov/textprov/discussions/13) |
| [`OQ-002`](#oq-002) | W󠄁h󠄁a󠄁t󠄁 `human` a󠄁s󠄁s󠄁e󠄁r󠄁t󠄁s󠄁 | [#󠄁1󠄁4󠄁](https://github.com/textprov/textprov/discussions/14) |
| [`OQ-003`](#oq-003) | R󠄁e󠄁u󠄁s󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 t󠄁h󠄁a󠄁t󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁n󠄁 e󠄁d󠄁i󠄁t󠄁e󠄁d󠄁 | [#󠄁1󠄁6󠄁](https://github.com/textprov/textprov/discussions/16) |
| [`OQ-004`](#oq-004) | R󠄁e󠄁u󠄁s󠄁e󠄁d󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 | [#󠄁1󠄁8󠄁](https://github.com/textprov/textprov/discussions/18) |
| [`OQ-005`](#oq-005) | S󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁 i󠄁n󠄁 r󠄁o󠄁w󠄁s󠄁 A󠄁–󠄁E󠄁 | [#󠄁1󠄁9󠄁](https://github.com/textprov/textprov/discussions/19) |
| [`OQ-006`](#oq-006) | R󠄁u󠄁n󠄁s󠄁,󠄁 m󠄁a󠄁r󠄁k󠄁u󠄁p󠄁,󠄁 a󠄁n󠄁d󠄁 f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁s󠄁 | [#󠄁2󠄁0󠄁](https://github.com/textprov/textprov/discussions/20) |

### Marking and states

T󠄁h󠄁e󠄁s󠄁e󠄁 c󠄁a󠄁m󠄁e󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁p󠄁o󠄁s󠄁i󠄁t󠄁o󠄁r󠄁y󠄁'󠄁s󠄁 o󠄁w󠄁n󠄁 u󠄁s󠄁e󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁c󠄁o󠄁l󠄁
(󠄁[d󠄁o󠄁g󠄁f󠄁o󠄁o󠄁d󠄁i󠄁n󠄁g󠄁](docs/development/dogfooding.md))󠄁.󠄁

#### OQ-001

**C󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁 a󠄁n󠄁d󠄁 f󠄁o󠄁r󠄁g󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁** A󠄁r󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁,󠄁 p󠄁u󠄁l󠄁l󠄁 r󠄁e󠄁q󠄁u󠄁e󠄁s󠄁t󠄁
d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁p󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 i󠄁s󠄁s󠄁u󠄁e󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁v󠄁i󠄁e󠄁w󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 t󠄁h󠄁e󠄁
[m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](#marking-scope)?󠄁 T󠄁h󠄁e󠄁y󠄁 a󠄁r󠄁e󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 p󠄁e󠄁o󠄁p󠄁l󠄁e󠄁,󠄁 b󠄁u󠄁t󠄁 t󠄁h󠄁e󠄁
t󠄁o󠄁o󠄁l󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 h󠄁o󠄁l󠄁d󠄁 t󠄁h󠄁e󠄁m󠄁 s󠄁e󠄁a󠄁r󠄁c󠄁h󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁r󠄁s󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁 a󠄁s󠄁 p󠄁l󠄁a󠄁i󠄁n󠄁 t󠄁e󠄁x󠄁t󠄁:󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 b󠄁r󠄁e󠄁a󠄁k󠄁
`git log --grep`,󠄁 C󠄁o󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 C󠄁o󠄁m󠄁m󠄁i󠄁t󠄁s󠄁 p󠄁a󠄁r󠄁s󠄁e󠄁r󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 f󠄁o󠄁r󠄁g󠄁e󠄁 s󠄁e󠄁a󠄁r󠄁c󠄁h󠄁.󠄁 A󠄁 g󠄁i󠄁t󠄁
t󠄁r󠄁a󠄁i󠄁l󠄁e󠄁r󠄁 w󠄁o󠄁u󠄁l󠄁d󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 b󠄁a󠄁n󠄁d󠄁,󠄁 f󠄁o󠄁r󠄁 a󠄁 w󠄁h󠄁o󠄁l󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁i󠄁t󠄁 r󠄁a󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁a󠄁n󠄁 a󠄁
p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁.󠄁 (󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁3󠄁](https://github.com/textprov/textprov/discussions/13))󠄁

#### OQ-002

**W󠄁h󠄁a󠄁t󠄁 `human` a󠄁s󠄁s󠄁e󠄁r󠄁t󠄁s󠄁.󠄁** D󠄁o󠄁e󠄁s󠄁 `human` s󠄁t󠄁a󠄁t󠄁e󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 w󠄁r󠄁o󠄁t󠄁e󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁,󠄁
o󠄁r󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁t󠄁e󠄁d󠄁 i󠄁t󠄁?󠄁 T󠄁h󠄁i󠄁s󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁s󠄁 `human` a󠄁s󠄁
h󠄁u󠄁m󠄁a󠄁n󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁,󠄁 b󠄁u󠄁t󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 u󠄁s󠄁u󠄁a󠄁l󠄁l󠄁y󠄁 o󠄁b󠄁s󠄁e󠄁r󠄁v󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁s󠄁s󠄁i󠄁o󠄁n󠄁.󠄁 A󠄁
p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 c󠄁a󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁d󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁,󠄁 a󠄁n󠄁d󠄁 a󠄁 s󠄁c󠄁r󠄁i󠄁p󠄁t󠄁 c󠄁a󠄁n󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁t󠄁 t󠄁e󠄁x󠄁t󠄁 n󠄁o󠄁
p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁 w󠄁r󠄁o󠄁t󠄁e󠄁.󠄁 (󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁4󠄁](https://github.com/textprov/textprov/discussions/14))󠄁

### Generational marking (proposed, non-normative)

A󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁 e󠄁x󠄁t󠄁e󠄁n󠄁s󠄁i󠄁o󠄁n󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 a󠄁 s󠄁e󠄁c󠄁o󠄁n󠄁d󠄁 f󠄁a󠄁c󠄁t󠄁 b󠄁e󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁:󠄁 h󠄁o󠄁w󠄁 m󠄁a󠄁n󠄁y󠄁 t󠄁i󠄁m󠄁e󠄁s󠄁 a󠄁
c󠄀h󠄀a󠄀r󠄀a󠄀c󠄀t󠄀e󠄀r󠄀 h󠄀a󠄀s󠄀 b󠄀e󠄀e󠄀n󠄀 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁d󠄁,󠄁 t󠄁h󠄁a󠄁t󠄁 i󠄁s󠄁,󠄁 t󠄁a󠄁k󠄁e󠄁n󠄁 f󠄁r󠄁o󠄁m󠄁 o󠄁n󠄁e󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁'󠄁s󠄁
t󠄀r󠄀a󠄀n󠄀s󠄀c󠄀r󠄀i󠄀p󠄀t󠄀 i󠄀n󠄀t󠄀o󠄀 t󠄀h󠄀e󠄀 i󠄀n󠄀p󠄀u󠄀t󠄀 o󠄀f󠄀 t󠄀h󠄀e󠄀 n󠄀e󠄀x󠄀t󠄀.󠄀 A󠄁 m󠄁a󠄁r󠄁k󠄁 b󠄁e󠄁c󠄁o󠄁m󠄁e󠄁s󠄁
`U+E01gs`,󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁 `g` i󠄁s󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 `s` i󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁 (󠄁`0`
`human`,󠄁 `1` `ai`;󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 `2`–󠄁`4` a󠄁r󠄁e󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 `5`–󠄁`F` a󠄁r󠄁e󠄁
u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁)󠄁.󠄁 G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁u󠄁n󠄁s󠄁
f󠄁r󠄁o󠄁m󠄁 0󠄁 t󠄁o󠄁 9󠄁,󠄁 a󠄁n󠄁d󠄁 9󠄁 m󠄁e󠄁a󠄁n󠄁s󠄁 n󠄁i󠄁n󠄁e󠄁 o󠄁r󠄁 m󠄁o󠄁r󠄁e󠄁.󠄁 E󠄀a󠄀c󠄀h󠄀 t󠄀i󠄀m󠄀e󠄀 a󠄀 t󠄀r󠄀a󠄀n󠄀s󠄀c󠄀r󠄀i󠄀p󠄀t󠄀 b󠄀e󠄀c󠄀o󠄀m󠄀e󠄀s󠄀 i󠄀n󠄀p󠄀u󠄀t󠄀 t󠄀o󠄀
a󠄀 n󠄀e󠄀w󠄀 c󠄀o󠄀n󠄀v󠄀e󠄀r󠄀s󠄀a󠄀t󠄀i󠄀o󠄀n󠄀,󠄀 e󠄀v󠄀e󠄀r󠄀y󠄀 m󠄀a󠄀r󠄀k󠄀 m󠄀o󠄀v󠄀e󠄀s󠄀 d󠄀o󠄀w󠄀n󠄀 o󠄀n󠄀e󠄀 r󠄀o󠄀w󠄀 (󠄁`+0x10`)󠄁;󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 d󠄁o󠄁e󠄁s󠄁
n󠄁o󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 R󠄁o󠄁w󠄁 0󠄁 i󠄁s󠄁 t󠄁o󠄁d󠄁a󠄁y󠄁'󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁.󠄁 R󠄁o󠄁w󠄁 0󠄁 o󠄁f󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 2󠄁–󠄁4󠄁 h󠄁o󠄁l󠄁d󠄁s󠄁 t󠄁h󠄁e󠄁 o󠄁b󠄁s󠄁o󠄁l󠄁e󠄁t󠄁e󠄁
r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 s󠄁o󠄁 n󠄁o󠄁 r󠄁o󠄁w󠄁 o󠄁f󠄁 t󠄁h󠄁o󠄁s󠄁e󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 i󠄁s󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁.󠄁 C󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 5󠄁–󠄁F󠄁
a󠄁r󠄁e󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 f󠄁o󠄁r󠄁 f󠄁u󠄁t󠄁u󠄁r󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁,󠄁 w󠄁i󠄁t󠄁h󠄁 n󠄁o󠄁 a󠄁d󠄁d󠄁i󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁,󠄁 a󠄁n󠄁d󠄁 r󠄁o󠄁w󠄁s󠄁 A󠄁–󠄁E󠄁
(󠄁`U+E01A0`–󠄁`U+E01EF`)󠄁 f󠄁o󠄁r󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁,󠄁 w󠄁h󠄁i󠄁c󠄁h󠄁 a󠄁r󠄁e󠄁 a󠄁l󠄁t󠄁e󠄁r󠄁n󠄁a󠄁t󠄁e󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 e󠄁a󠄁c󠄁h󠄁
k󠄁e󠄁e󠄁p󠄁 t󠄁h󠄁e󠄁i󠄁r󠄁 o󠄁w󠄁n󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 T󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁
i󠄁s󠄁 n󠄁o󠄁t󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 0󠄁.󠄁2󠄁,󠄁 a󠄁n󠄁d󠄁 n󠄁o󠄁t󠄁h󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁 t󠄁h󠄁i󠄁s󠄁 s󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 i󠄁s󠄁 a󠄁
r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁.󠄁
F󠄁o󠄁u󠄁r󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁s󠄁 a󠄁r󠄁e󠄁 s󠄁e󠄁t󠄁t󠄁l󠄁e󠄁d󠄁.󠄁

- R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁i󠄁n󠄁g󠄁 i󠄀s󠄀 a󠄀 s󠄀e󠄀p󠄀a󠄀r󠄀a󠄀t󠄀e󠄀 o󠄀p󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀 f󠄀r󠄀o󠄀m󠄀 m󠄀a󠄀r󠄀k󠄀i󠄀n󠄀g󠄀.󠄀 P󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 r󠄁u󠄁l󠄁e󠄁 3󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁
  g󠄁o󠄁v󠄁e󠄁r󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁,󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁i󠄁n󠄁g󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁
- A󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 m󠄁a󠄁r󠄁k󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁
  i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 k󠄁n󠄁o󠄁w󠄁,󠄁 a󠄁n󠄁d󠄁 s󠄁a󠄁t󠄁u󠄁r󠄁a󠄁t󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 9󠄁.󠄁 A󠄁n󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 m󠄁a󠄁y󠄁
  a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁 w󠄁i󠄁t󠄁h󠄁 f󠄁e󠄁w󠄁e󠄁r󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁.󠄁 A󠄁 c󠄁o󠄁a󠄁r󠄁s󠄁e󠄁r󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 s󠄁c󠄁a󠄁l󠄁e󠄁 i󠄁s󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁.󠄁
- P󠄁U󠄁A󠄁 s󠄁t󠄁a󠄁n󠄁d󠄁s󠄁 f󠄁o󠄁r󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 o󠄁n󠄁l󠄁y󠄁,󠄁 a󠄁s󠄁 a󠄁n󠄁 a󠄁d󠄁j󠄁u󠄁n󠄁c󠄁t󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁 f󠄁o󠄁r󠄁 c󠄁o󠄁m󠄁p󠄁a󠄁t󠄁i󠄁b󠄁i󠄁l󠄁i󠄁t󠄁y󠄁.󠄁 A󠄁
  r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁s󠄁 a󠄁 P󠄁U󠄁A󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 t󠄁o󠄁 b󠄁a󠄁s󠄁e󠄁 p󠄁l󠄁u󠄁s󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁n󠄁
  i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁.󠄁
- F󠄁o󠄁r󠄁 e󠄁a󠄁c󠄁h󠄁 m󠄁a󠄁r󠄁k󠄁 a󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁n󠄁d󠄁 a󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 F󠄁o󠄁r󠄁 a󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁
  i󠄁n󠄁 r󠄁o󠄁w󠄁s󠄁 A󠄁–󠄁E󠄁 w󠄁h󠄁o󠄁s󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁,󠄁 i󠄁t󠄁 r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 a󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁
  r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 v󠄁a󠄁l󠄁u󠄁e󠄁.󠄁

T󠄁h󠄁e󠄁 [f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁](docs/development/generations-formal-aka-9g.md) i󠄁s󠄁 t󠄁h󠄁e󠄁
s󠄁i󠄁n󠄁g󠄁l󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁i󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 a󠄁n󠄁d󠄁 i󠄁t󠄁s󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁.󠄁
[A󠄁D󠄁R󠄁 0󠄁0󠄁1󠄁0󠄁](docs/adr/0010-contributor-identity-is-out-of-band.md) r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 t󠄁h󠄁e󠄁
r󠄁e󠄁a󠄁s󠄁o󠄁n󠄁i󠄁n󠄁g󠄁 b󠄁e󠄁h󠄁i󠄁n󠄁d󠄁 i󠄁t󠄁.󠄁

#### OQ-003

**R󠄁e󠄁u󠄁s󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 t󠄁h󠄁a󠄁t󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁n󠄁 e󠄁d󠄁i󠄁t󠄁e󠄁d󠄁.󠄁** W󠄁h󠄁e󠄁n󠄁 s󠄁o󠄁m󠄁e󠄁o󠄁n󠄁e󠄁 e󠄁d󠄁i󠄁t󠄁s󠄁 t󠄁e󠄁x󠄁t󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁d󠄁
f󠄁r󠄁o󠄁m󠄁 a󠄁n󠄁 e󠄁a󠄁r󠄁l󠄁i󠄁e󠄁r󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 w󠄁h󠄁a󠄁t󠄁 d󠄁o󠄁 t󠄁h󠄁e󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁s󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁,󠄁 a󠄁n󠄁d󠄁
w󠄁h󠄁a󠄁t󠄁 h󠄁a󠄁p󠄁p󠄁e󠄁n󠄁s󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁t󠄁?󠄁 M󠄀a󠄀r󠄀k󠄀s󠄀 a󠄀r󠄀e󠄀 p󠄀e󠄀r󠄀 c󠄀l󠄀u󠄀s󠄀t󠄀e󠄀r󠄀,󠄀 s󠄀o󠄀 n󠄀e󠄀w󠄀 c󠄀h󠄀a󠄀r󠄀a󠄀c󠄀t󠄀e󠄀r󠄀s󠄀 c󠄁o󠄁u󠄁l󠄁d󠄁
t󠄁a󠄁k󠄁e󠄁 t󠄁h󠄁e󠄁 e󠄁d󠄁i󠄁t󠄁o󠄁r󠄁'󠄁s󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 w󠄁h󠄁i󠄁l󠄁e󠄁 u󠄁n󠄁t󠄁o󠄁u󠄁c󠄁h󠄁e󠄁d󠄁 o󠄁n󠄁e󠄁s󠄁 k󠄁e󠄁e󠄁p󠄁 t󠄁h󠄁e󠄁i󠄁r󠄁s󠄁.󠄁
T󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁 f󠄁i󠄁x󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁c󠄁r󠄁o󠄁s󠄁s󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁;󠄁 h󠄁o󠄁w󠄁 e󠄁d󠄁i󠄁t󠄁s󠄁 a󠄁f󠄁f󠄁e󠄁c󠄁t󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁s󠄁
a󠄁n󠄁d󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁s󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 n󠄁o󠄁t󠄁 a󠄁n󠄁 a󠄁d󠄁d󠄁i󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁.󠄁
(󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁6󠄁](https://github.com/textprov/textprov/discussions/16))󠄁

#### OQ-004

**R󠄁e󠄁u󠄁s󠄁e󠄁d󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁** W󠄁h󠄁a󠄁t󠄁 h󠄁a󠄁p󠄁p󠄁e󠄁n󠄁s󠄁 t󠄁o󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁d󠄁 i󠄁n󠄁t󠄁o󠄁 a󠄁 n󠄁e󠄁w󠄁
c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁?󠄁 I󠄁t󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁 m󠄁a󠄁r󠄁k󠄁 t󠄁o󠄁 m󠄁o󠄁v󠄁e󠄁 d󠄁o󠄁w󠄁n󠄁 a󠄁 r󠄁o󠄁w󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁r󠄁e󠄁 i󠄁s󠄁 n󠄁o󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁
f󠄁o󠄁r󠄁 "󠄁u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁,󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 1󠄁"󠄁.󠄁 L󠄁e󠄁a󠄁v󠄁i󠄁n󠄁g󠄁 i󠄁t󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁.󠄁
H󠄁o󠄁w󠄁 c󠄁a󠄁n󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 t󠄁h󠄁a󠄁t󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 b󠄁a󠄁n󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 i󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁
o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁?󠄁 A󠄁b󠄁s󠄁e󠄁n󠄁c󠄁e󠄁 o󠄁f󠄁 a󠄁 m󠄁a󠄁r󠄁k󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁s󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 `human` a󠄁n󠄁d󠄁 `ai`.󠄁
(󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁8󠄁](https://github.com/textprov/textprov/discussions/18))󠄁

#### OQ-005

**S󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁 i󠄁n󠄁 r󠄁o󠄁w󠄁s󠄁 A󠄁–󠄁E󠄁.󠄁** H󠄁o󠄁w󠄁 d󠄁o󠄁e󠄁s󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁
`U+E01A0`–󠄁`U+E01EF`?󠄁 U󠄁n󠄁d󠄁e󠄁c󠄁i󠄁d󠄁e󠄁d󠄁:󠄁 w󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁e󠄁 u󠄁n󠄁i󠄁t󠄁 i󠄁s󠄁 a󠄁 w󠄁h󠄁o󠄁l󠄁e󠄁 r󠄁o󠄁w󠄁 o󠄁f󠄁 1󠄁6󠄁 o󠄁r󠄁
a󠄁n󠄁y󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁,󠄁 a󠄁n󠄁d󠄁 h󠄁o󠄁w󠄁 `mapping.json` r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁'󠄁s󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁 a󠄁n󠄁d󠄁 m󠄁e󠄁a󠄁n󠄁i󠄁n󠄁g󠄁.󠄁
E󠄁a󠄁c󠄁h󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 k󠄁e󠄁e󠄁p󠄁s󠄁 a󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁
r󠄁a󠄁n󠄁g󠄁e󠄁 s󠄁o󠄁 a󠄁 m󠄁a󠄁r󠄁k󠄁 s󠄁t󠄁a󠄁y󠄁s󠄁 r󠄁e󠄁a󠄁d󠄁a󠄁b󠄁l󠄁e󠄁 o󠄁u󠄁t󠄁s󠄁i󠄁d󠄁e󠄁 i󠄁t󠄁s󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁o󠄁r󠄁 s󠄁l󠄁o󠄁t󠄁s󠄁
i󠄁n󠄁 [A󠄁D󠄁R󠄁 0󠄁0󠄁1󠄁0󠄁](docs/adr/0010-contributor-identity-is-out-of-band.md) a󠄁r󠄁e󠄁 o󠄁n󠄁e󠄁
c󠄁a󠄁n󠄁d󠄁i󠄁d󠄁a󠄁t󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁.󠄁
(󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁1󠄁9󠄁](https://github.com/textprov/textprov/discussions/19))󠄁

#### OQ-006

**R󠄁u󠄁n󠄁s󠄁,󠄁 m󠄁a󠄁r󠄁k󠄁u󠄁p󠄁,󠄁 a󠄁n󠄁d󠄁 f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁s󠄁.󠄁** H󠄁o󠄁w󠄁 d󠄁o󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 A󠄁P󠄁I󠄁 e󠄁x󠄁p󠄁o󠄁s󠄁e󠄁
g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁?󠄁 W󠄁h󠄁a󠄁t󠄁 a󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 f󠄁o󠄁r󠄁 o󠄁n󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁 i󠄁s󠄁 s󠄁e󠄁t󠄁t󠄁l󠄁e󠄁d󠄁 a󠄁b󠄁o󠄁v󠄁e󠄁.󠄁 R󠄁u󠄁n󠄁s󠄁 a󠄁r󠄁e󠄁
`(state, text)` t󠄁o󠄁d󠄁a󠄁y󠄁.󠄁 U󠄁n󠄁d󠄁e󠄁c󠄁i󠄁d󠄁e󠄁d󠄁:󠄁 w󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 r󠄁u󠄁n󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁
s󠄁h󠄁a󠄁r󠄁e󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 b󠄁u󠄁t󠄁 d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁 i󠄁n󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 m󠄁e󠄁r󠄁g󠄁e󠄁,󠄁 h󠄁o󠄁w󠄁 `merge_whitespace`
t󠄁r󠄁e󠄁a󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁 w󠄁h󠄁i󠄁t󠄁e󠄁s󠄁p󠄁a󠄁c󠄁e󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 t󠄁h󠄁e󠄁m󠄁,󠄁 w󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 m󠄁a󠄁r󠄁k󠄁u󠄁p󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁s󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
b󠄁e󠄁s󠄁i󠄁d󠄁e󠄁 `data-prov`,󠄁 a󠄁n󠄁d󠄁 h󠄁o󠄁w󠄁 e󠄁x󠄁p󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 r󠄁u󠄁n󠄁s󠄁 i󠄁n󠄁 `fixtures.json` r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 i󠄁t󠄁.󠄁
(󠄁[D󠄁i󠄁s󠄁c󠄁u󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 #󠄁2󠄁0󠄁](https://github.com/textprov/textprov/discussions/20))󠄁
