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
| PUA run delimiters | `TP_BEGIN(reference) + text + TP_END` | Private-agreement candidate; extensible run syntax, but partial copying and unaware display need rules |
| Musical scope controls | Existing begin/end pair plus a reference payload | Structural precedent; active musical semantics, not generic attribution delimiters |
| Deprecated formatting toggles | Attribution state followed by a run and a reset | Historical non-nesting state model; repurposing requires a standards argument |
| Bidi isolates, embeddings, or overrides | Directional opener plus text and matching pop | Existing scope machinery; changes directional processing and conflicts with genuine bidi text |
| ZWJ-based convention | Text interspersed with joiners and an additional reference convention | Comparison candidate; shaping and emoji collisions, no inherent reference repertoire or run scope |
| Combining-mark convention | Text plus an existing combining mark and a reference convention | Comparison candidate; attachment alone does not supply private attribution semantics |
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

## Candidate status and run scope

Inclusion records a design possibility, not a claim that an assigned character
already permits that use. Deprecated characters remain assigned with their
historical meaning; deprecation does not release them for private allocation.
A proposal can request reconsideration or new attribution semantics, with
compatibility evidence and a standards decision still needed.

Run syntax and code-point choice are separate decisions. A profile can define
paired delimiters, a prefix that sets state until changed, or repeated unit
references. Each needs a voice-reference payload; a begin/end pair alone carries
no source identity. Nested versus non-nested scope, paragraph boundaries, resets
to `Voice0`, and recovery from malformed input remain open. A copied interior
fragment may need newly synthesized delimiters or state to retain attribution.

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

### PUA run delimiters and sentinels

Private agreement can define PUA begin/end markers, reference payloads, and
resets, as well as suffixes. This is a separate candidate from per-unit marking.
Ordinary Unicode processing does not automatically give such characters nesting,
attachment, invisibility, or word-boundary behavior. A profile needs recognition,
escaping, delimiter balancing, and rules for literal PUA text and partial copying.

Existing private registries or font assignments do not establish a universal PUA
word-bracketing protocol. This proposal makes no claim that ConScript, SIL, or
NLP pipelines share one. A specific precedent needs its own documented mapping,
license or agreement, and demonstrated behavior before serving as evidence.

## Annotation structure and new characters

`U+FFF9`, `U+FFFA`, and `U+FFFB` delimit base and annotation text. Unicode requires
prior agreement for correct plain-text interchange. A candidate TextProv use preserves
the base/annotation distinction and defines attribution-reference syntax separately;
its suitability for source attribution remains an evaluation question. These
characters are not default ignorable. Unaware display can expose the annotation
payload or visible control glyphs. Partial selection, malformed delimiters, and
fallback display need evaluation; ruby support is not attribution support.

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

