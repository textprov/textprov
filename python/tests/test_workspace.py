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
from textprov.workspace import Workspace, git_moves_tree


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

    def shell(self, command):
        self.command(
            command,
            lambda: subprocess.run(
                command,
                shell=True,
                cwd=self.root,
                check=True,
                capture_output=True,
                timeout=10,
            ),
        )

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

    def test_apply_edit_uses_one_snapshot_despite_concurrent_changes(self):
        original = "Intro. " + ai("Old tail.") + "\n"
        for mutation in ("duplicate", "remove", "delete"):
            with self.subTest(mutation=mutation):
                self.write(original)
                original_read = workspace_module.read_text

                def read_then_mutate(
                    path, original_read=original_read, mutation=mutation
                ):
                    raw = original_read(path)
                    if mutation == "duplicate":
                        self.write(ai("Old tail.") + "\n" + original)
                    elif mutation == "remove":
                        self.write("Concurrent replacement.\n")
                    else:
                        (self.root / "a.md").unlink()
                    return raw

                with mock.patch.object(
                    workspace_module, "read_text", side_effect=read_then_mutate
                ) as read:
                    self.assertEqual(
                        self.workspace.apply_edit(
                            "a.md", "Old tail.", "New tail."
                        ),
                        1,
                    )
                self.assertEqual(read.call_count, 1)
                self.assertEqual(
                    self.read(), "Intro. " + ai("New tail.") + "\n"
                )

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

    def test_git_rename_and_append_preserves_source_provenance(self):
        original = (
            "Untouched unmarked paragraph.\n\n"
            + textprov.mark("Existing human paragraph.", "human")
            + "\n"
            + ai("Existing AI paragraph.")
            + "\n"
        )
        self.write(original)
        self.shell("git mv a.md b.md && printf 'Added paragraph.\\n' >> b.md")
        self.assertFalse((self.root / "a.md").exists())
        self.assertEqual(
            (self.root / "b.md").read_text(encoding="utf-8"),
            original + ai("Added paragraph.") + "\n",
        )

    def test_git_rename_with_C_uses_source_under_that_directory(self):
        (self.root / "sub dir").mkdir()
        self.git("mv", "a.md", "sub dir/a.md")
        original = "Untouched prose.\n"
        (self.root / "sub dir/a.md").write_text(original, encoding="utf-8")
        self.shell(
            "git -C 'sub dir' mv a.md b.md && "
            "printf 'Added prose.\\n' >> 'sub dir/b.md'"
        )
        self.assertEqual(
            (self.root / "sub dir/b.md").read_text(encoding="utf-8"),
            original + ai("Added prose.") + "\n",
        )

    def test_copy_and_modify_preserves_source_provenance(self):
        kept = (
            "Untouched unmarked paragraph.\n\n"
            + textprov.mark("Existing human paragraph.", "human")
            + "\n\n"
        )
        template = kept + "Placeholder goes here.\n"
        (self.root / "tmpl.md").write_text(template, encoding="utf-8")
        self.shell(
            "cp tmpl.md new.md && "
            "sed 's/Placeholder/Replacement/' new.md > filled.tmp && "
            "cat filled.tmp > new.md"
        )
        self.assertEqual(
            (self.root / "new.md").read_text(encoding="utf-8"),
            kept + ai("Replacement") + " goes here.\n",
        )
        self.assertEqual(
            (self.root / "tmpl.md").read_text(encoding="utf-8"), template
        )

    def test_move_over_existing_path_uses_source_not_old_destination(self):
        original = (
            "Source prose.\n" + textprov.mark("Human prose.", "human") + "\n"
        )
        (self.root / "b.md").write_text(original, encoding="utf-8")
        self.shell("mv b.md a.md && printf 'Added prose.\\n' >> a.md")
        self.assertEqual(self.read(), original + ai("Added prose.") + "\n")

    def test_copy_to_directory_and_quoted_paths(self):
        (self.root / "new dir").mkdir()
        original = "Untouched source.\n"
        (self.root / "source file.md").write_text(original, encoding="utf-8")
        self.shell(
            "cp -- 'source file.md' 'new dir/' && "
            "printf 'Added prose.\\n' >> 'new dir/source file.md'"
        )
        self.assertEqual(
            (self.root / "new dir/source file.md").read_text(encoding="utf-8"),
            original + ai("Added prose.") + "\n",
        )

    def test_unrelated_similar_new_file_is_not_matched_to_source(self):
        self.write("Common introductory paragraph.\n\nExisting conclusion.\n")
        self.shell(
            "printf 'Common introductory paragraph.\\n\\nDifferent conclusion.\\n' "
            "> new.md"
        )
        self.assertEqual(
            (self.root / "new.md").read_text(encoding="utf-8"),
            ai("Common introductory paragraph.")
            + "\n\n"
            + ai("Different conclusion.")
            + "\n",
        )

    def test_source_matching_does_not_restore_missing_marks(self):
        self.write(textprov.mark("Previously human prose.", "human") + "\n")
        self.command(
            "cp a.md b.md && strip b.md && append b.md",
            lambda: (self.root / "b.md").write_text(
                "Previously human prose.\nAdded prose.\n", encoding="utf-8"
            ),
        )
        self.assertEqual(
            (self.root / "b.md").read_text(encoding="utf-8"),
            "Previously human prose.\n" + ai("Added prose.") + "\n",
        )

    def test_multiple_possible_sources_fail_safe(self):
        (self.root / "b.md").write_text(
            textprov.mark("Source prose.", "human") + "\n", encoding="utf-8"
        )
        self.shell(
            "cp a.md new.md && cp b.md new.md && "
            "printf 'Added prose.\\n' >> new.md"
        )
        self.assertEqual(
            (self.root / "new.md").read_text(encoding="utf-8"),
            textprov.mark("Source prose.", "human") + "\nAdded prose.\n",
        )

    def test_unexecuted_transfers_mark_additions_to_existing_destination(self):
        destination = "Different untouched destination paragraph.\n"
        for transfer in (
            "false && cp a.md b.md",
            "true || cp a.md b.md",
            "if false; then cp a.md b.md; fi",
            "if true; then :; else cp a.md b.md; fi",
            "false && (cp a.md b.md)",
            "false && { :; cp a.md b.md; }",
            "false && sh -c 'cp a.md b.md'",
        ):
            with self.subTest(transfer=transfer):
                (self.root / "b.md").write_text(destination, encoding="utf-8")
                self.shell(transfer + "\nprintf 'Added prose.\\n' >> b.md")
                self.assertEqual(
                    (self.root / "b.md").read_text(encoding="utf-8"),
                    destination + ai("Added prose.") + "\n",
                )
                self.assertEqual(self.read(), "old\n")

    def test_uncertain_transfer_does_not_suppress_independent_additions(self):
        destination = "Different untouched destination paragraph.\n"
        (self.root / "b.md").write_text(destination, encoding="utf-8")
        self.shell(
            "false && cp a.md b.md\n"
            "printf 'Added prose.\\n' >> b.md\n"
            "printf 'Independent prose.\\n' >> a.md"
        )
        self.assertEqual(
            (self.root / "b.md").read_text(encoding="utf-8"),
            destination + ai("Added prose.") + "\n",
        )
        self.assertEqual(self.read(), "old\n" + ai("Independent prose.") + "\n")

    def test_executed_conditional_transfers_preserve_source_provenance(self):
        original = (
            "Untouched source paragraph.\n"
            + textprov.mark("Existing human prose.", "human")
            + "\n"
        )
        self.write(original)
        for transfer in (
            "true && cp a.md b.md",
            "false || cp a.md b.md",
            "if true; then cp a.md b.md; fi",
        ):
            with self.subTest(transfer=transfer):
                (self.root / "b.md").write_text(
                    "Different destination paragraph.\n", encoding="utf-8"
                )
                self.shell(transfer + "\nprintf 'Added prose.\\n' >> b.md")
                self.assertEqual(
                    (self.root / "b.md").read_text(encoding="utf-8"),
                    original + ai("Added prose.") + "\n",
                )

    def test_conditional_copy_does_not_label_possible_source_text(self):
        original = "Existing destination paragraph.\n"
        copied = original + "Possible copied paragraph.\n"
        self.write(copied)
        for gate in ("true", "false"):
            with self.subTest(gate=gate):
                (self.root / "b.md").write_text(original, encoding="utf-8")
                self.shell(
                    gate + " && cp a.md b.md\n"
                    "printf 'Possible copied paragraph.\\n' >> b.md"
                )
                self.assertEqual(
                    (self.root / "b.md").read_text(encoding="utf-8"),
                    copied
                    if gate == "false"
                    else copied + ai("Possible copied paragraph.") + "\n",
                )

    def test_missing_conditional_source_preserves_downstream_destination(self):
        destination = "Existing destination prose.\n"
        (self.root / "c.md").write_text(destination, encoding="utf-8")
        self.shell(
            "false && cp a.md b.md\n"
            "cp b.md c.md; printf 'Added prose.\\n' >> c.md"
        )
        self.assertFalse((self.root / "b.md").exists())
        self.assertEqual(
            (self.root / "c.md").read_text(encoding="utf-8"),
            destination + ai("Added prose.") + "\n",
        )

    def test_conditional_transfer_does_not_keep_truncated_cluster_marks(self):
        original = textprov.mark("\u0600 ", "human")
        self.write(original)
        (self.root / "b.md").write_text(original, encoding="utf-8")
        changed = original.replace(" ", "")
        self.command(
            "false && cp b.md a.md; strip_space a.md",
            lambda: self.write(changed),
        )
        self.assertEqual(self.read(), ai("\u0600"))

    def test_conditional_copy_preserves_valid_source_cluster_marks(self):
        source = textprov.mark("\u0600", "human")
        self.write(source)
        (self.root / "b.md").write_text(
            textprov.mark("\u0600 ", "human"), encoding="utf-8"
        )
        self.shell("true && cp a.md b.md")
        self.assertEqual(
            (self.root / "b.md").read_text(encoding="utf-8"), source
        )

    def test_heredoc_transfer_text_does_not_select_a_source(self):
        destination = "Different untouched destination paragraph.\n"
        for delimiter in ("EOF", "'EOF'"):
            with self.subTest(delimiter=delimiter):
                (self.root / "b.md").write_text(destination, encoding="utf-8")
                self.shell(
                    "cat <<" + delimiter + " > /dev/null\n"
                    "cp a.md b.md\nEOF\n"
                    "printf 'Added prose.\\n' >> b.md"
                )
                self.assertEqual(
                    (self.root / "b.md").read_bytes(),
                    (destination + "Added prose.\n").encode("utf-8"),
                )
                self.assertEqual(self.read(), "old\n")

    def test_certain_copy_overwrite_preserves_source_prose(self):
        destination = "Different destination paragraph.\n"
        (self.root / "b.md").write_text(destination, encoding="utf-8")
        self.shell("cp a.md b.md && printf 'Added prose.\\n' >> b.md")
        self.assertEqual(
            (self.root / "b.md").read_text(encoding="utf-8"),
            "old\n" + ai("Added prose.") + "\n",
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

    def test_quoted_git_text_does_not_skip_marking(self):
        self.shell("echo 'git checkout main' >> a.md")
        self.assertEqual(self.read(), "old\n" + ai("git checkout main") + "\n")

    def test_edit_then_commit_with_git_text_in_message_is_marked(self):
        self.command(
            "echo new >> a.md && git commit -am 'explain git reset'",
            lambda: self.write("old\nnew line\n"),
            lambda: self.git("commit", "-qam", "explain git reset"),
        )
        self.assertEqual(self.read(), "old\n" + ai("new line") + "\n")

    def test_wrapped_git_restores_are_not_marked_as_new_writing(self):
        for command in (
            "bash -c 'git restore a.md'",
            "sh -c 'git -C . restore a.md'",
            "eval 'git restore a.md'",
            "nice git restore a.md",
            "nice -n 5 git restore a.md",
            "nice -5 git restore a.md",
            "/usr/bin/nice git -C . restore a.md",
            "env MODE=test nice sh -c 'git restore a.md'",
            "nice -n 5 bash -c 'git restore a.md'",
        ):
            with self.subTest(command=command):
                self.write("Local rewritten prose.\n")
                self.shell(command)
                self.assertEqual(self.read(), "old\n")

    def test_nice_information_options_do_not_suppress_later_additions(self):
        for option in ("--help", "--version"):
            with self.subTest(option=option):
                self.write("old\n")
                self.shell(
                    "nice " + option + "; printf 'Added prose.\\n' >> a.md"
                )
                self.assertEqual(
                    self.read(), "old\n" + ai("Added prose.") + "\n"
                )

    def test_git_restores_in_substitutions_leave_restored_bytes_unmarked(self):
        for command in (
            'echo "$(git restore a.md)"',
            "echo $(git restore a.md)",
            "echo `git restore a.md`",
            'echo "`git restore a.md`"',
            'result="$(git -C . restore a.md)"',
            "sh -c 'echo \"$(git restore a.md)\"'",
        ):
            with self.subTest(command=command):
                self.write("Local rewritten prose.\n")
                self.shell(command)
                self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_unresolved_executable_and_payloads_leave_restored_bytes_unmarked(
        self,
    ):
        for command in (
            'payload="git restore a.md"; eval "$payload"',
            'payload="git restore a.md"; sh -c "$payload"',
            'executable=git; "$executable" restore a.md',
            'operation=restore; git "$operation" a.md',
        ):
            with self.subTest(command=command):
                self.write("Local rewritten prose.\n")
                self.shell(command)
                self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_interpolation_inside_code_payloads_keeps_restored_bytes_unmarked(
        self,
    ):
        for invocation in (
            'eval "echo $payload"',
            'sh -c "echo $payload"',
            'bash -c "echo $payload"',
            'eval -- "  echo prefix ${payload}"',
            'sh -c "  : ${payload}"',
            'env -u UNUSED sh -c "echo $payload"',
        ):
            with self.subTest(invocation=invocation):
                self.write("Local rewritten prose.\n")
                self.shell("payload='; git restore a.md'; " + invocation)
                self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_env_code_payloads_keep_restored_bytes_unmarked(self):
        for command in (
            "env payload='; git restore a.md' sh -c 'eval \"echo $payload\"'",
            "env -S 'git restore a.md'",
            "/usr/bin/env git restore a.md",
            "/usr/bin/env -S 'git restore a.md'",
            "/usr/bin/env -u UNUSED git restore a.md",
            "/usr/bin/env payload='; git restore a.md' sh -c 'eval \"echo $payload\"'",
            "command /usr/bin/env -- git restore a.md",
        ):
            with self.subTest(command=command):
                self.write("Local rewritten prose.\n")
                self.shell(command)
                self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_git_global_option_expansions_keep_restored_bytes_unmarked(self):
        for command in (
            "options='-c user.name=t'; git $options restore a.md",
            "configuration='user.name=t restore a.md'; git -c $configuration",
            'directory=.; git -C "$directory" restore a.md',
            "EDITOR=: git --config-env=core.editor=EDITOR restore a.md",
        ):
            with self.subTest(command=command):
                self.write("Local rewritten prose.\n")
                self.shell(command)
                self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_unresolved_code_and_env_context_skip_snapshots(self):
        for command in (
            "eval 'echo literal $5'",
            r"sh -c 'echo literal \$payload'",
            "env --split-string='git restore a.md'",
            "env -C . git restore a.md",
            "env --chdir=. cp a.md b.md",
            "/usr/bin/env -C . git restore a.md",
            "/usr/bin/env --split-string='git restore a.md'",
            "/usr/bin/env --chdir=. cp a.md b.md",
            "nice -n '$adjustment' git restore a.md",
            "nice --adjustment='$adjustment' git restore a.md",
            "nice --unknown-option git restore a.md",
        ):
            with self.subTest(command=command):
                self.assertTrue(git_moves_tree(command))
                self.workspace.before_command(command, "unresolved")
                self.assertFalse(
                    self.workspace.snapshot_path("unresolved").exists()
                )

    def test_dollars_in_ordinary_arguments_do_not_skip_marking(self):
        self.shell("echo 'Ordinary $payload prose.' >> a.md")
        self.assertEqual(
            self.read(), "old\n" + ai("Ordinary $payload prose.") + "\n"
        )
        self.command(
            "echo more >> a.md && git commit -am 'explain $payload and git reset'",
            lambda: self.write(self.read() + "More prose.\n"),
            lambda: self.git(
                "commit", "-qam", "explain $payload and git reset"
            ),
        )
        self.assertEqual(
            self.read(),
            "old\n"
            + ai("Ordinary $payload prose.")
            + "\n"
            + ai("More prose.")
            + "\n",
        )

    def test_git_restore_in_else_leaves_restored_bytes_unmarked(self):
        command = "if false; then :; else git restore a.md; fi"
        self.write("Local rewritten prose.\n")
        self.shell(command)
        self.assertEqual((self.root / "a.md").read_bytes(), b"old\n")

    def test_literal_substitution_strings_are_marked_without_execution(self):
        for argument, literal in (
            ("'Literal $(git restore a.md).'", "Literal $(git restore a.md)."),
            ("'Literal `git restore a.md`.'", "Literal `git restore a.md`."),
            (
                r'"Literal \$(git restore a.md)."',
                "Literal $(git restore a.md).",
            ),
        ):
            with self.subTest(argument=argument):
                original = "Local untouched paragraph.\n"
                self.write(original)
                command = "printf '%s\\n' " + argument + " >> a.md"
                self.assertFalse(git_moves_tree(command))
                self.shell(command)
                raw = self.read()
                self.assertTrue(raw.startswith(original))
                self.assertIn(ai("Literal"), raw)
                self.assertEqual(
                    textprov.strip_marks(raw), original + literal + "\n"
                )

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
            "echo ok;git reset --hard",
            "echo ok\ngit restore a.md",
            "git \\\ncheckout main",
            "(git switch main)",
            "git status | git apply patch",
            "MODE=test git -C site switch main",
            "env MODE=test git checkout main",
            "command git checkout main",
            "bash -c 'git checkout main'",
            "sh -c 'echo ok && git -C site reset --hard'",
            "bash -lc 'git restore a.md'",
            "eval 'git checkout main'",
            "eval git checkout main",
            "eval -- 'git checkout main'",
            "/usr/bin/git -Csite restore a.md",
            "git --config-env core.editor=EDITOR reset --hard",
            "git --config-env=core.editor=EDITOR reset --hard",
            "sh -c \"eval 'git reset --hard'\"",
            "nice git restore a.md",
            "nice -n 5 git restore a.md",
            "nice -n5 git restore a.md",
            "nice -5 git restore a.md",
            "nice --adjustment=5 git restore a.md",
            "nice --adjustment 5 git restore a.md",
            "nice -- git restore a.md",
            "nice -n 5 -- git restore a.md",
            "command env MODE=test /usr/bin/nice git restore a.md",
            "nice sh -c 'git restore a.md'",
        ):
            with self.subTest(command=command):
                self.assertTrue(git_moves_tree(command), command)
                self.workspace.before_command(command, "tree")
                self.assertFalse(self.workspace.snapshot_path("tree").exists())
        for command in (
            "git commit -am x",
            "git commit -m 'merge and apply'",
            "git log --grep reset",
            "gh pr checkout 1",
            "echo 'git checkout main' >> notes.md",
            "sed 's/git checkout/git switch/' a.md",
            "grep 'git merge' a.md",
            "git commit -m 'explain git reset'",
            "git -c alias.demo='git checkout main' commit -m text",
            "echo git checkout main",
            "command -v git checkout",
            "echo 'echo ok; git checkout main'",
            'echo "git checkout main"',
            "printf '%s' git reset",
            "echo '&&' git checkout main",
            "echo git; echo checkout main",
            "echo text > git checkout main",
            "# git checkout main\necho safe",
            "bash -c \"echo 'git checkout main'\"",
            "sh -c \"git commit -m 'git reset explained'\"",
            "eval \"echo 'git checkout main'\"",
            "nice echo 'git restore a.md'",
            "nice -n 5 git commit -m 'git restore explained'",
            "echo nice git restore a.md",
        ):
            with self.subTest(command=command):
                self.assertFalse(git_moves_tree(command), command)
                self.workspace.before_command(command, "prose")
                self.assertTrue(self.workspace.snapshot_path("prose").exists())
                self.workspace.after_command("prose")

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
