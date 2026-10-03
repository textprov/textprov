# python/tests/test_conformance.py

"""Conformance and unit tests for the textprov package.

Run from the python/ directory:

    python3 -m unittest discover -s tests -t .
"""

import html
import json
import unittest
from pathlib import Path

import textprov
from textprov._core import _runs, _to_html

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_PATH = ROOT / "fixtures.json"
GRAPHEME_TEST_PATH = ROOT / "ucd" / "GraphemeBreakTest.txt"
REGISTRY_PATH = ROOT / "mapping.json"

MAPPING = textprov.default_mapping()
SELECTORS = MAPPING.selectors
PUA2BASE = MAPPING.pua2base
AI = chr(SELECTORS["ai"])
HUMAN = chr(SELECTORS["human"])

FLAG = "\U0001f1e8\U0001f1e6"  # regional indicator pair
FAMILY = "\U0001f468‍\U0001f469‍\U0001f467"  # ZWJ sequence
TONE = "\U0001f44d\U0001f3fd"  # skin-tone modifier


def span(state, text, prefix="prov"):
    return f'<span class="{prefix} {prefix}-{state}" data-prov="{state}">{text}</span>'


class TestVendoredRegistry(unittest.TestCase):
    """The package vendors the registry; the copy must not drift (ADR 0006)."""

    def test_vendored_copy_matches_canonical(self):
        vendored = Path(textprov._core.MAPPING_PATH).read_text(encoding="utf-8")
        self.assertEqual(vendored, REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_pua_rule_holds_for_every_entry(self):
        # PUA_AI(cp) = 0x100000 + cp, and every v1 entry is state ai.
        for pua, (base, state) in PUA2BASE.items():
            self.assertEqual(pua - 0x100000, base, f"U+{pua:06X}")
            self.assertEqual(state, "ai", f"U+{pua:06X}")

    def test_loader_parses_u_plus_notation(self):
        # Regression: an earlier refactor replaced the explicit "U+" strip with
        # int(value, 0), which rejects "U+E0100" and left every public API path
        # broken on first use of default_mapping(). Load the vendored registry
        # from scratch and assert the canonical selector and PUA values.
        from textprov._core import load_mapping

        _, selectors, pua2base, base2pua = load_mapping()
        self.assertEqual(selectors["human"], 0xE0100)
        self.assertEqual(selectors["ai"], 0xE0101)
        self.assertEqual(set(selectors), {"human", "ai"})
        self.assertEqual(pua2base[0x100021], (0x0021, "ai"))
        self.assertEqual(base2pua[0x0021], 0x100021)

    def test_codepoint_parser_accepts_registry_notation(self):
        # Positive cases: canonical "U+HHHH" strings from the registry.
        from textprov._core import _codepoint

        self.assertEqual(_codepoint("U+E0100"), 0xE0100)
        self.assertEqual(_codepoint("U+0021"), 0x0021)
        self.assertEqual(_codepoint("U+100021"), 0x100021)

    def test_codepoint_parser_rejects_non_registry_notation(self):
        # Negative cases: everything a well-meaning refactor might substitute.
        # Each must raise ValueError so drift is loud, not silent.
        from textprov._core import _codepoint

        for bad in (
            "0xE0100",   # Python literal prefix, what int(_, 0) accepts
            "E0100",     # bare hex, no U+ prefix
            "u+E0100",   # lowercase prefix, not the canonical form
            "U+GGGG",    # not hex digits
            "",          # empty
            "U+",        # prefix with no digits
        ):
            with self.assertRaises(ValueError, msg=repr(bad)):
                _codepoint(bad)


class TestObsoleteSelectors(unittest.TestCase):
    def test_only_human_and_ai_states_are_exposed(self):
        self.assertEqual(textprov.GENERATED_STATES, ("human", "ai"))
        self.assertFalse(hasattr(textprov, "PROPOSED_STATES"))

    def test_obsolete_selectors_are_preserved_as_ordinary_text(self):
        for cp in range(0xE0102, 0xE0105):
            selector = chr(cp)
            for text in (
                selector,
                "a" + selector,
                " " + selector,
                "a" + AI + selector,
                "a" + selector + AI,
            ):
                with self.subTest(cp=cp, text=text):
                    self.assertEqual(
                        textprov.strip_marks(text), text.replace(AI, "")
                    )
                    for strip in (False, True):
                        state = "ai" if text.endswith(AI) else None
                        expected = text[:-1] if strip and state else text
                        self.assertEqual(
                            textprov.runs(text, strip=strip),
                            [(state, expected)],
                        )
                        rendered = span(state, expected) if state else expected
                        self.assertEqual(
                            textprov.to_html(text, strip=strip), rendered
                        )
                    for from_mode, to_mode in (("vs", "pua"), ("pua", "vs")):
                        expected = text
                        if from_mode == "vs":
                            expected = text.replace(
                                "a" + AI, chr(MAPPING.base2pua[ord("a")])
                            )
                        self.assertEqual(
                            textprov.convert(text, from_mode, to_mode), expected
                        )

    def test_inspect_does_not_report_obsolete_states(self):
        text = "a\U000e0102b\U000e0103c\U000e0104"
        report = textprov.inspect(text)
        self.assertIn("unmarked: 3\n", report)
        for state in ("mixed", "edited", "unknown"):
            self.assertNotIn(state + ":", report)
        self.assertIn(
            "unrecognised_selectors: U+E0102 U+E0103 U+E0104",
            textprov.inspect("\U000e0102\n\U000e0103\n\U000e0104"),
        )


class TestFixtures(unittest.TestCase):
    """fixtures.json defines conformance (ADR 0004)."""

    @classmethod
    def setUpClass(cls):
        cls.fx = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))

    def test_versions_match_the_implementation(self):
        self.assertEqual(textprov.SPEC_VERSION, self.fx["spec_version"])
        self.assertEqual(MAPPING.version, self.fx["registry_version"])

    def test_every_case(self):
        for case in self.fx["cases"]:
            with self.subTest(case["name"]):
                got = textprov.runs(case["input"], **case.get("options", {}))
                want = [(run["state"], run["text"]) for run in case["runs"]]
                self.assertEqual(got, want)


