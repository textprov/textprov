"""Characterize document author/checker alignment; optional external docs acceptance.

Run the portable tests from python/ with unittest discovery. The opt-in CLI runs
an unchanged docs checkout through an in-memory dogfood adapter; see alignment.md.
"""

import argparse
import inspect
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

import textprov
from textprov.check import check_text

DOCS = ("markdown", "markdoc", "directives")
mark = textprov.mark
strip = textprov.strip_marks

# Inputs from tools/tests/test_dogfood.py and test_docs_profile.py. Invalid
# origin, marked replacement, and partial-grapheme requests belong to the scoped
# docs wrapper, not the whole-document public API.
SYNTAX = (
    "---\ntitle: Metadata\n---\n\n# Heading\n\n"
    '**Bold** and _emphasis_ with `code()` and [label](https://example.test "title").\n\n'
    "[full label][ref] and [ref] and [ref][].\n\n"
    "[ref]: https://example.test\n\n"
    "https://example.test and <https://example.test>\n\n"
    "> Quote\n\n- List item\n\n"
    "| Header | Next |\n| --- | --- |\n| Cell | Value |\n\n"
    "Escaped \\* and &amp; stay intact.\n\n"
    '```python\nprint("code")\n```\n\n'
    '    indented_code()\n\n<div class="x">HTML block</div>\n'
)
FIXTURES = [
    ("separate_edits", "alpha unchanged omega", "Alpha unchanged Omega", None),
    ("inside_word", mark("cat", state="human"), "cart", None),
    ("deletion", "aXbc", "abc", None),
    (
        "reflow_move",
        "legacy paragraph\n" + mark("a different ending", state="human"),
        "a different\nending\nlegacy paragraph",
        None,
    ),
    ("utf8_crlf", "", "# Café 😀\r\n\r\nNew prose.\r\n", DOCS),
    ("syntax", "", SYNTAX, DOCS),
    (
        "directives",
        "",
        ":::note\nBody text.\n:::\n\n:::caution[Read this]{.wide}\nMore.\n::::\n",
        DOCS,
    ),
    (
        "outside_edit",
        mark("Hello", state="human") + " world",
        "Hello earth",
        None,
    ),
    (
        "legacy_defect",
        mark("# Legacy heading") + "\n\nold",
        "# Legacy heading\n\nold X",
        DOCS,
    ),
    (
        "legacy_pua",
        mark("Old", mode="pua") + " prose\n",
        "Old new prose\n",
        DOCS,
    ),
    (
        "markdoc",
        "",
        '---\ntitle: Plain title\n---\n\n{% card title="Do not mark" %}\n\nNew **prose**, `code`, and [label](/en/start).\n\n{% /card %}\n',
        DOCS,
    ),
    ("genuine_ivs", "辻\U000e0100 old text", "辻 new text", DOCS),
    ("singleton", "cat", "bag", None),
    ("two_cluster", "axyc", "bxyd", None),
    (
        "two_cluster_move",
        "a" + mark("xy", state="human") + "\nmiddle\n",
        "a\nmiddlexy\n",
        None,
    ),
    ("bulgarian", mark("Актив") + "ен", "Активна", None),
    ("spanish", "secreto", "valor SECRET", None),
]
FIXTURES += [
    ("grapheme_" + str(i), "", value, None)
    for i, value in enumerate(("e\u0301", "👨‍👩‍👧", "🇨🇦", "👍🏽", "❤️"))
]
FIXTURES += [("changed_grapheme", "e", "e\u0301", None)]
FIXTURES += [
    (
        "polish_first",
        "Czas życia sekretu.\n\n## Pytania lub potrzebujesz wsparcia?\n",
        "Czas ważności sekretu.\n\n## Pytania lub potrzebujesz wsparcia?\n",
        DOCS,
    ),
    (
        "polish_second",
        "Czas "
        + mark("wa")
        + "ż"
        + mark("noś")
        + "ci sekretu.\n\n## Pytania lub potrzebujesz wsparcia?\n",
        "Czas ważności sekretu.\n\n## Pytania lub potrzebujesz pomocy?\n",
        DOCS,
    ),
    ("cumulative_delete", "axy\nmiddle\n", "a\nmiddle\n", None),
    ("cumulative_insert", "a\nmiddle\n", "a\nmiddlexy\n", None),
]
FIXTURES += [
    ("survivor_" + str(i), "c" + value + "t", "bag", None)
    for i, value in enumerate(
        ("a", mark("a"), mark("a", state="human"), mark("a", mode="pua"))
    )
]


