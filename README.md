# TextProv

Text that carries its own provenance. A run of characters can say whether a
person wrote it, a machine generated it, or its origin is unknown. The state
travels in the text as Unicode code points, so it survives copy, paste, and
plain-text storage.

This repository is the protocol: the specification, the canonical code-point
registry, the conformance fixture, and reference implementations that put marks
in text and read them back out.

```
SPEC.md         the protocol
mapping.json    the canonical code-point registry
fixtures.json   the conformance suite; an implementation passes it or it is not TextProv
js/             @textprov/decorator — browser DOM decorator and optional stylesheet
python/         textprov — producer, decoder, HTML renderer, and CLI
docs/           goals, HTML rendering measurements, architecture decision records
```

## Reading marked text

In a browser, no font required:

```html
<link rel="stylesheet" href="textprov.css">
<script src="textprov.js"></script>
<script>textprov.render(document.body);</script>
```

On a server:

```python
import textprov
textprov.to_html("f\U000E0101oo")
# '<span class="prov prov-ai" data-prov="ai">f\U000E0101</span>oo'
```

Both emit the same markup:

```html
<span class="prov prov-ai" data-prov="ai">TEXT</span>
```

`data-prov` is the contract. The classes exist so CSS can show the state; the
bundled stylesheet is one choice of style, not part of the protocol.

## Producing marked text

Also here. Marking text needs the registry and nothing else — no font, no
shaping engine, no build step — so the reference producer ships in the Python
package and its CLI:

```sh
python3 -m textprov -o marked.txt mark --ai draft.txt   # or: textprov -o marked.txt mark ...
python3 -m textprov mark-added old.txt new.txt          # mark only what changed
python3 -m textprov convert --from vs --to pua marked.txt
python3 -m textprov inspect marked.txt
```

```python
textprov.mark("Hi", state="ai")        # 'H\U000E0101i\U000E0101'
textprov.mark_added("abc", "abXc")     # mark what an edit added
textprov.convert(marked, "vs", "pua")  # change encoding, same states
```

`fixtures.json` carries `producer_cases` and `convert_cases` beside the decoder
cases, so a producer either conforms or it does not; `SPEC.md` states the four
properties those cases exist to pin down. The JavaScript package reads marks
only.

What a producer does *not* decide here is which state applies to which text.
That belongs to the integration: an editor that knows who typed, a pipeline
that knows a model wrote a paragraph, or a person running the CLI.

Showing marks in a *font* is a different job with a different toolchain, and it
is a renderer, not a producer: that is the `--provenance` option of a
[Nerd Fonts fork](https://github.com/delano/nerd-fonts), which patches a font
with provenance variants of its own glyphs. See [Why TextProv publishes
selectors instead of PUA text](docs/SELECTORS-PUA-AND-INTERCHANGE.md) for the
interchange trade-off, including Nerd Fonts and Zed on macOS.

## Website

Preview the site locally with Vite:

```sh
cd site
npm ci
npm run dev
```

`npm run build` produces the GitHub Pages artifact in `site/dist`.

## Conformance

```sh
cd js && node check_fixtures.mjs
cd python && python3 -m unittest discover -s tests -t .
```

Each runner checks every case in `fixtures.json`, checks the contract and
registry versions it implements, and checks the registry tables it embeds
against `mapping.json`. The Python suite also runs the producer cases and the
properties behind them. An implementation in a new language is conforming when
it reproduces every recorded result for the roles it implements; add fixtures
rather than reading either reference implementation as the definition.

## Status

Early. The protocol is at contract version 1 and the registry at version 1.
Neither package is published yet; both reference implementations pass the
fixture. Open questions and the shape of what comes next are in
[docs/adr](docs/adr). The two encodings, the run algorithm, and the span markup
are settled and should be treated as stable.

## Acknowledgements

TextProv was inspired by Pipedrive's concept of encoding information in Unicode
text and by the Nerd Fonts tooling workflow that made the approach practical.

## License

MIT. See [LICENSE](LICENSE).
