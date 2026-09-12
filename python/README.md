# textprov (Python)

The TextProv decoder and renderer. It reads in-band provenance marks from text
and returns runs or HTML spans. It does not add marks; that is the producer's
job.

```python
import textprov

textprov.runs("f\U000E0101oo")
# [('ai', 'f\U000E0101'), (None, 'oo')]

textprov.to_html("f\U000E0101oo")
# '<span class="prov prov-ai" data-prov="ai">f\U000E0101</span>oo'
```

`runs` and `to_html` take `strip`, `merge_whitespace`, and (for `to_html`)
`class_prefix`. Pass `mapping=textprov.Mapping.load(path)` to use a registry
other than the copy vendored in this package.

The protocol is [SPEC.md](../SPEC.md); the registry is
[mapping.json](../mapping.json). `textprov/mapping.json` is a vendored copy and
the test suite fails if it drifts from the canonical file.

## Tests

```sh
python3 -m unittest discover -s tests -t .
```

The suite runs every case in [fixtures.json](../fixtures.json) and unit-tests
`cluster_end`, `to_html`, and `strip_marks` directly.
