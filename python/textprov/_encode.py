"""Producer and diagnostics: add marks to text, change encoding, report states.

A producer is pure text processing. It needs the registry and nothing else: no
font, no shaping engine, no build step. Producing marks and rendering them are
separate jobs, and a font is one renderer among three (see ../SPEC.md).

Extracted from bin/scripts/nfprov.py in the nerd-fonts provenance fork, which
uses these operations to mark its example text and keeps the font patcher.
"""

from ._core import cluster_end, default_mapping


def _mark(text, state, mode, selectors, pua2base, base2pua):
    """Attach the selector for `state` after every non-whitespace base.

    The selector goes after any combining marks, emoji variation selectors,
    skin-tone modifiers, ZWJ joins and regional-indicator pairs, so a cluster is
    marked once. Characters that already carry a provenance selector, selectors
    themselves, and PUA provenance characters are left alone (the operation is
    idempotent). With mode='pua' only single-code-point bases present in
    mapping.json are replaced by their PUA counterpart; every other base keeps
    the VS_AI encoding instead.
    """
    sel_cps = set(selectors.values())
    selector = chr(selectors[state])
    chars = list(text)
    out = []
    index = 0
    while index < len(chars):
        char = chars[index]
        cp = ord(char)
        if cp in sel_cps or cp in pua2base or char.isspace():
            out.append(char)
            index += 1
            continue
        start = index
        index = cluster_end(chars, index, sel_cps)
        cluster = chars[start:index]
        if index < len(chars) and ord(chars[index]) in sel_cps:
            out.extend(cluster)  # already marked
            continue
        if (
            mode == "pua"
            and state == "ai"
            and len(cluster) == 1
            and cp in base2pua
        ):
            out.append(chr(base2pua[cp]))
        else:
            out.extend(cluster)
            out.append(selector)
    return "".join(out)


def _mark_added(old_text, new_text, state, mode, selectors, pua2base, base2pua):
    """Find the common prefix and suffix of old_text and new_text,
    and mark the newly added/modified middle part of new_text.
    """
    if not old_text:
        return _mark(new_text, state, mode, selectors, pua2base, base2pua)
    pre = 0
    while pre < min(len(old_text), len(new_text)) and old_text[pre] == new_text[pre]:
        pre += 1
    suf = 0
    while (suf < min(len(old_text), len(new_text)) - pre
           and old_text[-1 - suf] == new_text[-1 - suf]):
        suf += 1
    end = len(new_text) - suf
    middle_marked = _mark(new_text[pre:end], state, mode, selectors, pua2base, base2pua)
    return new_text[:pre] + middle_marked + new_text[end:]


def _convert(text, from_mode, to_mode, selectors, pua2base, base2pua):
    """Convert the AI state between VS and PUA encodings; pass all else through."""
    if from_mode == to_mode:
        return text
    vs_ai = selectors["ai"]
    if from_mode == "vs":
        chars = list(text)
        out = []
        index = 0
        while index < len(chars):
            char = chars[index]
            index += 1
            if (
                index < len(chars)
                and ord(chars[index]) == vs_ai
                and ord(char) in base2pua
            ):
                out.append(chr(base2pua[ord(char)]))
                index += 1
            else:
                out.append(char)
        return "".join(out)
    out = []
    for char in text:
        entry = pua2base.get(ord(char))
        if entry and entry[1] == "ai":
            out.append(chr(entry[0]))
            out.append(chr(vs_ai))
        else:
            out.append(char)
    return "".join(out)


def _inspect(text, selectors, pua2base):
    """Return a plain-text 'key: value' report of provenance states."""
    sel2name = {cp: name for name, cp in selectors.items()}
    counts = dict.fromkeys(
        (
            "assumed_human",
            "explicit_human",
            "ai_vs",
            "ai_pua",
            "unknown",
            "edited",
            "mixed",
            "whitespace",
        ),
        0,
    )
    unrecognised_selectors = set()
    unrecognised_pua = set()

    chars = list(text)
    index = 0
    while index < len(chars):
        char = chars[index]
        cp = ord(char)
        index += 1
        if cp in sel2name:
            # A selector reached here has no base in front of it.
            unrecognised_selectors.add(cp)
            continue
        if 0xE0100 <= cp <= 0xE01EF:
            unrecognised_selectors.add(cp)
            continue
        if cp in pua2base:
            counts["ai_pua"] += 1
            continue
        if 0x100000 <= cp <= 0x10FFFD:
            unrecognised_pua.add(cp)
            continue
        if char.isspace():
            counts["whitespace"] += 1
            continue
        index = cluster_end(chars, index - 1, sel2name)
        if index < len(chars) and ord(chars[index]) in sel2name:
            name = sel2name[ord(chars[index])]
            index += 1
            counts[
                "explicit_human"
                if name == "human"
                else "ai_vs"
                if name == "ai"
                else name
            ] += 1
        else:
            counts["assumed_human"] += 1

    lines = [f"characters: {len(chars)}"]
    for key in (
        "assumed_human",
        "explicit_human",
        "ai_vs",
        "ai_pua",
        "unknown",
        "edited",
        "mixed",
        "whitespace",
    ):
        lines.append(f"{key}: {counts[key]}")
    lines.append(
        "unrecognised_selectors: {}".format(
            " ".join(f"U+{cp:04X}" for cp in sorted(unrecognised_selectors))
            or "-"
        )
    )
    lines.append(
        "unrecognised_pua: {}".format(
            " ".join(f"U+{cp:04X}" for cp in sorted(unrecognised_pua)) or "-"
        )
    )
    return "\n".join(lines) + "\n"


# --- public API ------------------------------------------------------------


def mark(text, state="ai", mode="vs", mapping=None):
    """Mark every unmarked cluster in `text` with `state`.

    `mode` is "vs" for the selector encoding or "pua" for the PUA encoding.
    Idempotent: marking marked text returns it unchanged. Whitespace is never
    marked. See ../SPEC.md, Producer.
    """
    mapping = mapping or default_mapping()
    return _mark(
        text, state, mode, mapping.selectors, mapping.pua2base, mapping.base2pua
    )


def mark_added(old_text, new_text, state="ai", mode="vs", mapping=None):
    """Mark only what `new_text` adds to `old_text`, by common prefix and suffix."""
    mapping = mapping or default_mapping()
    return _mark_added(
        old_text,
        new_text,
        state,
        mode,
        mapping.selectors,
        mapping.pua2base,
        mapping.base2pua,
    )


def convert(text, from_mode, to_mode, mapping=None):
    """Convert the ai state between the "vs" and "pua" encodings.

    Every other state and every unmarked character passes through: only ai has
    a PUA allocation in registry version 1.
    """
    mapping = mapping or default_mapping()
    return _convert(
        text, from_mode, to_mode, mapping.selectors, mapping.pua2base, mapping.base2pua
    )


def inspect(text, mapping=None):
    """Return a plain-text 'key: value' report of the states present in `text`."""
    mapping = mapping or default_mapping()
    return _inspect(text, mapping.selectors, mapping.pua2base)