class TestSegments(unittest.TestCase):
    """Extended grapheme clusters from the vendored tables, tested directly."""

    def test_ascii(self):
        self.assertEqual(textprov.segments("abc"), ["a", "b", "c"])

    def test_combining_marks(self):
        self.assertEqual(textprov.segments("éx"), ["é", "x"])
        self.assertEqual(textprov.segments("é̂x"), ["é̂", "x"])

    def test_zwj_sequence(self):
        self.assertEqual(textprov.segments(FAMILY + "x"), [FAMILY, "x"])

    def test_skin_tone(self):
        self.assertEqual(textprov.segments(TONE + "x"), [TONE, "x"])

    def test_regional_indicators_pair_up(self):
        self.assertEqual(
            textprov.segments(FLAG + "\U0001f1e8"), [FLAG, "\U0001f1e8"]
        )

    def test_emoji_variation_selectors(self):
        self.assertEqual(textprov.segments("❤️x"), ["❤️", "x"])
        self.assertEqual(textprov.segments("❤︎x"), ["❤︎", "x"])
        self.assertEqual(textprov.segments("️x"), ["️", "x"])

    def test_provenance_selector_extends_the_cluster(self):
        self.assertEqual(textprov.segments(AI + "x"), [AI, "x"])
        self.assertEqual(textprov.segments("a" + AI + "b"), ["a" + AI, "b"])
        self.assertEqual(textprov.segments(FAMILY + AI + "b"), [FAMILY + AI, "b"])

    def test_clusters_the_approximation_used_to_split(self):
        jamo = "\u1100\u1161\u11a8"
        conjunct = "\u0915\u094d\u0937"
        tag_flag = "\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"
        sara_am = "\u0e19\u0e33"
        for text in (jamo, conjunct, tag_flag, sara_am):
            self.assertEqual(textprov.segments(text), [text])
            self.assertEqual(textprov.segments(text + AI), [text + AI])

    def test_empty(self):
        self.assertEqual(textprov.segments(""), [])

    def test_unicode_version_matches_the_test_file(self):
        with open(GRAPHEME_TEST_PATH, encoding="utf-8") as handle:
            first = handle.readline()
        self.assertIn(f"GraphemeBreakTest-{textprov.UNICODE_VERSION}.txt", first)

    def test_grapheme_break_test(self):
        """Every line of Unicode's GraphemeBreakTest.txt for the pinned version.

        "÷" marks a boundary and "×" its absence; text after "#" is a comment.
        """
        total = 0
        with open(GRAPHEME_TEST_PATH, encoding="utf-8") as handle:
            for line in handle:
                body = line.split("#")[0].strip()
                if not body:
                    continue
                expected, current = [], ""
                for token in body.split()[1:]:
                    if token == "÷":
                        expected.append(current)
                        current = ""
                    elif token != "×":
                        current += chr(int(token, 16))
                with self.subTest(line=body):
                    self.assertEqual(textprov.segments("".join(expected)), expected)
                total += 1
        self.assertGreater(total, 700)


