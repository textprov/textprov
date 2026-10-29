"""Checker fixtures ported from tools/tests/test_dogfood.py in the docs site.

Fixed authoring outputs keep these tests independent of authoring alignment.
The correspondence limitations below are intentional, not authorship guarantees.
"""

import unittest

import textprov
from textprov.check import check_text

AI = chr(textprov.default_mapping().selectors["ai"])
HUMAN = chr(textprov.default_mapping().selectors["human"])
DOCS = ("markdown", "markdoc", "directives")
mark = textprov.mark
strip = textprov.strip_marks
MISSING = "new prose cluster has no supported origin mark"
CHANGED = "changed or lost an existing mark"
BACKFILL = "marked unchanged legacy text"
SELECTOR = "new prose cluster must have one selector mark"
OUTSIDE = "new mark is outside eligible prose or attached to whitespace"


class CheckerTests(unittest.TestCase):
    def messages(self, old, new, suffix=".txt", **kwargs):
        profile = None if suffix == ".txt" else DOCS
        return [
            message
            for _, _, message in check_text(old, new, profile=profile, **kwargs)
        ]

    def test_legacy_text_is_not_a_coverage_failure(self):
        self.assertEqual(self.messages("legacy", "legacy"), [])

    def test_new_unmarked_prose_fails(self):
        self.assertIn(MISSING, self.messages("old", "old X"))

    def test_marks_cannot_be_lost_relabelled_or_backfilled(self):
        for after in ("old", mark("old", state="human")):
            self.assertIn(CHANGED, self.messages(mark("old"), after))
        self.assertIn(BACKFILL, self.messages("old", mark("old")))

    def test_single_character_coincidence_is_not_a_move(self):
        self.assertEqual(
            self.messages("ay\nb\n", "a\nb" + mark("y") + "\n"), []
        )
        self.assertEqual(self.messages("ay\nb\n", "a\nby\n"), [])

    def test_cumulative_check_matches_separately_checked_edits(self):
        base = "Czas życia sekretu.\n\n## Pytania lub potrzebujesz wsparcia?\n"
        first = base.replace("życia", mark("wa") + "ż" + mark("noś") + "ci")
        second = first.replace(
            "wsparcia?", "p" + mark("omo") + "c" + mark("y") + "?"
        )
        self.assertEqual(self.messages(base, first, ".md"), [])
        self.assertEqual(self.messages(first, second, ".md"), [])
        self.assertEqual(self.messages(base, second, ".md"), [])

    def test_moved_and_unmoved_text_cannot_be_relabelled_or_lose_marks(self):
        legacy, marked = "legacy paragraph", mark("marked paragraph")
        self.assertIn(
            BACKFILL,
            self.messages(f"{legacy}\nmiddle\n", f"middle\n{mark(legacy)}\n"),
        )
        self.assertIn(BACKFILL, self.messages("a y b", "a " + mark("y") + " b"))
        for require_marks in (True, False):
            for old, new in (
                (f"{marked}\nmiddle\n", f"middle\n{strip(marked)}\n"),
                ("a " + mark("y") + " b", "a y b"),
            ):
                with self.subTest(require_marks=require_marks, old=ascii(old)):
                    self.assertIn(
                        CHANGED,
                        self.messages(old, new, require_marks=require_marks),
                    )

    def test_inserted_duplicate_does_not_steal_existing_attribution(self):
        for original in ("same", mark("same", state="human")):
            self.assertEqual(
                self.messages(original, mark("same") + " " + original), []
            )
            self.assertEqual(
                self.messages(original, original + " " + mark("same")), []
            )

    def test_invalid_new_marks_fail(self):
        for source in (
            "x" + AI + AI,
            mark("x", mode="pua"),
            "x" + chr(0xE0104),
            " " + AI,
            AI,
        ):
            with self.subTest(source=ascii(source)):
                self.assertTrue(self.messages("", source))

    def test_code_is_excluded_but_new_marks_in_code_fail(self):
        self.assertEqual(
            self.messages("", '```\nprint("hello")\n```\n', ".md"), []
        )
        self.assertTrue(self.messages("", "`" + mark("code") + "`", ".md"))

    def test_new_marks_cannot_corrupt_markdown_delimiters(self):
        self.assertTrue(self.messages("", mark("# Heading"), ".md"))

    def test_new_marks_inside_aside_fences_fail(self):
        body = "\n" + mark("Body.") + "\n"
        self.assertTrue(
            self.messages(
                "", mark(":::note") + body + mark(":::") + "\n", ".md"
            )
        )
        self.assertTrue(
            self.messages("", ":::" + mark("note") + body + ":::\n", ".md")
        )
        self.assertTrue(
            self.messages(
                "", ":::tip" + mark("[") + "Label]" + body + ":::\n", ".md"
            )
        )

    def test_removing_marks_from_an_aside_fence_repairs_it(self):
        before = (
            mark(":::note") + "\n" + mark("Body.") + "\n" + mark(":::") + "\n"
        )
        self.assertEqual(
            self.messages(
                before, ":::note\n" + mark("Body.") + "\n:::\n", ".md"
            ),
            [],
        )
        self.assertIn(
            CHANGED, self.messages(before, ":::note\nBody.\n:::\n", ".md")
        )


