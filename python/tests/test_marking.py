"""Speaker policy, document preservation, and Unicode copy/paste transport."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from textprov import (mark, mark_chat, mark_document, mark_document_edit,
                      strip_marks)
from textprov.editing import rewrite_edit


class TestMarking(unittest.TestCase):
    def test_chat_speaker_policy_needs_no_claim(self):
        text = "A café 👩🏽‍💻\n"
        self.assertEqual(mark(text, "human"), mark_chat(text, "user"))
        self.assertEqual(mark(text, "ai"), mark_chat(text, "assistant"))
        with self.assertRaisesRegex(ValueError, "role"):
            mark_chat(text, "system")
        with self.assertRaisesRegex(ValueError, "string"):
            mark_chat(None, "user")

    def test_chat_copy_between_speakers_preserves_supplied_marks(self):
        human = mark_chat("My words.", "user")
        ai = mark_chat("An answer.", "assistant")
        for role in ("user", "assistant"):
            with self.subTest(role=role):
                pasted = human + " " + ai
                self.assertEqual(pasted, mark_chat(pasted, role))
                self.assertEqual(mark_chat(pasted + " new", role),
                                 pasted + " " + mark_chat("new", role))

    def test_document_changes_preserve_unchanged_human_ai_and_unmarked(self):
        original = (mark("Human passage.", "human") + "\n" +
                    mark("AI passage.") + "\nEditor passage.\nOld conclusion.\n")
        proposed = "Human passage.\nAI passage.\nEditor passage.\nNew conclusion.\n"
        result = mark_document_edit(original, proposed)
        self.assertEqual(original.rsplit("Old conclusion.", 1)[0] +
                         mark("New") + " conclusion.\n", result)
        self.assertEqual(proposed, strip_marks(result))
        self.assertEqual(result, mark_document_edit(result, proposed))

    def test_document_replacement_preserves_equal_marked_word_context(self):
        original = mark("Keep these words", "human") + " old ending"
        proposed = "Keep these words new ending"
        result = mark_document_edit(original, proposed)
        self.assertTrue(result.startswith(mark("Keep these words", "human")))
        self.assertTrue(result.endswith(mark("new") + " ending"))

    def test_equal_pasted_marks_are_preserved_where_source_had_none(self):
        human = mark("Words", "human")
        ai = mark("Words", "ai")
        for supplied in (human, ai):
            self.assertEqual(supplied, mark_document_edit("Words", supplied))
            self.assertEqual(supplied + " " + mark("added"),
                             mark_document_edit("Words", supplied + " added"))
        self.assertEqual(human, mark_document_edit(human, ai))
        self.assertEqual(ai, mark_document_edit(ai, human))
        self.assertEqual(mark("Some", "human") + " " + mark("words", "ai"),
                         mark_document_edit(mark("Some", "human") + " words",
                                            mark("Some words", "ai")))
        self.assertEqual(("Words", human),
                         rewrite_edit("Words", "Words", human,
                                      preserve_new_marks=True))

    def test_equal_pasted_combining_emoji_and_pua_marks_are_preserved(self):
        plain = "e\u0301 👩🏽‍💻 cafe"
        pasted = mark_chat(plain, "assistant")
        self.assertEqual(pasted, mark_document_edit(plain, pasted))
        pua = mark("Words", "ai", "pua")
        self.assertEqual(pua, mark_document_edit("Words", pua))

    def test_pasted_marks_and_markdown_syntax_survive_new_document(self):
        pasted = mark_chat("Copied answer.", "assistant")
        source = "# Heading\n\n" + pasted + "\n\nUse `print(1)` and [link](https://example.test).\n"
        marked = mark_document(source)
        self.assertTrue(marked.startswith("# Heading\n\n" + pasted))
        self.assertIn("`print(1)`", marked)
        self.assertIn("](https://example.test)", marked)
        self.assertEqual(strip_marks(source), strip_marks(marked))
        self.assertEqual(marked, mark_document(marked))

    def test_copy_paste_utf8_json_and_plain_editor_roundtrip(self):
        human = mark_chat("Human e\u0301 👩🏽‍💻", "user")
        ai = mark_chat("AI 辻\U000e0100 answer", "assistant")
        source = human + "\n" + ai + "\r\n"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pasted.md"
            # The clipboard's text payload crosses JSON and UTF-8 boundaries.
            copied = json.loads(json.dumps({"text": source}, ensure_ascii=True))["text"]
            path.write_bytes(copied.encode("utf-8"))
            pasted = path.read_bytes().decode("utf-8")
            self.assertEqual(source, pasted)
            # An ordinary editor inserts raw text and retains pasted selectors.
            editor_text = pasted + "Editor words.\n"
            path.write_bytes(editor_text.encode("utf-8"))
            self.assertEqual(editor_text, path.read_bytes().decode("utf-8"))
            final = mark_document_edit(editor_text,
                                       editor_text + "Agent words.\n")
            self.assertEqual(editor_text + mark("Agent words.") + "\n", final)

    def test_json_cli_uses_the_same_policy(self):
        request = {"operation": "mark-chat", "role": "user", "text": "Hello 👋"}
        result = subprocess.run([sys.executable, "-m", "textprov.marking"],
                                input=json.dumps(request), capture_output=True,
                                text=True, check=True)
        self.assertEqual({"text": mark_chat(request["text"], "user")},
                         json.loads(result.stdout))
        request = {"operation": "mark-document", "old_text": mark("Keep", "human"),
                   "text": "Keep this"}
        result = subprocess.run([sys.executable, "-m", "textprov.marking"],
                                input=json.dumps(request), capture_output=True,
                                text=True, check=True)
        self.assertEqual(mark("Keep", "human") + " " + mark("this"),
                         json.loads(result.stdout)["text"])

    def test_json_cli_rejects_unknown_operations(self):
        result = subprocess.run([sys.executable, "-m", "textprov.marking"],
                                input='{"operation":"claim"}', capture_output=True,
                                text=True)
        self.assertEqual(1, result.returncode)
        self.assertIn("operation", json.loads(result.stderr)["error"])
