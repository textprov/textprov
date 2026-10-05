# Tag-character candidates

## Tag characters

Status: candidate for investigation, not an implemented TextProv encoding or a
claim that Unicode already sanctions attribution tags.

The block contains 97 special-use tag characters corresponding to ASCII-based
strings, separated from ordinary textual content. `U+E0001 LANGUAGE TAG` is
deprecated. The currently specified conformant use of the other 96 characters
is emoji tag sequences under UTS #51. Those emoji sequences are neither nested
nor stateful. See [Unicode 17 section 23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/#G30110)
and [UTS #51](https://www.unicode.org/reports/tr51/#Valid_Emoji_Tag_Sequences).

A candidate TextProv design could encode a voice reference as an ASCII-like tag
payload associated with a text unit. A suffix such as `text + tag(reference) + tag-end` is illustrative,
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

## Historical language tagging

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
Text](https://www.rfc-editor.org/rfc/rfc2482).
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

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
