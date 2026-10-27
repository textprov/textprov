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

## HTML display

`to_html` r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁 s󠄁p󠄁a󠄁n󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 i󠄁n󠄁j󠄁e󠄁c󠄁t󠄁i󠄁n󠄁g󠄁 s󠄁t󠄁y󠄁l󠄁e󠄁s󠄁.󠄁 `stylesheet()` r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁
p󠄁a󠄁c󠄁k󠄁a󠄁g󠄁e󠄁d󠄁 r󠄁e󠄁v󠄁e󠄁a󠄁l󠄁 C󠄁S󠄁S󠄁:󠄁 g󠄁r󠄁a󠄁d󠄁i󠄁e󠄁n󠄁t󠄁 m󠄁i󠄁s󠄁t󠄁 a󠄁n󠄁d󠄁 a󠄁 d󠄁o󠄁t󠄁t󠄁e󠄁d󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁 a󠄁t󠄁 8󠄁0󠄁%󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁-󠄁c󠄁o󠄁l󠄁o󠄁r󠄁
o󠄁p󠄁a󠄁c󠄁i󠄁t󠄁y󠄁.󠄁 T󠄁h󠄁e󠄁 w󠄁a󠄁v󠄁y󠄁/󠄁s󠄁a󠄁w󠄁t󠄁o󠄁o󠄁t󠄁h󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁l󠄁i󠄁n󠄁e󠄁 i󠄁s󠄁 d󠄁e󠄁f󠄁u󠄁n󠄁c󠄁t󠄁.󠄁

```python
from pathlib import Path
import textprov

Path("textprov.css").write_text(textprov.stylesheet(), encoding="utf-8")
html = textprov.to_html(textprov.mark("A draft", state="ai"))
```

S󠄁e󠄁r󠄁v󠄁e󠄁 t󠄁h󠄁a󠄁t󠄁 C󠄁S󠄁S󠄁 a󠄁s󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁i󠄁c󠄁 a󠄁s󠄁s󠄁e󠄁t󠄁 a󠄁n󠄁d󠄁 l󠄁i󠄁n󠄁k󠄁 i󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 H󠄁T󠄁M󠄁L󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁
s󠄁t󠄁y󠄁l󠄁e󠄁s󠄁h󠄁e󠄁e󠄁t󠄁 s󠄁h󠄁i󠄁p󠄁s󠄁 i󠄁n󠄁 a󠄁l󠄁l󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁 S󠄁D󠄁K󠄁s󠄁.󠄁 S󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁
[d󠄁i󠄁s󠄁p󠄁l󠄁a󠄁y󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁o󠄁n󠄁](../docs/development/provenance-display.md) f󠄁o󠄁r󠄁 n󠄁a󠄁t󠄁i󠄁v󠄁e󠄁
l󠄁i󠄁n󠄁k󠄁,󠄁 p󠄁r󠄁o󠄁o󠄁f󠄁i󠄁n󠄁g󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁s󠄁 u󠄁n󠄁a󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁e󠄁d󠄁.󠄁

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

Apache-2.0; see [LICENSE](LICENSE).

## Passage and exact display

```python
passages = textprov.to_html(marked_text, strip=True)  # default display="passage"
exact = textprov.to_html(marked_text, strip=True, display="exact", merge_whitespace=False)
```

T󠄁h󠄁e󠄁 C󠄁L󠄁I󠄁 a󠄁c󠄁c󠄁e󠄁p󠄁t󠄁s󠄁 `textprov render --display passage|exact FILE`.󠄁

P󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁 v󠄁i󠄁e󠄁w󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁.󠄁 I󠄁t󠄁 h󠄁i󠄁g󠄁h󠄁l󠄁i󠄁g󠄁h󠄁t󠄁s󠄁 a󠄁 p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁 **c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁i󠄁n󠄁g󠄁** r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁e󠄁d󠄁
m󠄁a󠄁r󠄁k󠄁s󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁s󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 t󠄁h󠄁e󠄁m󠄁;󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁 t󠄁h󠄁o󠄁s󠄁e󠄁
c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁s󠄁 a󠄁n󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁.󠄁 P󠄁l󠄁a󠄁i󠄁n󠄁 p󠄁a󠄁r󠄁a󠄁g󠄁r󠄁a󠄁p󠄁h󠄁s󠄁 s󠄁t󠄁a󠄁y󠄁 p󠄁l󠄁a󠄁i󠄁n󠄁.󠄁 A󠄁 p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁i󠄁n󠄁g󠄁 b󠄁o󠄁t󠄁h󠄁
b󠄁a󠄁s󠄁e󠄁l󠄁i󠄁n󠄁e󠄁 c󠄁l󠄁a󠄁s󠄁s󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 u󠄁s󠄁e󠄁s󠄁 a󠄁 n󠄁e󠄁u󠄁t󠄁r󠄁a󠄁l󠄁 m󠄁i󠄁x󠄁e󠄁d󠄁 t󠄁r󠄁e󠄁a󠄁t󠄁m󠄁e󠄁n󠄁t󠄁.󠄁 E󠄁x󠄁a󠄁c󠄁t󠄁 `[data-prov]`
s󠄁p󠄁a󠄁n󠄁s󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁 s󠄁e󠄁p󠄁a󠄁r󠄁a󠄁t󠄁e󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 d󠄁i󠄁s󠄁p󠄁l󠄁a󠄁y󠄁-󠄁o󠄁n󠄁l󠄁y󠄁 `[data-prov-passage]` w󠄁r󠄁a󠄁p󠄁p󠄁e󠄁r󠄁.󠄁

