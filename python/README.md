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

## Shared Chronicle and supplied attribution

The [Chronicle guide](CHRONICLE.md) documents local observations, claims and query
APIs. [Shared matching](ATTRIBUTION.md) defines original-coordinate policies.
The [policy guide](POLICY.md) covers explicit supplied-claim transfers, durable
evidence, experimental export and controlled exact Markdown edits. These APIs
never infer authorship from a prompt, channel or matching passage.

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
These helpers remain available as e󠄁x󠄁p󠄁e󠄁r󠄁i󠄁m󠄁e󠄁n󠄁t󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁i󠄁r󠄁 M󠄁a󠄁r󠄁k󠄁d󠄁o󠄁w󠄁n󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁,󠄁 p󠄁r󠄁o󠄁t󠄁e󠄁c󠄁t󠄁e󠄁d󠄁
s󠄁y󠄁n󠄁t󠄁a󠄁x󠄁,󠄁 p󠄁r󠄁o󠄁m󠄁p󠄁t󠄁 m󠄁a󠄁t󠄁c󠄁h󠄁i󠄁n󠄁g󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁m󠄁m󠄁a󠄁n󠄁d󠄁 s󠄁n󠄁a󠄁p󠄁s󠄁h󠄁o󠄁t󠄁s󠄁 a󠄁r󠄁e󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁 r󠄁a󠄁t󠄁h󠄁e󠄁r󠄁
t󠄁h󠄁a󠄁n󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁.󠄁 H󠄁o󠄁s󠄁t󠄁 p󠄁l󠄁u󠄁g󠄁i󠄁n󠄁s󠄁 c󠄁a󠄁n󠄁 a󠄁p󠄁p󠄁l󠄁y󠄁 t󠄁h󠄁e󠄁 s󠄁i󠄁m󠄁p󠄁l󠄁e󠄁r󠄁 a󠄁u󠄁t󠄁o󠄁m󠄁a󠄁t󠄁i󠄁c󠄁 p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁
b󠄁e󠄁l󠄁o󠄁w󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 p󠄁r󠄁o󠄁m󠄁p󠄁t󠄁 m󠄁a󠄁t󠄁c󠄁h󠄁i󠄁n󠄁g󠄁 o󠄁r󠄁 m󠄁a󠄁n󠄁u󠄁a󠄁l󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁s󠄁.󠄁

## Chat and document marking

T󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 p󠄁l󠄁u󠄁g󠄁i󠄁n󠄁 p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁 c󠄁l󠄁a󠄁s󠄁s󠄁i󠄁f󠄁i󠄁e󠄁s󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 u󠄁s󠄁e󠄁r󠄁 c󠄁h󠄁a󠄁t󠄁 a󠄁s󠄁 h󠄁u󠄁m󠄁a󠄁n󠄁 a󠄁n󠄁d󠄁 a󠄁s󠄁s󠄁i󠄁s󠄁t󠄁a󠄁n󠄁t󠄁
c󠄁h󠄁a󠄁t󠄁 a󠄁s󠄁 A󠄁I󠄁.󠄁 E󠄁x󠄁i󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 t󠄁a󠄁k󠄁e󠄁 p󠄁r󠄁e󠄁c󠄁e󠄁d󠄁e󠄁n󠄁c󠄁e󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 t󠄁e󠄁x󠄁t󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁d󠄁 f󠄁r󠄁o󠄁m󠄁 a󠄁n󠄁o󠄁t󠄁h󠄁e󠄁r󠄁
m󠄁e󠄁s󠄁s󠄁a󠄁g󠄁e󠄁.󠄁 C󠄁h󠄁a󠄁t󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 a󠄁p󠄁p󠄁l󠄁y󠄁 t󠄁o󠄁 a󠄁l󠄁l󠄁 e󠄁l󠄁i󠄁g󠄁i󠄁b󠄁l󠄁e󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁s󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 c󠄁o󠄁d󠄁e󠄁;󠄁 t󠄁h󠄁e󠄁 p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁
d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 i󠄁n󠄁f󠄁e󠄁r󠄁 w󠄁h󠄁o󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁a󠄁l󠄁l󠄁y󠄁 w󠄁r󠄁o󠄁t󠄁e󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁

```python
from textprov import mark_chat, mark_document, mark_document_edit

human_message = mark_chat("My message", "user")
ai_message = mark_chat("An answer", "assistant")
new_draft = mark_document("New prose.")
edited_draft = mark_document_edit(previous_raw_text, proposed_text)
```

D󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 e󠄁d󠄁i󠄁t󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁 A󠄁I󠄁 a󠄁d󠄁d󠄁i󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁,󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁 e󠄁x󠄁i󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 o󠄁n󠄁
u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 e󠄁v󠄁e󠄁n󠄁 w󠄁h󠄁e󠄁n󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 o󠄁m󠄁i󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁m󠄁,󠄁 a󠄁n󠄁d󠄁 p󠄁r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁
u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 e󠄁d󠄁i󠄁t󠄁o󠄁r󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁y󠄁 u󠄁s󠄁e󠄁 t󠄁h󠄁e󠄁 e󠄁x󠄁i󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 w󠄁h󠄁o󠄁l󠄁e󠄁-󠄁l󠄁i󠄁n󠄁e󠄁/󠄁w󠄁h󠄁o󠄁l󠄁e󠄁-󠄁w󠄁o󠄁r󠄁d󠄁 a󠄁l󠄁i󠄁g󠄁n󠄁m󠄁e󠄁n󠄁t󠄁 a󠄁n󠄁d󠄁
c󠄁o󠄁n󠄁s󠄁e󠄁r󠄁v󠄁a󠄁t󠄁i󠄁v󠄁e󠄁 M󠄁a󠄁r󠄁k󠄁d󠄁o󠄁w󠄁n󠄁 p󠄁r󠄁o󠄁t󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 s󠄁o󠄁 c󠄁o󠄁d󠄁e󠄁,󠄁 d󠄁e󠄁s󠄁t󠄁i󠄁n󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 p󠄁r󠄁o󠄁t󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 s󠄁y󠄁n󠄁t󠄁a󠄁x󠄁
r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁 e󠄁x󠄁e󠄁c󠄁u󠄁t󠄁a󠄁b󠄁l󠄁e󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁r󠄁s󠄁e󠄁a󠄁b󠄁l󠄁e󠄁.󠄁 F󠄁o󠄁r󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁 n󠄁a󠄁t󠄁i󠄁v󠄁e󠄁-󠄁t󠄁o󠄁o󠄁l󠄁 e󠄁d󠄁i󠄁t󠄁s󠄁 a󠄁g󠄁a󠄁i󠄁n󠄁s󠄁t󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁
f󠄁i󠄁l󠄁e󠄁s󠄁,󠄁 `textprov.editing.rewrite_edit` r󠄁e󠄁s󠄁o󠄁l󠄁v󠄁e󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁r󠄁-󠄁i󠄁n󠄁s󠄁e󠄁n󠄁s󠄁i󠄁t󠄁i󠄁v󠄁e󠄁 a󠄁n󠄁c󠄁h󠄁o󠄁r󠄁s󠄁 a󠄁n󠄁d󠄁
r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁 a󠄁n󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁 r󠄁a󠄁w󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁m󠄁e󠄁n󠄁t󠄁 p󠄁a󠄁i󠄁r󠄁.󠄁 A󠄁m󠄁b󠄁i󠄁g󠄁u󠄁o󠄁u󠄁s󠄁 m󠄁a󠄁t󠄁c󠄁h󠄁e󠄁s󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁 m󠄁o󠄁r󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁e󠄁x󠄁t󠄁.󠄁
O󠄁r󠄁d󠄁i󠄁n󠄁a󠄁r󠄁y󠄁 e󠄁d󠄁i󠄁t󠄁o󠄁r󠄁s󠄁 a󠄁r󠄁e󠄁 n󠄁o󠄁t󠄁 w󠄁a󠄁t󠄁c󠄁h󠄁e󠄁d󠄁 o󠄁r󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁.󠄁

M󠄁a󠄁r󠄁k󠄁s󠄁 a󠄁r󠄁e󠄁 a󠄁c󠄁t󠄁u󠄁a󠄁l󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁s󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁 p󠄁a󠄁y󠄁l󠄁o󠄁a󠄁d󠄁.󠄁 U󠄁T󠄁F󠄁-󠄁8󠄁 a󠄁n󠄁d󠄁 J󠄁S󠄁O󠄁N󠄁
r󠄁o󠄁u󠄁n󠄁d󠄁t󠄁r󠄁i󠄁p󠄁s󠄁 p󠄁r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁;󠄁 c󠄁o󠄁p󠄁y󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁t󠄁o󠄁 a󠄁 d󠄁e󠄁s󠄁t󠄁i󠄁n󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 t󠄁h󠄁a󠄁t󠄁 r󠄁e󠄁m󠄁o󠄁v󠄁e󠄁s󠄁 v󠄁a󠄁r󠄁i󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 c󠄁a󠄁n󠄁n󠄁o󠄁t󠄁 p󠄁r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁.󠄁 C󠄁l󠄁i󠄁p󠄁b󠄁o󠄁a󠄁r󠄁d󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁e󠄁r󠄁 b󠄁e󠄁h󠄁a󠄁v󠄁i󠄁o󠄁r󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁
n󠄁e󠄁e󠄁d󠄁s󠄁 v󠄁e󠄁r󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 i󠄁n󠄁 e󠄁a󠄁c󠄁h󠄁 h󠄁o󠄁s󠄁t󠄁.󠄁

A󠄁d󠄁a󠄁p󠄁t󠄁e󠄁r󠄁s󠄁 c󠄁a󠄁n󠄁 c󠄁a󠄁l󠄁l󠄁 `python -m textprov.marking` w󠄁i󠄁t󠄁h󠄁 o󠄁n󠄁e󠄁 J󠄁S󠄁O󠄁N󠄁 r󠄁e󠄁q󠄁u󠄁e󠄁s󠄁t󠄁 o󠄁n󠄁 s󠄁t󠄁d󠄁i󠄁n󠄁:󠄁
`{"operation":"mark-chat","text":"Hello","role":"user"}` o󠄁r󠄁
`{"operation":"mark-document","old_text":"Old prose","text":"New prose"}`.󠄁
T󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁p󠄁o󠄁n󠄁s󠄁e󠄁 i󠄁s󠄁 `{"text":"…"}`.󠄁 `old_text` d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁s󠄁 t󠄁o󠄁 e󠄁m󠄁p󠄁t󠄁y󠄁 f󠄁o󠄁r󠄁 n󠄁e󠄁w󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁s󠄁.󠄁

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
