# Demonstration and evaluation

Status: retained experimental baseline and proposed evaluation plan.

## What runs without extra support

The VS baseline stores human/AI labels in supplementary variation selectors. Ordinary
renderers generally display the underlying text without a special font. That
appearance does not interpret labels. A decoder or integration reads claims;
utility fonts provide optional inspection modes. The baseline does not implement
voice references, source dictionaries, or optional attribution metadata.

Python, Ruby, JavaScript, and website sources remain at their existing paths.
Mappings, fixtures, and specification describe baseline behavior. Passing baseline
conformance tests establishes agreement with that profile, not approval of its
Unicode semantics or preservation in arbitrary applications.

## Known collision

The [assessment](../development/encoding-recommendation.md) records
`U+8FBB U+E0100`, a legitimate ideographic variation sequence, being decoded as
`human`. Mark stripping removes its selector and glyph distinction. This is a
counterexample to safe interpretation of arbitrary Unicode input.

## Evaluation matrix

Candidates are evaluated with ordinary fonts and, separately, any aware renderer,
font, or editor. Samples include Latin prose, composed and decomposed accents,
emoji ZWJ and tag sequences, Hangul Jamo, registered ideographic variants, Arabic,
Hebrew, and unrelated PUA text.

Observations cover whole and interior passage copying, paste into an unaware
plain-text editor followed by copying again, cursor movement, backspace,
insertion, search, accessibility, and explicit NFC/NFD transformations. Recorded
code points and decoded annotations accompany application and platform versions.

Voice-reference experiments include plain Unicode text represented as `Voice0`
without mutation or assumed human origin, and anonymous nonzero sources kept
separate from unattributed text. They also cover documents reusing `Voice1`,
merging passages, copying without source dictionaries, anonymous sources, and
multiple sources of the same human/AI category. Results distinguish reference
survival, preservation of source distinctions, and access to source descriptions.

Tag-based experiments compare payload suffixes with stateful attribution runs.
They include genuine emoji tag sequences, copying a run without its opening tag,
concatenating runs, missing terminators, and resets to the abstract `Voice0` state.
No attribution semantics are inferred from the historical language-tagging use.

## Evidence status

This branch adds no new transport measurements or additive PUA implementation.
The matrix is a plan. The retained VS implementation and documented collision
are baseline evidence. Standards basis and measured usability are reported
separately.
