# Encoding candidates

Status: alternatives for evaluation. Symbols below are placeholders, not
code-point allocations. Candidate syntax illustrates carriage of a source
reference; nonzero reference scope, repertoire, and payload layout remain open.
`Voice0` denotes ordinary unattributed text at the model layer and needs no added
marker. Explicit serialization of that absence, if any, is profile-specific;
no zero marker is allocated here.

| Candidate | Illustrative serialization | Status and principal trade-off |
| --- | --- | --- |
| VS suffix | `text + selector` | Implemented baseline; useful default display and attachment, but collisions and a mismatch with sanctioned variation semantics |
| Additive PUA suffix | `text + TP_REFERENCE` | Private-agreement candidate; retains literal text, while display and attachment need evaluation |
| Interlinear annotation | `anchor + text + separator + reference + terminator` | Established annotation structure with receiver agreement; interior copying can lose enclosing context |
| Newly standardized characters | Proposed marker or annotation structure | Possible Unicode proposal; semantics, properties, acceptance, and allocation unresolved |
| External metadata | Text plus annotations outside the character stream | Complementary integration; plain-text intermediaries can lose the association |

## Variation selectors

The implemented VS profile carries human/AI classifications. An extension to
voice references is a separate candidate design, not implemented behavior.

Unicode defines sanctioned base-selector combinations in standardized variants,
emoji sequences, and the Ideographic Variation Database. A selector provides no
independent private label across bases. The baseline assigns global origin
meanings to `U+E0100` and `U+E0101`; legitimate Japanese text can therefore be
decoded as provenance and damaged by stripping.

Avoiding known registered pairs does not establish a private namespace. The
[assessment](../development/encoding-recommendation.md) records the collision.
[Unicode section 23.4](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
and [UTS #37](https://www.unicode.org/reports/tr37/) define intended semantics.

## Additive PUA

Unicode permits private-use semantics, including treatment as a combining mark,
by agreement among cooperating users. That agreement does not change unaware
editors. Normalization properties remain fixed. Other private conventions can
use the same values; recognition, escaping, and collision policy need definition.

This candidate appends a marker to unchanged text. The baseline's PUA mapping
instead substitutes a private character for a base character plus state. These
are different designs. No additive marker values are selected. A small fixed state-marker set does not
by itself encode an extensible voice-reference repertoire; payload syntax and
overhead need evaluation. See
[Unicode section 23.5](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).

## Annotation structure and new characters

`U+FFF9`, `U+FFFA`, and `U+FFFB` delimit base and annotation text. Unicode requires
prior agreement for correct plain-text interchange. A TextProv use preserves
those semantics and defines attribution-reference syntax separately. Partial selection,
malformed delimiters, and fallback display need evaluation.

Unassigned Specials positions are reserved, not private-use values. A proposal
may request new annotation characters and suggest placement; allocation remains
a Unicode decision. Specials is a location, not an independent encoding design.
See [Unicode direction](unicode.md).

## Other areas considered

Surrogates are UTF-16 machinery; lone surrogates prevent valid Unicode
interchange. Noncharacters suit internal sentinels rather than public character
semantics. BOM and replacement characters have encoding, object, or error roles.
Tag characters have specified emoji use; deprecated language tagging supplies no
private provenance convention. These areas provide no additional private
namespace. See [Unicode sections 23.6–23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).
