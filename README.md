# TextProv

TextProv is a protocol that lets text carry labels about its origin:
human-written, AI-generated, mixed, edited, or unknown. The labels are part of
the text, rather than metadata kept in a separate file or tied to one application.

Visit [textprov.org](https://textprov.org) for an introduction. This repository
holds the protocol specification, implementations, and website source together.

## How it works

An editor or content pipeline adds marks based on what it knows about the text.
For example, an application could mark a paragraph returned by a model as
AI-generated, while leaving the surrounding text unchanged.

The marks use Unicode characters and travel with the text through copy, paste,
and plain-text storage, provided the receiving software preserves them. A
TextProv-aware application can read those marks and make the labels visible.
With the default encoding, other applications display the ordinary text without
showing its provenance.

Adding marks and displaying them are separate tasks. You do not need a special
font to mark text or show its provenance in a browser.

## What the labels mean

TextProv records a claim about origin; it does not establish that claim. The
application or person adding a mark decides which label applies.

- **It is not an AI detector.** It carries information supplied by an integration.
- **It is not proof of authorship.** Anyone can add, remove, or change a mark.
- **Unmarked does not mean human-written.** It means no label is present.

The protocol gives applications a shared way to represent these labels, without
requiring them to use the same tools or visual styles.

## Using TextProv

The reference implementations cover the common uses:

- **[Python](python/README.md)** — add marks, read them back, or render marked
  text as HTML. Includes a command-line interface for working with text files.
- **[Ruby](ruby/README.md)** — the same producer, decoder, and renderer surface
  as Python, plus a `textprov` command-line interface. No runtime dependencies
  and not Rails-specific.
- **[JavaScript](js/README.md)** — read existing marks and display them in a
  browser, with an optional stylesheet.

For example, the Python API can mark text and turn it into HTML:

```python
import textprov

marked = textprov.mark("Hello", state="ai")
html = textprov.to_html(marked)
```

This labels the text supplied to `mark()`; it does not analyze who wrote it.

Marks can also be displayed with a patched font. The
[font and interchange guide](docs/SELECTORS-PUA-AND-INTERCHANGE.md) explains that
workflow and when to use it.

## Exploring the protocol

You do not need to work on the packages or website to use the protocol. If you
are considering an integration or writing an implementation, start here:

- [Specification](SPEC.md) — the labels, encodings, and rules for reading and
  writing marked text.
- [Code-point registry](mapping.json) — the characters assigned to those labels.
- [Conformance fixtures](fixtures.json) — shared examples with expected results
  for checking implementations.
- [Architecture decisions](docs/adr) — the reasoning behind the design and
  questions still under discussion.

Package usage and test instructions live in the implementation guides linked
above. Website development instructions are in [`site/`](site/README.md).

## Status

The project is early-stage. The JavaScript package is published on
[npm](https://www.npmjs.com/package/textprov), and the Python package is
published on [PyPI](https://pypi.org/project/textprov/). The Ruby gem lives in
[`ruby/`](ruby/) and is not yet published to rubygems.org. The version 1
protocol is treated as stable.

## Acknowledgements

TextProv was inspired by Pipedrive's concept of encoding information in Unicode
text and by the Nerd Fonts tooling workflow that made the approach practical.

## License

MIT. See [LICENSE](LICENSE).
