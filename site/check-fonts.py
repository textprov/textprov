"""Report ccmp and cmap-14 UVS coverage for the TextProv selectors in each demo TTF.

Safari (CoreText) only renders private variation selectors when the font implements
them via GSUB ccmp. Chrome/Firefox (HarfBuzz) additionally honour cmap format-14
UVS subtables. This script reports both paths for U+E0100 and U+E0101.
"""

import argparse
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

SELECTORS = (0xE0100, 0xE0101)
FONTS_DIR = Path(__file__).parent / "public" / "fonts"


def uvs_map(font):
    tables = [t for t in font["cmap"].tables if t.format == 14]
    if not tables:
        return {}
    assert len(tables) == 1
    return tables[0].uvsDict


def cmap14_coverage(uvs):
    return {sel: bool(uvs.get(sel)) for sel in SELECTORS}


def vs_glyphs(uvs):
    glyphs = set()
    for sel in SELECTORS:
        for _cp, glyph in uvs.get(sel, ()) or ():
            if glyph:
                glyphs.add(glyph)
    return glyphs


def ccmp_lookups(font):
    if "GSUB" not in font:
        return None
    gsub = font["GSUB"].table
    feature_list = gsub.FeatureList
    lookup_list = gsub.LookupList
    if feature_list is None or lookup_list is None:
        return []
    indices = set()
    for record in feature_list.FeatureRecord:
        if record.FeatureTag == "ccmp":
            indices.update(record.Feature.LookupListIndex)
    if not indices:
        return []
    return [lookup_list.Lookup[i] for i in sorted(indices)]


def ccmp_covers(lookups, vs_set):
    if not lookups or not vs_set:
        return False
    for lookup in lookups:
        for sub in lookup.SubTable:
            if _subtable_covers(sub, vs_set):
                return True
    return False


def _subtable_covers(sub, vs_set):
    lookup_type = getattr(sub, "LookupType", None) or type(sub).__name__
    if hasattr(sub, "ExtSubTable"):
        return _subtable_covers(sub.ExtSubTable, vs_set)
    name = type(sub).__name__
    if name == "LigatureSubst":
        for _first, ligs in sub.ligatures.items():
            for lig in ligs:
                if any(g in vs_set for g in lig.Component):
                    return True
    elif name == "ChainContextSubst":
        fmt = sub.Format
        if fmt == 3:
            for cov in (sub.InputCoverage or []) + (sub.BacktrackCoverage or []) + (sub.LookAheadCoverage or []):
                if any(g in vs_set for g in cov.glyphs):
                    return True
        elif fmt == 1:
            for ruleset in sub.ChainSubRuleSet or []:
                if not ruleset:
                    continue
                for rule in ruleset.ChainSubRule or []:
                    seq = (rule.Input or []) + (rule.Backtrack or []) + (rule.LookAhead or [])
                    if any(g in vs_set for g in seq):
                        return True
        elif fmt == 2:
            for cov in (sub.InputClassDef, sub.BacktrackClassDef, sub.LookAheadClassDef):
                if cov is None:
                    continue
                if any(g in vs_set for g in getattr(cov, "classDefs", {})):
                    return True
    elif name == "ContextSubst":
        fmt = sub.Format
        if fmt == 3:
            for cov in sub.Coverage or []:
                if any(g in vs_set for g in cov.glyphs):
                    return True
    return False


def check(path):
    font = TTFont(path)
    uvs = uvs_map(font)
    cmap14 = cmap14_coverage(uvs)
    vs = vs_glyphs(uvs)
    lookups = ccmp_lookups(font)
    has_ccmp = lookups is not None and len(lookups) > 0
    ccmp_ok = has_ccmp and ccmp_covers(lookups, vs)
    return {
        "file": path.name,
        "ccmp_present": has_ccmp,
        "ccmp_covers": ccmp_ok,
        "cmap14_e0100": cmap14.get(0xE0100, False),
        "cmap14_e0101": cmap14.get(0xE0101, False),
    }


def yn(v):
    return "yes" if v else "no"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true", help="exit non-zero if any font lacks ccmp coverage for U+E0100/U+E0101")
    args = parser.parse_args()

    fonts = sorted(FONTS_DIR.glob("*.ttf"))
    assert fonts, f"no TTFs under {FONTS_DIR}"
    rows = [check(p) for p in fonts]

    header = ("file", "ccmp", "ccmp covers VS", "cmap14 E0100", "cmap14 E0101")
    widths = [max(len(h), max(len(str(r[k])) for r in rows)) for h, k in zip(
        header, ("file", "ccmp_present", "ccmp_covers", "cmap14_e0100", "cmap14_e0101"),
    )]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*header))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(
            r["file"],
            yn(r["ccmp_present"]),
            yn(r["ccmp_covers"]),
            yn(r["cmap14_e0100"]),
            yn(r["cmap14_e0101"]),
        ))

    failing = [r["file"] for r in rows if not r["ccmp_covers"]]
    if failing:
        print()
        print("Missing ccmp coverage for U+E0100/U+E0101:")
        for name in failing:
            print(f"  - {name}")
    if args.strict and failing:
        sys.exit(1)


if __name__ == "__main__":
    main()