The historical protocol is [RFC 2482, Language Tagging in Unicode Plain
Text](https://www.rfc-editor.org/rfc/rfc2482), not RFC 6067 (BCP 47 Extension U).
`U+E007F` is named CANCEL TAG. In the historical protocol cancellation resets
state; it is not merely a payload terminator as in emoji tag sequences. That
difference belongs in any comparison of grammars.

The architectural question is whether a tag establishes attribution for a
following run instead of repeating a reference on each unit. This can reduce
repetition, but copying an interior passage can omit the opening state. Insertion,
concatenation, resets, and unclosed state also need rules. `Voice0` supplies the
abstract absence state; any encoded reset to it remains a profile decision.

An adapted design needs its own attribution grammar and semantics. A voice
reference is not a language identifier, and historical language tagging does not
by itself define that use. The historical pattern is evaluated alongside suffix
payloads and other candidates without selecting either.

## Musical scope controls: U+1D173–U+1D17A

Status: structural precedent and possible repurposing proposal, not an accepted
TextProv encoding. The four pairs are BEGIN/END BEAM, TIE, SLUR, and PHRASE;
this range does not provide staff or tuplet delimiter pairs. They are assigned
format controls and are **not deprecated** in Unicode 17. See
[Western musical symbols](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-21/)
and the [Deprecated property](https://www.unicode.org/Public/17.0.0/ucd/PropList.txt).

Their paired structure is relevant to run annotations, but their musical meaning
remains active. An attribution adaptation needs a reference payload, a means to
distinguish real musical notation, and a standards basis for changed semantics.
Default-ignorable display does not ensure retention by editors or sanitizers.
Evaluation includes genuine music, incomplete pairs, nesting, and interior copies.

## Deprecated formatting toggles: U+206A–U+206F

Status: historical stateful precedent and possible revival proposal. The three
pairs are INHIBIT/ACTIVATE SYMMETRIC SWAPPING (`206A/206B`), INHIBIT/ACTIVATE
ARABIC FORM SHAPING (`206C/206D`), and NATIONAL/NOMINAL DIGIT SHAPES
(`206E/206F`). They are not Arabic number-sign or Lam-Alef delimiters. Unicode
retains them as deprecated characters; they have not been removed.

Their non-nesting on/off model suggests attribution state changes, rather than
balanced nested brackets. It still lacks voice-reference syntax. A proposed
adaptation needs rules for defaults, resets, legacy content, and receivers that
ignore or discard these controls. Their historical rendering purposes cannot
simply be presumed inert in every implementation. See
[Unicode section 23.3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).

## Bidirectional scope controls

Status: comparison candidate with active layout effects. `U+2066 LRI`,
`U+2067 RLI`, and `U+2068 FSI` open isolates terminated by `U+2069 PDI`.
The older embeddings and overrides (`U+202A–U+202E`) use `U+202C PDF`.
These families have distinct scope rules; PDF and PDI are not interchangeable.
Their semantics and boundary handling are defined by
[UAX #9](https://www.unicode.org/reports/tr9/).

They scope directional processing, not source attribution. A TextProv convention
would require an additional reference encoding and recognition scheme. It could
change punctuation placement, ordering, and surrounding text even when all
controls are invisible. Genuine bidi controls must survive extraction. Evaluation
includes mixed Arabic/Hebrew/Latin text, nested isolates, unmatched controls,
paragraph boundaries, and copying into a different directional context.

## ZWJ and existing combining marks

Status: comparison candidates, not implemented voice-reference profiles.
`U+200D ZERO WIDTH JOINER` affects joining and emoji sequences; it is not a
begin/end delimiter or a general mechanism for turning words into one glyph.
One joiner supplies no extensible reference repertoire. A convention using it
needs additional syntax, collision handling, and shaping tests. See
[Unicode joining controls](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
and [UTS #51](https://www.unicode.org/reports/tr51/).

Existing combining marks can attach to a base, but may display, reorder under
normalization, or interact with shaping. Variation selectors are a specialized
case already considered above. General category Cf is not a synonym for an
invisible metadata channel: variation selectors and many combining marks are
Mn, and PUA characters are Co. Attachment and invisibility are independent
properties to verify. Private combining behavior belongs under the PUA agreement
candidate; newly encoded attribution marks belong under standardization.

## Markup interchange and evidence

The [published W3C/Unicode note](https://www.w3.org/TR/2007/NOTE-unicode-xml-20070516/)
discusses replacing several in-band controls with markup in XML/HTML. Its
recommendations are specific to the character and interchange context, not a
blanket rejection of all format controls. The supplied
[editor's draft](https://www.w3.org/International/docs/unicode-xml/) is dated 2012
and predates bidi isolates and the modern emoji-tag use. Unicode 17 and current
UAX/UTS specifications determine present character status.

Character assignment, permitted semantics, rendering support, and measured
transport behavior are separate evidence. Inclusion here does not establish
support in ordinary software. Evaluation compares raw plain-text carriage with
conversion to native markup and records any lost or altered attribution.

## Other areas considered

Surrogates are UTF-16 machinery; lone surrogates prevent valid Unicode
interchange. Noncharacters suit internal sentinels rather than public character
semantics. BOM and replacement characters have encoding, object, or error roles.
These areas provide no additional private namespace. Tag characters and the
historical language-tagging pattern are evaluated separately above. See [Unicode sections 23.6–23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).
