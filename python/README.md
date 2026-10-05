# textprov — Python SDK demonstration

This working experiment encodes and decodes `human`/`ai` classifications using
variation selectors, plus a limited replacement-PUA mode. Standard library only;
Python 3.9+. Package identity and version describe executable code, not a
versioned proposal standard. It does not implement voice references or detect
who wrote text.

Run from `python/`, or install this checkout with `python3 -m pip install .`:

```python
import textprov

marked = textprov.mark("foo", state="ai")
assert marked == "f\U000E0101o\U000E0101o\U000E0101"
assert textprov.strip_marks(marked) == "foo"
textprov.runs(marked)  # [('ai', marked)]
textprov.to_html(marked)  # span carrying data-prov="ai"
textprov.mark_added("abc", "abXc")  # mark only inserted text
textprov.convert(marked, "vs", "pua")
```

`mark` and `mark_added` take `state` and `mode` (`vs` or `pua`). Only `human`
and `ai` are accepted classifications. `runs` and `to_html` accept `strip` and
`merge_whitespace`; HTML also accepts `class_prefix`. Core functions accept an
explicit `mapping=textprov.Mapping.load(path)`.

The PUA mode replaces eligible base characters, rather than appending metadata.
The decoder recognizes selectors by value and collides with genuine Unicode
variation sequences. Stripping arbitrary text can therefore destroy a glyph
selection. Read the [baseline limitations](../experiments/baseline/README.md),
[VS profile](../docs/encodings/vs.md), and
[additive-PUA candidate](../docs/encodings/additive-pua.md).

The proposal's [model](../docs/model.md) defines unattributed text as `Voice0`.
This experiment reports unmarked runs as `None`; its classification labels are
not implementations of nonzero voice references.

## Editing and workspace helpers

`textprov.editing` provides `remark`, `rewrite_edit`, `human_shingles`, and
`Ambiguous`. These pure string operations preserve matched old marks and mark
new text. Optional, explicitly supplied word shingles can label matching
quotations `human`; this heuristic does not establish authorship or semantic
faithfulness. `rewrite_edit` returns an exact replacement pair or `None`, and
raises `Ambiguous` when one replacement cannot safely select a unique result.

`textprov.workspace.Workspace(root)` provides explicit filesystem integration:
`record_prompt`, `prepare_write`, `prepare_edit`, `apply_edit`, `before_command`,
`after_command`, and `load_shingles`. Preparation returns text for the caller to
write; `apply_edit` writes directly. Prompt records live in `<root>/.textprov`
unless `state_dir` is supplied. Recording a prompt applies the experimental
human classification by policy; submission is not evidence of authorship.
These helpers remain available as experiments; this repository installs no
automatic marking hooks. Their Markdown scope, protected syntax, prompt matching,
and command snapshots are implementation policy rather than proposal requirements.

## CLI

```sh
python3 -m textprov -o marked.txt mark --ai draft.txt
python3 -m textprov mark-added old.txt new.txt
python3 -m textprov convert --from vs --to pua marked.txt
python3 -m textprov strip marked.txt
python3 -m textprov render marked.txt
python3 -m textprov inspect marked.txt
```

Installed packages also expose `textprov`. A file argument may be `-` for stdin;
output goes to stdout unless `-o` is supplied. UTF-8 line endings are preserved.
Legacy `SPEC_VERSION` is a baseline identifier, not a proposal version.

## Checks

From `python/`:

```sh
python3 -m unittest discover -s tests -t .
```

Checks cover shared [fixtures](../experiments/baseline/fixtures.json), vendored
mapping agreement, producer behavior, editing/workspace helpers, CLI output, and
Unicode 17.0.0 grapheme segmentation. See [UCD sources](../ucd/README.md).

MIT; see [LICENSE](LICENSE).
