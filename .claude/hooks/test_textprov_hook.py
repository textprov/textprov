"""Tests for textprov_hook.py: python3 -m unittest discover -s .claude/hooks"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import textprov_hook as hook  # noqa: E402  (puts ../../python on the path)
import textprov  # noqa: E402

AI = "\U000E0101"
HUMAN = "\U000E0100"


def ai(text):
    return textprov.mark(text, state="ai")


def remark(old, new, **options):
    options.setdefault("shingles", set())
    return hook.remark(old, new, **options)


def states(text):
    return [(s, t) for s, t in textprov.runs(text, strip=True)]


class TestRemark(unittest.TestCase):
    def test_new_file_is_all_ai(self):
        self.assertEqual(remark("", "two words\n"), ai("two words\n"))

    def test_unchanged_text_gains_no_state(self):
        old = "first line\nsecond line\n"
        self.assertEqual(remark(old, old), old)

    def test_only_the_added_line_is_marked(self):
        old = "first\nthird\n"
        self.assertEqual(
            remark(old, "first\nsecond\nthird\n"),
            "first\n" + ai("second") + "\nthird\n",
        )

    def test_changed_line_marks_only_the_middle(self):
        self.assertEqual(
            remark("the quick fox\n", "the slow fox\n"),
            "the " + ai("slow") + " fox\n",
        )

    def test_existing_marks_survive_a_rewrite_typed_without_them(self):
        old = "kept " + textprov.mark("human words", state="human") + "\n"
        new = "kept human words\nmore\n"
        self.assertEqual(remark(old, new), old + ai("more") + "\n")

    def test_stripping_the_result_gives_back_what_was_written(self):
        new = "# T\n\nSome *prose* with `code` and [a link](http://x.y/z).\n"
        self.assertEqual(textprov.strip_marks(remark("", new)), new)

    def test_marking_is_idempotent(self):
        once = remark("", "plain prose here\n")
        self.assertEqual(remark(once, once), once)

    def test_without_carry_disk_content_wins(self):
        old = ai("was marked") + "\n"
        self.assertEqual(remark(old, "was marked\n", carry=False), "was marked\n")


class TestMarkdown(unittest.TestCase):
    def unmarked(self, source, fragment):
        marked = remark("", source)
        self.assertEqual(textprov.strip_marks(marked), source)
        self.assertIn(fragment, marked)

    def test_fenced_code(self):
        self.unmarked("text\n\n```json\n{\"a\": 1}\n```\n\nmore\n", '```json\n{"a": 1}\n```')

    def test_inline_code(self):
        self.unmarked("call `mark(text)` now\n", "`mark(text)`")

    def test_heading(self):
        self.unmarked("## Producer rules\n\nbody\n", "## Producer rules\n")

    def test_setext_heading(self):
        self.unmarked("Title\n=====\n\nbody\n", "Title\n=====\n")

    def test_link_destination(self):
        self.unmarked("see [the spec](../SPEC.md#markup) here\n", "](../SPEC.md#markup)")

    def test_reference_link_and_definition(self):
        source = "see [the spec][spec] and [spec]\n\n[spec]: http://x.y/z\n"
        self.unmarked(source, "][spec]")
        self.unmarked(source, "[spec]: http://x.y/z\n")
        self.unmarked(source, " [spec]\n")

    def test_list_markers_and_task_boxes(self):
        marked = remark("", "- one\n1. two\n- [x] three\n> quote\n")
        self.assertTrue(marked.startswith("- o" + AI))
        self.assertIn("\n1. t" + AI, marked)
        self.assertIn("\n- [x] t" + AI, marked)
        self.assertIn("\n> q" + AI, marked)

    def test_emphasis_delimiters(self):
        marked = remark("", "a **bold** word\n")
        self.assertIn("**b" + AI, marked)
        self.assertIn("d" + AI + "**", marked)

    def test_table(self):
        marked = remark("", "| a | b |\n| --- | :-: |\n| c | d |\n")
        self.assertIn("| --- | :-: |\n", marked)
        self.assertIn("| a" + AI + " | b" + AI + " |", marked)

    def test_html_and_front_matter(self):
        self.unmarked("---\nname: x\n---\n\n<b>bold</b> &amp; text\n", "---\nname: x\n---\n")
        self.unmarked("<!-- note\nmore -->\ntext\n", "<!-- note\nmore -->")
        self.unmarked("a <b>bold</b> &amp; b\n", "<b>")

    def test_prose_is_marked(self):
        self.assertEqual(
            states(remark("", "Hello, world.\n")),
            [("ai", "Hello, world."), (None, "\n")],
        )


class TestHuman(unittest.TestCase):
    def setUp(self):
        self.prompt = "Please get this repo eating its own dogfood."
        recorded = textprov.mark(self.prompt, state="human")
        words = [m.group() for m in hook.words_of(textprov.strip_marks(recorded))]
        n = hook.HUMAN_MIN_WORDS
        self.shingles = {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}

    def test_verbatim_quote_is_human(self):
        marked = hook.remark("", "He said:\n\n> " + self.prompt + "\n\nOK\n", shingles=self.shingles)
        runs = states(marked)
        self.assertIn(("human", self.prompt), runs)
        self.assertIn(("ai", "He said:"), runs)

    def test_quote_survives_reflow(self):
        source = "> Please get this repo\n> eating its own dogfood.\n"
        marked = hook.remark("", source, shingles=self.shingles)
        self.assertNotIn(AI, marked)
        self.assertIn(HUMAN, marked)

    def test_paraphrase_is_ai(self):
        marked = hook.remark("", "Get the repo to eat its dogfood.\n", shingles=self.shingles)
        self.assertNotIn(HUMAN, marked)

    def test_short_overlap_is_ai(self):
        marked = hook.remark("", "its own dogfood.\n", shingles=self.shingles)
        self.assertNotIn(HUMAN, marked)


class TestEdit(unittest.TestCase):
    def apply(self, raw, old, new, **options):
        options.setdefault("shingles", set())
        result = hook.rewrite_edit(raw, old, new, **options)
        self.assertIsNotNone(result)
        self.assertEqual(raw.count(result[0]), 1 if not options.get("replace_all") else raw.count(result[0]))
        return raw.replace(result[0], result[1]), result

    def test_matches_through_marks(self):
        raw = "intro\n" + ai("the quick fox") + "\nend\n"
        out, _ = self.apply(raw, "quick fox", "slow fox")
        self.assertEqual(textprov.strip_marks(out), "intro\nthe slow fox\nend\n")
        self.assertEqual(states(out)[1], ("ai", "the slow fox"))

    def test_unmarked_neighbours_stay_unmarked(self):
        raw = "alpha beta gamma\n"
        out, _ = self.apply(raw, "beta", "delta")
        self.assertEqual(out, "alpha " + ai("delta") + " gamma\n")

    def test_context_in_old_string_keeps_its_state(self):
        human = textprov.mark("alpha beta", state="human")
        out, _ = self.apply(human + " gamma\n", "alpha beta gamma", "alpha beta new gamma")
        self.assertEqual(out, human + " " + ai("new") + " gamma\n")

    def test_edit_inside_code_fence_is_unmarked(self):
        raw = "text\n\n```\nx = 1\n```\n"
        out, _ = self.apply(raw, "x = 1", "x = 2")
        self.assertEqual(out, "text\n\n```\nx = 2\n```\n")

    def test_absent_old_string(self):
        self.assertIsNone(hook.rewrite_edit("abc\n", "zzz", "y", shingles=set()))

    def test_ambiguous_once_marks_are_ignored(self):
        raw = "word here\n" + ai("word") + " there\n"
        with self.assertRaises(hook.Ambiguous):
            hook.rewrite_edit(raw, "word", "term", shingles=set())

    def test_replace_all_uniform(self):
        raw = "a cat\nb cat\n"
        out, (old, new) = self.apply(raw, "cat", "dog", replace_all=True)
        self.assertEqual(out, "a " + ai("dog") + "\nb " + ai("dog") + "\n")

    def test_replace_all_mixed_marks_is_refused(self):
        raw = "a cat\n" + ai("b cat") + "\n"
        with self.assertRaises(hook.Ambiguous):
            hook.rewrite_edit(raw, "cat", "dog", replace_all=True, shingles=set())


if __name__ == "__main__":
    unittest.main()
