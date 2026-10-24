---
name: textprov
description: Inspect the local TextProv Chronicle captured by this plugin; show status, observations, relationships and explicit claims without modifying source files.
---

Resolve the plugin root as two directories above this skill directory. Use its
`bin/textprov` executable. It requires the installed TextProv Python core; use
`TEXTPROV_PYTHON` when a dedicated interpreter was configured. Read the plugin
README if setup is incomplete. Do not edit host configuration automatically.

Start with `status --project <absolute-session-cwd>`. Set `PLUGIN_DATA` to the
plugin's writable data directory, or pass `--data <directory>` before the command
when running outside the hook environment. If that path is unavailable, ask for
it rather than choosing another storage location. Status reports captured native
session IDs in `observed_sessions`; select the intended session explicitly.

Use `list --project <cwd> --session <native-session-id>` to discover observation
IDs. `--agent <id>` selects a child agent; `--cross-agent` deliberately includes
all agents within that session. Listing and inspection return metadata, never
cached raw text. Respect the user's intended project, session and agent scope.

Use `inspect <observation-id>` with the same project/session options to examine
host ID relationships, completeness, cache availability and supplied claims.
`match <source-id> <target-id>` compares an explicit pair through the shared
core; available options are `--policy`, `--partial` and `--min-chars`. Matches
are evidence candidates and do not establish authorship.

Only use `claim` when the user supplies or authorizes a specific attribution.
Pass the exact content hash and scalar range from the selected observation,
the supplied voice context/identity/definition, basis, policy version, and each
supporting observation through `--support`. Use `claim --help` for syntax.

`query` reads one JSON request on stdin and forwards explicit `transfer`,
`resolve` and `export` operations to the shared core. Transfer requires the
chosen candidate index, source claim IDs and both content hashes. Export
requires an explicit voice-to-classification mapping and `allow_lossy: true`;
it returns text and the required report on stdout. Keep that report with the
result. Obtain user-supplied choices before attribution transfer or lossy
classification; never infer them from the transport channel.

Report known coverage gaps and errors from status alongside results. A missing
observation is not evidence of human origin. Do not infer a voice from a tool,
user, assistant, model, session or agent channel. Do not modify source files,
transcripts, permissions, clipboard behavior or attribution marks.
