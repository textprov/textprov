"""Reveal styles must be portable package resources and match the browser SDK."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import textprov

ROOT = Path(__file__).resolve().parents[2]


class TestStylesheet(unittest.TestCase):
    def test_packaged_stylesheet_matches_canonical_browser_styles(self):
        self.assertEqual(
            textprov.stylesheet(),
            (ROOT / "js" / "textprov.css").read_text(encoding="utf-8"),
        )

    def test_stylesheet_does_not_depend_on_the_working_directory(self):
        expected = textprov.stylesheet()
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                self.assertEqual(textprov.stylesheet(), expected)
            finally:
                os.chdir(original)

    def test_sync_check_detects_drift_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "tools" / "sync_display_styles.py"
            source = root / "js" / "textprov.css"
            copies = [
                root / "python" / "textprov" / "textprov.css",
                root / "ruby" / "lib" / "textprov" / "textprov.css",
            ]
            for path in [script, source, *copies]:
                path.parent.mkdir(parents=True, exist_ok=True)
            script.write_bytes((ROOT / "tools" / script.name).read_bytes())
            source.write_bytes(b"/* canonical */\n")

            def run(*args):
                return subprocess.run(
                    [sys.executable, str(script), *args],
                    capture_output=True,
                    text=True,
                    check=False,
                )

            self.assertEqual(run("--check").returncode, 1)
            self.assertTrue(all(not copy.exists() for copy in copies))
            self.assertEqual(run().returncode, 0)
            self.assertTrue(all(copy.read_bytes() == source.read_bytes() for copy in copies))
            self.assertEqual(run("--check").returncode, 0)
            copies[0].write_bytes(b"/* stale */\n")
            self.assertEqual(run("--check").returncode, 1)
            self.assertEqual(copies[0].read_bytes(), b"/* stale */\n")
