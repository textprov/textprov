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

    def test_read_of_a_marked_file_points_to_the_edit_command(self):
        self.workspace.has_marks.return_value = True
        result = self.dispatch(
            "PostToolUse", "Read", tool_input={"file_path": "/r/a \"b\".md"}
        )
        self.workspace.has_marks.assert_called_once_with('/r/a "b".md')
        assert result is not None
        fields = result["hookSpecificOutput"]
        self.assertEqual(fields["hookEventName"], "PostToolUse")
        note = fields["additionalContext"]
        self.assertIn(f"python3 {hook.SCRIPT} edit <<'JSON'", note)
        # The example is valid JSON with the path already quoted.
        example = note.split("<<'JSON'\n")[1].split("\nJSON")[0]
        self.assertEqual(json.loads(example)["file_path"], '/r/a "b".md')

    def test_session_start_explains_how_to_edit_marked_prose(self):
        result = self.dispatch("SessionStart", source="startup")
        assert result is not None
        fields = result["hookSpecificOutput"]
        self.assertEqual(fields["hookEventName"], "SessionStart")
        note = fields["additionalContext"]
        self.assertIn(f"python3 {hook.SCRIPT} edit <<'JSON'", note)
        self.assertIn(f"PYTHONPATH={hook.ROOT / 'python'} python3 -m", note)
        example = note.split("<<'JSON'\n")[1].split("\nJSON")[0]
        self.assertEqual(
            sorted(json.loads(example)),
            ["file_path", "new_string", "old_string"],
        )
        self.assertEqual(self.workspace.mock_calls, [])

    def test_settings_route_every_handled_event_to_the_script(self):
        with open(ROOT / ".claude" / "settings.json", encoding="utf-8") as f:
            hooks = json.load(f)["hooks"]
        matchers = {
            name: entries[0].get("matcher", "").split("|")
            for name, entries in hooks.items()
        }
        self.assertEqual(
            matchers,
            {
                "SessionStart": [""],
                "UserPromptSubmit": [""],
                "PreToolUse": ["Write", "Edit", "Bash"],
                "PostToolUse": ["Bash", "Read"],
                "PostToolUseFailure": ["Bash"],
            },
        )
        for entries in hooks.values():
            self.assertIn(
                "textprov_hook.py", entries[0]["hooks"][0]["command"]
            )

    def test_read_of_an_unmarked_file_has_no_response(self):
        self.workspace.has_marks.return_value = False
        self.assertIsNone(
            self.dispatch(
                "PostToolUse", "Read", tool_input={"file_path": "a.md"}
            )
        )
        self.assertIsNone(self.dispatch("PostToolUse", "Read"))
        self.assertIsNone(self.dispatch("PostToolUseFailure", "Read"))

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
            self.assertEqual(hook.main([]), 0)
        factory.assert_called_once_with(hook.ROOT, human_min_words=3)
        self.workspace.record_prompt.assert_called_once_with("text", None)

    def test_disabled_hook_does_not_read_input(self):
        with (
            mock.patch.dict(os.environ, {"TEXTPROV_HOOK": "off"}, clear=True),
            mock.patch("sys.stdin", None),
        ):
            self.assertEqual(hook.main([]), 0)

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
                self.assertEqual(hook.main([]), expected)
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