class CorrespondenceLimitTests(unittest.TestCase):
    """Explicitly retain the docs checker's unresolved correspondence gaps."""

    def check(self, before, after, **kwargs):
        return check_text(before, after, profile=None, **kwargs)

    def test_in_place_single_cluster_coincidence_is_still_aligned(self):
        before = "cat"
        after = mark("b") + "a" + mark("g")
        self.assertEqual(self.check(before, after), [])
        self.assertEqual(self.check(before, mark("bag")), [(1, 2, BACKFILL)])

    def test_single_cluster_survivor_keeps_each_existing_encoding(self):
        for survivor in (
            "a",
            mark("a"),
            mark("a", state="human"),
            mark("a", mode="pua"),
        ):
            with self.subTest(survivor=ascii(survivor)):
                before = "c" + survivor + "t"
                after = mark("b") + survivor + mark("g")
                self.assertEqual(self.check(before, after), [])
                if survivor != "a":
                    self.assertIn(
                        (1, 2, CHANGED),
                        self.check(
                            before,
                            mark("b") + "a" + mark("g"),
                            require_marks=False,
                        ),
                    )

    def test_in_place_two_cluster_coincidence_can_also_remain_unmarked(self):
        self.assertEqual(self.check("axyc", mark("b") + "xy" + mark("d")), [])

    def test_single_cluster_move_can_hide_mark_loss_or_relabelling(self):
        before = "a" + mark("y") + "\nmiddle\n"
        lost = "a\nmiddley\n"
        self.assertEqual(self.check(before, lost, require_marks=False), [])
        self.assertEqual(self.check(before, lost), [(2, 7, MISSING)])
        relabelled = "a\nmiddle" + mark("y", state="human") + "\n"
        for require_marks in (True, False):
            with self.subTest(require_marks=require_marks):
                self.assertEqual(
                    self.check(before, relabelled, require_marks=require_marks),
                    [],
                )

    def test_two_cluster_move_checks_backfill_loss_and_relabelling(self):
        for old, new, message in (
            ("xy", mark("xy"), BACKFILL),
            (mark("xy"), "xy", CHANGED),
            (mark("xy", state="human"), mark("xy"), CHANGED),
        ):
            for require_marks in (True, False):
                with self.subTest(
                    old=ascii(old), new=ascii(new), require_marks=require_marks
                ):
                    before, after = (
                        "a" + old + "\nmiddle\n",
                        "a\nmiddle" + new + "\n",
                    )
                    self.assertEqual(
                        self.check(before, after, require_marks=require_marks),
                        [(2, 7, message), (2, 8, message)],
                    )
        before = "a" + mark("xy", state="human") + "\nmiddle\n"
        after = "a\nmiddle" + mark("xy", state="human") + "\n"
        self.assertEqual(self.check(before, after), [])

    def test_cumulative_two_cluster_coincidence_remains_ambiguous(self):
        base = "axy\nmiddle\n"
        first = "a\nmiddle\n"
        second = "a\nmiddle" + mark("xy") + "\n"
        self.assertEqual(self.check(base, first), [])
        self.assertEqual(self.check(first, second), [])
        self.assertEqual(
            self.check(base, second), [(2, 7, BACKFILL), (2, 8, BACKFILL)]
        )

    def test_bulgarian_status_keeps_the_legacy_single_cluster(self):
        before = mark("Актив") + "ен"
        after = mark("Актив") + "н" + mark("а")
        self.assertEqual(self.check(before, after), [])
        self.assertEqual(
            self.check(before, mark("Активна")), [(1, 6, BACKFILL)]
        )

    def test_spanish_value_keeps_the_coincidental_legacy_r(self):
        before = "secreto"
        after = mark("valo") + "r " + mark("SECRET")
        self.assertEqual(self.check(before, after), [])
        self.assertEqual(
            self.check(before, mark("valor") + " " + mark("SECRET")),
            [(1, 5, BACKFILL)],
        )


