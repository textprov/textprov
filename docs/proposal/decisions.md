# Open decisions

Status: decision agenda. Alternatives are not accepted choices. A closed decision
records rationale, evidence, and affected documents.

| ID | Decision | Evidence or definition needed | Status |
| --- | --- | --- | --- |
| D01 | Minimum plain-text copying guarantee | Named workflows; selection assumptions; reference, distinction, and description preservation | Open |
| D02 | Annotation unit | Grapheme clusters versus other units; Unicode version; whitespace, controls, line breaks | Open |
| D03 | Source and role semantics | Contributor versus quoted speaker or persona; anonymous sources; joint contributions and multiple references | Open |
| D04 | Encoding direction | VS baseline compared with additive PUA, annotations, tag payloads, historical stateful patterns, musical/bidi controls, joiners, combining marks, and standardization options | Open |
| D05 | Recognition and collisions | Profile context versus automatic recognition; unrelated PUA and genuine variation sequences | Open |
| D06 | Escaping and versioning | Literal round trips, unknown versions, copying without a document header | Open |
| D07 | Editing semantics | Insertion, deletion, selection, duplicate and orphan markers, state propagation | Open |
| D08 | Fallback and accessibility | Glyphs, shaping, bidi, cursor stops, assistive technology | Open |
| D09 | Search, normalization, offsets | Raw versus extracted text; explicit transforms; byte, scalar, or UTF-16 offsets | Open |
| D10 | Standardization request | General function, stable properties, independent adoption, need for Unicode encoding | Open |
| D11 | Compatibility and migration | Existing VS content and published mappings; false-detection risk | Open |
| D12 | Content scope | Prose, snippets, source files, eligibility responsibility | Open |
| D13 | Voice-reference scope | Scope of nonzero references; independent documents using `Voice1`; merge and paste behavior | Open |
| D14 | Source context portability | Dictionaries and descriptions; partial copying; unresolved references; privacy | Open |
| D15 | Optional metadata | Human/AI classification, source descriptions, identity verification; carriage and relationships to references | Open |
| D16 | Tag-based attribution | Suffix payload versus stateful runs; grammar, resets, emoji preservation, standards basis, and interior-copy behavior | Open |
| D17 | Run annotation architecture | Paired versus stateful scope; reference payload; nesting, paragraph boundaries, resets, interior-copy repair; private agreement versus standards changes | Open |

## Established semantic decision

`Voice0` represents unattributed text. Plain Unicode text with no recognized
attribution has this abstract reference without added markers or assumed human
origin. It has no source identity and requires no source dictionary. The decision
makes absence referable while preserving uncertainty about origin; it does not
choose an encoding or collapse unresolved references into ordinary text.

Affected documents: [model](model.md), [requirements](requirements.md),
[encoding candidates](encodings.md), [evaluation](demonstration.md), and the
[project introduction](../../README.md).

## Framing established on this branch

Source attribution is the core concept; “voices” is its introductory framing.
Human/AI classification, source descriptions, and verified identity are optional
information separate from attribution references. Reference scope and metadata
serialization remain open.

Concept, model, profiles, and demonstration are documented separately. The VS
implementation remains an experimental baseline. No permanent encoding,
additive PUA allocation, or standardized attribution character is selected. Older
baseline ADRs do not determine the proposal's design.
