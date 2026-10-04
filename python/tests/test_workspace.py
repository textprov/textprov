"""Tests for provider-neutral Git workspace operations."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import textprov
from textprov import workspace as workspace_module
from textprov.editing import Ambiguous
from textprov.workspace import GIT_MOVES_TREE, Workspace


def ai(text):
    return textprov.mark(text, state="ai")


class TestCommands(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.workspace = Workspace(self.root)
        self.git("init", "-q")
        self.write("old\n")
        self.git("add", "a.md")
        self.git("commit", "-qm", "a")

    def git(self, *args):
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@t",
                "-c",
                "commit.gpgsign=false",
                "-c",
                "core.hooksPath=/dev/null",
                *args,
            ],
            check=True,
            capture_output=True,
        )

    def write(self, text):
        (self.root / "a.md").write_text(text, encoding="utf-8")

    def read(self):
        return (self.root / "a.md").read_text(encoding="utf-8")

    def command(self, command, *steps):
        self.workspace.before_command(command, "t")
        for step in steps:
            step()
        self.workspace.after_command("t")

    def test_operation_ids_have_distinct_snapshot_paths(self):
        ids = ("provider:1", "provider/1", "Provider:1", "../outside")
        paths = [self.workspace.snapshot_path(value) for value in ids]
        self.assertEqual(len({path.name.lower() for path in paths}), len(ids))
        self.assertTrue(
            all(path.parent == self.workspace.snapshots for path in paths)
        )

    def test_pending_operations_do_not_overwrite_each_other(self):
        self.workspace.before_command("first", "provider:1")
        self.write("old\nfirst line\n")
        self.workspace.before_command("second", "provider/1")
        self.write("old\nfirst line\nsecond line\n")
        self.workspace.after_command("provider:1")
        self.assertTrue(self.workspace.snapshot_path("provider/1").exists())
        self.workspace.after_command("provider/1")
        self.assertEqual(
            self.read(),
            "old\n" + ai("first line") + "\n" + ai("second line") + "\n",
        )

    def test_command_marking_does_not_follow_external_symlinks(self):
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside = Path(outside_dir.name) / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        link = self.root / "link.md"
        link.symlink_to(outside)
        self.assertFalse(self.workspace.in_scope(link))
        self.workspace.before_command("change files", "op")
        outside.write_text("outside\nnew line\n", encoding="utf-8")
        self.workspace.after_command("op")
        self.assertEqual(
            outside.read_text(encoding="utf-8"), "outside\nnew line\n"
        )

    def test_command_marking_rechecks_symlink_targets(self):
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside = Path(outside_dir.name) / "outside.md"
        outside.write_text("new text\n", encoding="utf-8")
        self.workspace.before_command("change files", "op")
        (self.root / "a.md").unlink()
        (self.root / "a.md").symlink_to(outside)
        self.workspace.after_command("op")
        self.assertEqual(outside.read_text(encoding="utf-8"), "new text\n")

    def test_command_marking_respects_resolved_path_exclusions(self):
        (self.root / "script.py").write_text("some code\n", encoding="utf-8")
        (self.root / "link.md").symlink_to(self.root / "script.py")
        self.workspace.before_command("change files", "op")
        (self.root / "script.py").write_text("new code\n", encoding="utf-8")
        self.workspace.after_command("op")
        self.assertEqual(
            (self.root / "script.py").read_text(encoding="utf-8"), "new code\n"
        )

    def test_relative_paths_resolve_under_root(self):
        self.assertEqual(
            self.workspace.prepare_write("a.md", "old\nnew\n"),
            "old\n" + ai("new") + "\n",
        )
        self.assertEqual(self.read(), "old\n")
        self.assertEqual(
            self.workspace.prepare_edit("a.md", "old", "new"),
            ("old", ai("new")),
        )

    def test_files_outside_scope_are_untouched(self):
        for path in (
            "script.py",
            "docs/examples/sample.md",
            "site/public/sample.md",
            "../outside.md",
        ):
            self.assertIsNone(
                self.workspace.prepare_write(path, "new text"), path
            )
        (self.root / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
        self.assertIsNone(
            self.workspace.prepare_write("ignored.md", "new text")
        )

    def test_prompt_matching_and_instance_isolation(self):
        prompt = "one two three four five"
        self.workspace.record_prompt(prompt, session="session")
        entry = json.loads(
            self.workspace.prompt_log.read_text(encoding="utf-8")
        )
        self.assertEqual(entry["session"], "session")
        self.assertEqual(textprov.strip_marks(entry["text"]), prompt)
        self.assertEqual(
            self.workspace.prepare_write("new.md", prompt),
            textprov.mark(prompt, state="human"),
        )
        isolated = Workspace(
            self.root, state_dir="other/state", human_min_words=2
        )
        self.assertEqual(isolated.prepare_write("new.md", prompt), ai(prompt))
        isolated.record_prompt("short quote")
        self.assertEqual(
            isolated.prepare_write("new.md", "short quote"),
            textprov.mark("short quote", state="human"),
        )

    def test_bad_prompt_entries_are_ignored(self):
        self.workspace.state_dir.mkdir()
        self.workspace.prompt_log.write_text(
            'bad json\n{}\n{"text": null}\n', encoding="utf-8"
        )
        self.assertEqual(self.workspace.load_shingles(), set())

    def test_invalid_word_threshold(self):
        with self.assertRaises(ValueError):
            Workspace(self.root, human_min_words=0)

    def test_snapshot_can_be_consumed_by_another_instance(self):
        self.workspace.before_command("write prose", "op")
        self.write("old\nnew line\n")
        Workspace(self.root).after_command("op")
        self.assertEqual(self.read(), "old\n" + ai("new line") + "\n")
        self.assertFalse(self.workspace.snapshot_path("op").exists())

    def test_apply_edit_matches_with_marks_ignored(self):
        human = textprov.mark("Kept words.", "human")
        self.write(human + " " + ai("Old tail.") + "\n")
        self.assertTrue(self.workspace.has_marks("a.md"))
        self.assertEqual(
            self.workspace.apply_edit("a.md", "Old tail.", "New tail."), 1
        )
        self.assertEqual(self.read(), human + " " + ai("New tail.") + "\n")

    def test_prepare_edit_reads_once_without_writing(self):
        with mock.patch.object(
            workspace_module, "read_text", wraps=workspace_module.read_text
        ) as read:
            self.assertEqual(
                self.workspace.prepare_edit("a.md", "old", "new"),
                ("old", ai("new")),
            )
        self.assertEqual(read.call_count, 1)
        self.assertEqual(self.read(), "old\n")

    def test_apply_edit_replace_all_counts_places(self):
        self.write(ai("One. Two. One.") + "\n")
        self.assertEqual(
            self.workspace.apply_edit("a.md", "One.", "Six.", True), 2
        )
        self.assertEqual(self.read(), ai("Six. Two. Six.") + "\n")

    def test_apply_edit_without_a_match_or_scope_changes_nothing(self):
        (self.root / "b.txt").write_text("old\n", encoding="utf-8")
        self.assertEqual(self.workspace.apply_edit("a.md", "absent", "x"), 0)
        self.assertEqual(self.workspace.apply_edit("b.txt", "old", "new"), 0)
        self.assertEqual(self.workspace.apply_edit("none.md", "old", "x"), 0)
        self.assertEqual(self.read(), "old\n")
        self.assertEqual((self.root / "b.txt").read_text("utf-8"), "old\n")

    def test_apply_edit_refuses_ambiguity(self):
        self.write("Same. " + ai("Same.") + "\n")
        before = self.read()
        for replace_all in (False, True):
            with self.assertRaises(Ambiguous):
                self.workspace.apply_edit("a.md", "Same.", "x", replace_all)
        self.assertEqual(self.read(), before)

    def test_has_marks(self):
        self.assertFalse(self.workspace.has_marks("a.md"))
        self.assertFalse(self.workspace.has_marks("missing.md"))
        (self.root / "b.txt").write_text(ai("x"), encoding="utf-8")
        self.assertFalse(self.workspace.has_marks("b.txt"))
        self.write(ai("x"))
        self.assertTrue(self.workspace.has_marks("a.md"))

    def test_new_copy_is_not_marked(self):
        self.workspace.before_command("copy", "op")
        (self.root / "copy.md").write_text("old\n", encoding="utf-8")
        self.workspace.after_command("op")
        self.assertEqual(
            (self.root / "copy.md").read_text(encoding="utf-8"), "old\n"
        )

    def test_new_file_is_marked(self):
        self.workspace.before_command("write prose", "op")
        (self.root / "new.md").write_text("new prose\n", encoding="utf-8")
        self.workspace.after_command("op")
        self.assertEqual(
            (self.root / "new.md").read_text(encoding="utf-8"),
            ai("new prose") + "\n",
        )

    def test_missing_snapshot_is_noop(self):
        self.workspace.after_command("missing")
        self.assertEqual(self.read(), "old\n")

    def test_tree_move_does_not_snapshot(self):
        self.workspace.before_command("git switch other", "op")
        self.assertFalse(self.workspace.snapshot_path("op").exists())

    def test_crlf_is_preserved(self):
        (self.root / "a.md").write_bytes(b"old\r\n")
        self.assertEqual(
            self.workspace.prepare_write("a.md", "old\r\nnew\r\n"),
            "old\r\n" + ai("new") + "\r\n",
        )

    def test_edit_is_marked(self):
        self.command("echo new >> a.md", lambda: self.write("old\nnew line\n"))
        self.assertEqual(self.read(), "old\n" + ai("new line") + "\n")

    def test_edit_then_commit_is_marked(self):
        self.command(
            "echo new >> a.md && git commit -am new",
            lambda: self.write("old\nnew line\n"),
            lambda: self.git("commit", "-qam", "new"),
        )
        self.assertEqual(self.read(), "old\n" + ai("new line") + "\n")

    def test_two_commits_are_not_marked(self):
        self.command(
            "echo new >> a.md && git commit -am new && git commit --allow-empty -m more",
            lambda: self.write("old\nnew line\n"),
            lambda: self.git("commit", "-qam", "new"),
            lambda: self.git("commit", "-q", "--allow-empty", "-m", "more"),
        )
        self.assertEqual(self.read(), "old\nnew line\n")

    def test_tree_moving_commands(self):
        for command in (
            "git checkout main",
            "git -C site switch x",
            "git --no-pager stash pop",
            "make && git -c a=b merge x",
            "git --git-dir x reset --hard",
            "git --work-tree . restore a.md",
            "git --work-tree=. restore a.md",
            'git -C "my dir" restore a.md',
            'git -c user.name="A B" stash pop',
            "git --namespace ns checkout x",
        ):
            self.assertTrue(GIT_MOVES_TREE.search(command), command)
        for command in (
            "git commit -am x",
            "git commit -m 'merge and apply'",
            "git log --grep reset",
            "gh pr checkout 1",
        ):
            self.assertFalse(GIT_MOVES_TREE.search(command), command)

    def test_checkout_of_a_child_commit_is_not_marked(self):
        self.git("checkout", "-qb", "side")
        self.write("old\ntheir line\n")
        self.git("commit", "-qam", "theirs")
        self.git("checkout", "-q", "-")
        self.command(
            "gh pr checkout 1", lambda: self.git("checkout", "-q", "side")
        )
        self.assertEqual(self.read(), "old\ntheir line\n")


if __name__ == "__main__":
    unittest.main()
