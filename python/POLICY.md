# Supplied attribution, export and controlled prose edits

Core 0.1.5 adds a policy over Chronicle observations. A person or application
supplies source claims, selects a passage candidate, and accepts a transfer.
The policy records that decision and its evidence. Channels, host IDs, text
matches and approval never establish authorship.

## Select and transfer supplied claims

Use `list_observations(provider, session_id, agent_id=None, cross_agent=False,
limit=100, before_id=None)` to discover observations without reading SQLite.
Results are newest first and metadata only. Pass `next_before_id` as `before_id`
to continue. The default selects the agentless scope; cross-agent access remains
within one provider and session.

Create explicit source claims with `claim()`. Inspect both observations and call
`match()` with one named comparison policy. Select a candidate index and the
source claims to carry. The JSON bridge accepts:

```json
{
  "operation": "transfer",
  "source_id": "<source observation UUID>",
  "target_id": "<target observation UUID>",
  "candidate_index": 0,
  "source_claim_ids": ["<existing source claim ID>"],
  "source_hash": "<original source SHA-256>",
  "target_hash": "<original target SHA-256>",
  "comparison_policy": "common-indent-v1",
  "partial": true,
  "min_match_chars": 16,
  "cross_agent": false,
  "policy": "supplied-claims-v1"
}
```

`transfer()` recomputes matching and validates the original hashes. Selection is
required even when only one candidate exists. Repeated candidates can be chosen
explicitly. Source claims must belong to the source observation and cover whole
mapped graphemes. Multiple supplied voices remain separate; unclaimed text and
indentation removed for comparison receive no claim. The operation refuses
conflicting source claims, overlapping selected claims and target voice conflicts.

Accepted passage evidence and all derived claims commit in one transaction.
`inspect()` shows the selected relationship, its comparison options, supporting
source claims and derived claim IDs. Evidence remains after raw-cache expiry;
an identical accepted transfer stays idempotent. A new transfer needs retained
content. No candidate list or extra raw-payload archive is persisted.

## Resolve and export

`resolve(observation_id, content_hash=None)` returns a partition of the original
scalar range. Each range contains its voice context, ID, definition and supporting
claim IDs. Unknown ranges have null voice fields. Compatible overlapping claims
can resolve together; competing voices or definitions cause a refusal. Resolution
works after text expiry because it reads retained claim metadata.

Portable export requires retained text and an explicit projection:

```json
{
  "operation": "export",
  "observation_id": "<observation UUID>",
  "content_hash": "<original observation SHA-256>",
  "profile": "experimental-vs-classification-v1",
  "allow_lossy": true,
  "markdown": true,
  "voice_states": [
    {"voice_context": "example", "voice_id": "writer-a", "state": "human"},
    {"voice_context": "example", "voice_id": "writer-b", "state": "ai"}
  ]
}
```

Every resolved voice needs a supplied `human` or `ai` mapping. This experimental
profile loses identities, contexts and claim evidence in the marked text. It is
not a rich voice encoding. Unknown ranges receive no new marks. Markdown syntax,
code and destinations are protected by default. Existing selectors and PUA remain
verbatim; the exporter never runs a general stripping operation on source text.

Keep the full result beside any exported text. It records observation identity,
source completeness, resolved voice definitions, source/output hashes,
the explicit projection, unencoded ranges and the exact inserted-selector
positions. `textprov.export.restore(report)` verifies both hashes and removes only
those inserted selectors, preserving genuine Unicode variation sequences such
as `U+8FBB U+E0100`. The companion is required for this exact recovery; arbitrary
third-party stripping still has the baseline's Unicode collision limitation.

## Opt-in edits in a controlled handoff

`textprov.prose.ProseEditor(root).edit()` prepares an exact replacement, or applies
it when `apply=True`. Calling this operation explicitly opts in; no hook, watcher
or shell reconciliation activates it automatically. The root must be the chosen
Git worktree, the path must be eligible Markdown, and `old_text` must be the exact
raw substring, including any existing marks. Pass the complete file's original
SHA-256 and a verified export result as `replacement`.

```python
from textprov.prose import ProseEditor, content_hash

# exported is the complete result of chronicle.export(...).
prepared = ProseEditor(root).edit(
    "draft.md",
    expected_content_hash=content_hash(original_raw_text),
    old_text="the exact old phrase",
    replacement=exported,
    apply=False,
)
```

Preparation returns an exact native-style `old_string`/`new_string` pair and the
full-file hash precondition. A native adapter must preserve that precondition and
its host's permission checks. A preparation result alone does not make a later
host tool atomic.

The explicit apply path serializes cooperating writers per worktree, rechecks
file content and identity, writes a temporary sibling and replaces atomically.
It preserves file mode, raw CRLF and unchanged bytes. Symlinks, hard links,
out-of-scope/generated files, stale content, ambiguous occurrences, protected
syntax, split graphemes and replacements joining retained graphemes are refused.
`replace_all=True` explicitly selects all exact occurrences.

External editors do not honor this lock. Use a controlled edit handoff and do not
claim arbitrary concurrent-writer safety. This operation edits existing prose;
whole-file creation, native patch rewriting and shell reconciliation are not
enabled by these APIs. Existing experimental workspace helpers remain separate.

The JSON entry point is `python -m textprov.prose --root <worktree>`. It reads the
same `edit()` keyword arguments, including `path`, from stdin and returns JSON.
Preparation is the default; only an explicit `"apply": true` writes the target.

## Validation boundaries

Core fixtures cover transfer selection, multiple voices, original Unicode ranges,
conflicts, rollback, expiry, scoped listing, export recovery and controlled files.
Adapter fixtures and subprocess tests are separate from real installed-host
trials. Trials run fixed builds, keep code unchanged, and record status, versions,
database observations, findings and untested behavior outside both repositories.
