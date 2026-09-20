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
from textprov._core import _runs, _to_html, cluster_end, is_combining

ROOT = Path(__file__).resolve().parents[2]
FIXTURES_PATH = ROOT / "fixtures.json"
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


class TestFixtures(unittest.TestCase):
    """fixtures.json defines conformance (ADR 0004)."""

    @classmethod
    def setUpClass(cls):
        cls.fx = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))

    def test_versions_match_the_implementation(self):
        self.assertEqual(textprov.CONTRACT_VERSION, self.fx["contract_version"])
        self.assertEqual(MAPPING.version, self.fx["mapping_version"])

    def test_every_case(self):
        for case in self.fx["cases"]:
            with self.subTest(case["name"]):
                got = textprov.runs(case["input"], **case.get("options", {}))
                want = [(run["state"], run["text"]) for run in case["runs"]]
                self.assertEqual(got, want)


class TestClusterEnd(unittest.TestCase):
    """The shared core's segmentation, tested directly rather than via runs."""

    def cluster(self, text, start=0):
        return cluster_end(list(text), start, set(SELECTORS.values()))

    def test_ascii(self):
        self.assertEqual(self.cluster("abc"), 1)
        self.assertEqual(self.cluster("abc", 1), 2)

    def test_combining_marks(self):
        self.assertEqual(self.cluster("éx"), 2)
        self.assertEqual(self.cluster("é̂x"), 3)

    def test_zwj_sequence(self):
        self.assertEqual(self.cluster(FAMILY + "x"), 5)
        self.assertEqual(self.cluster(FAMILY), 5)

    def test_skin_tone(self):
        self.assertEqual(self.cluster(TONE + "x"), 2)

    def test_regional_indicators(self):
        self.assertEqual(self.cluster(FLAG + "\U0001f1e8"), 2)
        self.assertEqual(self.cluster("\U0001f1e8x"), 1)

    def test_emoji_variation_selectors(self):
        self.assertEqual(self.cluster("❤️x"), 2)
        self.assertEqual(self.cluster("❤︎x"), 2)
        self.assertEqual(self.cluster("️x"), 1)

    def test_provenance_selector_ends_the_cluster(self):
        self.assertEqual(self.cluster(AI + "x"), 1)
        self.assertEqual(self.cluster("a" + AI + "b"), 1)
        self.assertEqual(self.cluster("é" + AI + "b"), 2)
        self.assertEqual(self.cluster(FAMILY + AI + "b"), 5)

    def test_is_combining(self):
        self.assertTrue(is_combining("́"))
        self.assertFalse(is_combining("a"))


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
        self.assertEqual(self.render("a" + AI + " b" + AI, strip=True), span("ai", "a b"))

    def test_pua_input(self):
        pua_cp, (pua_base, pua_state) = next(
            (cp, entry) for cp, entry in PUA2BASE.items() if entry[1] == "ai"
        )
        self.assertEqual(pua_state, "ai")
        self.assertEqual(self.render(chr(pua_cp)), span("ai", chr(pua_base) + AI))
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
            _to_html("a" + AI, mapping.selectors, mapping.pua2base, False, True, "prov"),
            textprov.to_html("a" + AI),
        )


if __name__ == "__main__":
    unittest.main()
