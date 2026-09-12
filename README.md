# TextProv

Text that carries its own provenance. A run of characters can say whether a
person wrote it, a machine generated it, or its origin is unknown. The state
travels in the text as Unicode code points, so it survives copy, paste, and
plain-text storage.

This repository is the protocol: the specification, the canonical code-point
registry, the conformance fixture, and reference implementations that read
marked text and render it.

```
SPEC.md         the protocol
mapping.json    the canonical code-point registry
fixtures.json   the conformance suite; an implementation passes it or it is not TextProv
js/             @textprov/decorator — browser DOM decorator and optional stylesheet
python/         textprov — decoder and HTML renderer
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

Not here. This repository defines the marks and reads them back. The reference
producer today is the `--provenance` option of a
[Nerd Fonts fork](https://github.com/delano/nerd-fonts), which patches a font
with provenance variants and ships the marker that adds the code points. A
producer is conforming when a decoder in this repository reproduces its intent.

## Conformance

```sh
cd js && node check_fixtures.mjs
cd python && python3 -m unittest discover -s tests -t .
```

Each runner checks every case in `fixtures.json`, checks the contract and
registry versions it implements, and checks the registry tables it embeds
against `mapping.json`. An implementation in a new language is conforming when
it reproduces every recorded `runs` result; add fixtures rather than reading
either reference implementation as the definition.

## Status

Early. The protocol is at contract version 1 and the registry at version 1.
Neither package is published yet; both reference implementations pass the
fixture. Open questions and the shape of what comes next are in
[docs/adr](docs/adr). The two encodings, the run algorithm, and the span markup
are settled and should be treated as stable.

## License

MIT. See [LICENSE](LICENSE).
