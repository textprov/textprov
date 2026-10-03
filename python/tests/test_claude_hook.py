"""Contract tests for the thin Claude Code adapter."""

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import textprov
from textprov.editing import Ambiguous
from textprov.workspace import Workspace

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".claude" / "hooks" / "textprov_hook.py"
spec = importlib.util.spec_from_file_location("textprov_claude_hook", SCRIPT)
assert spec is not None and spec.loader is not None
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class TestAdapter(unittest.TestCase):
    def setUp(self):
        self.workspace = mock.create_autospec(Workspace, instance=True)

    def dispatch(self, name, tool=None, **fields):
        event = dict(hook_event_name=name, tool_name=tool, **fields)
        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            hook.dispatch(event, self.workspace)
        return json.loads(output.getvalue()) if output.getvalue() else None

    def test_prompt_is_delegated(self):
        self.assertIsNone(
            self.dispatch(
                "UserPromptSubmit", prompt="human text", session_id="s"
            )
        )
        self.workspace.record_prompt.assert_called_once_with("human text", "s")

    def test_write_response_preserves_other_fields(self):
        marked = textprov.mark("new")
        self.workspace.prepare_write.return_value = marked
        result = self.dispatch(
            "PreToolUse",
            "Write",
            tool_input={
                "file_path": "a.md",
                "content": "new",
                "extra": True,
            },
        )
        self.workspace.prepare_write.assert_called_once_with("a.md", "new")
        self.assertEqual(
            result,
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "updatedInput": {
                        "file_path": "a.md",
                        "content": marked,
                        "extra": True,
                    },
                }
            },
        )

    def test_out_of_scope_and_unchanged_writes_have_no_response(self):
        for result in (None, "same"):
            self.workspace.prepare_write.return_value = result
            self.assertIsNone(
                self.dispatch(
                    "PreToolUse",
                    "Write",
                    tool_input={
                        "file_path": "a.md",
                        "content": "same",
                    },
                )
            )

    def test_edit_response(self):
        pair = (textprov.mark("old"), textprov.mark("new"))
        self.workspace.prepare_edit.return_value = pair
        result = self.dispatch(
            "PreToolUse",
            "Edit",
            tool_input={
                "file_path": "a.md",
                "old_string": "old",
                "new_string": "new",
                "replace_all": True,
            },
        )
        self.workspace.prepare_edit.assert_called_once_with(
            "a.md", "old", "new", True
        )
        assert result is not None
        data = result["hookSpecificOutput"]["updatedInput"]
        self.assertEqual((data["old_string"], data["new_string"]), pair)
        self.assertTrue(data["replace_all"])

    def test_ambiguous_edit_is_denied(self):
        self.workspace.prepare_edit.side_effect = Ambiguous("not unique")
        result = self.dispatch(
            "PreToolUse", "Edit", tool_input={"file_path": "a.md"}
        )
        assert result is not None
        fields = result["hookSpecificOutput"]
        self.assertEqual(fields["permissionDecision"], "deny")
        self.assertIn("not unique", fields["permissionDecisionReason"])

    def test_command_lifecycle_is_delegated(self):
        self.assertIsNone(
            self.dispatch(
                "PreToolUse",
                "Bash",
                tool_use_id="id",
                tool_input={"command": "cmd"},
            )
        )
        self.workspace.before_command.assert_called_once_with("cmd", "id")
        for name in ("PostToolUse", "PostToolUseFailure"):
            self.assertIsNone(self.dispatch(name, "Bash", tool_use_id="id"))
        self.assertEqual(
            self.workspace.after_command.call_args_list,
            [mock.call("id"), mock.call("id")],
        )

    def test_unhandled_event_is_noop(self):
        self.assertIsNone(self.dispatch("Other"))
        self.assertEqual(self.workspace.mock_calls, [])

    def test_main_builds_configured_workspace(self):
        event = {"hook_event_name": "UserPromptSubmit", "prompt": "text"}
        with (
            mock.patch.dict(
                os.environ, {"TEXTPROV_HUMAN_MIN_WORDS": "3"}, clear=True
            ),
            mock.patch("sys.stdin", io.StringIO(json.dumps(event))),
            mock.patch.object(
                hook, "Workspace", return_value=self.workspace
            ) as factory,
        ):
            self.assertEqual(hook.main(), 0)
        factory.assert_called_once_with(hook.ROOT, human_min_words=3)
        self.workspace.record_prompt.assert_called_once_with("text", None)

    def test_disabled_hook_does_not_read_input(self):
        with (
            mock.patch.dict(os.environ, {"TEXTPROV_HOOK": "off"}, clear=True),
            mock.patch("sys.stdin", None),
        ):
            self.assertEqual(hook.main(), 0)

    def test_runtime_errors_block_writes_and_edits_only(self):
        for tool, expected in (("Write", 2), ("Edit", 2), ("Bash", 1)):
            event = {
                "hook_event_name": "PreToolUse",
                "tool_name": tool,
                "tool_input": {},
            }
            error = io.StringIO()
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch("sys.stdin", io.StringIO(json.dumps(event))),
                mock.patch("sys.stderr", error),
                mock.patch.object(
                    hook, "dispatch", side_effect=RuntimeError("failed")
                ),
            ):
                self.assertEqual(hook.main(), expected)
            self.assertIn("failed", error.getvalue())

    def test_script_works_outside_repository_cwd(self):
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(ROOT / "docs" / "adapter-smoke.md"),
                "content": "new prose",
            },
        }
        env = dict(
            os.environ,
            TEXTPROV_HOOK="on",
            TEXTPROV_HUMAN_MIN_WORDS="5",
            PYTHONDONTWRITEBYTECODE="1",
        )
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input=json.dumps(event),
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
                cwd=cwd,
                env=env,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)["hookSpecificOutput"]["updatedInput"]
        self.assertEqual(output["content"], textprov.mark("new prose"))


if __name__ == "__main__":
    unittest.main()
