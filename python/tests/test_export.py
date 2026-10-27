"""Classification exports preserve original Unicode and require supplied voices."""

import hashlib
import unittest

from textprov import mark
from textprov.export import project, restore


def resolution(text, ranges=None):
    return dict(content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                scalar_length=len(text), ranges=ranges if ranges is not None else [
                    dict(range=[0, len(text)], voice_context="test", voice_id="writer")
                ] if text else [])


MAPPING = [dict(voice_context="test", voice_id="writer", state="ai")]


class TestExport(unittest.TestCase):
    def export(self, text, **options):
        return project(text, resolution(text), voice_states=MAPPING,
                       allow_lossy=True, **options)

    def test_explicit_projection_and_exact_round_trip(self):
        text = "A e\u0301 👩🏽‍💻\r\nZ"
        report = self.export(text)
        self.assertEqual(mark(text), report["text"])
        self.assertEqual(text, restore(report))
        self.assertTrue(report["lossy"])

    def test_legitimate_variations_and_existing_marks_survive_verbatim(self):
        text = "辻\U000e0100 x\U000e0101 ✈\ufe0f"
        report = self.export(text)
        self.assertIn("辻\U000e0100", report["text"])
        self.assertIn("x\U000e0101", report["text"])
        self.assertEqual(text, restore(report))
        self.assertEqual(1, len(report["inserted_at"]))

    def test_unknown_gaps_get_no_new_marks(self):
        text = "hello world"
        info = resolution(text, [
            dict(range=[0, 5], voice_context="test", voice_id="writer"),
            dict(range=[5, 11], voice_context=None, voice_id=None),
        ])
        report = project(text, info, voice_states=MAPPING, allow_lossy=True)
        self.assertEqual(mark("hello") + " world", report["text"])
        self.assertEqual(text, restore(report))

    def test_markdown_code_links_and_crlf_are_preserved(self):
        text = "# Title\r\n\r\nText `code` [link](https://example.test).\r\n```py\r\nx=1\r\n```\r\n"
        report = self.export(text)
        self.assertIn("# Title\r\n", report["text"])
        self.assertIn("`code`", report["text"])
        self.assertIn("(https://example.test)", report["text"])
        self.assertIn("```py\r\nx=1\r\n```", report["text"])
        self.assertEqual(text, restore(report))

    def test_identity_loss_and_missing_voice_require_explicit_choices(self):
        with self.assertRaisesRegex(ValueError, "allow_lossy"):
            project("hello", resolution("hello"), voice_states=MAPPING)
        with self.assertRaisesRegex(ValueError, "missing explicit"):
            project("hello", resolution("hello"), voice_states=[], allow_lossy=True)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            project("hello", resolution("hello"), voice_states=MAPPING * 2, allow_lossy=True)

    def test_stale_hash_and_split_grapheme_are_refused(self):
        with self.assertRaisesRegex(ValueError, "does not describe"):
            project("other", resolution("hello"), voice_states=MAPPING, allow_lossy=True)
        text = "e\u0301"
        info = resolution(text, [
            dict(range=[0, 1], voice_context="test", voice_id="writer"),
            dict(range=[1, 2], voice_context=None, voice_id=None),
        ])
        with self.assertRaisesRegex(ValueError, "grapheme"):
            project(text, info, voice_states=MAPPING, allow_lossy=True)

    def test_tampered_companion_never_removes_legitimate_selector(self):
        report = self.export("辻\U000e0100 X")
        report["inserted_at"] = [1]
        with self.assertRaisesRegex(ValueError, "restored content hash"):
            restore(report)

    def test_empty_export_round_trip(self):
        report = self.export("")
        self.assertEqual("", restore(report))

    def test_malformed_reports_are_explicit_refusals(self):
        for report in (None, [], "text"):
            with self.subTest(report=report), self.assertRaisesRegex(ValueError, "must be an object"):
                restore(report)


if __name__ == "__main__":
    unittest.main()
