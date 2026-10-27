# textprov — Ruby SDK demonstration

This working experiment encodes and decodes `human`/`ai` classifications using
variation selectors and a limited replacement-PUA mode. Ruby 3.2+, standard
library only. Its package identity and version describe executable code, not a
versioned proposal standard. It does not implement voice references or detect
who wrote text.

From `ruby/`, run with `ruby -Ilib`, or install this checkout as a gem:

```ruby
require "textprov"

marked = Textprov.mark("foo", state: "ai")
raise unless marked == "f\u{E0101}o\u{E0101}o\u{E0101}"
raise unless Textprov.strip_marks(marked) == "foo"
Textprov.runs(marked)  # [["ai", marked]]
Textprov.to_html(marked)  # span carrying data-prov="ai"
Textprov.mark_added("abc", "abXc")
Textprov.convert(marked, "vs", "pua")
```

`mark` and `mark_added` accept `state:` and `mode:` (`vs` or `pua`). Only `human`
and `ai` are accepted classifications. `runs` and `to_html` accept `strip:` and
`merge_whitespace:` (alias `mergeWhitespace:`); HTML also accepts `class_prefix:`.
Core functions accept `mapping: Textprov::Mapping.load(path)`.
`Textprov.inspect_text` reports classifications without shadowing Ruby's `inspect`.

The PUA mode replaces eligible base characters; it is distinct from the
[additive-PUA candidate](../docs/encodings/additive-pua.md). Genuine Unicode
variation sequences can collide with the decoder, and stripping can remove
legitimate glyph selection. Read the [baseline limitations](../experiments/baseline/README.md)
and [VS profile](../docs/encodings/vs.md) before using arbitrary text.

The proposal [model](../docs/model.md) defines unattributed text as `Voice0`.
This experiment reports unmarked runs as `nil`; classification labels are not
implementations of nonzero voice references. Legacy `SPEC_VERSION` is a baseline
identifier, not a proposal version.

## HTML display

`to_html` r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁 s󠄁p󠄁a󠄁n󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 i󠄁n󠄁j󠄁e󠄁c󠄁t󠄁i󠄁n󠄁g󠄁 s󠄁t󠄁y󠄁l󠄁e󠄁s󠄁.󠄁 `Textprov.stylesheet` r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁
t󠄁h󠄁e󠄁 p󠄁a󠄁c󠄁k󠄁a󠄁g󠄁e󠄁d󠄁 r󠄁e󠄁v󠄁e󠄁a󠄁l󠄁 C󠄁S󠄁S󠄁:󠄁 g󠄁r󠄁a󠄁d󠄁i󠄁e󠄁n󠄁t󠄁 m󠄁i󠄁s󠄁t󠄁 a󠄁n󠄁d󠄁 a󠄁 d󠄁o󠄁t󠄁t󠄁e󠄁d󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁 a󠄁t󠄁 6󠄁0󠄁%󠄁
s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁-󠄁c󠄁o󠄁l󠄁o󠄁r󠄁 o󠄁p󠄁a󠄁c󠄁i󠄁t󠄁y󠄁.󠄁 T󠄁h󠄁e󠄁 w󠄁a󠄁v󠄁y󠄁/󠄁s󠄁a󠄁w󠄁t󠄁o󠄁o󠄁t󠄁h󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁 i󠄁s󠄁 d󠄁e󠄁f󠄁u󠄁n󠄁c󠄁t󠄁.󠄁

```ruby
require "textprov"

File.write("textprov.css", Textprov.stylesheet, encoding: "UTF-8")
html = Textprov.to_html(Textprov.mark("A draft", state: "ai"))
```

S󠄁e󠄁r󠄁v󠄁e󠄁 t󠄁h󠄁a󠄁t󠄁 C󠄁S󠄁S󠄁 a󠄁s󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁i󠄁c󠄁 a󠄁s󠄁s󠄁e󠄁t󠄁 a󠄁n󠄁d󠄁 l󠄁i󠄁n󠄁k󠄁 i󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 H󠄁T󠄁M󠄁L󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁
s󠄁t󠄁y󠄁l󠄁e󠄁s󠄁h󠄁e󠄁e󠄁t󠄁 s󠄁h󠄁i󠄁p󠄁s󠄁 i󠄁n󠄁 a󠄁l󠄁l󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁 S󠄁D󠄁K󠄁s󠄁.󠄁 S󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁
[d󠄁i󠄁s󠄁p󠄁l󠄁a󠄁y󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁o󠄁n󠄁](../docs/development/provenance-display.md) f󠄁o󠄁r󠄁 n󠄁a󠄁t󠄁i󠄁v󠄁e󠄁
l󠄁i󠄁n󠄁k󠄁,󠄁 p󠄁r󠄁o󠄁o󠄁f󠄁i󠄁n󠄁g󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁s󠄁 u󠄁n󠄁a󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁e󠄁d󠄁.󠄁

## CLI

```sh
ruby -Ilib exe/textprov -o marked.txt mark --ai draft.txt
ruby -Ilib exe/textprov mark-added old.txt new.txt
ruby -Ilib exe/textprov convert --from vs --to pua marked.txt
ruby -Ilib exe/textprov strip marked.txt
ruby -Ilib exe/textprov render marked.txt
ruby -Ilib exe/textprov inspect marked.txt
```

An installed gem exposes `textprov`. A file argument may be `-` for stdin;
output goes to stdout unless `-o` is supplied. UTF-8 line endings are preserved.

## Checks

From `ruby/`:

```sh
ruby -Ilib -Itest -e 'Dir["test/test_*.rb"].each { |file| require File.expand_path(file) }'
```

Alternatively use `bundle exec rake test`. Checks cover shared
[fixtures](../experiments/baseline/fixtures.json), vendored mapping agreement,
producer behavior, CLI output, and Unicode 17.0.0 grapheme segmentation.
See [UCD sources](../ucd/README.md).

Apache-2.0; see [LICENSE](LICENSE).
