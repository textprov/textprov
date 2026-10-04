"""Tests for provider-neutral prose marking and mark-aware edits."""

import unittest

import textprov
from textprov import editing

AI = "\U000e0101"
HUMAN = "\U000e0100"


def ai(text):
    return textprov.mark(text, state="ai")


def remark(old, new, **options):
    options.setdefault("shingles", set())
    return editing.remark(old, new, **options)


def states(text):
    return [(s, t) for s, t in textprov.runs(text, strip=True)]


class TestRemark(unittest.TestCase):
    def test_plain_text_mode_does_not_protect_markdown(self):
        self.assertEqual(
            editing.remark("", "# Title\n`code`", markdown=False),
            ai("# Title\n`code`"),
        )

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

    def test_deleted_prepend_rechecks_the_surviving_cluster(self):
        raw = textprov.mark("\u0600 👍", "human")
        out = remark(raw, " 👍")
        self.assertEqual(out, " " + textprov.mark("👍", "human"))
        self.assertEqual(textprov.strip_marks(out), " 👍")
        self.assertEqual(states(out), [(None, " "), ("human", "👍")])

    def test_without_carry_disk_content_wins(self):
        old = ai("was marked") + "\n"
        self.assertEqual(
            remark(old, "was marked\n", carry=False), "was marked\n"
        )


class TestMarkdown(unittest.TestCase):
    def unmarked(self, source, fragment):
        marked = remark("", source)
        self.assertEqual(textprov.strip_marks(marked), source)
        self.assertIn(fragment, marked)

    def test_fenced_code(self):
        self.unmarked(
            'text\n\n```json\n{"a": 1}\n```\n\nmore\n', '```json\n{"a": 1}\n```'
        )

    def test_inline_code(self):
        self.unmarked("call `mark(text)` now\n", "`mark(text)`")

    def test_dollar_math_preserves_surrounding_prose_marks(self):
        for math in (
            r"$\rho$",
            r"$\rho + \alpha$",
            r"$$\rho$$",
            "$$\n\\rho + \\alpha\n$$",
        ):
            with self.subTest(math=math):
                source = "before " + math + " after\n"
                self.assertEqual(
                    remark("", source), ai("before ") + math + ai(" after\n")
                )

    def test_multiple_math_spans(self):
        self.assertEqual(
            remark("", r"$\rho$ and $\alpha$"),
            r"$\rho$" + ai(" and ") + r"$\alpha$",
        )

    def test_escaped_dollars_do_not_delimit_math(self):
        self.assertEqual(
            remark("", r"cost \$five and \$ten"),
            ai("cost ") + r"\$" + ai("five and ") + r"\$" + ai("ten"),
        )

    def test_escaped_dollar_inside_math(self):
        self.unmarked(r"before $\text{\$} + \rho$ after", r"$\text{\$} + \rho$")

    def test_unmatched_dollar_does_not_protect_prose(self):
        self.assertEqual(
            remark("", "$unfinished prose"), ai("$unfinished prose")
        )

    def test_currency_and_invalid_math_delimiters_are_prose(self):
        for source in (
            "The total is $5 for coffee and $3 for tea.\n",
            "$5, $3, and $12.50\n",
            "before $ x$ after",
            "before $x $ after",
            "before $x$2 after",
        ):
            with self.subTest(source=source):
                marked = remark("", source)
                self.assertEqual(marked, ai(source))
                self.assertEqual(textprov.strip_marks(marked), source)
                self.assertIn(("ai", source.rstrip()), states(marked))

    def test_math_does_not_cross_blank_lines(self):
        for gap in ("\n\n", "\n \t\n", "\r\n\t\r\n", "\r\r"):
            for delimiter in ("$", "$$"):
                with self.subTest(gap=gap, delimiter=delimiter):
                    source = (
                        delimiter
                        + "first"
                        + gap
                        + "middle"
                        + gap
                        + "last"
                        + delimiter
                    )
                    marked = remark("", source)
                    self.assertEqual(marked, ai(source))
                    self.assertEqual(textprov.strip_marks(marked), source)
                    self.assertEqual(states(marked), [("ai", source)])
        for source in (
            "$5 for coffee\n\nmore prose\n\n$12 for tea",
            "$first\\\n\nmiddle\n\nlast$",
            "$$first\\\n\nmiddle\n\nlast$$",
        ):
            with self.subTest(source=source):
                self.assertEqual(remark("", source), ai(source))

    def test_single_newline_and_numeric_math_are_protected(self):
        for math in (
            "$x +\ny$",
            "$x +\r\ny$",
            "$x +\ry$",
            "$x\\\ny$",
            "$5 + 3$",
            "$$ x $$",
        ):
            with self.subTest(math=math):
                self.assertEqual(
                    remark("", "before " + math + " after"),
                    ai("before ") + math + ai(" after"),
                )

    def test_math_protection_preserves_existing_prose_states(self):
        human = textprov.mark("human prose", state="human")
        old = human + " " + ai("agent prose") + "\n"
        new = "human prose agent prose " + r"$\rho$" + "\n"
        self.assertEqual(remark(old, new), old[:-1] + " " + r"$\rho$" + "\n")

    def test_heading(self):
        self.unmarked("## Producer rules\n\nbody\n", "## Producer rules\n")

    def test_setext_heading(self):
        self.unmarked("Title\n=====\n\nbody\n", "Title\n=====\n")
        self.unmarked("Title\n---\n\nbody\n", "Title\n---\n")

    def test_prose_above_a_thematic_break_is_marked(self):
        for rule in ("***", "___", "- - -"):
            marked = remark("", "Agent prose\n" + rule + "\n")
            self.assertTrue(marked.startswith(ai("Agent prose") + "\n"), rule)
            self.assertTrue(marked.endswith("\n" + rule + "\n"), rule)

    def test_link_destination(self):
        self.unmarked(
            "see [the spec](../SPEC.md#markup) here\n", "](../SPEC.md#markup)"
        )

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
        self.unmarked(
            "---\nname: x\n---\n\n<b>bold</b> &amp; text\n",
            "---\nname: x\n---\n",
        )
        self.unmarked("<!-- note\nmore -->\ntext\n", "<!-- note\nmore -->")
        self.unmarked("a <b>bold</b> &amp; b\n", "<b>")

    def test_prose_is_marked(self):
        self.assertEqual(
            states(remark("", "Hello, world.\n")),
            [("ai", "Hello, world."), (None, "\n")],
        )