class TestToHtml(unittest.TestCase):
    """The renderer: span shape, escaping, options."""

    def render(self, text, **options):
        return textprov.to_html(text, **options)

    def test_empty_and_plain(self):
        self.assertEqual(self.render(""), "")
        self.assertEqual(self.render("plain"), "plain")

    def test_span_shape(self):
        self.assertEqual(self.render("a" + AI), span("ai", "a" + AI))

    def test_escaping(self):
        self.assertEqual(self.render('<&"'), "&lt;&amp;&quot;")
        self.assertEqual(
            self.render("<" + AI + "&" + AI + '"' + AI),
            span("ai", "&lt;" + AI + "&amp;" + AI + "&quot;" + AI),
        )
        self.assertEqual(
            self.render("a" + AI + "<b>" + HUMAN + " & x"),
            span("ai", "a" + AI)
            + "&lt;b"
            + span("human", "&gt;" + HUMAN)
            + " &amp; x",
        )

    def test_class_prefix(self):
        out = self.render("a" + AI, class_prefix="x")
        self.assertEqual(out, span("ai", "a" + AI, prefix="x"))
        self.assertIn('data-prov="ai"', out)

    def test_merge_whitespace(self):
        self.assertEqual(
            self.render("a" + AI + " b" + AI), span("ai", "a" + AI + " b" + AI)
        )
        self.assertEqual(
            self.render("a" + AI + " b" + AI, merge_whitespace=False),
            span("ai", "a" + AI) + " " + span("ai", "b" + AI),
        )

    def test_strip(self):
        self.assertEqual(
            self.render("a" + AI + " b" + AI, strip=True), span("ai", "a b")
        )

    def test_pua_input(self):
        pua_cp, (pua_base, pua_state) = next(
            (cp, entry) for cp, entry in PUA2BASE.items() if entry[1] == "ai"
        )
        self.assertEqual(pua_state, "ai")
        self.assertEqual(
            self.render(chr(pua_cp)), span("ai", chr(pua_base) + AI)
        )
        self.assertEqual(
            self.render(chr(pua_cp), strip=True), span("ai", chr(pua_base))
        )

    def test_span_text_reproduces_the_input(self):
        source = "x<y" + AI + " & " + FAMILY + HUMAN + '\n"z"'
        rendered = self.render(source)
        for tag in (span("ai", ""), span("human", "")):
            rendered = rendered.replace(tag[: -len("</span>")], "")
        self.assertEqual(html.unescape(rendered.replace("</span>", "")), source)


class TestStripMarks(unittest.TestCase):
    def test_cleanup_removes_selectors_that_decoder_stripping_keeps(self):
        for selector in (AI, HUMAN):
            for text, clean in (
                (selector + "A", "A"),
                ("A " + selector + "B", "A B"),
                ("A" + selector + " " + selector, "A "),
                ("A" + selector * 2, "A"),
                ("A" + HUMAN + AI, "A"),
            ):
                with self.subTest(text=text):
                    self.assertEqual(textprov.strip_marks(text), clean)
                    self.assertNotEqual(
                        "".join(
                            out for _, out in textprov.runs(text, strip=True)
                        ),
                        clean,
                    )

    def test_selectors_and_pua_are_removed(self):
        pua_cp, (pua_base, _) = next(iter(PUA2BASE.items()))
        self.assertEqual(textprov.strip_marks("a" + AI + "b" + HUMAN), "ab")
        self.assertEqual(textprov.strip_marks(chr(pua_cp)), chr(pua_base))


class TestExplicitMapping(unittest.TestCase):
    """Every public function accepts a caller-supplied registry."""

    def test_mapping_argument(self):
        mapping = textprov.Mapping.load(REGISTRY_PATH)
        self.assertEqual(mapping.version, MAPPING.version)
        self.assertEqual(
            textprov.runs("a" + AI, mapping), textprov.runs("a" + AI)
        )
        self.assertEqual(
            _runs("a" + AI, mapping.selectors, mapping.pua2base, False, True),
            textprov.runs("a" + AI),
        )
        self.assertEqual(
            _to_html(
                "a" + AI,
                mapping.selectors,
                mapping.pua2base,
                False,
                True,
                "prov",
            ),
            textprov.to_html("a" + AI),
        )


if __name__ == "__main__":
    unittest.main()
