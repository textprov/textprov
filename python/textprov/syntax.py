"""Offset-preserving syntax protection for document authoring.

Profiles take unmarked text and return one bool per Python code point. True
protects syntax from new marks; False leaves prose eligible for marking.
These are conservative heuristics, not full document parsers.

The Markdown profile protects CommonMark HTML blocks (types 1-6) whole, so a
`<div>` body is not prose. Type 7 blocks and blocks inside blockquotes or list
items are not recognised; see `editing`. The composed Markdown and Markdoc
scanner treats HTML blocks like fenced code: `{% %}` inside them is literal
and is not masked, so a tag-only line cannot end the block early.
"""

import re

# Distinguish an omitted profile (legacy markdown boolean) from explicit None.
DEFAULT_PROFILE = object()


def plain_protected(text):
    return [False] * len(text)


def markdown_protected(text):
    # Keep the existing heuristic and its plugin-facing import path in editing.
    from .editing import markdown_protected as protect

    return protect(text)


def _tag_end(text, start):
    end, quote = start + 2, None
    while end < len(text):
        char = text[end]
        if quote:
            if char == "\\":
                end = min(end + 2, len(text))
                continue
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif text.startswith("%}", end):
            return end + 2
        end += 1
    return end


def markdoc_protected(text):
    """Protect tags, ignoring escaped quotes and closing tokens inside strings."""
    flags = [False] * len(text)
    cursor = 0
    while True:
        start = text.find("{%", cursor)
        if start < 0:
            return flags
        end = _tag_end(text, start)
        flags[start:end] = [True] * (end - start)
        cursor = end


def _mask_tag_line(line, flags):
    # A neutral non-space prevents tag width from becoming code indentation.
    # Tag-only lines stay blank so they do not interrupt block boundaries.
    standalone = all(flag or char.isspace() for char, flag in zip(line, flags))
    neutral = " " if standalone else "x"
    return "".join(
        neutral if flag and char not in "\r\n" else char
        for char, flag in zip(line, flags)
    )


def _mask_tags(text, flags):
    masked, offset = [], 0
    for line in text.splitlines(True):
        end = offset + len(line)
        masked.append(_mask_tag_line(line, flags[offset:end]))
        offset = end
    return "".join(masked)


def _markdown_markdoc_protected(text):
    """Scan literal code and tags in source order; attributes are never Markdown.

    Fenced code, indented code and HTML blocks are tracked with the same rules
    as `editing.markdown_protected`, so the two scanners agree on where literal
    text starts and ends. Tags inside them are literal and stay unmasked.
    """
    from .editing import FENCE, HTML_BLOCK_END, INLINE, LIST_ITEM, html_block_end

    flags = [False] * len(text)
    fence = html = None
    previous_blank, previous_code, in_list = True, False, False
    offset = skip_until = 0
    for line in text.splitlines(True):
        end = offset + len(line)
        view = _mask_tag_line(line, flags[offset:end])
        blank = not view.strip()
        delimiter = FENCE.match(view)
        if fence:
            if (
                delimiter
                and delimiter.group(1)[0] == fence[0]
                and len(delimiter.group(1)) >= len(fence)
                and not view[delimiter.end() :].strip()
            ):
                fence = None
            offset = end
            continue
        if html is HTML_BLOCK_END and not line.strip():
            html = None
        elif html:
            if html is not HTML_BLOCK_END and html.search(line):
                html = None
            offset = end
            continue
        if offset >= skip_until and delimiter:
            fence = delimiter.group(1)
            previous_blank = previous_code = False
            offset = end
            continue
        if (
            offset >= skip_until
            and view.startswith(("    ", "\t"))
            and not blank
            and not in_list
            and (previous_blank or previous_code)
        ):
            previous_code, previous_blank = True, False
            offset = end
            continue
        if offset >= skip_until:
            html = html_block_end(line)
            if html:
                previous_blank = previous_code = False
                if html is not HTML_BLOCK_END and html.search(line):
                    html = None
                offset = end
                continue
        cursor = max(offset, skip_until)
        while cursor < end:
            if text.startswith("{%", cursor):
                skip_until = _tag_end(text, cursor)
                flags[cursor:skip_until] = [True] * (skip_until - cursor)
                cursor = skip_until
            elif text[cursor] == "`":
                code = INLINE[0].match(text, cursor)
                # A code span cannot cross a fenced block boundary.
                if code and not any(
                    FENCE.match(part)
                    for part in text[cursor : code.end()].splitlines()[1:]
                ):
                    skip_until = code.end()
                    cursor = skip_until
                else:
                    cursor += 1
            else:
                cursor += 1
        view = _mask_tag_line(line, flags[offset:end])
        blank = not view.strip()
        if not blank:
            previous_code = False
            if LIST_ITEM.match(view):
                in_list = True
            elif not view[0].isspace():
                in_list = False
        previous_blank = blank
        offset = end
    return flags


DIRECTIVE = re.compile(
    r"^((?:[ \t]*>)*[ \t]*)(:{3,}[A-Za-z0-9_-]*)"
    r"(?:\[([^\r\n]*)\])?(\{[^\r\n]*\})?[ \t]*\r?$",
    re.MULTILINE,
)


def directives_protected(text):
    """Protect container fence syntax; only an optional label is prose."""
    flags = [False] * len(text)
    for match in DIRECTIVE.finditer(text):
        start, end = match.span()
        flags[start:end] = [True] * (end - start)
        if match.group(3) is not None:
            start, end = match.span(3)
            flags[start:end] = [False] * (end - start)
    return flags


PROFILES = {
    "markdown": markdown_protected,
    "markdoc": markdoc_protected,
    "directives": directives_protected,
}


def resolve_profile(profile="markdown"):
    """Resolve a name, comma string, sequence of names, callable, or None.

    Named compositions union protection masks. With Markdown, Markdoc tags
    outside literal code are masked with neutral characters (blank on tag-only
    lines), retaining line endings and offsets without creating indentation.
    """
    if profile is None:
        return plain_protected
    if callable(profile):
        return profile
    if isinstance(profile, str):
        names = [name.strip() for name in profile.split(",")]
    elif isinstance(profile, (tuple, list)):
        names = list(profile)
    else:
        raise TypeError("profile must be a name, names, callable, or None")
    for name in names:
        if not isinstance(name, str) or name not in PROFILES:
            raise ValueError(f"unknown syntax profile: {name!r}")

    def protected(text):
        result = [False] * len(text)
        if "markdoc" in names:
            scanner = (
                _markdown_markdoc_protected
                if "markdown" in names
                else markdoc_protected
            )
            markdoc = scanner(text)
        else:
            markdoc = result
        masked = _mask_tags(text, markdoc) if "markdoc" in names else text
        for name in names:
            flags = (
                markdoc
                if name == "markdoc"
                else PROFILES[name](masked if name == "markdown" else text)
            )
            result = [a or b for a, b in zip(result, flags)]
        return result

    return protected
