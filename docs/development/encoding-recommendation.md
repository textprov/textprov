# TextProv encoding recommendation

Status: recommendation for evaluation; no replacement encoding is selected.
Date: 2026-09-28.
Scope: TextProv's work-in-progress 0.1.0 design, treated as unreleased for this
assessment. This note does not change the protocol or its compatibility rules.

## Recommendation

Preserve TextProv's central requirement: origin labels accompany copied passages
through plain-text workflows without requiring every intermediary to understand
TextProv. Evaluate a small set of **Private Use Area (PUA) state markers appended
to ordinary grapheme clusters** before choosing a replacement for the existing
variation-selector encoding.

HTML attributes, JSON representations, sidecars, and custom clipboard formats
are complementary integrations. Making them the sole representation would give
up the plain-text passage portability described in the [project overview](../../README.md).
A passage pasted into a plain-text editor and copied again loses metadata carried
only in richer formats. Visible enclosing delimiters also lose their context
when a user copies only the middle of the passage.

The existing per-cluster encoding has a useful property: a complete marked
cluster carries its own state without a document header or a distant opening
delimiter. That property deserves to remain a design objective. It does not
guarantee preservation when software strips characters or selection cuts a
cluster apart.

## Evidence and constraints

### Variation selectors collide with ordinary Unicode text

