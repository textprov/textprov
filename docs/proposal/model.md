# TextProv concept and model

Status: proposal. Encoding-independent vocabulary; unresolved details appear in
[open decisions](decisions.md).

## Concept

TextProv concerns origin claims attached to text and their preservation when
passages move between applications. The proposal focuses on prose and passage
copying. Exact boundaries of eligible content remain open.

## Semantics

An origin claim is supplied by a person or producing application. It is not an
inference from the text and does not establish its own authenticity. An absent
claim conveys no conclusion about origin.

`human`, `ai`, and `mixed` are vocabulary candidates. The retained baseline
implements `human` and `ai`; the definition of `mixed`, its relationship to
multiple contributions, and its inclusion in the repertoire remain unresolved.
Author identity, model identity, timestamps, and signatures are separate concerns.

## Abstract representation

```text
AnnotatedUnit = { text: TextUnit, origin: OriginClaim }
AnnotatedPassage = ordered sequence of annotated or unannotated units
```

This notation expresses information, not a wire format. Association is written
`TextUnit + OriginClaim → AnnotatedUnit`. It neither implies string concatenation
nor creates a new Unicode character.

A Unicode extended grapheme cluster is a candidate text unit. A cluster can
contain combining marks, meaningful variation selectors, and emoji joiners.
The choice of unit and Unicode segmentation version remain open.

## Separation of layers

| Layer | Defines | Does not settle |
| --- | --- | --- |
| Concept | User need | Labels or code points |
| Semantic model | Meaning and attachment target | Serialization |
| Abstract representation | Information carried | Byte or character layout |
| Encoding profile | Concrete syntax and decoding rules | Global Unicode assignment |
| Implementation | Executable behavior | Behavior of other applications |
| Unicode proposal | Requested semantics and properties | Approval or final allocation |

TextProv conformance, Unicode encoding validity, and measured application
interoperability are distinct claims. Future conformance language identifies
its profile and version explicitly.
