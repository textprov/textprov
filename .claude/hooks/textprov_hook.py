#!/usr/bin/env python3
"""Translate Claude Code hook events to the provider-neutral Workspace API.

    textprov_hook.py        handle one hook event read from stdin
    textprov_hook.py edit   apply one Edit-shaped JSON object read from stdin

Set TEXTPROV_HOOK=off to disable the hook events. Reusable policy and storage
live in the Python package, not in this adapter.

Claude Code checks an Edit's old_string against the file before it runs any
hook, so it refuses an edit to marked prose and the PreToolUse rewrite never
sees it. The `edit` command is the route that works for marked files. A note
at SessionStart, repeated when a marked file is Read, tells the agent to use it.
"""

import json
import os
import shlex
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(ROOT / "python"))

from textprov.editing import Ambiguous
from textprov.workspace import Workspace

EDIT_USAGE = (
    "run this through Bash, giving old_string and new_string as plain text "
    "without marks:\n"
    "python3 {script} edit <<'JSON'\n"
    '{{"file_path": {path}, "old_string": "...", "new_string": "..."}}\n'
    "JSON\n"
    'Add "replace_all": true to replace every occurrence. Write, and Edit on '
    "unmarked lines such as headings and code, work as usual."
)
READ_NOTE = (
    "textprov: this file carries provenance marks, so the Edit tool cannot "
    "match its prose. To change it, " + EDIT_USAGE
)
SESSION_NOTE = (
    "textprov: prose in this repository's markdown files carries invisible "
    "provenance marks, one variation selector after each character. The Edit "
    "tool and plain-text search such as grep do not match marked prose. To "
    "edit it, " + EDIT_USAGE + " To read or search a file without its marks: "
    "PYTHONPATH={python} python3 -m textprov strip FILE"
)


def respond(event="PreToolUse", **fields):
    fields["hookEventName"] = event
    print(json.dumps({"hookSpecificOutput": fields}))


def dispatch(event, workspace):
    name = event.get("hook_event_name")
    tool = event.get("tool_name")
    if name == "UserPromptSubmit":
        workspace.record_prompt(event.get("prompt"), event.get("session_id"))
    elif name == "PreToolUse" and tool == "Write":
        data = event["tool_input"]
        content = data.get("content", "")
        marked = workspace.prepare_write(data.get("file_path", ""), content)
        if marked is not None and marked != content:
            respond(updatedInput=dict(data, content=marked))
    elif name == "PreToolUse" and tool == "Edit":
        # Reached only when old_string already matches the file exactly.
        data = event["tool_input"]
        old, new = data.get("old_string", ""), data.get("new_string", "")
        try:
            result = workspace.prepare_edit(
                data.get("file_path", ""),
                old,
                new,
                bool(data.get("replace_all")),
            )
        except Ambiguous as problem:
            respond(
                permissionDecision="deny",
                permissionDecisionReason=f"textprov hook: {problem}",
            )
            return
        if result and result != (old, new):
            respond(
                updatedInput=dict(
                    data, old_string=result[0], new_string=result[1]
                )
            )
    elif name == "PreToolUse" and tool == "Bash":
        workspace.before_command(
            event["tool_input"].get("command", ""), event.get("tool_use_id")
        )
    elif name in ("PostToolUse", "PostToolUseFailure") and tool == "Bash":
        workspace.after_command(event.get("tool_use_id"))
    elif name == "PostToolUse" and tool == "Read":
        path = (event.get("tool_input") or {}).get("file_path", "")
        if path and workspace.has_marks(path):
            respond(
                "PostToolUse",
                additionalContext=READ_NOTE.format(
                    script=shlex.quote(str(SCRIPT)), path=json.dumps(str(path))
                ),
            )
    elif name == "SessionStart":
        respond(
            "SessionStart",
            additionalContext=SESSION_NOTE.format(
                script=shlex.quote(str(SCRIPT)),
                path='"PATH"',
                python=shlex.quote(str(ROOT / "python")),
            ),
        )


def workspace_from_environment():
    return Workspace(
        ROOT,
        human_min_words=int(os.environ.get("TEXTPROV_HUMAN_MIN_WORDS", "5")),
    )


def edit_command():
    """Apply the mark-aware edit that the Edit tool cannot make itself."""
    try:
        data = json.load(sys.stdin)
        path = data["file_path"]
        old, new = data["old_string"], data["new_string"]
        replace_all = bool(data.get("replace_all"))
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        print(
            "textprov edit: expected a JSON object with file_path, "
            f"old_string, and new_string on stdin ({error!r})",
            file=sys.stderr,
        )
        return 2
    workspace = workspace_from_environment()
    if not workspace.in_scope(path):
        print(
            f"textprov edit: {path} is outside the marking scope; "
            "use the Edit tool.",
            file=sys.stderr,
        )
        return 1
    if old == new:
        print(
            "textprov edit: old_string and new_string are the same.",
            file=sys.stderr,
        )
        return 1
    try:
        count = workspace.apply_edit(path, old, new, replace_all)
    except Ambiguous as problem:
        print(f"textprov edit: {problem}", file=sys.stderr)
        return 1
    if not count:
        print(
            f"textprov edit: old_string not found in {path}, with "
            "provenance marks ignored.",
            file=sys.stderr,
        )
        return 1
    places = "1 place" if count == 1 else f"{count} places"
    print(f"textprov edit: replaced {places} in {path}; new prose is marked.")
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["edit"]:
        return edit_command()
    if argv:
        print(f"usage: {SCRIPT.name} [edit]", file=sys.stderr)
        return 2
    if os.environ.get("TEXTPROV_HOOK", "").lower() in ("off", "0", "false"):
        return 0
    event = {}
    try:
        event = json.load(sys.stdin)
        dispatch(event, workspace_from_environment())
    except Exception as error:  # noqa: BLE001
        print(f"textprov hook failed: {error!r}", file=sys.stderr)
        # Claude uses exit 2 to block a tool call; writes and edits fail closed.
        blocking = event.get("hook_event_name") == "PreToolUse" and event.get(
            "tool_name"
        ) in ("Write", "Edit")
        return 2 if blocking else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
