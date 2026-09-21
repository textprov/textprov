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

## Contract and mapping versions

- Draft contract version 0.1 (see [SPEC.md](../SPEC.md)).
- Draft registry version 0.1 (see [mapping.json](../mapping.json)). `lib/textprov/mapping.json`
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
unit-tests `cluster_end`, `to_html`, `strip_marks`, and the CLI.

## License

MIT. See [LICENSE](LICENSE).
