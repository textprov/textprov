# Experimental variation-selector profile

The implemented VS profile carries human/AI classifications. An extension to
voice references is a separate candidate design, not implemented behavior.

Unicode defines sanctioned base-selector combinations in standardized variants,
emoji sequences, and the Ideographic Variation Database. A selector provides no
independent private label across bases. The baseline assigns global origin
meanings to `U+E0100` and `U+E0101`; legitimate Japanese text can therefore be
decoded as provenance and damaged by stripping.

Avoiding known registered pairs does not establish a private namespace. The
[evaluation](../evaluation.md#variation-sequence-collision) records the collision.
[Unicode section 23.4](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
and [UTS #37](https://www.unicode.org/reports/tr37/) define intended semantics.

## Experimental demonstration

The homepage contains a deliberately marked sample decoded by a retained JavaScript SDK
renderer. Its historical `human` and `ai` labels are classifications, not
implemented voice references. Unmarked text has no experimental classification;
the proposal represents absent attribution as `Voice0`. No human origin is
inferred. The demonstration does not define source dictionaries or metadata.

Ordinary fonts generally display the sample without visible selector glyphs;
the toggle adds HTML/CSS decoration. This shows rendering behavior, not guaranteed
clipboard transport or safe automatic recognition of arbitrary Unicode text.
The experimental values are `U+E0100` and `U+E0101`; they are not private
allocations or proposed Unicode assignments.

## Registered variation sequences

Unicode defines three separate repertoires: [standardized variation sequences](https://www.unicode.org/Public/17.0.0/ucd/StandardizedVariants.txt),
[emoji variation sequences](https://www.unicode.org/Public/17.0.0/ucd/emoji/emoji-variation-sequences.txt),
and [registered ideographic variation sequences](https://www.unicode.org/ivd/).
The first two are versioned Unicode data; the IVD follows the registration process
in UTS #37 and has its own dated releases. These lists describe base-selector
combinations and their glyph variants, not independent selector labels.

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
