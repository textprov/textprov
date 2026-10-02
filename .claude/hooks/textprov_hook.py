#!/usr/bin/env python3
"""Claude Code hooks that make this repository carry its own TextProv marks.

The harness runs this script, not the model, so a label never depends on the
model remembering to apply it. One script serves every event:

    UserPromptSubmit     record the prompt, marked `human`, in the prompt log
    PreToolUse  Write    rewrite `content` so what the agent adds is marked
    PreToolUse  Edit     match `old_string` through existing marks, and mark
                         what `new_string` adds
    PreToolUse  Bash     snapshot the markdown files
    PostToolUse Bash     mark what the command added to them

Text the agent adds is marked `ai`, except a passage that repeats a recorded
prompt word for word, which is marked `human`. Text that was already in a file
keeps whatever state it had, including none. Only markdown is marked, and only
its prose: code, link targets, headings, and markdown syntax are left alone.

This is the integration, in SPEC.md's terms: it decides which state applies.
The marks themselves come from the producer in ../../python/textprov.

Set TEXTPROV_HOOK=off to disable.
"""

import json
import os
import re
import subprocess
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

# The repository this script is committed to, wherever the session started.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

import textprov  # noqa: E402
from textprov import cluster_end  # noqa: E402

MAPPING = textprov.default_mapping()
SELECTORS = set(MAPPING.selectors.values())
PUA = MAPPING.pua2base

STATE_DIR = ROOT / ".textprov"
PROMPT_LOG = STATE_DIR / "prompts.jsonl"
SNAPSHOTS = STATE_DIR / "snapshots"

SUFFIXES = (".md", ".markdown")
# Hand-built samples whose marks are the content; never touch them.
EXCLUDED = ("docs/examples/", "site/public/", "site/dist/", "node_modules/")
HUMAN_MIN_WORDS = int(os.environ.get("TEXTPROV_HUMAN_MIN_WORDS", "5"))
PROMPT_LOG_TAIL = 300
SNAPSHOT_MAX_AGE = 24 * 3600

# A command that moves the working tree to another revision changes files the
# agent did not write.
GIT_MOVES_TREE = re.compile(
    r"\bgit\b[^|;&\n]*\b(checkout|switch|merge|pull|rebase|stash|reset|restore"
    r"|cherry-pick|revert|apply|am|worktree|bisect)\b"
)