The [specification](../../SPEC.md#states) assigns global provenance meanings to
`U+E0100` a󠄁n󠄁d󠄁 `U+E0101`.󠄁 Unicode variation selectors acquire meaning through
particular base-and-selector sequences; they are not a private namespace.
[UTS #37](https://www.unicode.org/reports/tr37/) explicitly states that a selector
has no independently designated purpose across bases.

For example, `U+8FBB U+E0100` is a registered ideographic variation sequence for
the character 辻, documented in the
[Adobe-Japan1 implementation example](https://www.unicode.org/irg/docs/n1435-IVS.pdf).
The Python implementation produces the following result, reproduced during this
assessment:

```text
Input:         U+8FBB U+E0100
runs():        state = human
strip_marks(): U+8FBB
```

No TextProv producer was involved. The decoder invents a provenance claim and
mark removal deletes a legitimate glyph distinction. This is a correctness
defect independently of any standards-conformance claim. Selecting different
variation selectors does not establish a private namespace.

The [Unicode 18 chapter 3 text](https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-3/)
explicitly disallows private interpretation of unassigned variation sequences
and misplaced variation selectors. Its
[version landing page](https://www.unicode.org/versions/Unicode18.0.0/) still
displayed a preliminary-draft notice when checked, despite being the destination
of Unicode's latest-version link. The publication-status inconsistency warrants
qualification; the cited restriction is present in the chapter text. Earlier
[Unicode guidance](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
already describes variation selectors as unsuitable for a general extension
mechanism.

These findings justify correcting the collision and qualifying Unicode claims.
They do not, by themselves, establish that an experimental release must abandon
in-band encoding or adopt sidecars as its primary format.

### Additive PUA is distinct from the existing PUA encoding

TextProv's [existing PUA encoding](../../SPEC.md#encodings) replaces a supported
base character with a private character. The proposed experiment retains the
ordinary text and appends a private state marker:

```text
Existing PUA:  ordinary letter -> private character representing letter + state
Candidate PUA: ordinary cluster -> unchanged cluster + private state marker
```

[Unicode §23.5](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
permits cooperating applications to define private-use character semantics,
including treating a private character as a combining mark. Such an agreement
can be openly published. PUA characters also normalize to themselves; their
normalization properties cannot be changed by private agreement.

This makes additive PUA a legitimate candidate for a private annotation
convention. It does not grant universal behavior:

- Unaware software can display missing-glyph boxes or other glyphs for markers.
- Default segmentation can give markers separate cursor stops and selection
  boundaries. TextProv-specific handling does not change other applications.
- A custom font can improve display without fixing selection and editing.
- Other private conventions can assign the same code points. Recognition,
  escaping, and preservation of unrelated PUA text remain design questions.

No code points are allocated by this recommendation.

## Alternatives and their trade-offs

| Representation | Useful property | Principal limitation |
| --- | --- | --- |
| Existing variation-selector suffix | State accompanies each complete marked cluster; often invisible | Collides with registered sequences and conflicts with Unicode's intended semantics |
| Additive PUA marker | Keeps base text and uses Unicode's private-agreement mechanism | Display and cluster attachment require evaluation in unaware applications |
| Existing PUA replacement | Supports controlled font workflows | Ordinary letters are unavailable without the private mapping |
| Interlinear annotation characters | Unicode defines an annotation structure | Enclosing structure complicates partial copying; fallback needs receiver agreement |
| Visible escaped syntax | Inspectable and transportable as ordinary text | Adds visible content; enclosing delimiters may be left behind during selection |
| HTML, JSON, sidecars, rich clipboard formats | Carry structured annotations without altering base text | Metadata does not survive an intermediate plain-text-only representation |

Interlinear annotation characters are permitted for interchange with prior
agreement; they are not categorically forbidden.
[Unicode §23.8.3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
discourages their use with unknown receivers. The Tags block is not an established
alternative for provenance: its documented conformant use is emoji tagging,
and its earlier language-tagging use was deprecated.

## Proposed bounded experiment

The existing implementation serves as the experimental baseline. A small
additive-PUA prototype provides a comparison without committing the protocol to
a new registry or serialization. Interlinear annotations provide an optional
third comparison if range enclosure remains attractive.

The evaluation uses a few representative browsers and plain-text editors,
recording application and platform versions. Its samples include ordinary Latin
text, composed and decomposed accents, emoji sequences, Hangul Jamo, registered
ideographic variation sequences, and unrelated PUA characters.

The observations cover:

- Display with ordinary fonts and a TextProv-aware renderer or font.
- Actual selection, copy, paste into an unaware plain-text editor, and copying
  again. Copying only an interior word tests whether state needs distant context.
- Cursor movement, backspace, deletion, and insertion beside a marker.
- Search and exact preservation of the underlying text.
- NFC and NFD transformations, recording both code points and decoded states.
- False provenance detection and accidental removal of existing Unicode content.

Recorded output sequences establish transport behavior; screenshots alone do
not. A candidate is credible when measured benefits preserve the passage-copy
requirement and its limitations are explicit. If additive PUA loses essential
selection behavior or produces unacceptable fallback, that result calls for a
decision about which requirement can relax. It does not automatically select a
sidecar architecture.

## Normalization and immediate follow-through

TextProv preserves original code-point sequences by default. NFC is an explicit
application policy where canonical comparison is useful, rather than a silent
producer or decoder transformation. Any normalization used for offsets or hashes
occurs before those values are calculated. Normalization neither resolves marker
ambiguity nor guarantees passage portability.

The immediate recommendations are to record the variation-sequence collision as
a regression case, evaluate additive PUA, and correct the specification's block
name to **Variation Selectors Supplement**. The experiment also needs to expose
segmentation d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁e󠄁n󠄁c󠄁e󠄁s󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 o󠄁n󠄁 d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁e󠄁n󠄁t󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁s󠄁;󠄁
t󠄁h󠄁e󠄁 r󠄁e󠄁f󠄁e󠄁r󠄁e󠄁n󠄁c󠄁e󠄁 p󠄁o󠄁r󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁m󠄁s󠄁e󠄁l󠄁v󠄁e󠄁s󠄁 n󠄁o󠄁w󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 o󠄁n󠄁e󠄁 v󠄁e󠄁n󠄁d󠄁o󠄁r󠄁e󠄁d󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁 s󠄁e󠄁t󠄁
(󠄁[A󠄁D󠄁R󠄁 0󠄁0󠄁1󠄁7󠄁](../adr/0017-vendor-grapheme-segmentation.md))󠄁.󠄁

The prototype remains useful for learning. Choosing a permanent encoding,
changing published compatibility promises, and rewriting the protocol follow
from an explicit decision informed by the experiment.
