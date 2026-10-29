"""Public authoring/check APIs and their command-line transports."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import textprov

DOCS = ("markdown", "markdoc", "directives")


class CheckTransportTests(unittest.TestCase):
    def command(self, module, args=(), request=None):
        env = dict(
            os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1])
        )
        return subprocess.run(
            [sys.executable, "-m", module, *args],
            input=None if request is None else json.dumps(request),
            text=True,
            capture_output=True,
            env=env,
        )

    def test_public_document_profile_and_check(self):
        source = (
            '{% card title="Literal" %}\n:::note[Label]\n## Heading\n::::\n'
        )
        marked = textprov.mark_document(source, profile=DOCS)
        self.assertIn('{% card title="Literal" %}', marked)
        self.assertIn("## " + textprov.mark("Heading"), marked)
        self.assertEqual(textprov.check_text("", marked, profile=DOCS), [])
        self.assertEqual(
            textprov.mark_document_edit("", source, profile=DOCS), marked
        )

    def test_json_document_profile_and_check(self):
        source = ":::note\n## Title\n:::\n"
        result = self.command(
            "textprov.marking",
            request={
                "operation": "mark-document",
                "text": source,
                "profile": list(DOCS),
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        marked = json.loads(result.stdout)["text"]
        self.assertEqual(marked, textprov.mark_document(source, profile=DOCS))
        checked = self.command(
            "textprov.marking",
            request={
                "operation": "check",
                "before": "",
                "after": marked,
                "profile": list(DOCS),
            },
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout), {"problems": []})

    def test_json_failure_preserve_only_and_invalid_profile(self):
        request = {"operation": "check", "before": "", "after": "new"}
        result = self.command("textprov.marking", request=request)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(json.loads(result.stdout)["problems"]), 3)
        request["preserve_only"] = True
        result = self.command("textprov.marking", request=request)
        self.assertEqual(result.returncode, 0, result.stderr)
        request["profile"] = "missing"
        result = self.command("textprov.marking", request=request)
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "unknown syntax profile", json.loads(result.stderr)["error"]
        )

    def test_cli_locations_preserve_only_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            before, after = [
                Path(directory) / name for name in ("old.md", "new.md")
            ]
            before.write_bytes(b"old\r\n")
            after.write_bytes(b"old\r\nX")
            args = ["check", "--before", str(before), "--after", str(after)]
            result = self.command("textprov", args)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                result.stdout,
                str(after)
                + ":2:1: new prose cluster has no supported origin mark\n",
            )
            result = self.command("textprov", args + ["--preserve-only"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            result = self.command("textprov", args + ["--profile", "missing"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown syntax profile", result.stderr)
            before.unlink()
            result = self.command("textprov", args)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_composition_plain_and_output(self):
        with tempfile.TemporaryDirectory() as directory:
            before, after, output = [
                Path(directory) / name
                for name in ("old.md", "new.md", "out.txt")
            ]
            before.write_bytes(b"")
            source = ":::note\nBody\n:::\n"
            after.write_bytes(
                textprov.mark_document(source, profile=DOCS).encode("utf-8")
            )
            args = [
                "-o",
                str(output),
                "check",
                "--before",
                str(before),
                "--after",
                str(after),
            ]
            result = self.command(
                "textprov", args + ["--profile", ",".join(DOCS)]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), b"")
            result = self.command("textprov", args + ["--profile", "plain"])
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"no supported origin mark", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
