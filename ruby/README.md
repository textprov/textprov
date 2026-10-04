# textprov (Ruby)

The TextProv reference implementation in Ruby: it puts provenance marks in text
and reads them back out. Standard library only.

```ruby
require "textprov"

Textprov.mark("foo", state: "ai")             # "f\u{E0101}o\u{E0101}o\u{E0101}"
Textprov.mark_added("abc", "abXc")            # mark only what an edit added
Textprov.convert(marked, "vs", "pua")         # same states, other encoding
Textprov.strip_marks(marked)                  # back to the original text

Textprov.runs("f\u{E0101}oo")
# => [["ai", "f\u{E0101}"], [nil, "oo"]]

Textprov.to_html("f\u{E0101}oo")
# => '<span class="prov prov-ai" data-prov="ai">f\u{E0101}</span>oo'

Textprov.inspect_text(marked)                 # a 'key: value' report of the states
```

`runs` and `to_html` take `strip:`, `merge_whitespace:` (also `mergeWhitespace:`
as an alias per SPEC's cross-language rule), and (for `to_html`)
`class_prefix:`. `mark` and `mark_added` take `state:` and `mode:` (`"vs"` or
`"pua"`). Every function takes `mapping: Textprov::Mapping.load(path)` to use a
registry other than the copy vendored in this package.

Only `human` and `ai` are provenance states. Producers reject obsolete state
names (`mixed`, `edited`, `unknown`). Their former selectors, U+E0102–U+E0104,
are ordinary non-TextProv selectors: decoding, rendering, stripping, and
conversion preserve them, including with `strip: true`.

The Ruby method is `Textprov.inspect_text`, not `.inspect`, so it does not
shadow `Kernel#inspect`.

## Install

```sh
gem install textprov
```

Ruby 3.2+ is required. No runtime dependencies.

## CLI

```sh
textprov -o marked.txt mark --ai draft.txt
textprov mark-added old.txt new.txt
textprov convert --from vs --to pua marked.txt
textprov strip marked.txt
textprov render marked.txt
textprov inspect marked.txt
```

A file argument may be `-` for stdin; output goes to stdout unless `-o` is
given. Text is read and written as UTF-8 verbatim, so CRLF survives.

## Specification and registry versions

- Draft specification version 0.2 (see [SPEC.md](../SPEC.md)).
- Draft registry version 0󠄁.󠄁2󠄁 (see [mapping.json](../mapping.json)). `lib/textprov/mapping.json`
  is a vendored copy and the test suite fails if it drifts from the canonical
  file.

## Tests

```sh
bundle install
bundle exec rake test
```

The suite runs every decoder, producer, and convert case in
[fixtures.json](../fixtures.json), tests the producer properties from
[SPEC.md](../SPEC.md) directly rather than only through recorded outputs, and
r󠄁u󠄁n󠄁s󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 l󠄁i󠄁n󠄁e󠄁 o󠄁f󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁'󠄁s󠄁 `GraphemeBreakTest.txt` t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 `segments`,󠄁 a󠄁n󠄁d󠄁
u󠄁n󠄁i󠄁t󠄁-󠄁t󠄁e󠄁s󠄁t󠄁s󠄁 `to_html`, `strip_marks`, and the CLI.

## License

T󠄁h󠄁e󠄁 p󠄁a󠄁c󠄁k󠄁a󠄁g󠄁e󠄁 l󠄁i󠄁c󠄁e󠄁n󠄁s󠄁e󠄁 i󠄁s󠄁 `Apache-2.0 AND CC0-1.0 AND Unicode-3.0`.󠄁 T󠄁h󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 i󠄁s󠄁
l󠄁i󠄁c󠄁e󠄁n󠄁s󠄁e󠄁d󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁 A󠄁p󠄁a󠄁c󠄁h󠄁e󠄁 2󠄁.󠄁0󠄁 (󠄁[L󠄁I󠄁C󠄁E󠄁N󠄁S󠄁E󠄁](LICENSE))󠄁.󠄁 T󠄁h󠄁e󠄁 b󠄁u󠄁n󠄁d󠄁l󠄁e󠄁d󠄁 c󠄁o󠄁p󠄁y󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁
T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 i󠄁s󠄁 d󠄁e󠄁d󠄁i󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 p󠄁u󠄁b󠄁l󠄁i󠄁c󠄁 d󠄁o󠄁m󠄁a󠄁i󠄁n󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁 C󠄁C󠄁0󠄁 1󠄁.󠄁0󠄁
(󠄁[L󠄁I󠄁C󠄁E󠄁N󠄁S󠄁E󠄁-󠄁C󠄁C󠄁0󠄁-󠄁1󠄁.󠄁0󠄁](LICENSE-CC0-1.0))󠄁.󠄁 T󠄁h󠄁e󠄁 g󠄁r󠄁a󠄁p󠄁h󠄁e󠄁m󠄁e󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁
g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁e󠄁d󠄁 f󠄁r󠄁o󠄁m󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 d󠄁a󠄁t󠄁a󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁v󠄁e󠄁r󠄁e󠄁d󠄁 b󠄁y󠄁 t󠄁h󠄁e󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 L󠄁i󠄁c󠄁e󠄁n󠄁s󠄁e󠄁 v󠄁3󠄁
(󠄁[L󠄁I󠄁C󠄁E󠄁N󠄁S󠄁E󠄁-󠄁U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁-󠄁3󠄁.󠄁0󠄁](LICENSE-Unicode-3.0))󠄁.󠄁 A󠄁l󠄁l󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁 a󠄁p󠄁p󠄁l󠄁y󠄁.󠄁
