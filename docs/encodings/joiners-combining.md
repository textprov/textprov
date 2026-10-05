# Joiners and combining marks

Status: comparison candidates, not implemented voice-reference profiles.
`U+200D ZERO WIDTH JOINER` affects joining and emoji sequences; it is not a
begin/end delimiter or a general mechanism for turning words into one glyph.
One joiner supplies no extensible reference repertoire. A convention using it
needs additional syntax, collision handling, and shaping tests. See
[Unicode joining controls](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
and [UTS #51](https://www.unicode.org/reports/tr51/).

Existing combining marks can attach to a base, but may display, reorder under
normalization, or interact with shaping. Variation selectors are a specialized
case considered in the [VS profile](vs.md). General category Cf is not a synonym for an
invisible metadata channel: variation selectors and many combining marks are
Mn, and PUA characters are Co. Attachment and invisibility are independent
properties to verify. Private combining behavior belongs under the PUA agreement
candidate; newly encoded attribution marks belong under standardization.

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
