# TextProv for Codex (local prototype)

This plugin captures supported Codex hook payloads into the shared Python
Chronicle. It provides metadata inspection, passage matching and explicit claims.
It does not assign authorship from channels or change workspace files.

Version: **0.1.0**, requiring the local **TextProv core 0.1.5** and Python 3.9+ on
macOS or Linux. Only local distribution is intended. The package contains a
portable root manifest, hooks, a thin Python adapter and an inspection skill.

## Prepare the Python runtime

Install the core into the Python interpreter that will execute hooks. From the
TextProv repository root, one example is:

```sh
python3 -m venv /absolute/private/path/textprov-venv
/absolute/private/path/textprov-venv/bin/python -m pip install ./python
```

Make that interpreter the host's `python3`, or launch the host with
`TEXTPROV_PYTHON=/absolute/private/path/textprov-venv/bin/python` in its
environment. `TEXTPROV_PYTHON` is one executable path, not a shell command. The
wrapper quotes paths containing spaces. The plugin imports the installed core;
it does not depend on the source checkout or silently choose another checkout.
After updating core, reinstall its package in that interpreter.

For development fixture tests, `PYTHONPATH=python` intentionally selects the
working source package. This is separate from installed-plugin verification.

## Load and trust locally

The [official plugin packaging guide](https://developers.openai.com/plugins/build/plugins)
describes local marketplaces and the portable `plugin.json` entry point. For a
repository marketplace, merge this entry into the repository's
`.agents/plugins/marketplace.json`, resolving `source.path` from the repository
root:

```json
{
  "name": "textprov-local",
  "plugins": [
    {
      "name": "textprov",
      "source": {"source": "local", "path": "./plugins/codex"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Productivity"
    }
  ]
}
```

Restart the desktop app, find TextProv in the local marketplace, and install it
for the intended project. Alternatively, a personal marketplace can point to an
absolute local copy. Preserve any other marketplace entries when adding this
one. This repository does not install that marketplace or modify host settings.

Installing or enabling a plugin does not trust its hooks. Review and trust the
current hook definition through the host's hooks review interface. Inspect
[`hooks/hooks.json`](hooks/hooks.json) and [`bin/textprov`](bin/textprov) first:
all handlers invoke the same local adapter and emit `{}`. They provide no tool
rewrite, allow/deny decision or additional model context. A changed hook
definition needs host review again. The official [hooks reference](https://learn.chatgpt.com/docs/hooks)
defines the payload fields, matching, trust and coverage used here.

After changing the plugin, update the source folder registered in the marketplace
and restart the app to refresh its installed copy. The package alone does not
prove that the installed host discovered or trusted it.

## Capture and storage

| Event | Captured observation | Identity and coverage |
| --- | --- | --- |
| `UserPromptSubmit` | Original `prompt` string | Native session and turn ID; changed payload under the same identity is a reported conflict |
| `PreToolUse` | Entire `tool_input`; an additional exact `command` block for documented `Bash`/`apply_patch` arguments | Native turn and tool-call ID; JSON-string arguments remain intact alongside the decoded command |
| `PostToolUse` | Observed executed input/command and entire `tool_response`, preserving structured values as explicit JSON | Joins the pre-call by native tool-call ID; preserves input changed by other hooks; local results use model visibility, MCP results use structured visibility |
| `Stop` | Latest `last_assistant_message` string | First stop per native turn; continued stops lack a documented per-message identity and produce a gap |
| `SubagentStop` | Latest subagent message | Parent native session/turn plus child agent scope; continued stops produce a gap |

Strings retain their exact Unicode and line endings. Structured values are
serialized as compact JSON with sorted keys; JSON object formatting is not
claimed as original host bytes. JSON `null` tool input/output remains a captured
structured value. A missing output field or null assistant message becomes an
`unobserved` record and a diagnostic; an empty string remains observed empty
content. Tool responses and latest assistant messages are conservatively
`partial`: the hook does not guarantee complete output or a complete turn.
An incomplete source cannot be used for a full passage match by the core.

The host supplies `PLUGIN_DATA`. State lives at:

```text
PLUGIN_DATA/
  diagnostics.jsonl                   # errors without a trustworthy scope
  projects/<sha256-canonical-cwd>/
    chronicle.sqlite                  # core owns this format
    adapter.lock                      # process coordination
    sessions/<sha256-native-session>/
      session.json                    # native session ID for discovery
      diagnostics.jsonl               # gap/error codes, no raw payloads
```

The canonical absolute session `cwd` defines the project namespace. Different
worktrees or working directories use different databases; the adapter does not
guess a Git root. Core scopes observations by provider, session and optional
agent ID. The CLI requires a session for individual observations and checks
scope before inspection, matching or claims. `--cross-agent` stays within the
chosen provider/session.

A project process lock covers translation and database access, including first
creation. Duplicate deliveries reuse stable native-ID keys through core
`observe()`. Equal text with different IDs remains separate. Missing turn or
tool/child-agent IDs produce durable gap codes, without inventing content-based
identity. No capture sequence is allocated from a maximum or process clock.

Core defaults retain at most 1 MiB of raw UTF-8 content for at most one hour
across the project. Metadata and explicit claims persist; retries do not renew
cache retention. Expiry is lazy and is not a secure-erasure guarantee. The
adapter does not archive transcripts or full hook envelopes. Diagnostics retain
only timestamps, event/field names and fixed codes; they contain no prompts,
commands, tool outputs or raw exception messages. Status includes failures from
earlier processes and unscoped malformed payloads.

The adapter rejects hook input exceeding 4 MiB. This is an adapter input bound,
independent of the host's model-visible hook-output spill threshold. Errors
return a nonzero exit code and a safe diagnostic on stderr; successful hooks
return `{}`. These hooks do not enforce policy or block tool execution.

## Inspect explicitly

Outside the hook environment, provide the actual plugin data directory through
`--data` or `PLUGIN_DATA`. Use the same absolute project path as the captured
session. All CLI results are JSON:

```sh
plugin=/absolute/path/to/installed/textprov
data=/absolute/path/to/plugin-data
project=/absolute/path/to/session-project

"$plugin/bin/textprov" --data "$data" status --project "$project"
"$plugin/bin/textprov" --data "$data" list --project "$project" --session NATIVE_SESSION_ID
"$plugin/bin/textprov" --data "$data" inspect OBSERVATION_ID --project "$project" --session NATIVE_SESSION_ID
"$plugin/bin/textprov" --data "$data" match SOURCE_ID TARGET_ID --project "$project" --session NATIVE_SESSION_ID --policy line-endings-v1 --partial --min-chars 16
```

`status` reports versions, database/cache totals, observed native session IDs,
persistent diagnostics and limitations. `list` returns metadata and an exclusive
`next_before_id` cursor; pass it back as `--before ID`. Use `--limit 1..1000`.
Select `--agent ID` for a child or `--cross-agent` deliberately. Inspection
returns relationships, completeness and content availability without raw text.

Matching forwards `--policy` (including `exact-v1`, `line-endings-v1` and
`common-indent-v1`), `--partial`, `--min-chars` and `--cross-agent` to the shared
core. It does not create claims. To record a user-supplied attribution:

```sh
"$plugin/bin/textprov" --data "$data" claim TARGET_ID \
  --project "$project" --session NATIVE_SESSION_ID \
  --start 0 --end 12 --content-hash EXACT_OBSERVATION_HASH \
  --voice-context local-authors --voice-id supplied-author \
  --voice-definition 'Author supplied by the user' \
  --basis user_attestation --policy-version manual-v1 \
  --support SUPPORTING_OBSERVATION_ID
```

Ranges are half-open Unicode scalar offsets and must respect whole grapheme
boundaries. Repeat `--support` for multiple observations. The core checks the
content hash, available content and scope; the plugin supplies no implicit voice.
`query --project ... --session ...` reads one JSON request on stdin and forwards
the explicit core operations `transfer`, `resolve` and `export`. It checks every
selected observation against the project/session/agent scope first. For example,
the following resolves supplied claims and unknown gaps without returning raw
text:

```sh
printf '%s\n' '{"operation":"resolve","observation_id":"TARGET_ID","content_hash":"EXACT_OBSERVATION_HASH"}' \
  | "$plugin/bin/textprov" --data "$data" query --project "$project" --session NATIVE_SESSION_ID
```

For `transfer`, provide `source_id`, `target_id`, exact `source_hash` and
`target_hash`, an explicit `candidate_index` and the selected `source_claim_ids`.
The shared core checks the selected passage, projects only supplied attribution
and rejects conflicts. Matching alone never performs a transfer. For `export`,
provide `observation_id`, `content_hash`, explicit `voice_states` mappings and
`allow_lossy: true`. The result contains exported text plus its required
projection/round-trip report in JSON on stdout. Export is opt-in and does not
write source files or change clipboard contents. See the core
[`CHRONICLE.md`](../../python/CHRONICLE.md) for the full request contract.

## Verification and remaining coverage

Run from the TextProv repository root:

```sh
PYTHONPATH=python python3 -m unittest discover -s plugins/codex/tests -v
```

The sanitized fixtures and independent subprocess tests verify package command
wiring, exact Unicode content hashes, structured visibility, pre/post call joins,
parallel first-open and retries, repeated text under distinct IDs, malformed and
missing data, JSON-string tool arguments, persistent diagnostics, project/session/
agent isolation, matching options, explicit claims, transfer/resolve/export
forwarding and metadata pagination.
They exercise the real shared core without reading its storage schema.

These tests establish fixture behavior. Plugin discovery, hook trust review,
runtime environment variables, host version compatibility, denied/retried calls,
mid-turn steering, resume, native child event scope and host UI need a separate
installed-host trial on a recorded build. No host config was changed and no such
trial is included in this implementation session.

Hosted tools (including hosted web search), specialized tool paths that bypass
hooks, reasoning, intermediate assistant messages, permission outcomes, full
turn coverage and clipboard behavior remain unobserved. `write_stdin` polling
can deliver the original command's post-tool event; it does not create another
pre-tool observation. Transcript parsing, automatic marking, patch preparation,
clipboard changes and automatic export are outside this plugin's current behavior. The
inspection skill and `status.limitations` keep these boundaries visible.
