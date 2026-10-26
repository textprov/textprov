"""Controlled file edits preserve attribution and refuse stale/unsafe targets."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

from textprov import mark
from textprov.export import project
from textprov.prose import ProseEditor, content_hash


def exported(text):
    resolution = dict(content_hash=content_hash(text), scalar_length=len(text), ranges=[
        dict(range=[0, len(text)], voice_context="test", voice_id="writer")
    ] if text else [])
    return project(text, resolution,
                   voice_states=[dict(voice_context="test", voice_id="writer", state="ai")],
                   allow_lossy=True)


class TestProse(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.path = self.root / "draft.md"
        self.editor = ProseEditor(self.root)

    def write(self, text):
        self.path.write_bytes(text.encode("utf-8"))

    def read(self):
        return self.path.read_bytes().decode("utf-8")

    def test_prepare_then_apply_preserves_all_unmodified_bytes(self):
        original = "辻\U000e0100 " + mark("kept", "human") + " old\r\n"
        self.write(original)
        args = dict(expected_content_hash=content_hash(original), old_text="old",
                    replacement=exported("new"))
        prepared = self.editor.edit("draft.md", **args)
        self.assertFalse(prepared["applied"])
        self.assertEqual(original, self.read())
        self.assertTrue(self.editor.edit("draft.md", apply=True, **args)["applied"])
        self.assertEqual(original.replace("old", mark("new")), self.read())

    def test_stale_and_ambiguous_edits_leave_file_untouched(self):
        self.write("old old")
        args = dict(old_text="old", replacement=exported("new"))
        with self.assertRaisesRegex(ValueError, "stale"):
            self.editor.edit("draft.md", expected_content_hash=content_hash("other"), apply=True, **args)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.editor.edit("draft.md", expected_content_hash=content_hash("old old"), apply=True, **args)
        self.assertEqual("old old", self.read())
        self.editor.edit("draft.md", expected_content_hash=content_hash("old old"),
                         replace_all=True, apply=True, **args)
        self.assertEqual(mark("new") + " " + mark("new"), self.read())

    def test_code_and_grapheme_fragments_are_refused(self):
        for text, old, message in (("Use `old`", "old", "protected"),
                                   ("e\u0301", "e", "grapheme")):
            self.write(text)
            with self.assertRaisesRegex(ValueError, message):
                self.editor.edit("draft.md", expected_content_hash=content_hash(text),
                                 old_text=old, replacement=exported("new"), apply=True)
            self.assertEqual(text, self.read())

    def test_symlinks_parent_traversal_source_and_generated_files_refused(self):
        self.write("old")
        (self.root / "alias.md").symlink_to(self.path)
        (self.root / "source.py").write_text("old")
        (self.root / "site" / "public").mkdir(parents=True)
        (self.root / "site" / "public" / "sample.md").write_text("old")
        args = dict(expected_content_hash=content_hash("old"), old_text="old",
                    replacement=exported("new"), apply=True)
        for path in ("alias.md", "../draft.md", "source.py", "site/public/sample.md"):
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                self.editor.edit(path, **args)
        self.assertEqual("old", self.read())

    def test_hardlinks_and_tampered_exports_are_refused(self):
        self.write("old")
        report = exported("new")
        report["text"] += " tampered"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.editor.edit("draft.md", expected_content_hash=content_hash("old"),
                             old_text="old", replacement=report, apply=True)
        os.link(str(self.path), str(self.root / "linked.md"))
        with self.assertRaisesRegex(ValueError, "hard links"):
            self.editor.edit("draft.md", expected_content_hash=content_hash("old"),
                             old_text="old", replacement=exported("new"), apply=True)

    def test_replacement_cannot_attach_a_mark_to_retained_neighbor(self):
        self.write("aOLD")
        with self.assertRaisesRegex(ValueError, "neighboring grapheme"):
            self.editor.edit("draft.md", expected_content_hash=content_hash("aOLD"),
                             old_text="OLD", replacement=exported("\u0301"), apply=True)
        self.assertEqual("aOLD", self.read())

    def test_mode_survives_atomic_replacement(self):
        import os
        import stat
        self.write("old")
        self.path.chmod(0o640)
        original_umask = os.umask(0o077)
        try:
            self.editor.edit("draft.md", expected_content_hash=content_hash("old"),
                             old_text="old", replacement=exported("new"), apply=True)
        finally:
            os.umask(original_umask)
        self.assertEqual(0o640, stat.S_IMODE(self.path.stat().st_mode))

    def test_cli_malformed_export_is_json_refusal(self):
        self.write("old")
        request = dict(path="draft.md", expected_content_hash=content_hash("old"),
                       old_text="old", replacement=None, apply=True)
        result = subprocess.run([sys.executable, "-m", "textprov.prose", "--root", str(self.root)],
                                input=json.dumps(request), text=True, capture_output=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("must be an object", json.loads(result.stderr)["error"])
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual("old", self.read())


if __name__ == "__main__":
    unittest.main()
