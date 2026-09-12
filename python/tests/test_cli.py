"""The CLI is the reference producer's user interface; smoke-test each verb."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import textprov
from textprov.__main__ import main

AI = chr(textprov.default_mapping().selectors["ai"])


class TestCli(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, name, text):
        # open() rather than Path.write_text: the newline argument to
        # Path.write_text is Python 3.10+, and this package supports 3.9.
        path = Path(self.dir.name) / name
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return str(path)

    def run_cli(self, *argv):
        out = Path(self.dir.name) / "out.txt"
        self.assertEqual(main(["-o", str(out), *argv]), 0)
        with open(out, encoding="utf-8", newline="") as handle:
            return handle.read()

    def test_mark_convert_strip_round_trip(self):
        source = "Written by a human."
        path = self.write("s.txt", source)
        marked = self.run_cli("mark", path)
        self.assertEqual(marked, textprov.mark(source))
        pua = self.run_cli("convert", self.write("m.txt", marked), "--from", "vs", "--to", "pua")
        self.assertEqual(pua, textprov.convert(marked, "vs", "pua"))
        self.assertEqual(self.run_cli("strip", self.write("p.txt", pua)), source)

    def test_mark_state_and_mode_flags(self):
        path = self.write("s.txt", "Hi")
        self.assertEqual(self.run_cli("mark", "--human", path), textprov.mark("Hi", "human"))
        self.assertEqual(
            self.run_cli("mark", "--mode", "pua", path), textprov.mark("Hi", "ai", "pua")
        )

    def test_mark_added(self):
        old = self.write("old.txt", "abc")
        new = self.write("new.txt", "abXc")
        self.assertEqual(self.run_cli("mark-added", old, new), "abX" + AI + "c")

    def test_render_and_inspect(self):
        path = self.write("m.txt", "a" + AI)
        self.assertEqual(self.run_cli("render", path), textprov.to_html("a" + AI))
        self.assertIn(
            'class="x x-ai"', self.run_cli("render", "--class-prefix", "x", path)
        )
        self.assertIn("ai_vs: 1", self.run_cli("inspect", path))

    def test_stdout_is_used_when_no_output_file(self):
        path = self.write("s.txt", "Hi")
        buffer = io.BytesIO()
        stdout = io.TextIOWrapper(buffer, encoding="utf-8")
        with redirect_stdout(stdout):
            main(["mark", path])
            main(["mark", path])  # main() must not close stdout behind itself
        self.assertEqual(
            buffer.getvalue().decode("utf-8"), textprov.mark("Hi") * 2
        )

    def test_crlf_survives(self):
        path = self.write("s.txt", "a\r\nb")
        self.assertEqual(self.run_cli("mark", path), "a" + AI + "\r\nb" + AI)