class TestHuman(unittest.TestCase):
    def test_shingles_only_include_human_runs(self):
        human = textprov.mark("one two three", state="human")
        marked = human + " " + ai("four five six")
        self.assertEqual(
            editing.human_shingles([marked], min_words=2),
            {
                ("one", "two"),
                ("two", "three"),
            },
        )

    def test_custom_word_threshold(self):
        human = textprov.mark("one two three", state="human")
        shingles = editing.human_shingles([human], min_words=2)
        self.assertEqual(
            editing.remark("", "one two", shingles=shingles, min_words=2),
            textprov.mark("one two", state="human"),
        )

    def test_default_does_not_read_prompt_logs(self):
        self.assertEqual(
            editing.remark("", "one two three four five"),
            ai("one two three four five"),
        )

    def test_invalid_word_threshold(self):
        for operation in (
            lambda: editing.human_shingles([], min_words=0),
            lambda: editing.remark("", "text", min_words=0),
            lambda: editing.rewrite_edit("text", "text", "new", min_words=0),
        ):
            with self.assertRaises(ValueError):
                operation()

    def setUp(self):
        self.prompt = "Please get this repo eating its own dogfood."
        recorded = textprov.mark(self.prompt, state="human")
        words = [
            m.group() for m in editing.words_of(textprov.strip_marks(recorded))
        ]
        n = editing.HUMAN_MIN_WORDS
        self.shingles = {
            tuple(words[i : i + n]) for i in range(len(words) - n + 1)
        }

    def test_verbatim_quote_is_human(self):
        marked = editing.remark(
            "",
            "He said:\n\n> " + self.prompt + "\n\nOK\n",
            shingles=self.shingles,
        )
        runs = states(marked)
        self.assertIn(("human", self.prompt), runs)
        self.assertIn(("ai", "He said:"), runs)

    def test_quote_survives_reflow(self):
        source = "> Please get this repo\n> eating its own dogfood.\n"
        marked = editing.remark("", source, shingles=self.shingles)
        self.assertNotIn(AI, marked)
        self.assertIn(HUMAN, marked)

    def test_paraphrase_is_ai(self):
        marked = editing.remark(
            "", "Get the repo to eat its dogfood.\n", shingles=self.shingles
        )
        self.assertNotIn(HUMAN, marked)

    def test_short_overlap_is_ai(self):
        marked = editing.remark(
            "", "its own dogfood.\n", shingles=self.shingles
        )
        self.assertNotIn(HUMAN, marked)


