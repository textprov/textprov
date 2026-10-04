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
| Tag-character payload | `text + tag(reference) + tag-end` | Candidate for investigation; ASCII-like payload and unobtrusive display, but existing emoji semantics and no established TextProv use |
| Historical language-tagging pattern | Attribution tag followed by a text run and a reset | Deprecated language-tagging precedent; an adapted attribution design needs new semantics and can lose state during interior copying |
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

## Tag characters: U+E0000–U+E007F

Status: candidate for investigation, not an implemented TextProv encoding or a
claim that Unicode already sanctions attribution tags.

The block contains 97 special-use tag characters corresponding to ASCII-based
strings, separated from ordinary textual content. `U+E0001 LANGUAGE TAG` is
deprecated. The currently specified conformant use of the other 96 characters
is emoji tag sequences under UTS #51. Those emoji sequences are neither nested
nor stateful. See [Unicode 17 section 23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/#G30110)
and [UTS #51](https://www.unicode.org/reports/tr51/#Valid_Emoji_Tag_Sequences).

A candidate TextProv design could encode a voice reference as an ASCII-like tag
payload associated with a text unit. The table's suffix syntax is illustrative,
not a defined grammar. Its appeal is an extensible reference payload with
normally invisible tag characters. Recognition, attachment, payload length,
terminators, and context scope remain open. Existing emoji tags need preservation;
an attribution decoder cannot treat every tag sequence as TextProv.

Evaluation distinguishes suffix attachment from the historical stateful
language-tagging pattern below. It includes actual selection and clipboard
sequences, shaping, segmentation, filtering, and detection of unrelated tags.
Unobtrusive rendering alone does not establish correct copying or interpretation.
A profile also needs to establish its standards basis: a new standardized use or
another explicitly justified protocol treatment, rather than assuming a private
namespace from the tag block's name or properties.

## Deprecated use for language tagging

Status: historical design precedent included among the alternatives. Language
tagging itself remains deprecated; its adaptation to attribution is a proposal,
not a revival authorized by this document.

Tag characters originally supported language tagging of plain text. That use
was deprecated in Unicode 5.1. Unicode 8.0 removed deprecation from the tag
characters except `U+E0001 LANGUAGE TAG` and `U+E007F CANCEL TAG`; Unicode 9.0
also removed deprecation from `CANCEL TAG` and repurposed the characters for
emoji tag sequences. The historical specification is linked from Unicode 17:
[Unicode 5.0 section 16.9](https://www.unicode.org/versions/Unicode5.0.0/ch16.pdf#G17521).

The architectural question is whether a tag establishes attribution for a
following run instead of repeating a reference on each unit. This can reduce
repetition, but copying an interior passage can omit the opening state. Insertion,
concatenation, resets, and unclosed state also need rules. `Voice0` supplies the
abstract absence state; any encoded reset to it remains a profile decision.

An adapted design needs its own attribution grammar and semantics. A voice
reference is not a language identifier, and historical language tagging does not
by itself define that use. The historical pattern is evaluated alongside suffix
payloads and other candidates without selecting either.

## Other areas considered

Surrogates are UTF-16 machinery; lone surrogates prevent valid Unicode
interchange. Noncharacters suit internal sentinels rather than public character
semantics. BOM and replacement characters have encoding, object, or error roles.
These areas provide no additional private namespace. Tag characters and the
historical language-tagging pattern are evaluated separately above. See [Unicode sections 23.6–23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).
