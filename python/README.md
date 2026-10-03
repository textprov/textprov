# python/README.md

---

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
`"pua"`). These core functions take `mapping=textprov.Mapping.load(path)` to use a
registry other than the copy vendored in this package.

## Editing API

The reusable prose-marking APIs live in the Python package. Import editing
helpers from `textprov.editing` and
filesystem policy from `textprov.workspace`; integrations do not need to import
`.claude/hooks/textprov_hook.py`.

`textprov.editing` exposes pure functions. They operate on supplied strings and
options, without automatic disk or environment access. Omitting `shingles`
means **no prompt matching**, not an implicit read of a prompt log.

```python
import textprov
from textprov.editing import Ambiguous, human_shingles, remark, rewrite_edit

old_raw = textprov.mark("Keep this paragraph.", state="human") + "\n"
new_raw = "Keep this paragraph.\nAn agent added this paragraph.\n"
marked = remark(old_raw, new_raw)
# The first paragraph keeps its human marks; the addition is marked ai.

prompt = textprov.mark("Please keep these exact five words", state="human")
shingles = human_shingles([prompt], min_words=5)
quoted = remark("", "Please keep these exact five words", shingles=shingles)
# The supplied human word sequences match, so the addition is marked human.

try:
    edit = rewrite_edit(marked, "An agent added", "An agent revised")
except Ambiguous as error:
    print(f"Edit refused: {error}")
else:
    if edit is not None:
        exact_old, marked_new = edit
        # Pass this pair to the editor's exact-string replacement operation.
```

- `remark(old_raw, new_raw, markdown=True, carry=True, shingles=None, min_words=5)`
  returns the new text with additions marked. By default it protects Markdown
  syntax and code, and carries marks from unchanged old text even when the new
  text omits them. Set `markdown=False` for plain text. Set `carry=False` to keep
  unchanged portions as supplied in `new_raw`, rather than restoring old marks.
- `rewrite_edit(raw, old_string, new_string, replace_all=False, shingles=None,
  min_words=5)` returns an `(exact_old, marked_new)` tuple for editing a marked
  Markdown document. It finds the old text with marks ignored, then returns the
  marked strings needed for an exact replacement. It returns `None` when there
  is no usable match, leaving missing-match reporting to the caller.
- `human_shingles(marked_texts, min_words=5)` builds a set of consecutive word
  sequences from runs marked `human` in the supplied texts. Unmarked and
  non-human runs do not supply matches. Pass the set explicitly to `remark` or
  `rewrite_edit`, with the same `min_words` value used to build it.
- `Ambiguous` is raised when a single edit matches more than one location, or
  when `replace_all=True` would require different replacements because the
  occurrences have different marks or Markdown contexts. Add surrounding
  context or edit the occurrences separately; do not silently choose one.

## Workspace API

`Workspace(root, *, state_dir=None, human_min_words=5)` owns filesystem and Git
policy, prompt persistence, and command snapshots. The root is explicit;
relative file paths resolve under it, not under the caller's current working
directory. Configuration is passed as constructor arguments, not read from
hook environment variables.

```python
from pathlib import Path
from textprov.editing import Ambiguous
from textprov.workspace import Workspace

root = Path("/path/to/repository")
workspace = Workspace(root, human_min_words=5)
workspace.record_prompt("Please keep these exact five words", session="session-1")

content = workspace.prepare_write(
    "docs/draft.md", "Please keep these exact five words\nAn agent addition.\n"
)
if content is not None:
    # Give content to your write tool; prepare_write does not write the file.
    print(content)

try:
    edit = workspace.prepare_edit("docs/draft.md", "old phrase", "new phrase")
except Ambiguous as error:
    print(f"Edit refused: {error}")
else:
    if edit is not None:
        exact_old, marked_new = edit
        # Give this pair to your edit tool; prepare_edit does not apply it.

shingles = workspace.load_shingles()
# This is an explicit disk read, unlike textprov.editing.human_shingles().
```

- `record_prompt(prompt, session=None)` records a prompt in the workspace's
  prompt log, marking its text `human` while retaining existing provenance.
  Only submit prompts your integration intends to treat as human input.
