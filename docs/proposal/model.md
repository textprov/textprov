# TextProv concept and model

Status: proposal. Encoding-independent vocabulary; unresolved details appear in
[open decisions](decisions.md).

## Concept

TextProv concerns source attribution attached to text and its preservation when
passages move between applications. “Voices” is the introductory term for
sources distinguishable within an attribution context. The proposal focuses on
prose and passage copying. Exact boundaries of eligible content remain open.

## Semantics

Attribution is an association supplied by a person or application, not inferred
speaker identification. An attribution reference distinguishes a source; it does
not establish that source's identity, authorship, or authenticity. `Voice0`
represents the absence of attribution and conveys no conclusion about who
supplied the text.

A voice can represent a person, software system, quoted speaker, or another
defined source. Whether a reference denotes a contributor, quoted speaker, or
narrative persona is explicit in its context; those roles are not interchangeable.
The representation of roles remains open.

`Voice1`, `Voice2`, and `Voice3` illustrate references, not standardized values.
Several people can have distinct references, as can several assistants. Sources
can be anonymous or unspecified. A single source may also perform different
roles; reference reuse across roles remains a decision.

Human/AI classification is optional metadata, not the organizing distinction.
Source descriptions, model information, timestamps, and verified identity are
also optional information separate from the reference. Their serialization is
unresolved. The VS baseline implements human/AI classifications, not this voice
reference model.

“Attribution” follows established terminology for associating content with a
source; see [W3C PROV attribution](https://www.w3.org/TR/prov-o/#Attribution).
This proposal does not claim to implement the PROV data model. “Origin claims”
was descriptive working language, not an adopted term from a text standard.

## Voice0: unattributed text

`Voice0` is the reserved abstract reference for unattributed text. Ordinary
Unicode text with no recognized attribution is represented as `Voice0` without
requiring an added marker, a source dictionary, or a transformation of its code
points. This gives plain text a name in the model without assuming human origin.

`Voice0` is an absence state, not a shared source identity. Two `Voice0` passages
need not come from the same source. An anonymous source that is distinguished
from other sources can have a nonzero reference even when its identity is unknown.

The abstract distinction does not allocate a Unicode character or require a
serialized zero marker. Any explicit spelling of `Voice0` in an encoding profile
remains an encoding decision. Malformed annotations and unresolved nonzero
references remain distinguishable from ordinary unattributed text; `Voice0`
does not explain away decoding errors or missing context.

## Abstract representation

```text
AttributedUnit = { text: TextUnit, source: VoiceReference }
AttributedPassage = ordered sequence of units, including Voice0 units

plain Unicode text → { text: original TextUnit, source: Voice0 }
```

This notation expresses information, not a wire format. Association is written
`TextUnit + VoiceReference → AttributedUnit`. It neither implies string
concatenation nor creates a new Unicode character. One reference per unit is an
illustrative form; joint contributions and multiple references remain open.

A Unicode extended grapheme cluster is a candidate text unit. A cluster can
contain combining marks, meaningful variation selectors, and emoji joiners.
The choice of unit and Unicode segmentation version remain open.

## Reference scope and copying

| Approach | Benefit | Unresolved limitation |
| --- | --- | --- |
| Local `Voice1`, `Voice2` | Compact anonymous distinctions | Different contexts reuse names; descriptions may stay behind |
| Scoped reference such as `ContextA:Voice1` | Distinguishes sources after merging | Scope syntax, overhead, and context portability |
| Globally unique source identifier | Stable reference across contexts | Identifier lifecycle, overhead, and privacy |

These scope alternatives concern source references other than `Voice0`.
`Voice0` has the same absence meaning across contexts and needs no dictionary.

No scope approach for source references is selected. Preserving a reference,
preserving its distinction from
other sources, and preserving its description are different outcomes. A copied
passage may retain a distinction without enough context to explain it. The
minimum required outcome belongs in the copying guarantee.

## Separation of layers

| Layer | Defines | Does not settle |
| --- | --- | --- |
| Concept | User need | Source references or code points |
| Semantic model | Attribution meaning and target | Serialization |
| Abstract representation | Information carried | Byte or character layout |
| Encoding profile | Concrete syntax and decoding rules | Global Unicode assignment |
| Implementation | Executable behavior | Behavior of other applications |
| Unicode proposal | Requested semantics and properties | Approval or final allocation |

TextProv conformance, Unicode encoding validity, and measured application
interoperability are distinct claims. Future conformance language identifies
its profile and version explicitly.