class TestEditCommand(unittest.TestCase):
    """The route for marked prose, which the Edit tool refuses before hooks."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        subprocess.run(
            ["git", "-C", str(self.root), "init", "-q"],
            check=True,
            capture_output=True,
        )
        self.path = self.root / "a.md"
        self.human = textprov.mark("Kept words stay here.", "human")
        self.write(self.human + "\n\n" + textprov.mark("Same.") + "\n\nSame.\n")

    def write(self, text):
        with open(self.path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)

    def read(self):
        with open(self.path, encoding="utf-8", newline="") as handle:
            return handle.read()

    def run_edit(self, payload, argv=("edit",)):
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        out, err = io.StringIO(), io.StringIO()
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("sys.stdin", io.StringIO(payload)),
            mock.patch("sys.stdout", out),
            mock.patch("sys.stderr", err),
            mock.patch.object(
                hook,
                "workspace_from_environment",
                return_value=Workspace(self.root),
            ),
        ):
            code = hook.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def edit(self, old, new, **extra):
        return self.run_edit(
            dict(
                file_path=str(self.path),
                old_string=old,
                new_string=new,
                **extra,
            )
        )

    def test_plain_old_string_edits_marked_prose(self):
        before = self.read()
        code, out, err = self.edit("stay here.", "stay here, with more.")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("replaced 1 place", out)
        after = self.read()
        self.assertEqual(
            textprov.strip_marks(after),
            textprov.strip_marks(before).replace(
                "stay here.", "stay here, with more."
            ),
        )
        self.assertEqual(
            textprov.runs(after.split("\n")[0], strip=True),
            [
                ("human", "Kept words stay"),
                (None, " "),
                ("ai", "here, with more."),
            ],
        )

    def test_relative_path_resolves_under_the_workspace_root(self):
        code, _, err = self.run_edit(
            dict(file_path="a.md", old_string="Kept", new_string="Held")
        )
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(textprov.strip_marks(self.read()).startswith("Held"))

    def test_replace_all_with_matching_marks(self):
        self.write(textprov.mark("One. Two. One.") + "\n")
        code, out, _ = self.edit("One.", "Three.", replace_all=True)
        self.assertEqual(code, 0)
        self.assertIn("replaced 2 places", out)
        self.assertEqual(
            textprov.strip_marks(self.read()), "Three. Two. Three.\n"
        )

    def test_failures_leave_the_file_alone(self):
        before = self.read()
        cases = (
            (self.edit("Same.", "Other."), 1, "matches 2 places"),
            (
                self.edit("Same.", "Other.", replace_all=True),
                1,
                "different provenance marks",
            ),
            (self.edit("absent text", "x"), 1, "not found"),
            (self.edit("Kept", "Kept"), 1, "are the same"),
            (
                self.run_edit(
                    dict(
                        file_path=str(self.root / "a.py"),
                        old_string="a",
                        new_string="b",
                    )
                ),
                1,
                "outside the marking scope",
            ),
            (self.run_edit("not json"), 2, "expected a JSON object"),
            (self.run_edit({"file_path": "a.md"}), 2, "old_string"),
            (self.run_edit("[]"), 2, "expected a JSON object"),
            (self.run_edit({}, argv=("other",)), 2, "usage"),
        )
        for (code, out, err), expected, message in cases:
            self.assertEqual((code, out), (expected, ""), err)
            self.assertIn(message, err)
        self.assertEqual(self.read(), before)

    def test_edit_ignores_the_hook_switch(self):
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"TEXTPROV_HOOK": "off"}, clear=True),
            mock.patch(
                "sys.stdin",
                io.StringIO(
                    json.dumps(
                        dict(
                            file_path=str(self.path),
                            old_string="Kept",
                            new_string="Held",
                        )
                    )
                ),
            ),
            mock.patch("sys.stdout", out),
            mock.patch.object(
                hook,
                "workspace_from_environment",
                return_value=Workspace(self.root),
            ),
        ):
            self.assertEqual(hook.main(["edit"]), 0)
        self.assertTrue(textprov.strip_marks(self.read()).startswith("Held"))

    def test_script_edit_runs_outside_repository_cwd(self):
        payload = dict(
            file_path=str(ROOT / "python" / "textprov" / "workspace.py"),
            old_string="a",
            new_string="b",
        )
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "edit"],
                input=json.dumps(payload),
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
                cwd=cwd,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
            )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("outside the marking scope", result.stderr)


if __name__ == "__main__":
    unittest.main()
