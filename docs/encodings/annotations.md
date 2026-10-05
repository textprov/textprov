# Interlinear annotation candidate

Status: candidate, not an implemented attribution profile.

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
See [Unicode direction](../proposals/unicode.md).

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
