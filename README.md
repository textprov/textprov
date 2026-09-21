# TextProv

TextProv is a protocol that lets text carry labels about its origin:
human-written, AI-generated, mixed, edited, or unknown. The labels are part of
the text, rather than metadata kept in a separate file or tied to one application.

Use TextProv in an editor or content pipeline when you know how text was
produced and want that information to accompany copied passages.
[Try the browser reader](https://textprov.org/#try-it) without installing
anything, or [start with a package](#using-textprov).

This repository holds the protocol specification, implementations, and website
source.

## How it works

An editor or content pipeline adds marks based on what it knows about the text.
For example, an application could mark a paragraph returned by a model as
AI-generated, while leaving the surrounding text unchanged.

The marks use Unicode characters and travel with the text through copy, paste,
and plain-text storage, provided the receiving software preserves them. A
TextProv-aware application can read those marks and make the labels visible.
With the default encoding, other applications normally display the ordinary
text without showing its provenance. Software that strips the marks removes
the labels, so test the copy-and-paste and storage paths your application uses.

Adding marks and displaying them are separate tasks. You do not need a special
font to mark text or show its provenance in a browser.

## What the labels mean

TextProv records a claim about origin; it does not establish that claim. The
application or person adding a mark decides which label applies.

- **It is not an AI detector.** It carries information supplied by an integration.
- **It is not proof of authorship.** Anyone can add, remove, or change a mark.
- **Unmarked does not mean human-written.** It means no label is present.

The labels do not identify an author, model, or timestamp. Store that information
separately if your workflow needs it. An explicit `unknown` label is also
different from unmarked text: one records a claim; the other has no label.

The protocol gives applications a shared way to represent these labels, without
requiring them to use the same tools or visual styles.

## Alongside C2PA and sidecar metadata

TextProv focuses on plain text and passages copied between applications. It
complements C2PA (Content Credentials), rather than replacing its signed
provenance records. TextProv is not a provenance format for images, audio, or
video.

C2PA uses cryptographic hashes and signatures to bind provenance records to
digital assets. These records are packaged in **manifests**, which can be
embedded in supported formats or stored externally, including in a **sidecar**:
a separate metadata file accompanying
an asset. C2PA does not exclude plain text; its
[technical specification, section 11.4](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html),
explicitly names `.txt` files as a reason to use an external manifest.

TextProv addresses what happens when only a passage is copied. Copying it into
another editor or message does not automatically carry the source document's
manifest, sidecar, or verification context. TextProv labels are part of the
character sequence and can accompany the passage without that surrounding
metadata, provided the receiving software preserves the marks.

A workflow could use TextProv for labels within the text and C2PA for a signed
record bound to the marked file. Add marks before creating a manifest that
binds those bytes: adding or removing marks changes the file's bytes. A copied
passage does not inherit the original file's verified status merely because
its labels remain.

TextProv does not create or validate C2PA manifests, and its labels are not
Content Credentials. This is coexistence at the workflow level, not a built-in
integration. Neither an origin label nor a valid signature establishes factual
accuracy.

## Using TextProv

The reference implementations cover the common uses:

- **[Python](python/README.md)** — add marks, read them back, or render marked
  text as HTML. Includes a command-line interface for working with text files.
- **[Ruby](ruby/README.md)** — add marks, read them back, or render marked text
  as HTML, with a `textprov` command-line interface. Requires Ruby 3.2+;
  no runtime dependencies or Rails requirement.
- **[JavaScript](js/README.md)** — read existing marks and display them in a
  browser, with an optional stylesheet.

### Python quick start

Requires Python 3.9+. On macOS or Linux, create an isolated environment and
install the package from PyPI:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install textprov
.venv/bin/python
```

At the Python prompt, mark text, render it as HTML, and recover the plain text:

```python
import textprov

marked = textprov.mark("Hello", state="ai")
print(textprov.to_html(marked))
print(textprov.strip_marks(marked))  # Hello
```

The first call to `print()` shows an HTML span with `data-prov="ai"`; the second
prints `Hello` without marks. Rendering HTML does not add visual styling by
itself. This example labels the text supplied to `mark()`; it does not analyze
who wrote it.

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
[npm](https://www.npmjs.com/package/textprov), the Python package is published
on [PyPI](https://pypi.org/project/textprov/), and the Ruby gem is published on
[RubyGems](https://rubygems.org/gems/textprov). The version 1 protocol is
treated as stable.

## Acknowledgements

TextProv was inspired by Pipedrive's concept of encoding information in Unicode
text and by the Nerd Fonts tooling workflow that made the approach practical.

## License

MIT. See [LICENSE](LICENSE).