class DocumentAlignmentTests(unittest.TestCase):
    def test_every_authoring_fixture_is_checked(self):
        # Filled with exact observed checker results below rather than asserting
        # the two different notions of unchanged text are interchangeable.
        for name, old, new, profile in FIXTURES:
            with self.subTest(fixture=name):
                result = textprov.mark_document_edit(old, new, profile=profile)
                self.assertEqual(strip(result), new)
                problems = check_text(old, result, profile=profile)
                expected = EXPECTED_PROBLEMS.get(name, [])
                self.assertEqual(problems, expected)

    def test_new_documents_use_the_same_public_profile(self):
        for name, old, new, profile in FIXTURES:
            if not old:
                with self.subTest(fixture=name):
                    self.assertEqual(
                        textprov.mark_document(new, profile=profile),
                        textprov.mark_document_edit("", new, profile=profile),
                    )

    def test_singleton_is_new_to_author_but_legacy_to_checker(self):
        result = textprov.mark_document_edit("cat", "bag", profile=None)
        self.assertEqual(result, mark("bag"))
        self.assertEqual(
            check_text("cat", result, profile=None),
            [(1, 2, "marked unchanged legacy text")],
        )

    def test_html_block_body_is_protected(self):
        # Issue #39: the heuristic now agrees with the docs AST, which treats
        # the entire raw HTML node as protected. Only the following paragraph
        # is prose.
        source = '<div class="x">HTML block</div>\n\nAfter.\n'
        result = textprov.mark_document(source, profile=DOCS)
        self.assertEqual(result, source[:-7] + mark("After.") + "\n")
        self.assertEqual(check_text("", result, profile=DOCS), [])
        self.assertTrue(
            any(
                message == "new prose cluster has no supported origin mark"
                for _, _, message in check_text("", source, profile=DOCS)
            )
        )

    def test_whole_document_and_declared_span_have_different_edit_context(self):
        old = "axy\nmiddle\n"
        whole = textprov.mark_document_edit(old, "a\nmiddle\n", profile=None)
        scoped = (
            old[:1]
            + textprov.mark_document_edit("xy", "", profile=None)
            + old[3:]
        )
        self.assertEqual(whole, mark("a") + "\nmiddle\n")
        self.assertEqual(scoped, "a\nmiddle\n")
        self.assertEqual(check_text(old, whole, profile=None), [(1, 1, LEGACY)])
        self.assertEqual(check_text(old, scoped, profile=None), [])

    def test_inside_word_replacement_does_not_carry_partial_human_word(self):
        old = mark("cat", state="human")
        result = textprov.mark_document_edit(old, "cart", profile=None)
        self.assertEqual(result, mark("cart"))
        self.assertEqual(
            check_text(old, result, profile=None),
            [
                (1, 1, "changed or lost an existing mark"),
                (1, 2, "changed or lost an existing mark"),
                (1, 4, "changed or lost an existing mark"),
            ],
        )


LEGACY = "marked unchanged legacy text"
CHANGED = "changed or lost an existing mark"


def at(line, columns, message=LEGACY):
    return [(line, column, message) for column in columns]


