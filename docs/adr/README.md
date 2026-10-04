> **Experimental baseline.** This document describes the retained demonstration.
> The [proposal](../proposal/decisions.md) keeps encoding and design decisions open.
> Baseline rules and compatibility statements do not govern the proposal.

# Architecture decision records

One file per decision. Status is `accepted` only when the decision is
implemented or measured; otherwise `proposed`. Superseded records stay in
place with a pointer to their replacement.

0005 and 0007 are font-build decisions and stay in the
[Nerd Fonts fork](https://github.com/delano/nerd-fonts/tree/main/docs/adr):
serving the patched font as a woff2 subset, and reaching variants under
CoreText through a `ccmp` ligature. The numbering is shared, so a number
appears in one repository or the other, never both.

Two records set scope rather than mechanism.
[ADR 0014](0014-the-protocol-defines-structure-not-use.md) keeps the
protocol to structure and encoding, a shared baseline, and leaves how labels
are used to consumers. [ADR 0015](0015-fonts-are-for-inspection-and-demonstration.md)
positions P9E fonts as an inspection and demonstration tool.

Records written before the repository split use the Nerd Fonts fork's original
paths. They remain historical records; use
[ADR 0006](0006-decorator-packages-and-repository.md) for the split and
[ADR 0011](0011-the-producer-is-text-processing.md) for the current producer
boundary.

[ADR 0013](0013-use-p9e-as-provenance-shorthand.md) records the shorthand
`p9e` / `P9E` and its transition from the `P+` font suffix. Earlier records
retain `P+` when describing the fonts and measurements they recorded.
