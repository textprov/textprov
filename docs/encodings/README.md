# Encoding candidates

Status: alternatives for evaluation. Symbols below are placeholders, not
code-point allocations. Candidate syntax illustrates carriage of a source
reference; nonzero reference scope, repertoire, and payload layout remain open.
`Voice0` denotes ordinary unattributed text at the model layer and needs no added
marker. Explicit serialization of that absence, if any, is profile-specific;
no zero marker is allocated here.

| Candidate | Illustrative serialization | Status and principal trade-off |
| --- | --- | --- |
| [VS suffix](vs.md) | `text + selector` | Implemented baseline; useful default display and attachment, but collisions and a mismatch with sanctioned variation semantics |
| [Additive PUA suffix](additive-pua.md) | `text + TP_REFERENCE` | Private-agreement candidate; retains literal text, while display and attachment need evaluation |
| [PUA run delimiters](run-delimiters.md) | `TP_BEGIN(reference) + text + TP_END` | Private-agreement candidate; extensible run syntax, but partial copying and unaware display need rules |
| [Musical scope controls](run-delimiters.md) | Existing begin/end pair plus a reference payload | Structural precedent; active musical semantics, not generic attribution delimiters |
| [Deprecated formatting toggles](run-delimiters.md) | Attribution state followed by a run and a reset | Historical non-nesting state model; repurposing requires a standards argument |
| [Bidi isolates, embeddings, or overrides](other-controls.md) | Directional opener plus text and matching pop | Existing scope machinery; changes directional processing and conflicts with genuine bidi text |
| [ZWJ-based convention](joiners-combining.md) | Text interspersed with joiners and an additional reference convention | Comparison candidate; shaping and emoji collisions, no inherent reference repertoire or run scope |
| [Combining-mark convention](joiners-combining.md) | Text plus an existing combining mark and a reference convention | Comparison candidate; attachment alone does not supply private attribution semantics |
| [Interlinear annotation](annotations.md) | `anchor + text + separator + reference + terminator` | Established annotation structure with receiver agreement; interior copying can lose enclosing context |
| [Tag-character payload](tags.md) | `text + tag(reference) + tag-end` | Candidate for investigation; ASCII-like payload and unobtrusive display, but existing emoji semantics and no established TextProv use |
| [Historical language-tagging pattern](tags.md) | Attribution tag followed by a text run and a reset | Deprecated language-tagging precedent; an adapted attribution design needs new semantics and can lose state during interior copying |
| [Newly standardized characters](../proposals/unicode.md) | Proposed marker or annotation structure | Possible Unicode proposal; semantics, properties, acceptance, and allocation unresolved |
| [External metadata](external-metadata.md) | Text plus annotations outside the character stream | Complementary integration; plain-text intermediaries can lose the association |

## Candidate status

Inclusion records a design possibility, not a claim that an assigned character
already permits that use. Deprecated characters remain assigned with their
historical meaning; deprecation does not release them for private allocation.
A proposal can request reconsideration or new attribution semantics, with
compatibility evidence and a standards decision still needed.


The [published W3C/Unicode note](https://www.w3.org/TR/2007/NOTE-unicode-xml-20070516/)
discusses replacing several in-band controls with markup in XML/HTML. Its
recommendations are specific to the character and interchange context, not a
blanket rejection of all format controls. The
[editor's draft](https://www.w3.org/International/docs/unicode-xml/) is dated 2012
and predates bidi isolates and the modern emoji-tag use. Unicode 17 and current
UAX/UTS specifications determine present character status.

Character assignment, permitted semantics, rendering support, and measured
transport behavior are separate evidence. Inclusion here does not establish
support in ordinary software. Evaluation compares raw plain-text carriage with
conversion to native markup and records any lost or altered attribution.

See [run architecture](run-delimiters.md) for paired versus stateful scope.