EXPECTED_PROBLEMS = {
    "separate_edits": at(
        1, [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20, 21]
    ),
    "inside_word": at(1, [1, 2, 4], CHANGED),
    "deletion": at(1, [1, 2, 3]),
    "reflow_move": at(1, [1, 3, 4, 5, 6, 7, 8, 9, 10, 11], CHANGED)
    + at(2, [1, 2, 3, 4, 5, 6], CHANGED)
    + at(3, [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16]),
    "outside_edit": at(1, [9]),
    "singleton": at(1, [2]),
    "two_cluster": at(1, [2, 3]),
    "two_cluster_move": at(1, [1])
    + at(2, [1, 2, 3, 4, 5, 6])
    + at(2, [7, 8], CHANGED),
    "bulgarian": at(1, [6]),
    "spanish": at(1, [5]),
    "survivor_0": at(1, [2]),
    "survivor_2": at(1, [2], CHANGED),
    "survivor_3": at(1, [2], CHANGED),
    "polish_first": at(1, [8, 12, 13]),
    "polish_second": at(3, [29, 33, 35]),
    "cumulative_delete": at(1, [1]),
    "cumulative_insert": at(2, [1, 2, 3, 4, 5, 6]),
}


def profile_for(path):
    return None if path.suffix.lower() == ".txt" else DOCS


def install_adapter(root, mode):
    """Load real docs integration; replace only its declared computation seams."""
    path = root / "tools/dogfood.py"
    module = types.ModuleType("dogfood")
    module.__file__ = str(path)
    sys.modules["dogfood"] = module
    source = path.read_text()

    exec(compile(source, str(path), "exec"), module.__dict__)
    original_edit = module.mark_edit
    original_check = module.check_text
    captures = []

    def checked(path, before, after, require_marks=True):
        if mode in ("checker-ast", "integrated") and path.suffix.lower() in (
            ".md",
            ".mdoc",
        ):
            module.markdown_info([strip(after)])
        problems = check_text(
            before,
            after,
            profile=profile_for(path),
            require_marks=require_marks,
        )
        if (
            mode in ("checker-ast", "integrated")
            and not problems
            and before != after
        ):
            try:
                module.validate_markdown(path, after)
            except ValueError as error:
                try:
                    module.validate_markdown(path, before)
                except ValueError:
                    pass
                else:
                    problems.append((1, 1, str(error)))
        return problems

    def edited(path, source, start, end, replacement, state):
        # All docs input validation is retained verbatim by running the original
        # operation first. Its result is an AST baseline, NOT the returned edit.
        baseline = original_edit(path, source, start, end, replacement, state)
        plain = strip(source)
        old = module.clusters(source)
        inside = "".join(
            item.raw for item in old if item.start >= start and item.end <= end
        )
        before = "".join(item.raw for item in old if item.end <= start)
        after = "".join(item.raw for item in old if item.start >= end)
        candidate = plain[:start] + replacement + plain[end:]
        from textprov.syntax import resolve_profile

        flags = resolve_profile(profile_for(path))(candidate)

        def scoped_profile(text):
            if text != replacement:
                raise ValueError(
                    "scoped public authoring changed replacement text"
                )
            return flags[start : start + len(replacement)]

        marked = textprov.mark_document_edit(
            inside, replacement, profile=scoped_profile
        )
        if state == "human":
            # The API declares AI, not human. A second call with old AI selectors
            # changed to human identifies carried selectors without reimplementing
            # merge. Only AI selectors identical in both outputs are introduced.
            ai = chr(module.MAPPING.selectors["ai"])
            human = chr(module.MAPPING.selectors["human"])
            probe = textprov.mark_document_edit(
                inside.replace(ai, human), replacement, profile=scoped_profile
            )
            a, b = (
                list(textprov.segments(marked)),
                list(textprov.segments(probe)),
            )
            if len(a) != len(b):
                raise ValueError("human-origin probe changed grapheme count")
            marked = "".join(
                x[:-1] + human if x == y and x.endswith(ai) else x
                for x, y in zip(a, b)
            )
        result = before + marked + after
        if strip(result) != candidate:
            raise ValueError("edit did not preserve the intended plain text")
        if mode == "integrated":
            module.validate_markdown(path, result, baseline)
        return result

    def captured(path, source, start, end, replacement, state):
        result = original_edit(path, source, start, end, replacement, state)
        if state == "ai":
            label = next(
                (
                    frame.function
                    for frame in inspect.stack()
                    if frame.function.startswith("test_")
                ),
                "unknown",
            )
            captures.append(
                (label, path, source, start, end, replacement, result)
            )
        return result

    if mode == "baseline":
        module.mark_edit = captured
    elif mode in ("checker", "checker-ast"):
        module.check_text = checked
    else:
        module.check_text = checked
        module.mark_edit = edited
    return module, captures, original_check


