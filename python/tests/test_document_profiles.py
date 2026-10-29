"""Document syntax profiles, ported from the docs authoring fixtures (no Node)."""

import unittest

import textprov
from textprov import editing

DOCS = ("markdown", "markdoc", "directives")
mark = textprov.mark


class DocumentProfileTests(unittest.TestCase):
    def render(self, source, profile=DOCS):
        result = editing.remark("", source, profile=profile)
        self.assertEqual(textprov.strip_marks(result), source)
        return result

    def test_default_headings_are_prose(self):
        self.assertEqual(
            editing.remark("", "## Heading ##\n"),
            "## " + mark("Heading") + " ##\n",
        )
        for underline in ("=====", "---"):
            self.assertEqual(
                editing.remark("", "Title\n" + underline + "\n"),
                mark("Title") + "\n" + underline + "\n",
            )

    def test_atx_delimiters_inline_syntax_and_crlf(self):
        source = "   ### Café 😀 **bold** `code` ###\r\n"
        self.assertEqual(
            self.render(source, "markdown"),
            "   ### "
            + mark("Café 😀 ")
            + "**"
            + mark("bold")
            + "** `code` ###\r\n",
        )
        self.assertEqual(
            self.render("# Has#\n", "markdown"), "# " + mark("Has#") + "\n"
        )
        self.assertEqual(self.render("###\n", "markdown"), "###\n")

    def test_markdoc_tags_and_attributes_are_protected(self):
        source = (
            '---\ntitle: Plain title\n---\n\n{% card title="Do not mark" %}\n\n'
            "New **prose**, `code`, and [label](/en/start).\n\n{% /card %}\n"
        )
        result = self.render(source)
        for fragment in (
            "title: Plain title",
            '{% card title="Do not mark" %}',
            "{% /card %}",
            "`code`",
            "](/en/start)",
        ):
            self.assertIn(fragment, result)
        self.assertIn(mark("prose"), result)
        self.assertIn("[" + mark("label") + "]", result)

    def test_markdoc_quotes_escapes_multiline_and_offsets(self):
        for tag in (
            '{% card title="a %} b" %}',
            "{% card title='a %} b' %}",
            '{% card title="escaped \\" %} still quoted" %}',
            "{% card\r\n title='`code` 😀 %} text'\r\n%}",
        ):
            with self.subTest(tag=tag):
                self.assertEqual(
                    self.render("😀 before " + tag + " after\r\n"),
                    mark("😀 before ") + tag + mark(" after\r\n"),
                )

    def test_markdoc_mask_does_not_create_markdown_code_or_headings(self):
        tag = '{% card title="`" %}'
        self.assertEqual(
            self.render("Before " + tag + " visible `code`\n"),
            mark("Before ") + tag + " " + mark("visible") + " `code`\n",
        )
        source = "{% card %}\n# Heading\n{% /card %}\n"
        self.assertEqual(
            self.render(source),
            "{% card %}\n# " + mark("Heading") + "\n{% /card %}\n",
        )

    def assert_coverage(self, source, result):
        from textprov.check import check_text

        self.assertEqual(check_text("", result, profile=DOCS), [])
        self.assertTrue(
            any(
                message == "new prose cluster has no supported origin mark"
                for _, _, message in check_text("", source, profile=DOCS)
            )
        )

    def test_tag_mask_does_not_indent_following_prose(self):
        for tag in (
            "{% card %}",
            '{% card\n title="value" %}',
            '{% card\r\n title="😀 %} quoted"\r\n%}',
        ):
            with self.subTest(tag=tag):
                source = tag + " Visible prose\n"
                result = self.render(source)
                self.assertEqual(result, tag + mark(" Visible prose\n"))
                self.assert_coverage(source, result)

    def test_literal_markdoc_openers_do_not_suppress_later_prose(self):
        for literal in (
            "```\n{%\n```",
            "~~~text\n{%\n~~~",
            "    {%",
            "\t{%",
            "`{%` is the opener.",
            "``{% ` literal`` is the opener.",
            "`a\n{%\nb` is the opener.",
        ):
            with self.subTest(literal=literal):
                source = literal + "\n\nNew prose.\n"
                result = self.render(source)
                self.assertIn(mark("New prose."), result)
                self.assertIn("{%", result)
                self.assert_coverage(source, result)

    def test_standalone_multiline_tags_do_not_obscure_fences(self):
        for tag in (
            "{% card %}",
            '{% card\n title="`"\n%}',
            '{% card\r\n title="```"\r\n%}',
        ):
            with self.subTest(tag=tag):
                source = tag + "\n```\n{%\n```\n\nNew prose.\n"
                result = self.render(source)
                self.assertEqual(
                    result,
                    tag + "\n```\n{%\n```\n\n" + mark("New prose.") + "\n",
                )
                self.assert_coverage(source, result)

    def test_literal_openers_do_not_hide_later_genuine_tags(self):
        for literal in ("`{%`", "```\n{%\n```", "    {%"):
            for tag in (
                '{% card title="` %} quoted" %}',
                "{% card title='unfinished\nNew prose.",
            ):
                with self.subTest(literal=literal, tag=tag):
                    source = literal + "\n\n" + tag
                    result = self.render(source)
                    self.assertEqual(result, source)

    def test_unterminated_markdoc_is_conservatively_protected(self):
        self.assertEqual(
            self.render("before {% tag title='unfinished\ntext"),
            mark("before ") + "{% tag title='unfinished\ntext",
        )

    def test_aside_fences_are_syntax_but_labels_are_prose(self):
        source = ":::note\nBody text.\n:::\n\n:::caution[Read this]{.wide}\nMore.\n::::\n"
        expected = (
            ":::note\n"
            + mark("Body text.")
            + "\n:::\n\n:::caution["
            + mark("Read this")
            + "]{.wide}\n"
            + mark("More.")
            + "\n::::\n"
        )
        self.assertEqual(self.render(source), expected)

    def test_blockquoted_directives_and_crlf(self):
        source = "> > :::caution[Read this]{.wide}\r\n> Body\r\n> > ::::  \r\n"
        self.assertEqual(
            self.render(source),
            "> > :::caution["
            + mark("Read this")
            + "]{.wide}\r\n> "
            + mark("Body")
            + "\r\n> > ::::  \r\n",
        )

    def test_syntax_link_code_metadata_parity(self):
        source = (
            "---\ntitle: Metadata\n---\n\n# Heading\n\n"
            '**Bold** and _emphasis_ with `code()` and [label](https://example.test "title").\n\n'
            "[full label][ref] and [ref] and [ref][].\n\n[ref]: https://example.test\n\n"
            "https://example.test and <https://example.test>\n\n> Quote\n\n- List item\n\n"
            "| Header | Next |\n| --- | --- |\n| Cell | Value |\n\n"
            'Escaped \\* and &amp; stay intact.\n\n```python\nprint("code")\n```\n\n'
            '    indented_code()\n\n<div class="x">HTML block</div>\n'
        )
        result = self.render(source)
        for fragment in (
            "title: Metadata",
            "`code()`",
            "https://example.test",
            '"title"',
            "[ref]",
            "[ref][]",
            "\\*",
            "&amp;",
            'print("code")',
            "    indented_code()",
            '<div class="x">',
        ):
            self.assertIn(fragment, result)
        for prose in (
            "Heading",
            "Bold",
            "emphasis",
            "label",
            "full label",
            "Cell",
            "Quote",
            "List item",
        ):
            self.assertIn(mark(prose), result)

    def test_plain_text_and_legacy_markdown_boolean(self):
        source = "# Heading\n`code` {% tag %} :::note"
        self.assertEqual(self.render(source, None), mark(source))
        self.assertEqual(
            editing.remark("", source, markdown=False), mark(source)
        )
        self.assertEqual(
            editing.remark("", source, markdown=False, profile="markdown"),
            self.render(source, "markdown"),
        )

    def test_callable_profile_and_cluster_protection(self):
        seen = []

        def profile(text):
            seen.append(text)
            return [i == 1 for i in range(len(text))]

        self.assertEqual(
            self.render("e\u0301 prose", profile), "e\u0301 " + mark("prose")
        )
        self.assertEqual(seen, ["e\u0301 prose"])

    def test_resolver_names_composition_and_lengths(self):
        from textprov.syntax import resolve_profile

        source = "😀 {% card %}\r\n:::note\n# Heading\n"
        for profile in (
            DOCS,
            "markdown,markdoc,directives",
            " markdown, markdoc, directives ",
        ):
            flags = resolve_profile(profile)(source)
            self.assertEqual(len(flags), len(source))
            self.assertTrue(all(isinstance(flag, bool) for flag in flags))
            self.assertEqual(self.render(source, profile), self.render(source))
        self.assertEqual(resolve_profile(None)(source), [False] * len(source))
        with self.assertRaises(ValueError):
            resolve_profile("unknown")
        with self.assertRaises(ValueError):
            resolve_profile("markdown,,markdoc")
        with self.assertRaises(TypeError):
            resolve_profile(12)

    def test_names_are_opt_in_and_compose_in_any_order(self):
        from textprov.syntax import resolve_profile

        source = "Before {% card %}\n:::note\n`code`\n"
        self.assertEqual(
            editing.remark("", source), self.render(source, "markdown")
        )
        self.assertEqual(
            self.render(source, "markdoc"),
            mark("Before ") + "{% card %}" + mark("\n:::note\n`code`\n"),
        )
        self.assertEqual(
            self.render(source, "directives"),
            mark("Before {% card %}\n") + ":::note\n" + mark("`code`\n"),
        )
        expected = resolve_profile(DOCS)(source)
        self.assertEqual(
            resolve_profile(tuple(reversed(DOCS)))(source), expected
        )
        self.assertEqual(resolve_profile(DOCS + DOCS)(source), expected)

    def test_markdoc_mask_preserves_exact_code_point_offsets(self):
        from textprov.syntax import resolve_profile

        tag = '{% card title="😀 %} quoted"\r\n other="value" %}'
        source = "😀 " + tag + " prose"
        flags = resolve_profile("markdoc")(source)
        self.assertEqual(flags, [False] * 2 + [True] * len(tag) + [False] * 6)

    def test_rewrite_profile_uses_surrounding_document_context(self):
        source = '{% card title="old" %}\nBody\n'
        pair = editing.rewrite_edit(source, "old", "new", profile=DOCS)
        self.assertEqual(source.replace(*pair), source.replace("old", "new"))
        source = "```\nold\n```\n"
        pair = editing.rewrite_edit(source, "old", "new", profile=DOCS)
        self.assertEqual(source.replace(*pair), source.replace("old", "new"))
        source = ":::caution[Old]{.wide}\n"
        pair = editing.rewrite_edit(source, "Old", "New label", profile=DOCS)
        self.assertEqual(
            source.replace(*pair),
            ":::caution[" + mark("New label") + "]{.wide}\n",
        )

    def test_invalid_callable_mask_is_rejected(self):
        for profile in (lambda text: [], lambda text: [1] * len(text)):
            with self.assertRaises(ValueError):
                self.render("prose", profile)

    def test_finalize_accepts_profile(self):
        source = ":::note\nBody\n:::\n"
        self.assertEqual(
            editing.finalize(
                source, [True] * len(source), True, set(), 5, profile=DOCS
            ),
            self.render(source),
        )

    def test_rewrite_edit_threads_profile_and_legacy_boolean(self):
        source = "old\n"
        replacement = ":::note\n# New\n:::\n"
        old, new = editing.rewrite_edit(
            source, source, replacement, profile=DOCS
        )
        self.assertEqual(old, source)
        self.assertEqual(new, self.render(replacement))
        old, new = editing.rewrite_edit(source, source, "`code`", profile=None)
        self.assertEqual(new, mark("`code`"))
        old, new = editing.rewrite_edit(
            source, source, "`code`", markdown=False
        )
        self.assertEqual(new, mark("`code`"))

    def test_existing_pua_and_genuine_ivs_survive(self):
        for prefix in (
            mark("Old", mode="pua"),
            "辻\U000e0100",
            mark("Human", state="human"),
        ):
            with self.subTest(prefix=prefix):
                source = prefix + " old text\n"
                plain = textprov.strip_marks(source)
                result = editing.remark(
                    source, plain + ":::note\nNew prose\n:::\n", profile=DOCS
                )
                self.assertTrue(result.startswith(source))
                self.assertIn(
                    ":::note\n" + mark("New prose") + "\n:::\n", result
                )
                pair = editing.rewrite_edit(
                    source, "old text", "old text plus", profile=DOCS
                )
                self.assertEqual(
                    source.replace(*pair),
                    prefix + " old text " + mark("plus") + "\n",
                )

    def test_profiles_do_not_relabel_unchanged_or_delete_marks(self):
        source = mark("# Legacy heading") + "\n\nold"
        self.assertEqual(
            editing.remark(
                source, textprov.strip_marks(source) + " X", profile=DOCS
            ),
            source + " " + mark("X"),
        )


if __name__ == "__main__":
    unittest.main()