class TestEdit(unittest.TestCase):
    def apply(self, raw, old, new, **options):
        options.setdefault("shingles", set())
        result = editing.rewrite_edit(raw, old, new, **options)
        assert result is not None
        self.assertEqual(
            raw.count(result[0]),
            1 if not options.get("replace_all") else raw.count(result[0]),
        )
        return raw.replace(result[0], result[1]), result

    def test_matches_through_marks(self):
        raw = "intro\n" + ai("the quick fox") + "\nend\n"
        out, _ = self.apply(raw, "quick fox", "slow fox")
        self.assertEqual(
            textprov.strip_marks(out), "intro\nthe slow fox\nend\n"
        )
        self.assertEqual(states(out)[1], ("ai", "the slow fox"))

    def test_unmarked_neighbours_stay_unmarked(self):
        raw = "alpha beta gamma\n"
        out, _ = self.apply(raw, "beta", "delta")
        self.assertEqual(out, "alpha " + ai("delta") + " gamma\n")

    def test_context_in_old_string_keeps_its_state(self):
        human = textprov.mark("alpha beta", state="human")
        out, _ = self.apply(
            human + " gamma\n", "alpha beta gamma", "alpha beta new gamma"
        )
        self.assertEqual(out, human + " " + ai("new") + " gamma\n")

    def test_edit_inside_code_fence_is_unmarked(self):
        raw = "text\n\n```\nx = 1\n```\n"
        out, _ = self.apply(raw, "x = 1", "x = 2")
        self.assertEqual(out, "text\n\n```\nx = 2\n```\n")

    def test_edit_inside_math_is_unmarked(self):
        for math in (r"$\rho$", r"$$\rho$$", "$$\n\\rho\n$$"):
            with self.subTest(math=math):
                raw = ai("before") + " " + math + " " + ai("after")
                out, _ = self.apply(raw, r"\rho", r"\alpha")
                self.assertEqual(out, raw.replace(r"\rho", r"\alpha"))

    def assert_valid_selectors(self, marked):
        for cluster in textprov.segments(marked):
            selectors = [c for c in cluster if c in (AI, HUMAN)]
            if selectors:
                self.assertEqual(selectors, [cluster[-1]])
                self.assertGreater(len(cluster), 1)
                base = cluster[:-1]
                self.assertEqual(ai(base), base + AI)
        self.assertEqual(
            [textprov.strip_marks(c) for c in textprov.segments(marked)],
            textprov.segments(textprov.strip_marks(marked)),
        )

    def test_partial_grapheme_edits_relabel_the_changed_clusters(self):
        for source, old, new in (
            ("e\u0301", "e", "X"),
            ("e\u0301", "\u0301", "\u0300"),
            ("e\u0301", "\u0301", ""),
            ("👩\u200d💻", "💻", "🔬"),
            ("👩\u200d💻", "\u200d", ""),
            ("👍🏽", "🏽", "🏻"),
            ("👍🏽", "🏽", ""),
            ("का", "ा", "ि"),
            ("क्ष", "ष", "त"),
            ("\u1100\u1161\u11a8", "\u1161", "\u1162"),
            ("\u1100\u1161\u11a8", "\u1161", ""),
            ("🇨🇦", "🇦", "🇧"),
            ("❤\ufe0f", "\ufe0f", "\ufe0e"),
        ):
            for state in (None, "human", "ai"):
                with self.subTest(source=source, old=old, state=state):
                    marked = textprov.mark(source, state) if state else source
                    raw = (
                        textprov.mark("L ", "human")
                        + marked
                        + textprov.mark(" R", "human")
                    )
                    changed = source.replace(old, new)
                    out, _ = self.apply(raw, old, new)
                    self.assertEqual(
                        textprov.strip_marks(out), "L " + changed + " R"
                    )
                    self.assertEqual(
                        states(out),
                        [
                            ("human", "L"),
                            (None, " "),
                            ("ai", changed),
                            (None, " "),
                            ("human", "R"),
                        ],
                    )
                    self.assert_valid_selectors(out)

    def test_edits_that_join_neighbouring_clusters_relabel_the_whole_cluster(
        self,
    ):
        for source, old, new, changed in (
            ("aX", "X", "\u0301", "a\u0301"),
            ("👩X", "X", "\u200d💻", "👩\u200d💻"),
            ("\u1100X", "X", "\u1161", "\u1100\u1161"),
            ("Xa", "X", "\u0600", "\u0600a"),
            ("e \u0301", " ", "", "e\u0301"),
            ("👩 💻", " ", "\u200d", "👩\u200d💻"),
            ("\u1100 \u1161", " ", "", "\u1100\u1161"),
            ("🇦🇧🇨🇩", "🇦", "", "🇧🇨🇩"),
        ):
            with self.subTest(source=source):
                raw = textprov.mark(source, "human")
                out, _ = self.apply(raw, old, new)
                self.assertEqual(textprov.strip_marks(out), changed)
                self.assertEqual(states(out), [("ai", changed)])
                self.assert_valid_selectors(out)

    def test_unchanged_graphemes_keep_their_marks(self):
        kept = textprov.mark("e\u0301 👩\u200d💻 👍🏽 का \u1100\u1161", "human")
        raw = kept + " old " + kept
        out, _ = self.apply(raw, "old", "new")
        self.assertEqual(out, kept + " " + ai("new") + " " + kept)
        self.assertEqual(
            textprov.strip_marks(out),
            textprov.strip_marks(raw).replace("old", "new"),
        )
        self.assertIn(("human", textprov.strip_marks(kept)), states(out))
        self.assert_valid_selectors(out)

    def test_partial_grapheme_no_op_preserves_marks(self):
        for source, old in (
            ("e\u0301", "e"),
            ("👩\u200d💻", "💻"),
            ("का", "ा"),
            ("\u0600 👍", "\u0600"),
        ):
            with self.subTest(source=source):
                raw = textprov.mark(source, "human")
                out, _ = self.apply(raw, old, old)
                self.assertEqual(out, raw)
                self.assertEqual(states(out), [("human", source)])
                self.assert_valid_selectors(out)

    def test_replacements_leave_whitespace_and_control_breaks_unmarked(self):
        for new in (
            " ",
            "\u0085",
            "\x00",
            "\x1c",
            "\u00ad",
            "\u200b",
            "\u2060",
            "\ufeff",
            "\r\n",
        ):
            with self.subTest(new=new):
                raw = textprov.mark("aXb", "human")
                out, _ = self.apply(raw, "X", new)
                self.assertEqual(
                    out,
                    textprov.mark("a", "human")
                    + new
                    + textprov.mark("b", "human"),
                )
                self.assertEqual(textprov.strip_marks(out), "a" + new + "b")
                self.assertEqual(
                    textprov.runs(out, strip=True, merge_whitespace=False),
                    [("human", "a"), (None, new), ("human", "b")],
                )
                self.assert_valid_selectors(out)

    def test_deleted_prepend_leaves_whitespace_unmarked_and_emoji_human(self):
        for whitespace in (" ", "\u00a0", "\u2009", "\u202f", "\u3000"):
            with self.subTest(whitespace=whitespace):
                raw = textprov.mark("\u0600" + whitespace + "👍", "human")
                out, _ = self.apply(raw, "\u0600", "")
                self.assertEqual(out, whitespace + textprov.mark("👍", "human"))
                self.assertEqual(textprov.strip_marks(out), whitespace + "👍")
                self.assertEqual(
                    states(out), [(None, whitespace), ("human", "👍")]
                )
                self.assert_valid_selectors(out)

    def test_deleted_prepend_preserves_untouched_inert_selectors(self):
        inert = "\x00" + HUMAN + " " + AI + "\n"
        raw = inert + textprov.mark("\u0600 👍", "human")
        for include_context in (False, True):
            with self.subTest(include_context=include_context):
                context = textprov.strip_marks(inert) if include_context else ""
                out, _ = self.apply(raw, context + "\u0600", context)
                self.assertEqual(
                    out, inert + " " + textprov.mark("👍", "human")
                )
                self.assertEqual(
                    textprov.strip_marks(out),
                    textprov.strip_marks(raw).replace("\u0600", ""),
                )
                self.assertEqual(
                    states(out), [(None, inert + " "), ("human", "👍")]
                )
                self.assert_valid_selectors(out[len(inert) :])

    def test_prepend_edits_at_control_boundaries_leave_no_orphan_selectors(
        self,
    ):
        for control in (
            "\x00",
            "\x1c",
            "\u00ad",
            "\u200b",
            "\u2060",
            "\ufeff",
            "\r\n",
        ):
            for source, replacement, changed in (
                ("\u0600 " + control + "👍", "", " " + control + "👍"),
                ("\u0600 👍", control, control + " 👍"),
            ):
                with self.subTest(control=control, replacement=replacement):
                    raw = textprov.mark(source, "human")
                    out, _ = self.apply(raw, "\u0600", replacement)
                    self.assertEqual(
                        out, changed[:-1] + textprov.mark("👍", "human")
                    )
                    self.assertEqual(textprov.strip_marks(out), changed)
                    self.assertEqual(
                        states(out), [(None, changed[:-1]), ("human", "👍")]
                    )
                    self.assert_valid_selectors(out)

    def test_replace_all_deleted_prepend_preserves_human_emoji(self):
        raw = textprov.mark("\u0600 👍\n\u0600 👍", "human")
        out, _ = self.apply(raw, "\u0600", "", replace_all=True)
        self.assertEqual(out, textprov.mark(" 👍\n 👍", "human"))
        self.assertEqual(textprov.strip_marks(out), " 👍\n 👍")
        self.assertEqual(states(out), [(None, " "), ("human", "👍\n 👍")])
        self.assert_valid_selectors(out)

    def test_supplied_inert_selectors_do_not_mark_whitespace_or_controls(self):
        for new in (" ", "\u0085", "\x00", "\u00ad", "\u200b", "\r\n"):
            with self.subTest(new=new):
                out, _ = self.apply("old", "old", new + HUMAN)
                self.assertEqual(out, new)
                self.assertEqual(textprov.strip_marks(out), new)
                self.assertEqual(states(out), [(None, new)])
                self.assert_valid_selectors(out)

    def test_joined_cluster_inside_code_stays_unmarked(self):
        raw = ai("prose ") + "`ab`" + ai(" prose")
        out, _ = self.apply(raw, "b", "\u0301")
        self.assertEqual(out, ai("prose ") + "`a\u0301`" + ai(" prose"))
        self.assertEqual(textprov.strip_marks(out), "prose `a\u0301` prose")
        self.assert_valid_selectors(out)

    def test_supplied_marks_on_wholly_new_clusters_are_preserved(self):
        supplied = textprov.mark("e\u0301", "human")
        out, _ = self.apply("old", "old", supplied)
        self.assertEqual(out, supplied)
        self.assertEqual(states(out), [("human", "e\u0301")])
        self.assert_valid_selectors(out)

    def test_supplied_partial_cluster_marks_do_not_claim_source_context(self):
        for source, old, new, changed in (
            ("aX", "X", "\u0301", "a\u0301"),
            ("Xa", "X", "\u0600", "\u0600a"),
        ):
            with self.subTest(source=source):
                raw = ai(source)
                out, _ = self.apply(raw, old, textprov.mark(new, "human"))
                self.assertEqual(textprov.strip_marks(out), changed)
                self.assertEqual(states(out), [("ai", changed)])
                self.assert_valid_selectors(out)
        out, _ = self.apply(ai("aX"), "X", textprov.mark("\u0301 Z", "human"))
        self.assertEqual(textprov.strip_marks(out), "a\u0301 Z")
        self.assertEqual(
            states(out), [("ai", "a\u0301"), (None, " "), ("human", "Z")]
        )
        self.assert_valid_selectors(out)

    def test_pua_neighbour_join_uses_a_single_final_selector(self):
        raw = textprov.mark("aX", "ai", "pua")
        out, _ = self.apply(raw, "X", "\u0301")
        self.assertEqual(out, "a\u0301" + AI)
        self.assertEqual(textprov.strip_marks(out), "a\u0301")
        self.assertEqual(states(out), [("ai", "a\u0301")])
        self.assert_valid_selectors(out)

    def test_edit_inside_currency_is_marked(self):
        raw = "The total is $5 for coffee and $3 for tea."
        out, _ = self.apply(raw, "coffee", "water")
        self.assertEqual(
            textprov.strip_marks(out), raw.replace("coffee", "water")
        )
        self.assertEqual(
            states(out),
            [
                (None, "The total is $5 for "),
                ("ai", "water"),
                (None, " and $3 for tea."),
            ],
        )
        self.assert_valid_selectors(out)

    def test_replace_all_partial_graphemes(self):
        for source, old, new in (("e\u0301", "e", "X"), ("aX", "X", "\u0301")):
            with self.subTest(source=source):
                raw = textprov.mark(source + " " + source, "human")
                out, _ = self.apply(raw, old, new, replace_all=True)
                changed = source.replace(old, new)
                self.assertEqual(
                    textprov.strip_marks(out), changed + " " + changed
                )
                self.assertEqual(states(out), [("ai", changed + " " + changed)])
                self.assert_valid_selectors(out)

    def test_replace_all_different_grapheme_contexts_is_refused(self):
        raw = textprov.mark("e\u0301 e", "human")
        with self.assertRaises(editing.Ambiguous):
            editing.rewrite_edit(raw, "e", "X", replace_all=True)

    def test_replace_all_overlapping_expanded_clusters_is_refused(self):
        raw = textprov.mark("e\u0301\u0301", "human")
        with self.assertRaises(editing.Ambiguous):
            editing.rewrite_edit(raw, "\u0301", "", replace_all=True)

    def test_absent_old_string(self):
        self.assertIsNone(
            editing.rewrite_edit("abc\n", "zzz", "y", shingles=set())
        )

    def test_ambiguous_once_marks_are_ignored(self):
        raw = "word here\n" + ai("word") + " there\n"
        with self.assertRaises(editing.Ambiguous):
            editing.rewrite_edit(raw, "word", "term", shingles=set())

    def test_replace_all_uniform(self):
        raw = "a cat\nb cat\n"
        out, _ = self.apply(raw, "cat", "dog", replace_all=True)
        self.assertEqual(out, "a " + ai("dog") + "\nb " + ai("dog") + "\n")

    def test_replace_all_mixed_marks_is_refused(self):
        raw = "a cat\n" + ai("b cat") + "\n"
        with self.assertRaises(editing.Ambiguous):
            editing.rewrite_edit(
                raw, "cat", "dog", replace_all=True, shingles=set()
            )


if __name__ == "__main__":
    unittest.main()
