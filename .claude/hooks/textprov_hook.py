#!/usr/bin/env python3
"""Translate Claude Code hook events to the provider-neutral Workspace API.

Set TEXTPROV_HOOK=off to disable. Reusable policy and storage live in the
Python package, not in this adapter.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from textprov.editing import Ambiguous
from textprov.workspace import Workspace


def respond(**fields):
    fields["hookEventName"] = "PreToolUse"
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


def main():
    if os.environ.get("TEXTPROV_HOOK", "").lower() in ("off", "0", "false"):
        return 0
    event = {}
    try:
        event = json.load(sys.stdin)
        workspace = Workspace(
            ROOT,
            human_min_words=int(
                os.environ.get("TEXTPROV_HUMAN_MIN_WORDS", "5")
            ),
        )
        dispatch(event, workspace)
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
