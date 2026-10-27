"""Passage paint must never broaden the exact attribution metadata."""
from html.parser import HTMLParser
import unittest

import textprov

AI = "\U000e0101"
HUMAN = "\U000e0100"


class Projection(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.stack = [None]
        self.groups = []
        self.characters = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.stack.append(attrs.get("data-prov", self.stack[-1]))
        if "data-prov-passage" in attrs:
            self.groups.append(attrs["data-prov-passage"])

    def handle_endtag(self, tag):
        self.stack.pop()

    def handle_data(self, data):
        self.characters.extend((char, self.stack[-1]) for char in data)


class TestPassageDisplay(unittest.TestCase):
    def test_default_groups_partial_marks_without_changing_exact_metadata(self):
        source = "C" + AI + "ho" + AI + "ose a guide."
        before = textprov.runs(source, strip=True, merge_whitespace=False)
        view = Projection(textprov.to_html(source, strip=True))
        self.assertEqual(view.groups, ["ai"])
        self.assertEqual(view.characters, [(char, state) for state, text in before for char in text])
        self.assertEqual(source, "C" + AI + "ho" + AI + "ose a guide.")

    def test_paragraphs_do_not_relabel_plain_text_or_other_sources(self):
        source = "a" + AI + " rest\n\nUnmarked.\n\nb" + HUMAN + " human"
        view = Projection(textprov.to_html(source, strip=True, class_prefix="custom"))
        self.assertEqual(view.groups, ["ai", "human"])
        mixed = Projection(textprov.to_html("a" + AI + " and b" + HUMAN, strip=True))
        self.assertEqual(mixed.groups, ["mixed"])
        self.assertEqual([state for _, state in mixed.characters if state], ["ai", "human"])

    def test_exact_option_and_invalid_options(self):
        source = "a" + AI + " plain"
        self.assertNotIn("data-prov-passage", textprov.to_html(source, display="exact"))
        self.assertEqual(Projection(textprov.to_html(source)).characters,
                         Projection(textprov.to_html(source, display="exact")).characters)
        spaced = "a" + AI + " b" + AI
        self.assertEqual(Projection(textprov.to_html(spaced, strip=True, display="exact")).characters,
                         [("a", "ai"), (" ", None), ("b", "ai")])
        with self.assertRaises(ValueError):
            textprov.to_html(source, display="word")
