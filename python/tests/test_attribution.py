"""Shared matching policies, original-coordinate mappings and conservative limits."""

import hashlib
from itertools import product
import unittest

from textprov.attribution import comparison_view, match_passages


class TestAttribution(unittest.TestCase):
    def test_exact_default_keeps_repetition_and_unicode(self):
        result = match_passages("😀é", "😀é and 😀é")
        self.assertEqual("ambiguous", result["status"])
        self.assertEqual([[0, 2], [7, 9]], [c["target_range"] for c in result["candidates"]])
        self.assertTrue(all(not c["selected"] for c in result["candidates"]))
        for source, target in (("e", "e\u0301"), ("é", "e\u0301"), ("👩", "👩‍💻")):
            self.assertEqual([], match_passages(source, target)["candidates"])

    def test_line_endings_map_back_to_exact_original_hash_and_range(self):
        source, target = "a\r\nb\rc", "prefix a\nb\nc suffix"
        self.assertEqual([], match_passages(source, target)["candidates"])
        result = match_passages(source, target, policy="line-endings-v1")
        candidate = result["candidates"][0]
        self.assertEqual([0, 6], candidate["source_range"])
        self.assertEqual([7, 12], candidate["target_range"])
        self.assertEqual([[0, 6]], candidate["source_segments"])
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), candidate["source_hash"])
        self.assertEqual("normalized", candidate["method"])
        self.assertEqual("line-endings-v1", candidate["policy"])

    def test_indent_mapping_excludes_removed_prefixes(self):
        source, target = "  alpha\r\n    beta", "\talpha\n\t  beta"
        view = comparison_view(source, policy="common-indent-v1")
        self.assertEqual("alpha\n  beta", view.text)
        self.assertEqual([[2, 9], [11, 17]], view.original_segments(0, len(view.text)))
        candidate = match_passages(source, target, policy="common-indent-v1")["candidates"][0]
        self.assertEqual([[2, 9], [11, 17]], candidate["source_segments"])
        self.assertEqual([[1, 7], [8, 14]], candidate["target_segments"])
        self.assertEqual([1, 14], candidate["target_range"])
        self.assertEqual("full", candidate["source_coverage"])

    def test_indent_policy_is_literal_and_preserves_blank_lines_and_trailing_spaces(self):
        cases = ((" \tA\n \tB\n", "A\nB\n"),
                 ("  A\n\n  B", "A\n\nB"),
                 ("  A\n \tB", " A\n\tB"),
                 ("  \n\t", "  \n\t"),
                 ("  A  ", "A  "))
        for source, expected in cases:
            self.assertEqual(expected, comparison_view(source, policy="common-indent-v1").text)
        self.assertEqual([], match_passages("a ", "a", policy="common-indent-v1")["candidates"])

    def test_partial_returns_disjoint_runs_without_filling_a_changed_middle(self):
        result = match_passages("abcXYZdef", "abc123def", partial=True, min_match_chars=3)
        self.assertEqual("ambiguous", result["status"])
        self.assertEqual([[0, 3], [6, 9]], [c["source_range"] for c in result["candidates"]])
        self.assertEqual([[0, 3], [6, 9]], [c["target_range"] for c in result["candidates"]])
        self.assertTrue(all(c["source_coverage"] == "partial" for c in result["candidates"]))
        self.assertEqual([], match_passages("abcXYZdef", "abc123def")["candidates"])

    def test_partial_keeps_repeated_alternatives_and_grapheme_boundaries(self):
        result = match_passages("😀é!", "😀é?😀é", partial=True, min_match_chars=2)
        self.assertEqual([[0, 2], [3, 5]], [c["target_range"] for c in result["candidates"]])
        self.assertEqual([], match_passages("eX", "e\u0301X", partial=True,
                                          min_match_chars=2)["candidates"])
        # No occurrence inside a cluster even when normalization removes spaces.
        self.assertEqual([], match_passages("\u0301", " \u0301",
                                          policy="common-indent-v1")["candidates"])

    def test_partial_normalization_maps_original_offsets(self):
        candidate = match_passages("head\r\nbody\r\nend", "body\nchanged",
                                   policy="line-endings-v1", partial=True,
                                   min_match_chars=5)["candidates"][0]
        self.assertEqual([6, 12], candidate["source_range"])
        self.assertEqual([0, 5], candidate["target_range"])
        self.assertEqual("partial", candidate["source_coverage"])

    def test_partial_enumerates_all_maximal_alignments(self):
        # A small exhaustive oracle catches repeated/overlapping alternatives.
        words = ["".join(chars) for chars in product("ab", repeat=4)]
        for source in words:
            for target in words:
                expected = []
                for i in range(len(source)):
                    for j in range(len(target)):
                        if source[i] != target[j] or (i and j and source[i-1] == target[j-1]):
                            continue
                        end = 1
                        while i+end < len(source) and j+end < len(target) and source[i+end] == target[j+end]:
                            end += 1
                        if end >= 2:
                            expected.append(([i, i+end], [j, j+end]))
                result = match_passages(source, target, partial=True, min_match_chars=2)
                actual = [(c["source_range"], c["target_range"]) for c in result["candidates"]]
                self.assertEqual(expected, actual, (source, target))

    def test_limits_return_no_subset_and_invalid_options_fail(self):
        self.assertEqual("empty_source", match_passages("", "abc")["status"])
        for args in (dict(policy="guess"), dict(partial=1), dict(min_match_chars=0),
                     dict(min_match_chars=True)):
            with self.assertRaises(ValueError):
                match_passages("a", "a", **args)
        with self.assertRaises(ValueError):
            comparison_view("\ud800")
        pairs = match_passages("a" * 1001, "a" * 1001, partial=True)
        self.assertEqual(("limit_exceeded", "partial_pairs", []),
                         (pairs["status"], pairs["limit"], pairs["candidates"]))
        many = match_passages("a", "a" * 1001)
        self.assertEqual(("limit_exceeded", "candidates", []),
                         (many["status"], many["limit"], many["candidates"]))


if __name__ == "__main__":
    unittest.main()
