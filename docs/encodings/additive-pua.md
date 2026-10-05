# Additive private-use markers

Status: candidate, not implemented or allocated.

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


The Unicode private-use ranges are U+E000–U+F8FF, U+F0000–U+FFFFD, and
U+100000–U+10FFFD. Their meanings come from private agreement rather than a
public Unicode assignment. A published agreement may define attribution
semantics, but unaware software retains ordinary private-use processing.

Illustrative syntax is `unchanged TextUnit + reference payload`. Payload grammar,
recognition, literal escaping, scope, and versioning remain open. PUA need not
mean one code point per source; an extensible payload is a separate design.

Run-oriented private syntax is considered in [run delimiters](run-delimiters.md).

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