D󠄁O󠄁M󠄁 p󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁s󠄁 f󠄁o󠄁l󠄁l󠄁o󠄁w󠄁 p󠄁a󠄁r󠄁a󠄁g󠄁r󠄁a󠄁p󠄁h󠄁s󠄁,󠄁 h󠄁e󠄁a󠄁d󠄁i󠄁n󠄁g󠄁s󠄁,󠄁 l󠄁i󠄁s󠄁t󠄁 i󠄁t󠄁e󠄁m󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁 c󠄁e󠄁l󠄁l󠄁s󠄁 w󠄁h󠄁i󠄁l󠄁e󠄁
r󠄁e󠄁t󠄁a󠄁i󠄁n󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁l󠄁i󠄁n󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁t󠄁i󠄁n󠄁g󠄁.󠄁 P󠄁l󠄁a󠄁i󠄁n󠄁-󠄁t󠄁e󠄁x󠄁t󠄁 H󠄁T󠄁M󠄁L󠄁 e󠄁x󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 u󠄁s󠄁e󠄁 b󠄁l󠄁a󠄁n󠄁k󠄁 l󠄁i󠄁n󠄁e󠄁s󠄁 a󠄁s󠄁 p󠄁a󠄁r󠄁a󠄁g󠄁r󠄁a󠄁p󠄁h󠄁
b󠄁o󠄁u󠄁n󠄁d󠄁a󠄁r󠄁i󠄁e󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁 o󠄁p󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 s󠄁h󠄁a󠄁r󠄁e󠄁d󠄁 s󠄁t󠄁y󠄁l󠄁e󠄁s󠄁h󠄁e󠄁e󠄁t󠄁 p󠄁a󠄁i󠄁n󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 l󠄁a󠄁y󠄁e󠄁r󠄁 o󠄁n󠄁l󠄁y󠄁.󠄁
S󠄁w󠄁i󠄁t󠄁c󠄁h󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁 a󠄁n󠄁c󠄁e󠄁s󠄁t󠄁o󠄁r󠄁'󠄁s󠄁 `data-prov-display` b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 `passage` a󠄁n󠄁d󠄁 `exact` c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁s󠄁
p󠄁a󠄁i󠄁n󠄁t󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁i󠄁n󠄁g󠄁 t󠄁e󠄁x󠄁t󠄁 o󠄁r󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁 s󠄁p󠄁a󠄁n󠄁s󠄁.󠄁

T󠄁h󠄁e󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁'󠄁s󠄁 `runs()` A󠄁P󠄁I󠄁 i󠄁s󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁.󠄁 F󠄁o󠄁r󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁 w󠄁h󠄁i󠄁t󠄁e󠄁s󠄁p󠄁a󠄁c󠄁e󠄁 a󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 u󠄁s󠄁e󠄁
`merge_whitespace: false` (󠄁J󠄁a󠄁v󠄁a󠄁S󠄁c󠄁r󠄁i󠄁p󠄁t󠄁/󠄁R󠄁u󠄁b󠄁y󠄁)󠄁 o󠄁r󠄁 `merge_whitespace=False` (󠄁P󠄁y󠄁t󠄁h󠄁o󠄁n󠄁)󠄁.󠄁
P󠄁a󠄁s󠄁s󠄁a󠄁g󠄁e󠄁 m󠄁e󠄁t󠄁a󠄁d󠄁a󠄁t󠄁a󠄁 a󠄁l󠄁w󠄁a󠄁y󠄁s󠄁 k󠄁e󠄁e󠄁p󠄁s󠄁 w󠄁h󠄁i󠄁t󠄁e󠄁s󠄁p󠄁a󠄁c󠄁e󠄁 u󠄁n󠄁a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁;󠄁 t󠄁h󠄁e󠄁 l󠄁e󠄁g󠄁a󠄁c󠄁y󠄁 w󠄁h󠄁i󠄁t󠄁e󠄁s󠄁p󠄁a󠄁c󠄁e󠄁-󠄁m󠄁e󠄁r󠄁g󠄁e󠄁
o󠄁p󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁p󠄁p󠄁l󠄁i󠄁e󠄁s󠄁 t󠄁o󠄁 e󠄁x󠄁p󠄁l󠄁i󠄁c󠄁i󠄁t󠄁l󠄁y󠄁 r󠄁e󠄁q󠄁u󠄁e󠄁s󠄁t󠄁e󠄁d󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁 H󠄁T󠄁M󠄁L󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁.󠄁