- `prepare_write(path, content)` reads the previous file and returns marked
  content, or `None` if the path is out of scope. The caller performs the write.
- `prepare_edit(path, old_string, new_string, replace_all=False)` reads the file
  and returns an exact replacement tuple, or `None` if the path is out of scope
  or no edit can be prepared. It propagates `Ambiguous`; the caller must refuse
  or disambiguate the edit.
- `apply_edit(path, old_string, new_string, replace_all=False)` p󠄁r󠄁e󠄁p󠄁a󠄁r󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁
  s󠄁a󠄁m󠄁e󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁m󠄁e󠄁n󠄁t󠄁 a󠄁n󠄁d󠄁 w󠄁r󠄁i󠄁t󠄁e󠄁s󠄁 i󠄁t󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁,󠄁 f󠄁o󠄁r󠄁 c󠄁a󠄁l󠄁l󠄁e󠄁r󠄁s󠄁 w󠄁h󠄁o󠄁s󠄁e󠄁 e󠄁d󠄁i󠄁t󠄁 t󠄁o󠄁o󠄁l󠄁
  c󠄁a󠄁n󠄁n󠄁o󠄁t󠄁 t󠄁a󠄁k󠄁e󠄁 a󠄁 r󠄁e󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁 i󠄁n󠄁p󠄁u󠄁t󠄁.󠄁 I󠄁t󠄁 r󠄁e󠄁t󠄁u󠄁r󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁 o󠄁f󠄁 p󠄁l󠄁a󠄁c󠄁e󠄁s󠄁 r󠄁e󠄁p󠄁l󠄁a󠄁c󠄁e󠄁d󠄁,󠄁 0󠄁
  i󠄁f󠄁 t󠄁h󠄁e󠄁 p󠄁a󠄁t󠄁h󠄁 i󠄁s󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁 o󠄁r󠄁 `old_string` i󠄁s󠄁 a󠄁b󠄁s󠄁e󠄁n󠄁t󠄁,󠄁 a󠄁n󠄁d󠄁 p󠄁r󠄁o󠄁p󠄁a󠄁g󠄁a󠄁t󠄁e󠄁s󠄁
  `Ambiguous` w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁.󠄁
- `has_marks(path)` r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 w󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 a󠄁n󠄁 i󠄁n󠄁-󠄁s󠄁c󠄁o󠄁p󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁s󠄁 p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁.󠄁
- `before_command(command, operation_id)` snapshots scoped files before an
  externally executed command. `after_command(operation_id)` compares the
  snapshot with the resulting files and writes provenance marks for additions.
  Use the same operation ID for both calls and pair them on command failure as
  well as success. IDs are hashed for snapshot filenames so provider-specific
  separators do not cause collisions. Neither method executes the command.
  Finish in-flight hooked commands before upgrading from the old hook;
  snapshots using its previous filenames are not migrated.
- `load_shingles()` reads the prompt log and builds the matching word sequences
  used by workspace preparation and command marking.

The defaults retain the repository's dogfooding policy:

- State lives under `<root>/.textprov` unless `state_dir` is supplied. It includes
  `prompts.jsonl` and command snapshots; recorded prompts are stored locally.
- Scope is `.md` and `.markdown` files under the root, excluding `.git/`,
  `docs/examples/`, `site/public/`, `site/dist/`, `node_modules/`, and Git-ignored
  paths. Within Markdown, protected syntax and code stay unmarked.
- Prompt matching uses the latest 300 prompt entries and a five-word minimum
  by default. Snapshots older than 24 hours are cleaned up.
- Commands that move the Git working tree are skipped. A changed `HEAD` is
  accepted only for a single new commit on the previous head, not an amend or
  multiple commits. Moved or copied files are not treated as new writing.
  Marking after a command that edits and commits leaves marks in the working
  tree; it does not rewrite that commit.

## Integration boundary