class ProfileCheckerTests(unittest.TestCase):
    def test_default_markdown_and_plain_profile(self):
        self.assertEqual(check_text("", "`code`"), [])
        self.assertEqual(
            check_text("", "`code`", profile=None),
            [(1, i, MISSING) for i in range(1, 7)],
        )
        self.assertEqual(check_text("", "# " + mark("Heading")), [])

    def test_profile_compositions_and_markdoc_protection(self):
        source = (
            '{% card title="Do not mark" %}\n:::note\n'
            + mark("Body.")
            + "\n:::\n{% /card %}"
        )
        for profile in (DOCS, list(DOCS), ",".join(DOCS)):
            with self.subTest(profile=profile):
                self.assertEqual(check_text("", source, profile=profile), [])
                self.assertEqual(
                    check_text(
                        "", "{% " + mark("card") + " %}", profile=profile
                    ),
                    [(1, i, OUTSIDE) for i in range(4, 8)],
                )

    def test_callable_profile_receives_plain_text_and_protects_whole_cluster(
        self,
    ):
        seen = []

        def profile(text):
            seen.append(text)
            return [i == 1 for i in range(len(text))]

        self.assertEqual(
            check_text("", "e\u0301 " + mark("X"), profile=profile), []
        )
        self.assertEqual(seen, ["e\u0301 X"])
        self.assertEqual(
            check_text("", mark("e\u0301"), profile=profile), [(1, 1, OUTSIDE)]
        )

    def test_profile_errors_are_not_silenced(self):
        with self.assertRaisesRegex(ValueError, "unknown syntax profile"):
            check_text("", "", profile="unknown")

    def test_plain_codepoint_locations_with_crlf_and_graphemes(self):
        source = mark("😀e\u0301") + "\r\n X"
        self.assertEqual(
            check_text("", source, profile=None), [(2, 2, MISSING)]
        )
        self.assertEqual(
            check_text("", mark("😀") + "e\u0301", profile=None),
            [(1, 2, MISSING)],
        )

    def test_unsupported_states_whitespace_and_selector_multiplicity(self):
        unsupported = chr(0xE0104)
        for require_marks in (True, False):
            for source, message in (
                ("x" + AI + AI, SELECTOR),
                ("x" + HUMAN + AI, SELECTOR),
                (mark("x", mode="pua"), SELECTOR),
                (" " + AI, OUTSIDE),
                ("\t" + HUMAN, OUTSIDE),
                (AI, OUTSIDE),
            ):
                with self.subTest(
                    source=ascii(source), require_marks=require_marks
                ):
                    problems = check_text(
                        "", source, profile=None, require_marks=require_marks
                    )
                    self.assertTrue(problems)
                    self.assertEqual({p[2] for p in problems}, {message})
            self.assertEqual(
                check_text(
                    "",
                    "x" + unsupported,
                    profile=None,
                    require_marks=require_marks,
                ),
                [(1, 1, MISSING)] if require_marks else [],
            )

    def test_natural_ivs_and_emoji_variation_selectors_are_not_provenance(self):
        for cluster in (
            "漢\U000e0104",
            "漢\U000e01ef",
            "❤\ufe0f",
            "e\u0301",
            "👨‍👩‍👧",
            "🇨🇦",
        ):
            with self.subTest(cluster=cluster):
                self.assertEqual(check_text(cluster, cluster, profile=DOCS), [])
                self.assertEqual(
                    check_text("", mark(cluster), profile=DOCS), []
                )
                self.assertEqual(
                    check_text("", cluster, profile=DOCS), [(1, 1, MISSING)]
                )
                self.assertEqual(
                    check_text("", cluster, profile=DOCS, require_marks=False),
                    [],
                )

    def test_docs_mixed_legacy_pua_human_ai_preserve_only(self):
        before = (
            "# Legacy\n\n"
            + mark("PUA", mode="pua")
            + " "
            + mark("human", state="human")
            + " "
            + mark("AI")
            + " 漢\U000e0104\n"
        )
        after = (
            before
            + '\n{% card title="plain" %}\nNew human contribution.\n{% /card %}\n'
        )
        self.assertEqual(
            check_text(before, after, profile=DOCS, require_marks=False), []
        )
        self.assertTrue(check_text(before, after, profile=DOCS))
        for original, replacement in (
            (mark("PUA", mode="pua"), "PUA"),
            (mark("human", state="human"), mark("human")),
            (mark("AI"), "AI"),
        ):
            with self.subTest(original=ascii(original)):
                self.assertIn(
                    CHANGED,
                    [
                        p[2]
                        for p in check_text(
                            before,
                            after.replace(original, replacement),
                            profile=DOCS,
                            require_marks=False,
                        )
                    ],
                )

    def test_legacy_syntax_defects_do_not_require_retrospective_repair(self):
        before = mark("# Legacy heading") + "\n\nold"
        self.assertEqual(
            check_text(before, before + " " + mark("X"), profile=DOCS), []
        )
        self.assertEqual(check_text(mark("`code`"), "`code`", profile=DOCS), [])

    def test_reflow_preserves_mixed_encodings(self):
        before = "legacy paragraph\n" + mark(
            "a different ending", state="human"
        )
        after = (
            mark("a different", state="human")
            + "\n"
            + mark("ending", state="human")
            + "\nlegacy paragraph"
        )
        self.assertEqual(check_text(before, after, profile=DOCS), [])


if __name__ == "__main__":
    unittest.main()
