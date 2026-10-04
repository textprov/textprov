# Open decisions

Status: decision agenda. Alternatives are not accepted choices. A closed decision
records rationale, evidence, and affected documents.

| ID | Decision | Evidence or definition needed | Status |
| --- | --- | --- | --- |
| D01 | Minimum plain-text copying guarantee | Named workflows, complete-unit selection assumptions, acceptable failure modes | Open |
| D02 | Annotation unit | Grapheme clusters versus other units; Unicode version; whitespace, controls, line breaks | Open |
| D03 | Origin vocabulary | Definitions of `human`, `ai`, possible `mixed`; relabelling and contributions | Open |
| D04 | Encoding direction | VS baseline compared with additive PUA, annotations, and standardization options | Open |
| D05 | Recognition and collisions | Profile context versus automatic recognition; unrelated PUA and genuine variation sequences | Open |
| D06 | Escaping and versioning | Literal round trips, unknown versions, copying without a document header | Open |
| D07 | Editing semantics | Insertion, deletion, selection, duplicate and orphan markers, state propagation | Open |
| D08 | Fallback and accessibility | Glyphs, shaping, bidi, cursor stops, assistive technology | Open |
| D09 | Search, normalization, offsets | Raw versus extracted text; explicit transforms; byte, scalar, or UTF-16 offsets | Open |
| D10 | Standardization request | General function, stable properties, independent adoption, need for Unicode encoding | Open |
| D11 | Compatibility and migration | Existing VS content and published mappings; false-detection risk | Open |
| D12 | Content scope | Prose, snippets, source files, eligibility responsibility | Open |

## Framing established on this branch

Concept, model, profiles, and demonstration are documented separately. The VS
implementation remains an experimental baseline. No permanent encoding,
additive PUA allocation, or standardized origin character is selected. Older
baseline ADRs do not determine the proposal's design.
