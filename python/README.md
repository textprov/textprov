# textprov (Python)

The TextProv reference implementation: it puts provenance marks in text and
reads them back out. Standard library only.

```python
import textprov

textprov.mark("foo", state="ai")       # 'f\U000E0101o\U000E0101o\U000E0101'
textprov.mark_added("abc", "abXc")     # mark only what an edit added
textprov.convert(marked, "vs", "pua")  # same states, other encoding
textprov.strip_marks(marked)           # back to the original text

textprov.runs("f\U000E0101oo")
# [('ai', 'f\U000E0101'), (None, 'oo')]

textprov.to_html("f\U000E0101oo")
# '<span class="prov prov-ai" data-prov="ai">f\U000E0101</span>oo'

textprov.inspect(marked)               # a 'key: value' report of the states
```

`runs` and `to_html` take `strip`, `merge_whitespace`, and (for `to_html`)
`class_prefix`. `mark` and `mark_added` take `state` and `mode` (`"vs"` or
`"pua"`). Every function takes `mapping=textprov.Mapping.load(path)` to use a
registry other than the copy vendored in this package.

## CLI

```sh
python3 -m textprov -o marked.txt mark --ai draft.txt
python3 -m textprov mark-added old.txt new.txt
python3 -m textprov convert --from vs --to pua marked.txt
python3 -m textprov strip marked.txt
python3 -m textprov render marked.txt
python3 -m textprov inspect marked.txt
```

An installed package also provides a `textprov` entry point. A file argument
may be `-` for stdin; output goes to stdout unless `-o` is given. Text is read
and written as UTF-8 verbatim, so CRLF survives.

The protocol is [SPEC.md](../SPEC.md); the registry is
[mapping.json](../mapping.json). `textprov/mapping.json` is a vendored copy and
the test suite fails if it drifts from the canonical file.

## Tests

```sh
python3 -m unittest discover -s tests -t .
```

The suite runs every decoder, producer, and convert case in
[fixtures.json](../fixtures.json), tests the producer properties from
[SPEC.md](../SPEC.md) directly rather than only through recorded outputs, and
unit-tests `cluster_end`, `to_html`, `strip_marks`, and the CLI.
