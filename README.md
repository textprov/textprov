# TextProv

TextProv is a protocol that lets p󠄁r󠄁o󠄁s󠄁e󠄁 carry labels about its origin:
h󠄁u󠄁m󠄁a󠄁n󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁 o󠄁r󠄁 A󠄁I󠄁-󠄁g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁e󠄁d󠄁.󠄁 The labels are part of
the text, rather than metadata kept in a separate file or tied to one application.

Use TextProv in an editor or content pipeline when you know how text was
produced and want that information to accompany copied passages.
[Try the browser reader](https://textprov.org/#try-it) without installing
anything, or [start with a package](#using-textprov).

TextProv provides a shared structure, encoding, and vocabulary so applications
can exchange the same provenance information and choose how best to use it.
Displaying labels, interpreting agent prompts, and other integrations can
build on that common foundation.

This repository holds the protocol specification, implementations, and website
source.

## How it works

An editor or content pipeline adds marks based on what it knows about the text.
For example, an application could mark a paragraph returned by a model as
AI-generated, while leaving the surrounding text unchanged.

The marks use Unicode characters and travel with the text through copy, paste,
and plain-text storage, provided the receiving software preserves them. A
TextProv-aware application can read those marks to inform its own processing
or make the labels visible.
With the default encoding, other applications normally display the ordinary
text without showing its provenance. Software that strips the marks removes
the labels, so test the copy-and-paste and storage paths your application uses.

Adding marks and displaying them are separate tasks. You do not need a special
font to mark text or show its provenance in a browser.

## Marking scope

T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 a󠄁d󠄁d󠄁r󠄁e󠄁s󠄁s󠄁e󠄁s󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 e󠄁x󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 p󠄁e󠄁o󠄁p󠄁l󠄁e󠄁.󠄁 S󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁
e󠄁x󠄁c󠄁l󠄁u󠄁d󠄁e󠄁d󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁s󠄁,󠄁 d󠄁o󠄁c󠄁s󠄁t󠄁r󠄁i󠄁n󠄁g󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 i󠄁n󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁.󠄁 S󠄁o󠄁u󠄁r󠄁c󠄁e󠄁
c󠄁o󠄁d󠄁e󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁s󠄁 t󠄁o󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁o󠄁l󠄁 a󠄁n󠄁d󠄁 d󠄁e󠄁v󠄁e󠄁l󠄁o󠄁p󠄁m󠄁e󠄁n󠄁t󠄁 w󠄁o󠄁r󠄁k󠄁f󠄁l󠄁o󠄁w󠄁s󠄁.󠄁

C󠄁o󠄁d󠄁e󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 a󠄁n󠄁 a󠄁r󠄁t󠄁i󠄁c󠄁l󠄁e󠄁,󠄁 m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁,󠄁 o󠄁r󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 m󠄁a󠄁y󠄁 b󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁,󠄁 b󠄁u󠄁t󠄁
m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁m󠄁 i󠄁s󠄁 o󠄁p󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁.󠄁 S󠄁u󠄁c󠄁h󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁;󠄁 t󠄁h󠄁e󠄁y󠄁 d󠄁o󠄁 n󠄁o󠄁t󠄁 m󠄁a󠄁k󠄁e󠄁 a󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁
s󠄁u󠄁i󠄁t󠄁a󠄁b󠄁l󠄁e󠄁 f󠄁o󠄁r󠄁 d󠄁i󠄁r󠄁e󠄁c󠄁t󠄁 e󠄁x󠄁e󠄁c󠄁u󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 I󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁 e󠄁l󠄁i󠄁g󠄁i󠄁b󠄁l󠄁e󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁;󠄁 t󠄁h󠄁e󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁e󠄁r󠄁
d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁c󠄁o󠄁g󠄁n󠄁i󠄁z󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁 t󠄁y󠄁p󠄁e󠄁s󠄁 o󠄁r󠄁 p󠄁r󠄁o󠄁g󠄁r󠄁a󠄁m󠄁m󠄁i󠄁n󠄁g󠄁 s󠄁y󠄁n󠄁t󠄁a󠄁x󠄁.󠄁 S󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁'󠄁s󠄁
[m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](SPEC.md#marking-scope).󠄁

## What the labels mean

TextProv records a claim about origin; it does not establish that claim. The
application or person adding a mark decides which label applies.

- **It is not an AI detector.** It carries information supplied by an integration.
- **It is not proof of authorship.** Anyone can add, remove, or change a mark.
- **Unmarked does not mean human-written.** It means no label is present.

The labels do not identify an author, model, or timestamp. Store that information
separately if your workflow needs it. O󠄁n󠄁l󠄁y󠄁 `human` a󠄁n󠄁d󠄁 `ai` a󠄁r󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁d󠄁;󠄁
u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁.󠄁

The protocol gives applications a shared way to represent these labels, while
leaving decision policies and presentation to each integration.

## Agent prompt integrations

A prompt can combine an operator's instructions with text copied from model
output. TextProv marks can preserve that distinction across copying, giving
an agent integration context that would otherwise be lost. An integration
could use the decoded states to experiment with how much weight to give each
passage in its decision process.

This is a potential use that requires further integration to read the marks,
apply a policy, and evaluate its effect. The protocol supplies a common
foundation for that work. Unmarked text remains unlabelled; treating it as
operator-written depends on the input workflow. The specification's
[application use discussion](SPEC.md#application-use-non-normative) gives an
illustrative weighting example and explains the integration boundary.

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

The **TextProv Utility P9E fonts** are development and debugging adjuncts.
The suite provides Sans, Serif, Fixed, Mono, and Proportional families that
reveal supported provenance marks with compatible rendering. Their visible
patterns make stored encoding easier to inspect and demonstrate; consuming
applications and sites choose the presentation that fits their users. See the
[utility font guide](docs/FONT-UTILITIES.md) for downloads, rebuilding, licensing,
and compatibility, and the
[font and interchange guide](docs/SELECTORS-PUA-AND-INTERCHANGE.md) for the
choice between selector and PUA encoding. `P9E` is the provenance shorthand
that succeeds the earlier `P+` font suffix.

## Exploring the protocol

You do not need to work on the packages or website to use the protocol. If you
are considering an integration or writing an implementation, start here:

- [Specification](SPEC.md) — the labels, encodings, and rules for reading and
  writing marked text.
- [Maturity lifecycle](docs/MATURITY.md) — compatibility promises and the evidence
  required to promote a release.
- [Code-point registry](mapping.json) — the characters assigned to those labels.
- [Conformance fixtures](fixtures.json) — shared examples with expected results
  for checking implementations.
- [Changelog](CHANGELOG.md) — dated protocol and registry changes.
- [Architecture decisions](docs/adr) — the reasoning behind the design and
  questions still under discussion.

Package usage and test instructions live in the implementation guides linked
above. Website development instructions are in [`site/`](site/README.md).

## Status

The protocol is **Draft 0.2**, last updated 2026-10-03. Specification behavior may
change incompatibly; implementers should pin an immutable revision. Published
registry allocations remain reserved and are never reassigned or removed. The
JavaScript package is published on [npm](https://www.npmjs.com/package/textprov),
the Python package is published on [PyPI](https://pypi.org/project/textprov/),
and the Ruby gem is published on
[RubyGems](https://rubygems.org/gems/textprov). See the
[maturity lifecycle](docs/MATURITY.md) for compatibility promises and promotion
criteria before implementing it.

## Acknowledgements

TextProv was inspired by Pipedrive's concept of encoding information in Unicode
text and by the Nerd Fonts tooling workflow that made the approach practical.

## License

Project code is MIT licensed. See [LICENSE](LICENSE). Bundled utility fonts
and their derivatives are licensed under the SIL Open Font License 1.1; each
font bundle includes its upstream copyright and license. See
[utility font licensing](docs/FONT-UTILITIES.md#licensing-and-attribution).