# --- text plumbing ---------------------------------------------------------


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
    re.S | re.I,
)
INLINE = [
    # code span
    re.compile(r"(?<!`)(`+)(?!`)(?:(?!\n\s*\n).)+?(?<!`)\1(?!`)", re.S),
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
    front_matter = bool(lines) and lines[0].strip() == "---" and any(
        line.strip() in ("---", "...") for line in lines[1:]
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
                and not line[closing.end():].strip()
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
        if RULE.match(line):
            whole[number] = True
            if number and not previous_blank:
                whole[number - 1] = True  # setext heading text
        elif HEADING.match(line) or TABLE_RULE.match(line):
            whole[number] = True
        elif definition and not definition.group(1).startswith("^"):
            labels.add(definition.group(1).strip().lower())
            whole[number] = True
        elif definition:
            protect(at[number], at[number] + definition.end())
        else:
            protect(at[number], at[number] + LEADER.match(line).end())
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
        block = plain[base:at[number]]
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


def load_shingles():
    """Every run of HUMAN_MIN_WORDS words a recorded prompt marks as human."""
    shingles = set()
    try:
        with open(PROMPT_LOG, encoding="utf-8") as handle:
            entries = handle.readlines()[-PROMPT_LOG_TAIL:]
    except OSError:
        return shingles
    for entry in entries:
        try:
            text = json.loads(entry)["text"]
        except (ValueError, KeyError, TypeError):
            continue
        for state, run in textprov.runs(text, strip=True):
            if state != "human":
                continue
            words = [match.group() for match in words_of(run)]
            for start in range(len(words) - HUMAN_MIN_WORDS + 1):
                shingles.add(tuple(words[start:start + HUMAN_MIN_WORDS]))
    return shingles


def human_mask(plain, added, shingles):
    """Flag added text that repeats a recorded prompt word for word."""
    human = [False] * len(plain)
    if not shingles:
        return human
    words = [
        match
        for match in words_of(plain)
        if all(added[match.start():match.end()])
    ]
    size = HUMAN_MIN_WORDS
    for start in range(len(words) - size + 1):
        window = words[start:start + size]
        if tuple(match.group() for match in window) in shingles:
            first, last = window[0].start(), window[-1].end()
            # A word that was not added breaks the window apart.
            if all(
                added[k] for k in range(first, last) if not plain[k].isspace()
            ):
                human[first:last] = [True] * (last - first)
    return human


# --- marking ---------------------------------------------------------------


def finalize(raw, flags, markdown, shingles):
    """Mark the flagged, unprotected clusters of `raw`; leave the rest alone."""
    plain, index = plain_map(raw)
    added = [flags[position] for position in index]
    protected = (
        markdown_protected(plain) if markdown else [False] * len(plain)
    )
    human = human_mask(plain, added, shingles)
    want = [None] * len(raw)
    for k, position in enumerate(index):
        if added[k] and not protected[k]:
            want[position] = "human" if human[k] else "ai"

    chars = list(raw)
    out, segment, state = [], [], None

    def flush():
        text = "".join(segment)
        out.append(textprov.mark(text, state=state) if state else text)
        del segment[:]

    position = 0
    while position < len(chars):
        char = chars[position]
        cp = ord(char)
        if cp in SELECTORS or cp in PUA or char.isspace():
            end, cluster_state = position + 1, state
        else:
            end = cluster_end(chars, position, SELECTORS)
            if end < len(chars) and ord(chars[end]) in SELECTORS:
                end += 1
            cluster_state = want[position]
        if cluster_state != state:
            flush()
            state = cluster_state
        segment.extend(chars[position:end])
        position = end
    flush()
    return "".join(out)


def remark(old_raw, new_raw, markdown=True, carry=True, shingles=None):
    """Return `new_raw` with what it adds to `old_raw` marked."""
    if shingles is None:
        shingles = load_shingles()
    text, flags = merge(old_raw, new_raw, carry)
    return finalize(text, flags, markdown, shingles)


class Ambiguous(Exception):
    pass


def rewrite_edit(raw, old_string, new_string, replace_all=False, shingles=None):
    """Translate an Edit so it applies to a marked file and marks what it adds.

    Returns (old_string, new_string) to hand to the tool, or None when
    `old_string` is absent and the tool should report that itself.
    """
    if shingles is None:
        shingles = load_shingles()
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
        )
        results.add((raw[first:last], whole[first:len(whole) - tail]))
    if len(results) > 1:
        raise Ambiguous(
            "replace_all would touch occurrences that carry different "
            "provenance marks or sit in different markdown contexts. Edit "
            "them one at a time."
        )
    return results.pop()


# --- files -----------------------------------------------------------------


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def relative(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def suffix_in_scope(rel):
    return (
        rel is not None
        and rel.lower().endswith(SUFFIXES)
        and not rel.startswith(".git/")
        and not any(part in rel for part in EXCLUDED)
    )


def in_scope(path):
    rel = relative(path)
    if not suffix_in_scope(rel):
        return False
    return git("check-ignore", "-q", "--", rel).returncode != 0


def read_text(path):
    try:
        with open(path, encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def scoped_files():
    listing = git("ls-files", "-co", "--exclude-standard", "-z").stdout
    return [rel for rel in listing.split("\0") if suffix_in_scope(rel)]


def head():
    return git("rev-parse", "--verify", "-q", "HEAD").stdout.strip()


# --- hook handlers ---------------------------------------------------------


def respond(**fields):
    fields["hookEventName"] = "PreToolUse"
    print(json.dumps({"hookSpecificOutput": fields}))


def deny(reason):
    respond(permissionDecision="deny", permissionDecisionReason=reason)


def on_prompt(event):
    prompt = event.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return
    STATE_DIR.mkdir(exist_ok=True)
    entry = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "session": event.get("session_id"),
        "text": textprov.mark(prompt, state="human"),
    }
    with open(PROMPT_LOG, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def on_write(event):
    tool_input = event["tool_input"]
    path = tool_input.get("file_path", "")
    if not in_scope(path):
        return
    content = tool_input.get("content", "")
    marked = remark(read_text(path) or "", content)
    if marked != content:
        respond(updatedInput=dict(tool_input, content=marked))


def on_edit(event):
    tool_input = event["tool_input"]
    path = tool_input.get("file_path", "")
    if not in_scope(path):
        return
    raw = read_text(path)
    if raw is None:
        return
    old_string = tool_input.get("old_string", "")
    new_string = tool_input.get("new_string", "")
    try:
        result = rewrite_edit(
            raw, old_string, new_string, bool(tool_input.get("replace_all"))
        )
    except Ambiguous as problem:
        deny(f"textprov hook: {problem}")
        return
    if result and result != (old_string, new_string):
        respond(
            updatedInput=dict(
                tool_input, old_string=result[0], new_string=result[1]
            )
        )


def snapshot_path(event):
    name = re.sub(r"[^A-Za-z0-9_-]", "_", event.get("tool_use_id") or "none")
    return SNAPSHOTS / f"{name}.json"


def on_bash_before(event):
    if GIT_MOVES_TREE.search(event["tool_input"].get("command", "")):
        return
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for stale in SNAPSHOTS.glob("*.json"):
        if now - stale.stat().st_mtime > SNAPSHOT_MAX_AGE:
            stale.unlink()
    files = {}
    for rel in scoped_files():
        text = read_text(ROOT / rel)
        if text is not None:
            files[rel] = text
    snapshot_path(event).write_text(
        json.dumps({"head": head(), "files": files}), encoding="utf-8"
    )


def on_bash_after(event):
    path = snapshot_path(event)
    if not path.exists():
        return
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    path.unlink()
    if snapshot["head"] != head():
        return
    before = snapshot["files"]
    known = None
    shingles = None
    for rel in scoped_files():
        text = read_text(ROOT / rel)
        if text is None or text == before.get(rel):
            continue
        if rel not in before:
            # A moved or copied file is not new writing.
            if known is None:
                known = {plain_map(old)[0] for old in before.values()}
            if plain_map(text)[0] in known:
                continue
        if shingles is None:
            shingles = load_shingles()
        marked = remark(
            before.get(rel, ""), text, carry=False, shingles=shingles
        )
        if marked != text:
            write_text(ROOT / rel, marked)


def dispatch(event):
    name = event.get("hook_event_name")
    tool = event.get("tool_name")
    if name == "UserPromptSubmit":
        on_prompt(event)
    elif name == "PreToolUse" and tool == "Write":
        on_write(event)
    elif name == "PreToolUse" and tool == "Edit":
        on_edit(event)
    elif name == "PreToolUse" and tool == "Bash":
        on_bash_before(event)
    elif name in ("PostToolUse", "PostToolUseFailure") and tool == "Bash":
        on_bash_after(event)


def main():
    if os.environ.get("TEXTPROV_HOOK", "").lower() in ("off", "0", "false"):
        return 0
    event = {}
    try:
        event = json.load(sys.stdin)
        dispatch(event)
    except Exception as error:  # noqa: BLE001
        print(f"textprov hook failed: {error!r}", file=sys.stderr)
        # Exit 2 blocks the tool call. A Write or Edit is stopped rather than
        # let unmarked text through; anything else is reported and carries on.
        blocking = event.get("hook_event_name") == "PreToolUse" and event.get(
            "tool_name"
        ) in ("Write", "Edit")
        return 2 if blocking else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