def acceptance(root, mode, output):
    """Run every real docs test, including subprocess and repository cases."""
    root = root.resolve()
    module, captures, original_check = install_adapter(root, mode)
    sys.path.insert(0, str(root / "tools"))
    # The executable wrapper ensures normal dogfood subprocesses use the same
    # adapter. -S dependency tests deliberately run the real interpreter.
    with tempfile.TemporaryDirectory(
        prefix=".alignment-acceptance-", dir=root
    ) as temporary:
        wrapper = Path(temporary) / "python"
        wrapper.write_text(
            "#!" + sys.executable + "\n"
            "import os,sys,runpy\n"
            "real=" + repr(sys.executable) + "\n"
            "if sys.argv[1:2] == ['-S']:\n    os.execv(real,[real,*sys.argv[1:]])\n"
            "ns=runpy.run_path(" + repr(str(Path(__file__).resolve())) + ")\n"
            "m,_,_=ns['install_adapter']("
            + "__import__('pathlib').Path("
            + repr(str(root))
            + "),"
            + repr(mode)
            + ")\n"
            "sys.exit(m.main(sys.argv[2:]))\n"
        )
        wrapper.chmod(0o755)
        print("SHIM", wrapper, flush=True)
        real = sys.executable
        sys.executable = str(wrapper)
        try:
            suite = unittest.defaultTestLoader.discover(
                str(root / "tools/tests")
            )
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        finally:
            sys.executable = real
    records = []
    for index, (label, path, old, start, end, new, docs_result) in enumerate(
        captures
    ):
        candidate = strip(old)[:start] + new + strip(old)[end:]
        public = textprov.mark_document_edit(
            old, candidate, profile=profile_for(path)
        )
        records.append(
            {
                "fixture": index,
                "test": label,
                "path": str(path),
                "old": old,
                "new": candidate,
                "docs_result": docs_result,
                "public_result": public,
                "bytes_equal": docs_result == public,
                "upstream_problems": check_text(
                    old, public, profile=profile_for(path)
                ),
                "docs_problems": original_check(path, old, public),
            }
        )
    report = {
        "mode": mode,
        "executable": sys.executable,
        "pythonpath": os.environ.get("PYTHONPATH"),
        "version": textprov.__version__,
        "module": textprov.__file__,
        "tests": result.testsRun,
        "failures": [(test.id(), detail) for test, detail in result.failures],
        "errors": [(test.id(), detail) for test, detail in result.errors],
        "cross": records,
    }
    output.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
    print("REPORT", output)
    return int(not result.wasSuccessful())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-root", type=Path)
    parser.add_argument(
        "--mode",
        choices=("baseline", "checker", "checker-ast", "direct", "integrated"),
        default="integrated",
    )
    parser.add_argument("--output", type=Path)

    args = parser.parse_args()

    if args.docs_root:
        if args.output is None:
            parser.error("--output is required for external acceptance")
        raise SystemExit(acceptance(args.docs_root, args.mode, args.output))
    unittest.main(argv=[sys.argv[0]])
