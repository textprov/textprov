"""Speaker policy, document preservation, and Unicode copy/paste transport."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from textprov import (
    mark,
    mark_chat,
    mark_chat_parts,
    mark_document,
    mark_document_edit,
    strip_marks,
)
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
                self.assertEqual(
                    mark_chat(pasted + " new", role),
                    pasted + " " + mark_chat("new", role),
                )

    def test_default_chat_scope_keeps_commands_literals_and_urls_copyable(self):
        source = (
            "Run `git status --short` in `/tmp/repo`.\r\n\r\n"
            "```sh\r\nprintf '%s\\n' \"hello\"\r\ngit status\r\n```\r\n\r\n"
            "See https://example.test/a?b=c and [help](https://example.test).\r\n"
        )
        for role, state in (("user", "human"), ("assistant", "ai")):
            with self.subTest(role=role):
                result = mark_chat(source, role)
                self.assertTrue(result.startswith(mark("Run", state)))
                for literal in (
                    "`git status --short`",
                    "`/tmp/repo`",
                    "```sh\r\nprintf '%s\\n' \"hello\"\r\ngit status\r\n```",
                    "https://example.test/a?b=c",
                    "](https://example.test)",
                ):
                    self.assertIn(literal, result)
                self.assertEqual(source, strip_marks(result))
                self.assertEqual(result, mark_chat(result, role))

    def test_chat_scopes_preserve_existing_marks_without_cleaning(self):
        pasted = mark("git status", "ai")
        source = "Use `" + pasted + "` now."
        for role, state in (("user", "human"), ("assistant", "ai")):
            with self.subTest(role=role):
                self.assertEqual(source, mark_chat(source, role, scope="off"))
                self.assertEqual(
                    mark(source, state), mark_chat(source, role, scope="all")
                )
                self.assertIn("`" + pasted + "`", mark_chat(source, role))
                self.assertTrue(
                    mark_chat(source, role).startswith(mark("Use", state))
                )

    def test_container_fences_are_unmarked_in_list_and_blockquote_commands(
        self,
    ):
        samples = (
            "> ```sh\r\n> git status\r\n> ```\r\n",
            "- ```bash\n  git status\n  printf '%s' hello\n  ```\n",
            "1. ~~~shell\n   git status\n   ~~~~\n",
            "> - ```sh\n>   git status\n>   ```\n",
            "- > ```sh\n  > # note\n\n  > git status\n  > ```\n",
            "- - ```sh\n    # note\n\n    git status\n    ```\n",
            "> - - ```sh\n>     # note\n\n>     git status\n>     ```\n",
            "> ```sh\n> git status\n",  # an unfinished fence stays literal
        )
        for sample in samples:
            for role in ("user", "assistant"):
                with self.subTest(sample=sample, role=role):
                    source = "Commands:\n\n" + sample
                    result = mark_chat(source, role)
                    self.assertTrue(result.endswith(sample))
                    self.assertEqual(source, strip_marks(result))

    def test_indented_commands_in_lists_and_quotes_remain_literal(self):
        for source, literal in (
            ("1. Run:\n\n       git status\n", "       git status\n"),
            ("- Run:\n\n      git status\n", "      git status\n"),
            ("> Run:\n>\n>     git status\n", ">     git status\n"),
        ):
            with self.subTest(source=source):
                self.assertIn(literal, mark_chat(source, "assistant"))

    def test_unfinished_inline_code_is_conservatively_literal(self):
        for source, literal in (
            ("Run `git status", "`git status"),
            ("Run ``git `status`", "``git `status`"),
            ("Run `git\r\nstatus", "`git\r\nstatus"),
            ("Run `git status\r\n\r\nMore prose.", "`git status\r\n\r\n"),
        ):
            with self.subTest(source=source):
                result = mark_chat(source, "assistant")
                self.assertIn(literal, result)
                self.assertEqual(source, strip_marks(result))
        self.assertTrue(
            mark_chat("Run `git\n\nMore prose.", "assistant").endswith(
                mark("More prose.")
            )
        )

    def test_chat_marks_heading_prose_without_marking_its_syntax(self):
        source = "## Run `git status` now ##\r\n"
        self.assertEqual(
            "## " + mark("Run") + " `git status` " + mark("now") + " ##\r\n",
            mark_chat(source, "assistant"),
        )
        # A heading-looking line inside a fence still remains literal.
        code = "```sh\n## comment\ngit status\n```\n"
        self.assertEqual(code, mark_chat(code, "assistant"))

    def test_chat_graphemes_and_line_endings_survive_prose_filtering(self):
        prose = "e\u0301 👩🏽‍💻 🇨🇦 ❤️ 辻\U000e0100"
        literal = "`e\u0301 👩🏽‍💻 🇨🇦 ❤️`"
        source = prose + "\r\n" + literal + "\r\n"
        self.assertEqual(
            mark(prose) + "\r\n" + literal + "\r\n",
            mark_chat(source, "assistant"),
        )
        self.assertEqual(source, mark_chat(source, "assistant", scope="off"))

    def test_chat_invalid_scopes_are_rejected_for_both_roles(self):
        for role in ("user", "assistant"):
            for scope in ("safe", "", None, False, [], {}):
                with self.subTest(role=role, scope=scope):
                    with self.assertRaisesRegex(ValueError, "scope"):
                        mark_chat("text", role, scope=scope)
        with self.assertRaisesRegex(ValueError, "role"):
            mark_chat("text", "system", scope="off")
        with self.assertRaisesRegex(ValueError, "string"):
            mark_chat(None, "assistant", scope="off")

    def test_chat_parts_share_fence_and_inline_context(self):
        samples = (
            [
                "Commands:\n\n``",
                "`sh\n",
                "git ",
                "status\n`",
                "``\n\nFinished.",
            ],
            ["Use `git", " status", "` now."],
            ["- > ```sh\n", "  > # note\n\n", "  > git status\n", "  > ```\n"],
        )
        for parts in samples:
            for role in ("user", "assistant"):
                with self.subTest(parts=parts, role=role):
                    result = mark_chat_parts(parts, role)
                    self.assertEqual(len(parts), len(result))
                    self.assertEqual(
                        mark_chat("".join(parts), role), "".join(result)
                    )
                    for source_part, marked_part in zip(parts, result):
                        self.assertEqual(source_part, strip_marks(marked_part))
        self.assertEqual("git ", mark_chat_parts(samples[0], "assistant")[2])
        self.assertEqual(" status", mark_chat_parts(samples[1], "assistant")[1])

    def test_chat_parts_keep_cross_part_graphemes_and_empty_parts(self):
        selector = mark("x")[1:]
        parts = ["", "e", "\u0301", "", " 👩", "\u200d", "💻", " ❤️", ""]
        expected = [
            "",
            "e",
            "\u0301" + selector,
            "",
            " 👩",
            "\u200d",
            "💻" + selector,
            " ❤️" + selector,
            "",
        ]
        self.assertEqual(expected, mark_chat_parts(parts, "assistant"))
        self.assertEqual(
            mark_chat("".join(parts), "assistant"), "".join(expected)
        )
        self.assertEqual([], mark_chat_parts([], "assistant"))
        self.assertEqual(["", ""], mark_chat_parts(["", ""], "user"))

    def test_chat_parts_preserve_supplied_marks_and_selected_scope(self):
        ai = mark("A")
        pua = mark("B", mode="pua")
        parts = [ai[0], ai[1:], "", pua, " `git", " status`"]
        for scope in ("prose", "all", "off"):
            with self.subTest(scope=scope):
                result = mark_chat_parts(parts, "user", scope=scope)
                self.assertEqual(parts[:4], result[:4])
                self.assertEqual(
                    mark_chat("".join(parts), "user", scope=scope),
                    "".join(result),
                )
        self.assertEqual(parts, mark_chat_parts(parts, "user", scope="off"))

    def test_chat_parts_reject_invalid_inputs_and_empty_message_controls(self):
        for parts in (None, "hello", ("text",), ["text", None], [1]):
            with self.subTest(parts=parts):
                with self.assertRaisesRegex(ValueError, "list of strings"):
                    mark_chat_parts(parts, "assistant")
        with self.assertRaisesRegex(ValueError, "role"):
            mark_chat_parts([], "system")
        with self.assertRaisesRegex(ValueError, "scope"):
            mark_chat_parts([], "user", scope="safe")

    def test_long_list_like_prose_completes_without_backtracking_timeout(self):
        source = "-    " * 1000 + "tail"
        request = dict(operation="mark-chat", role="assistant", text=source)
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
            timeout=3,
        )
        self.assertEqual(source, strip_marks(json.loads(result.stdout)["text"]))

    def test_document_changes_preserve_unchanged_human_ai_and_unmarked(self):
        original = (
            mark("Human passage.", "human")
            + "\n"
            + mark("AI passage.")
            + "\nEditor passage.\nOld conclusion.\n"
        )
        proposed = (
            "Human passage.\nAI passage.\nEditor passage.\nNew conclusion.\n"
        )
        result = mark_document_edit(original, proposed)
        self.assertEqual(
            original.rsplit("Old conclusion.", 1)[0]
            + mark("New")
            + " conclusion.\n",
            result,
        )
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
            self.assertEqual(
                supplied + " " + mark("added"),
                mark_document_edit("Words", supplied + " added"),
            )
        self.assertEqual(human, mark_document_edit(human, ai))
        self.assertEqual(ai, mark_document_edit(ai, human))
        self.assertEqual(
            mark("Some", "human") + " " + mark("words", "ai"),
            mark_document_edit(
                mark("Some", "human") + " words", mark("Some words", "ai")
            ),
        )
        self.assertEqual(
            ("Words", human),
            rewrite_edit("Words", "Words", human, preserve_new_marks=True),
        )

    def test_equal_pasted_combining_emoji_and_pua_marks_are_preserved(self):
        plain = "e\u0301 👩🏽‍💻 cafe"
        pasted = mark_chat(plain, "assistant")
        self.assertEqual(pasted, mark_document_edit(plain, pasted))
        pua = mark("Words", "ai", "pua")
        self.assertEqual(pua, mark_document_edit("Words", pua))

    def test_pasted_marks_and_markdown_syntax_survive_new_document(self):
        pasted = mark_chat("Copied answer.", "assistant")
        source = (
            "# Heading\n\n"
            + pasted
            + "\n\nUse `print(1)` and [link](https://example.test).\n"
        )
        marked = mark_document(source)
        self.assertTrue(
            marked.startswith("# " + mark("Heading") + "\n\n" + pasted)
        )
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
            copied = json.loads(
                json.dumps({"text": source}, ensure_ascii=True)
            )["text"]
            path.write_bytes(copied.encode("utf-8"))
            pasted = path.read_bytes().decode("utf-8")
            self.assertEqual(source, pasted)
            # An ordinary editor inserts raw text and retains pasted selectors.
            editor_text = pasted + "Editor words.\n"
            path.write_bytes(editor_text.encode("utf-8"))
            self.assertEqual(editor_text, path.read_bytes().decode("utf-8"))
            final = mark_document_edit(
                editor_text, editor_text + "Agent words.\n"
            )
            self.assertEqual(editor_text + mark("Agent words.") + "\n", final)

    def test_json_cli_uses_the_same_policy(self):
        request = {"operation": "mark-chat", "role": "user", "text": "Hello 👋"}
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            {"text": mark_chat(request["text"], "user")},
            json.loads(result.stdout),
        )
        request = {
            "operation": "mark-document",
            "old_text": mark("Keep", "human"),
            "text": "Keep this",
        }
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            mark("Keep", "human") + " " + mark("this"),
            json.loads(result.stdout)["text"],
        )

    def test_json_cli_rejects_unknown_operations(self):
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input='{"operation":"claim"}',
            capture_output=True,
            text=True,
        )
        self.assertEqual(1, result.returncode)
        self.assertIn("operation", json.loads(result.stderr)["error"])

    def test_json_cli_chat_scope_and_explicit_strip_marks(self):
        source = mark("git", "human") + " `status`\r\n"
        for scope in ("prose", "all", "off"):
            with self.subTest(scope=scope):
                request = dict(
                    operation="mark-chat",
                    role="assistant",
                    text=source,
                    scope=scope,
                )
                result = subprocess.run(
                    [sys.executable, "-m", "textprov.marking"],
                    input=json.dumps(request),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(
                    mark_chat(source, "assistant", scope=scope),
                    json.loads(result.stdout)["text"],
                )
        # Explicit extraction uses the experimental registry, preserving unrelated
        # variation selectors and private-use text rather than sanitizing Unicode.
        source = mark("git status") + " ❤️ x\U000e0102 \ue000\r\n"
        request = dict(operation="strip-marks", text=source)
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            "git status ❤️ x\U000e0102 \ue000\r\n",
            json.loads(result.stdout)["text"],
        )

    def test_json_cli_rejects_invalid_chat_scope_and_strip_text(self):
        for request in (
            dict(operation="mark-chat", role="user", text="hello", scope=None),
            dict(operation="strip-marks", text=None),
        ):
            result = subprocess.run(
                [sys.executable, "-m", "textprov.marking"],
                input=json.dumps(request),
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("error", json.loads(result.stderr))

    def test_json_cli_chat_parts_preserves_complete_message_context(self):
        parts = ["Run `git", " status", "` now.", ""]
        request = dict(
            operation="mark-chat-parts",
            role="assistant",
            parts=parts,
            scope="prose",
        )
        result = subprocess.run(
            [sys.executable, "-m", "textprov.marking"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            {"parts": mark_chat_parts(parts, "assistant")},
            json.loads(result.stdout),
        )