The Claude hook is an adapter only: it maps Claude events, response envelopes,
operation IDs, and environment configuration to `Workspace` calls. It selects
an explicit repository root, translates `TEXTPROV_HUMAN_MIN_WORDS` into
`human_min_words`, and handles `TEXTPROV_HOOK=off` itself. Those environment
variables do not configure direct package calls.

`UserPromptSubmit` maps to `record_prompt`; Write and Edit pre-tool events map
to `prepare_write` and `prepare_edit`. Bash pre-tool events map to
`before_command`, and post-tool events, including failures, map to
`after_command`. The adapter converts prepared values into updated tool inputs
and `Ambiguous` into a denial. C󠄁l󠄁a󠄁u󠄁d󠄁e󠄁 C󠄁o󠄁d󠄁e󠄁 v󠄁a󠄁l󠄁i󠄁d󠄁a󠄁t󠄁e󠄁s󠄁 a󠄁n󠄁 E󠄁d󠄁i󠄁t󠄁 a󠄁g󠄁a󠄁i󠄁n󠄁s󠄁t󠄁 t󠄁h󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁
b󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 a󠄁n󠄁y󠄁 h󠄁o󠄁o󠄁k󠄁 r󠄁u󠄁n󠄁s󠄁,󠄁 s󠄁o󠄁 a󠄁n󠄁 e󠄁d󠄁i󠄁t󠄁 t󠄁o󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 r󠄁e󠄁a󠄁c󠄁h󠄁e󠄁s󠄁 `prepare_edit`.󠄁
F󠄁o󠄁r󠄁 t󠄁h󠄁o󠄁s󠄁e󠄁 t󠄁h󠄁e󠄁 a󠄁d󠄁a󠄁p󠄁t󠄁e󠄁r󠄁 h󠄁a󠄁s󠄁 a󠄁n󠄁 `edit` c󠄁o󠄁m󠄁m󠄁a󠄁n󠄁d󠄁 t󠄁h󠄁a󠄁t󠄁 c󠄁a󠄁l󠄁l󠄁s󠄁 `apply_edit`,󠄁 a󠄁n󠄁d󠄁 i󠄁t󠄁
a󠄁n󠄁s󠄁w󠄁e󠄁r󠄁s󠄁 `SessionStart` a󠄁n󠄁d󠄁 R󠄁e󠄁a󠄁d󠄁 e󠄁v󠄁e󠄁n󠄁t󠄁s󠄁 o󠄁n󠄁 f󠄁i󠄁l󠄁e󠄁s󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁 `has_marks` i󠄁s󠄁 t󠄁r󠄁u󠄁e󠄁 w󠄁i󠄁t󠄁h󠄁
a󠄁 n󠄁o󠄁t󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁 a󠄁g󠄁e󠄁n󠄁t󠄁 t󠄁o󠄁 t󠄁h󠄁a󠄁t󠄁 c󠄁o󠄁m󠄁m󠄁a󠄁n󠄁d󠄁.󠄁 Workspace owns the reusable policy; editing
helpers own string transformations. Other editors and agents can provide their
own adapters without depending on Claude's event format.

See the [dogfooding guide](../docs/development/dogfooding.md) for this
repository's hook setup and operational limits.

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

Run from `python/`:

```sh
python3 -m unittest discover -s tests -t .
```

The suite runs every decoder, producer, and convert case in
[fixtures.json](../fixtures.json), tests the producer properties from
[SPEC.md](../SPEC.md) directly rather than only through recorded outputs, and
r󠄁u󠄁n󠄁s󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 l󠄁i󠄁n󠄁e󠄁 o󠄁f󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁'󠄁s󠄁 `GraphemeBreakTest.txt` t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 `segments`,󠄁 a󠄁n󠄁d󠄁
u󠄁n󠄁i󠄁t󠄁-󠄁t󠄁e󠄁s󠄁t󠄁s󠄁 `to_html`, `strip_marks`, and the CLI.

As part of the extraction, editing, workspace, and Claude-adapter tests move
from `.claude/hooks/` into `python/tests/`. The same discovery command includes
them in the existing Python job in the
[conformance workflow](../.github/workflows/conformance.yml); there is no
separate hook-test command.
