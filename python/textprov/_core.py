# python/textprov/_core.py

"""Shared core of the TextProv decorator: registry, clusters, runs, markup.

Extracted from bin/scripts/nfprov.py in the nerd-fonts provenance fork, which
keeps the encoder. The functions here are the decoder and renderer halves.
"""

import html
import json
import unicodedata
from pathlib import Path

MAPPING_PATH = Path(__file__).with_name("mapping.json")

CONTRACT_VERSION = 1  # see SPEC.md
GENERATED_STATES = ("human", "ai", "mixed")
PROPOSED_STATES = ("edited", "unknown")


class Mapping:
    """The code-point registry, loaded once and passed to every operation."""

    __slots__ = ("raw", "version", "selectors", "pua2base", "base2pua")

    def __init__(self, raw, version, selectors, pua2base, base2pua):
        self.raw = raw
        self.version = version
        self.selectors = selectors
        self.pua2base = pua2base
        self.base2pua = base2pua

    @classmethod
    def load(cls, path=MAPPING_PATH):
        """Load a registry file. Defaults to the copy vendored in this package."""
        raw, selectors, pua2base, base2pua = load_mapping(path)
        return cls(raw, raw["version"], selectors, pua2base, base2pua)


_DEFAULT = None


def default_mapping():
    """The vendored registry, loaded on first use."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = Mapping.load()
    return _DEFAULT


def load_mapping(path=MAPPING_PATH):
    """Load mapping.json and return (mapping, selectors, pua2base, base2pua)."""
    with open(path, encoding="utf-8") as handle:
        mapping = json.load(handle)
    selectors = {
        name: int(value[2:], 16)
        for name, value in mapping["variation_selectors"].items()
    }
    pua2base = {}
    base2pua = {}
    for pua_string, entry in mapping["pua"].items():
        pua = int(pua_string[2:], 16)
        base = int(entry["base"][2:], 16)
        pua2base[pua] = (base, entry.get("provenance", "ai"))
        if entry.get("provenance", "ai") == "ai":
            base2pua[base] = pua
    return mapping, selectors, pua2base, base2pua


ZWJ = 0x200D
VS15, VS16 = 0xFE0E, 0xFE0F
SKIN_TONES = range(0x1F3FB, 0x1F400)  # emoji modifiers, category Sk
REGIONAL = range(0x1F1E6, 0x1F200)  # regional indicator symbols


def is_combining(char):
    """True for combining marks (Mn/Mc/Me) that attach to a base character."""
    return unicodedata.combining(char) != 0 or unicodedata.category(char) in (
        "Mn",
        "Mc",
        "Me",
    )


def cluster_end(chars, start, sel_cps):
    """Return the index just past the grapheme-ish cluster starting at `start`.

    A cluster is a base character plus everything that visually belongs to it:
    combining marks, the emoji variation selectors VS15/VS16, skin-tone
    modifiers, ZWJ joins (the ZWJ and whatever follows it), and the second half
    of a regional-indicator pair (a flag). A provenance selector always ends the
    cluster, because it is the mark we are about to place ourselves.
    """
    index = start + 1
    if (
        ord(chars[start]) in REGIONAL
        and index < len(chars)
        and ord(chars[index]) in REGIONAL
    ):
        index += 1  # flag: two regional indicators
    while index < len(chars):
        cp = ord(chars[index])
        if cp in sel_cps:
            break
        if cp == ZWJ:
            # The ZWJ and the character it joins stay in this cluster.
            index += 2 if index + 1 < len(chars) else 1
            continue
        if cp in (VS15, VS16) or cp in SKIN_TONES or is_combining(chars[index]):
            index += 1
            continue
        break
    return index




# --- runs and markup -------------------------------------------------------


def _strip(text, selectors, pua2base):
    """Remove all provenance selectors and map PUA entries back to their base."""
    sel_cps = set(selectors.values())
    out = []
    for char in text:
        cp = ord(char)
        if cp in sel_cps:
            continue
        entry = pua2base.get(cp)
        out.append(chr(entry[0]) if entry else char)
    return "".join(out)


def _runs(text, selectors, pua2base, strip=False, merge_whitespace=True):
    """Split `text` into an ordered list of (state, text) runs.

    Implements the decorator contract in SPEC.md version 1. `state` is a
    selector name from mapping.json's variation_selectors, or None.
    """
    sel_cps = set(selectors.values())
    sel2name = {cp: name for name, cp in selectors.items()}
    chars = list(text)
    items = []
    index = 0
    while index < len(chars):
        cp = ord(chars[index])
        if cp in pua2base:
            base_cp, state = pua2base[cp]
            out = chr(base_cp) if strip else chr(base_cp) + chr(selectors[state])
            index += 1
        elif chars[index].isspace():
            state = "ws"
            out = chars[index]
            index += 1
        else:
            end = cluster_end(chars, index, sel_cps)
            cluster = "".join(chars[index:end])
            state, out, index = None, cluster, end
            if index < len(chars) and ord(chars[index]) in sel_cps:
                state = sel2name[ord(chars[index])]
                if not strip:
                    out += chars[index]
                index += 1
        if items and items[-1][0] == state:
            items[-1][1] += out
        else:
            items.append([state, out])

    merged = []
    for position, (state, out) in enumerate(items):
        following = items[position + 1][0] if position + 1 < len(items) else None
        if merge_whitespace and state == "ws" and merged and merged[-1][0] and merged[-1][0] == following:
            merged[-1][1] += out
            continue
        if state == "ws":
            state = None
        if merged and merged[-1][0] == state:
            merged[-1][1] += out
        else:
            merged.append([state, out])
    return [(state, out) for state, out in merged]


def _to_html(text, selectors, pua2base, strip=False, merge_whitespace=True, class_prefix="prov"):
    """Render `text` as HTML spans per the decorator contract's Markup section."""
    parts = []
    for state, out in _runs(text, selectors, pua2base, strip, merge_whitespace):
        escaped = html.escape(out)
        if state:
            parts.append(
                f'<span class="{class_prefix} {class_prefix}-{state}" '
                f'data-prov="{state}">{escaped}</span>'
            )
        else:
            parts.append(escaped)
    return "".join(parts)


# --- public API ------------------------------------------------------------


def runs(text, mapping=None, strip=False, merge_whitespace=True):
    """Split `text` into an ordered list of (state, text) runs per SPEC.md."""
    mapping = mapping or default_mapping()
    return _runs(text, mapping.selectors, mapping.pua2base, strip, merge_whitespace)


def to_html(text, mapping=None, strip=False, merge_whitespace=True, class_prefix="prov"):
    """Render `text` as HTML spans per the contract's Markup section."""
    mapping = mapping or default_mapping()
    return _to_html(
        text, mapping.selectors, mapping.pua2base, strip, merge_whitespace, class_prefix
    )


def strip_marks(text, mapping=None):
    """Remove every selector and map PUA entries back to their base character."""
    mapping = mapping or default_mapping()
    return _strip(text, mapping.selectors, mapping.pua2base)
