"""Provider-neutral prose marking and mark-aware edits.

These functions process text only: callers supply any recorded human passages.
Markdown protection is a conservative heuristic, not a complete parser.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from . import default_mapping, mark, runs, segments

MAPPING = default_mapping()
SELECTORS = set(MAPPING.selectors.values())
PUA = MAPPING.pua2base
HUMAN_MIN_WORDS = 5


def plain_map(raw):
    """Return `raw` without marks and, for each plain char, its index in `raw`."""
    plain, index = [], []
    for position, char in enumerate(raw):
        cp = ord(char)
        if cp in SELECTORS:
            continue
        entry = PUA.get(cp)
        plain.append(chr(entry[0]) if entry else char)
        index.append(position)
    return "".join(plain), index


def raw_span(raw, index, start, end):
    """The slice of `raw` holding plain[start:end] and the marks on it."""
    if start >= end:
        return ""
    first = index[start] if start else 0
    last = index[end] if end < len(index) else len(raw)
    return raw[first:last]


def common_affixes(old, new):
    """Lengths of the common prefix and suffix, cut back to whole words.

    "beta" and "delta" share "ta", but "delta" is one new word, not a new
    "del" in front of an old "ta".
    """
    limit = min(len(old), len(new))
    pre = 0
    while pre < limit and old[pre] == new[pre]:
        pre += 1
    suf = 0
    while suf < limit - pre and old[-1 - suf] == new[-1 - suf]:
        suf += 1

    def space(text, position):
        return not 0 <= position < len(text) or text[position].isspace()

    if not (space(old, pre) and space(new, pre)):
        while pre and not new[pre - 1].isspace():
            pre -= 1
    if not (space(old, len(old) - suf - 1) and space(new, len(new) - suf - 1)):
        while suf and not new[-suf].isspace():
            suf -= 1
    return pre, suf


def line_offsets(lines):
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def merge(old_raw, new_raw, carry):
    """Align `new_raw` to `old_raw` and flag what is new.

    Lines are diffed on their unmarked text. Within a changed hunk the common
    prefix and suffix count as unchanged and only the middle is flagged: a
    character diff would call the letters a rewritten sentence happens to share
    unchanged. Returns (text, flags), one flag per code point of text.

    With `carry`, unchanged text is taken from `old_raw`, so marks the agent
    failed to retype survive. Without it `new_raw` is kept as found on disk.
    """
    old_plain, old_index = plain_map(old_raw)
    new_plain, new_index = plain_map(new_raw)
    old_lines = old_plain.splitlines(True)
    new_lines = new_plain.splitlines(True)
    old_at = line_offsets(old_lines)
    new_at = line_offsets(new_lines)
    out, flags = [], []

    def emit(text, flag):
        out.append(text)
        flags.extend([flag] * len(text))

    def kept(old_range, new_range):
        if carry:
            emit(raw_span(old_raw, old_index, *old_range), False)
        else:
            emit(raw_span(new_raw, new_index, *new_range), False)

    matcher = SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        a1, a2, b1, b2 = old_at[i1], old_at[i2], new_at[j1], new_at[j2]
        if tag == "equal":
            kept((a1, a2), (b1, b2))
        elif tag == "insert":
            emit(raw_span(new_raw, new_index, b1, b2), True)
        elif tag == "replace":
            pre, suf = common_affixes(old_plain[a1:a2], new_plain[b1:b2])
            kept((a1, a1 + pre), (b1, b1 + pre))
            emit(raw_span(new_raw, new_index, b1 + pre, b2 - suf), True)
            kept((a2 - suf, a2), (b2 - suf, b2))
    return "".join(out), flags


# --- markdown --------------------------------------------------------------

FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r" {0,3}#{1,6}(\s|$)")
RULE = re.compile(r" {0,3}(=+|-+|([-*_])( *\2){2,})\s*$")
TABLE_RULE = re.compile(r"\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
DEFINITION = re.compile(r" {0,3}\[([^\]]+)\]:")
LEADER = re.compile(
    r"(\s*>)*(\s*(?:[-+*]|\d{1,9}[.)])(?=\s))*(\s+\[[ xX]\](?=\s))?\s*"
)
LIST_ITEM = re.compile(r"\s*(?:[-+*]|\d{1,9}[.)])\s")
RAW_BLOCKS = re.compile(
    r"<!--.*?-->|<(script|style|pre|code|textarea)\b.*?</\1\s*>",
    re.DOTALL | re.IGNORECASE,
)
INLINE = [
    # code span
    re.compile(r"(?<!`)(`+)(?!`)(?:(?!\n\s*\n).)+?(?<!`)\1(?!`)", re.DOTALL),
    # Dollar-delimited LaTeX, including multiline display math. Escaped dollars
    # are content, not delimiters; require matching single or double dollars.
    re.compile(
        r"(?<![\\$])(\${1,2})(?!\$)(?:\\.|[^\\$])+?\1(?!\$)",
        re.DOTALL,
    ),
    # link or image destination, second label of a reference link, footnote
    re.compile(r"\]\((?:[^()\\\n]|\\.|\([^()\n]*\))*\)"),
    re.compile(r"\]\[[^\]\n]*\]"),
    re.compile(r"\[[\^!][^\]\n]+\]"),
    # autolink, bare URL, HTML tag, entity, backslash escape
    re.compile(r"<[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*>|<[^<>\s@]+@[^<>\s]+>"),
    re.compile(r"\b(?:https?://|www\.)[^\s<>)\]]+"),
    re.compile(r"</?[A-Za-z][^<>\n]*>"),
    re.compile(r"&(?:#\d+|#[xX][0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]*);"),
    re.compile(r"\\."),
    # characters that are, or may begin, inline syntax
    re.compile(r"[*_~`\[\]<|]|!(?=\[)"),
]


def markdown_protected(plain):
    """One flag per code point: true where a mark could change how it parses."""
    protected = [False] * len(plain)

    def protect(start, end):
        protected[start:end] = [True] * (end - start)

    lines = plain.splitlines(True)
    at = line_offsets(lines)
    whole = [False] * len(lines)

    labels = set()
    fence = None
    in_list = False
    previous_blank = True
    previous_code = False
    front_matter = (
        bool(lines)
        and lines[0].strip() == "---"
        and any(line.strip() in ("---", "...") for line in lines[1:])
    )
    for number, line in enumerate(lines):
        blank = not line.strip()
        if front_matter:
            whole[number] = True
            if number and line.strip() in ("---", "..."):
                front_matter = False
            continue
        if fence:
            whole[number] = True
            closing = FENCE.match(line)
            if (
                closing
                and closing.group(1)[0] == fence[0]
                and len(closing.group(1)) >= len(fence)
                and not line[closing.end() :].strip()
            ):
                fence = None
            continue
        opening = FENCE.match(line)
        if opening:
            fence = opening.group(1)
            whole[number] = True
            previous_blank = previous_code = False
            continue
        indented = line.startswith(("    ", "\t")) and not blank
        if indented and not in_list and (previous_blank or previous_code):
            whole[number] = True
            previous_code, previous_blank = True, False
            continue
        if not blank:
            previous_code = False
            if LIST_ITEM.match(line):
                in_list = True
            elif not line[0].isspace():
                in_list = False
        definition = DEFINITION.match(line)
        rule = RULE.match(line)
        if rule:
            whole[number] = True
            # Only a run of = or - underlines a setext heading; a thematic
            # break (***, ___, - - -) leaves the line above it prose.
            if number and not previous_blank and not rule.group(2):
                whole[number - 1] = True  # setext heading text
        elif HEADING.match(line) or TABLE_RULE.match(line):
            whole[number] = True
        elif definition and not definition.group(1).startswith("^"):
            labels.add(definition.group(1).strip().lower())
            whole[number] = True
        elif definition:
            protect(at[number], at[number] + definition.end())
        else:
            leader = LEADER.match(line)
            if leader:
                protect(at[number], at[number] + leader.end())
        previous_blank = blank

    for number, flag in enumerate(whole):
        if flag:
            protect(at[number], at[number + 1])

    for match in RAW_BLOCKS.finditer(plain):
        protect(match.start(), match.end())

    # Inline syntax, within each stretch of lines that is not wholly protected.
    number = 0
    while number < len(lines):
        if whole[number]:
            number += 1
            continue
        first = number
        while number < len(lines) and not whole[number]:
            number += 1
        base = at[first]
        block = plain[base : at[number]]
        for pattern in INLINE:
            for match in pattern.finditer(block):
                protect(base + match.start(), base + match.end())
        if labels:
            for match in re.finditer(r"\[([^\]\n]+)\]", block):
                if match.group(1).strip().lower() in labels:
                    protect(base + match.start(), base + match.end())
    return protected


# --- the prompt log -----------------------------------------------------------

WORD = re.compile(r"\S+")
BLOCK_MARKERS = {">", "-", "*", "+"}


def words_of(text):
    return [
        match
        for match in WORD.finditer(text)
        if match.group() not in BLOCK_MARKERS
    ]


def human_shingles(marked_texts, min_words=HUMAN_MIN_WORDS):
    """Build word windows from human-marked runs in supplied text strings."""
    if min_words < 1:
        raise ValueError("min_words must be positive")
    shingles = set()
    for text in marked_texts:
        for state, run in runs(text, strip=True):
            if state != "human":
                continue
            words = [match.group() for match in words_of(run)]
            for start in range(len(words) - min_words + 1):
                shingles.add(tuple(words[start : start + min_words]))
    return shingles


def human_mask(plain, added, shingles, min_words):
    """Flag added text that repeats a recorded prompt word for word."""
    human = [False] * len(plain)
    if not shingles:
        return human
    words = [
        match
        for match in words_of(plain)
        if all(added[match.start() : match.end()])
    ]
    size = min_words
    for start in range(len(words) - size + 1):
        window = words[start : start + size]
        if tuple(match.group() for match in window) in shingles:
            first, last = window[0].start(), window[-1].end()
            # A word that was not added breaks the window apart.
            if all(
                added[k] for k in range(first, last) if not plain[k].isspace()
            ):
                human[first:last] = [True] * (last - first)
    return human


# --- marking ---------------------------------------------------------------


def finalize(raw, flags, markdown, shingles, min_words):
    """Mark the flagged, unprotected clusters of `raw`; leave the rest alone."""
    plain, index = plain_map(raw)
    added = [flags[position] for position in index]
    protected = markdown_protected(plain) if markdown else [False] * len(plain)
    human = human_mask(plain, added, shingles, min_words)
    want: list[str | None] = [None] * len(raw)
    for k, position in enumerate(index):
        if added[k] and not protected[k]:
            want[position] = "human" if human[k] else "ai"

    out, segment, state = [], [], None

    def flush():
        text = "".join(segment)
        out.append(mark(text, state=state) if state else text)
        del segment[:]

    position = 0
    for cluster in segments(raw):
        cp = ord(cluster[0])
        base = (
            cluster[:-1]
            if len(cluster) > 1 and ord(cluster[-1]) in SELECTORS
            else cluster
        )
        if (
            len(cluster) == 1 and (cp in SELECTORS or cp in PUA)
        ) or base.isspace():
            cluster_state = (
                state  # inert: a lone selector, a PUA mark, whitespace
            )
        else:
            cluster_state = want[position]
        if cluster_state != state:
            flush()
            state = cluster_state
        segment.extend(cluster)
        position += len(cluster)
    flush()
    return "".join(out)


def remark(
    old_raw,
    new_raw,
    markdown=True,
    carry=True,
    shingles=None,
    min_words=HUMAN_MIN_WORDS,
):
    """Mark added prose, preserving old marks when carry is true.

    Without shingles, all new eligible text is AI-labelled. Supply windows
    from human_shingles to label verbatim human passages instead.
    """
    if min_words < 1:
        raise ValueError("min_words must be positive")
    if shingles is None:
        shingles = set()
    text, flags = merge(old_raw, new_raw, carry)
    return finalize(text, flags, markdown, shingles, min_words)


class Ambiguous(Exception):
    pass


def rewrite_edit(
    raw,
    old_string,
    new_string,
    replace_all=False,
    shingles=None,
    min_words=HUMAN_MIN_WORDS,
):
    """Translate a replacement so it applies to a marked file and marks what it adds.

    Returns (old_string, new_string) to apply to the raw text, or None when
    `old_string` is absent and the tool should report that itself.
    """
    if min_words < 1:
        raise ValueError("min_words must be positive")
    if shingles is None:
        shingles = set()
    plain, index = plain_map(raw)
    needle, _ = plain_map(old_string)
    if not needle:
        return None
    found = []
    start = plain.find(needle)
    while start != -1:
        found.append(start)
        start = plain.find(needle, start + len(needle))
    if not found:
        return None
    if len(found) > 1 and not replace_all:
        raise Ambiguous(
            f"old_string matches {len(found)} places in the file once "
            "provenance marks are ignored. Add surrounding context to make "
            "it unique, or use replace_all."
        )
    results = set()
    for start in found:
        end = start + len(needle)
        first = index[start] if start else 0
        last = index[end] if end < len(index) else len(raw)
        text, flags = merge(raw[first:last], new_string, carry=True)
        tail = len(raw) - last
        whole = finalize(
            raw[:first] + text + raw[last:],
            [False] * first + flags + [False] * tail,
            True,
            shingles,
            min_words,
        )
        results.add((raw[first:last], whole[first : len(whole) - tail]))
    if len(results) > 1:
        raise Ambiguous(
            "replace_all would touch occurrences that carry different "
            "provenance marks or sit in different markdown contexts. Edit "
            "them one at a time."
        )
    return results.pop()
