# Architecture decision records

One file per decision. Status is `accepted` only when the decision is
implemented or measured; otherwise `proposed`. Superseded records stay in
place with a pointer to their replacement.

0005 and 0007 are font-build decisions and stay in the
[Nerd Fonts fork](https://github.com/delano/nerd-fonts/tree/main/docs/adr):
serving the patched font as a woff2 subset, and reaching variants under
CoreText through a `ccmp` ligature. The numbering is shared, so a number
appears in one repository or the other, never both.

Records written before the repository split use the Nerd Fonts fork's original
paths. They remain historical records; use
[ADR 0006](0006-decorator-packages-and-repository.md) for the split and
[ADR 0011](0011-the-producer-is-text-processing.md) for the current producer
boundary.
