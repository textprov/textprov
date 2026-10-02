#!/usr/bin/env python3
"""Verify P9E utility font names, metrics, both shaping paths and distribution.

This checker independently derives expected coverage from the pinned source
fonts and registry. It requires cached originals but never fetches or rebuilds
outputs. All checks are strict. --strict is accepted for compatibility.
"""

import argparse
import copy
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import uharfbuzz as hb
from fontTools import subset
from fontTools.misc.xmlWriter import XMLWriter
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import USE_MY_METRICS

SITE = Path(__file__).resolve().parent
SELECTORS = (0xE0100, 0xE0101)
BASES = set(range(0x20, 0x100)) | set(range(0x2010, 0x2028)) | {0x20AC, 0x2122, 0x2212}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def cp(value):
    return int(value.removeprefix("U+"), 16)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def xml(table, font):
    stream = io.BytesIO()
    table.toXML(XMLWriter(stream), font)
    return stream.getvalue()


def uvs(font):
    tables = [table for table in font["cmap"].tables if table.format == 14]
    require(len(tables) == 1, "expected exactly one cmap format 14")
    require(set(tables[0].uvsDict) == set(SELECTORS), "unexpected visual selector states")
    return {selector: dict(pairs) for selector, pairs in tables[0].uvsDict.items()}


def outline(font, glyph):
    pen = RecordingPen()
    font.getGlyphSet()[glyph].draw(pen)
    return pen.value


def shaper(data, font):
    face = hb.Face(data)
    shaped_font = hb.Font(face)
    shaped_font.scale = (font["head"].unitsPerEm, font["head"].unitsPerEm)
    return shaped_font


def shape(shaped_font, font, text, **properties):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    for key, value in properties.items():
        setattr(buffer, key, value)
    hb.shape(shaped_font, buffer)
    return [(font.getGlyphName(info.codepoint), position.x_advance, position.y_advance,
             position.x_offset, position.y_offset)
            for info, position in zip(buffer.glyph_infos, buffer.glyph_positions)]


def vertical(font):
    return (font["head"].unitsPerEm, font["hhea"].ascent, font["hhea"].descent, font["hhea"].lineGap,
            font["OS/2"].sTypoAscender, font["OS/2"].sTypoDescender, font["OS/2"].sTypoLineGap,
            font["OS/2"].usWinAscent, font["OS/2"].usWinDescent, font["OS/2"].fsSelection)


def subset_baseline(source, bases):
    font = copy.deepcopy(source)
    for tag in ("DSIG", "FFTM", "meta"):
        if tag in font:
            del font[tag]
    options = subset.Options()
    options.name_IDs, options.name_languages = ["*"], ["*"]
    options.name_legacy, options.glyph_names = True, True
    options.layout_features = ["*"]
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=bases)
    worker.subset(font)
    return font


def check_layout(font, baseline, variants, cmap):
    for tag in ("GPOS", "GDEF"):
        if tag in baseline:
            require(tag in font and font.getTableData(tag) == baseline.getTableData(tag), f"changed upstream {tag}")
    gsub = font["GSUB"].table
    original = baseline["GSUB"].table if "GSUB" in baseline else None
    if original:
        lookups = original.LookupList.Lookup
        require(len(gsub.LookupList.Lookup) == len(lookups) + 1, "expected one appended GSUB lookup")
        for index, lookup in enumerate(lookups):
            require(xml(gsub.LookupList.Lookup[index], font) == xml(lookup, baseline), "changed upstream GSUB lookup")
        before = [xml(record.Feature, baseline) for record in original.FeatureList.FeatureRecord if record.FeatureTag != "ccmp"]
        after = [xml(record.Feature, font) for record in gsub.FeatureList.FeatureRecord if record.FeatureTag != "ccmp"]
        require(before == after, "changed upstream non-ccmp features")
    expected = {(cmap[base], cmap[selector]): glyph for selector, pairs in variants.items() for base, glyph in pairs.items()}
    for record in gsub.ScriptList.ScriptRecord:
        script = record.Script
        languages = [item.LangSys for item in script.LangSysRecord]
        if script.DefaultLangSys is not None:
            languages.append(script.DefaultLangSys)
        for language in languages:
            indices = list(language.FeatureIndex)
            if language.ReqFeatureIndex != 0xFFFF:
                indices.append(language.ReqFeatureIndex)
            ccmp = [gsub.FeatureList.FeatureRecord[index].Feature for index in indices
                    if gsub.FeatureList.FeatureRecord[index].FeatureTag == "ccmp"]
            require(ccmp, f"script {record.ScriptTag} has no ccmp feature")
            # Check each reachable ccmp feature independently: some engines pick one.
            for feature in ccmp:
                actual = {}
                for index in feature.LookupListIndex:
                    lookup = gsub.LookupList.Lookup[index]
                    if lookup.LookupType != 4:
                        continue
                    for subtable in lookup.SubTable:
                        for first, ligatures in subtable.ligatures.items():
                            for ligature in ligatures:
                                if len(ligature.Component) == 1:
                                    actual[(first, ligature.Component[0])] = ligature.LigGlyph
                require(all(actual.get(pair) == glyph for pair, glyph in expected.items()),
                        f"incomplete base+VS ligatures in {record.ScriptTag} ccmp")


def check_font(entry, recorded, args, registry):
    label = entry["key"]
    source_path = args.cache_dir / entry["font_cache_file"]
    license_path = args.cache_dir / entry["license_cache_file"]
    source_data, license_data = source_path.read_bytes(), license_path.read_bytes()
    require(digest(source_data) == entry["font_sha256"], "source font SHA-256 mismatch")
    require(digest(license_data) == entry["license_sha256"], "source license SHA-256 mismatch")
    require(all(recorded.get(key) == value for key, value in entry.items()), "manifest source metadata mismatch")
    stem = f"textprov-{label}-utility-p9e"
    for filename, expected in recorded["outputs"].items():
        require(Path(filename).name == filename, "invalid output filename")
        require(digest((args.output / filename).read_bytes()) == expected, f"output SHA-256 mismatch: {filename}")
    expected_outputs = {stem + suffix for suffix in (".ttf", ".woff2", ".zip", "-OFL.txt", "-README.txt")}
    require(set(recorded["outputs"]) == expected_outputs, "missing/unexpected output hashes")
    require((args.output / (stem + "-OFL.txt")).read_bytes() == license_data, "license copy differs from source")
    ttf_data = (args.output / (stem + ".ttf")).read_bytes()
    source = TTFont(io.BytesIO(source_data), recalcTimestamp=False)
    font = TTFont(io.BytesIO(ttf_data), recalcTimestamp=False)
    woff = TTFont(args.output / (stem + ".woff2"), recalcTimestamp=False)
    original_cmap, cmap = source.getBestCmap(), font.getBestCmap()
    bases = sorted(BASES & original_cmap.keys())
    marked = sorted(base for base in bases if chr(base).isprintable() and not chr(base).isspace())
    variants = uvs(font)
    require(all(set(pairs) == set(marked) for pairs in variants.values()), "UVS base coverage mismatch")
    expected_pua = {encoded: info["base"] for encoded, info in registry["pua"].items()
                    if info["provenance"] == "ai" and cp(info["base"]) in marked}
    expected_coverage = {"base": [f"U+{base:04X}" for base in bases],
                         "marked": [f"U+{base:04X}" for base in marked], "pua": expected_pua}
    require(recorded["coverage"] == expected_coverage, "manifest coverage mismatch")
    require(recorded["selectors"] == {"human": "U+E0100", "ai": "U+E0101"}, "manifest selector mismatch")
    expected_cmap = set(bases) | set(SELECTORS) | {cp(encoded) for encoded in expected_pua}
    require(set(cmap) == expected_cmap, "unexpected encoded characters or private-use aliases")
    for table in font["cmap"].tables:
        if table.isUnicode() and table.format in (4, 12):
            require(table.cmap == {code: glyph for code, glyph in cmap.items() if table.format == 12 or code <= 0xFFFF},
                    "inconsistent Unicode cmap")
    require(vertical(font) == vertical(source), "changed source line metrics")
    require(font["post"].isFixedPitch == source["post"].isFixedPitch, "changed fixed-pitch classification")
    require(font["OS/2"].panose.bProportion == source["OS/2"].panose.bProportion, "changed PANOSE proportionality")
    require(not any(tag in font for tag in ("fvar", "CFF ", "DSIG")), "variable/CFF font or stale signature")
    require(font["head"].fontRevision == float(recorded["version"]), "font version mismatch")
    family = entry["family"]
    legacy = "TextProv Propo Utility P9E" if label == "proportional" else family
    expected_names = {1: legacy, 2: "Regular", 3: f"{recorded['version']};TextProv;{re.sub(r'[^A-Za-z0-9]', '', family)}-Regular",
                      4: family, 6: re.sub(r"[^A-Za-z0-9]", "", family) + "-Regular", 16: family, 17: "Regular"}
    for name_id, value in expected_names.items():
        records = [record.toUnicode() for record in font["name"].names if record.nameID == name_id]
        require(records and all(record == value for record in records), f"wrong name ID {name_id}")
    require(len(legacy) <= 31 and len(expected_names[6]) <= 63, "name exceeds platform limits")
    require(not any(record.nameID in (18, 21, 22) for record in font["name"].names), "stale compatibility/WWS name")
    for name_id in (0, 13, 14):
        before = [(record.platformID, record.platEncID, record.langID, record.toUnicode())
                  for record in source["name"].names if record.nameID == name_id]
        after = [(record.platformID, record.platEncID, record.langID, record.toUnicode())
                 for record in font["name"].names if record.nameID == name_id]
        require(sorted(before) == sorted(after), f"changed copyright/license name ID {name_id}")
    for base in bases:
        glyph, original = cmap[base], original_cmap[base]
        require(font["hmtx"][glyph] == source["hmtx"][original], f"changed base metrics U+{base:04X}")
        require(outline(font, glyph) == outline(source, original), f"changed base outline U+{base:04X}")
    for selector in SELECTORS:
        require(font["hmtx"][cmap[selector]] == (0, 0), "selector glyph has nonzero metrics")
        require(not outline(font, cmap[selector]), "selector glyph should have no outline")
    descent = source["OS/2"].sTypoDescender if source["OS/2"].fsSelection & 0x80 else max(source["hhea"].descent, -source["OS/2"].usWinDescent)
    for base in marked:
        ordinary, human, ai = cmap[base], variants[SELECTORS[0]][base], variants[SELECTORS[1]][base]
        require(human == ordinary, "Human variation must be the ordinary glyph")
        require(ai != ordinary and font["hmtx"][ai] == font["hmtx"][ordinary], "AI variation missing or changes advance")
        composite = font["glyf"][ai]
        require(composite.isComposite() and len(composite.components) == 2, "AI glyph is not base plus mark")
        first, second = composite.components
        require(first.getComponentInfo() == (ordinary, (1, 0, 0, 1, 0, 0)) and first.flags & USE_MY_METRICS,
                "AI glyph changes source outline placement/metrics")
        require(second.getComponentInfo()[1] == (1, 0, 0, 1, 0, 0), "mark transform changed")
        strip = font["glyf"][second.glyphName]
        require(strip.numberOfContours > 0 and descent <= strip.yMin < strip.yMax <= 0,
                "mark absent or outside source descent/baseline bounds")
    for encoded, base in expected_pua.items():
        require(cmap[cp(encoded)] == variants[SELECTORS[1]][cp(base)], "PUA differs from canonical AI variation")
    baseline = subset_baseline(source, bases)
    check_layout(font, baseline, variants, cmap)
    require(font.getGlyphOrder() == woff.getGlyphOrder() and cmap == woff.getBestCmap() and variants == uvs(woff), "TTF/WOFF2 mapping mismatch")
    require(font["hmtx"].metrics == woff["hmtx"].metrics and vertical(font) == vertical(woff), "TTF/WOFF2 metric mismatch")
    for glyph in font.getGlyphOrder():
        require(outline(font, glyph) == outline(woff, glyph), f"TTF/WOFF2 outline mismatch: {glyph}")
    for tag in ("name", "GSUB", "GPOS", "GDEF", "OS/2", "post"):
        if tag in font:
            require(font.getTableData(tag) == woff.getTableData(tag), f"TTF/WOFF2 {tag} mismatch")
    # Exercise the canonical UVS path and the actual ccmp-only fallback separately.
    fallback = copy.deepcopy(font)
    fallback["cmap"].tables = [table for table in fallback["cmap"].tables if table.format != 14]
    stream = io.BytesIO()
    fallback.save(stream)
    hb_font, hb_source = shaper(ttf_data, font), shaper(source_data, source)
    hb_woff_stream = io.BytesIO()
    woff.flavor = None
    woff.save(hb_woff_stream)
    paths = [("TTF UVS", hb_font, font), ("TTF ccmp", shaper(stream.getvalue(), fallback), fallback),
             ("WOFF2 UVS", shaper(hb_woff_stream.getvalue(), woff), woff)]
    for base in marked:
        plain = shape(hb_font, font, chr(base))
        require(plain == shape(hb_source, source, chr(base)), "plain source shaping changed")
        for selector in SELECTORS:
            for label_path, hb_path, face in paths:
                result = shape(hb_path, face, chr(base) + chr(selector))
                require(len(result) == 1 and result[0][0] == variants[selector][base], f"{label_path} failed U+{base:04X}+U+{selector:05X}")
                require(result[0][1:] == plain[0][1:], f"{label_path} changes shaped per-glyph advance/position")
        for state in ("mixed", "edited", "unknown"):
            text = chr(base) + chr(cp(registry["variation_selectors"][state]))
            expected = shape(hb_source, source, text)
            for label_path, hb_path, face in paths:
                require(shape(hb_path, face, text) == expected, f"{label_path} gives unsupported {state} a visual variant")
    for text in ["AVATAR", "office ffi", "caf\u00e9 na\u00efve", "\u00c5ngstr\u00f6m", "12345.67 \u20ac", "\u201cHello\u201d\u2014debug"]:
        if all(ord(character) in bases for character in text):
            require(shape(hb_font, font, text) == shape(hb_source, source, text), f"plain shaping changed: {text}")
    with zipfile.ZipFile(args.output / (stem + ".zip")) as archive:
        expected_members = {stem + ".ttf": ttf_data, stem + ".woff2": (args.output / (stem + ".woff2")).read_bytes(),
                            "OFL.txt": license_data, "README.txt": (args.output / (stem + "-README.txt")).read_bytes()}
        require(set(archive.namelist()) == set(expected_members) and len(archive.namelist()) == len(expected_members), "family bundle contents mismatch")
        require(all(archive.read(name) == data for name, data in expected_members.items()), "family bundle bytes mismatch")
        require(archive.testzip() is None, "family ZIP corruption")
    return len(marked)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sources", type=Path, default=SITE / "utility-font-sources.json")
    parser.add_argument("--cache-dir", type=Path, default=SITE / ".font-cache")
    parser.add_argument("--output", type=Path, default=SITE / "public/fonts/utility")
    parser.add_argument("--strict", action="store_true", help="all checks are always strict")
    args = parser.parse_args()
    source_data, registry_data = args.sources.read_bytes(), (SITE.parent / "mapping.json").read_bytes()
    entries, registry = json.loads(source_data), json.loads(registry_data)
    manifest_data = (args.output / "sources.json").read_bytes()
    manifest = json.loads(manifest_data)
    require(manifest["source_manifest_sha256"] == digest(source_data), "source manifest hash mismatch")
    require(manifest["registry_sha256"] == digest(registry_data), "registry hash mismatch")
    require(manifest["protocol_version"] == registry["version"], "protocol version mismatch")
    require({cp(registry["variation_selectors"][state]) for state in ("human", "ai")} == set(SELECTORS), "registry selectors mismatch")
    require([font["key"] for font in manifest["fonts"]] == [entry["key"] for entry in entries], "manifest family list mismatch")
    count = 0
    for entry, recorded in zip(entries, manifest["fonts"]):
        try:
            require(recorded["version"] == manifest["version"], "version mismatch")
            stem = f"textprov-{entry['key']}-utility-p9e"
            for extension in (".ttf", ".woff2"):
                with TTFont(args.output / (stem + extension), recalcTimestamp=False) as font:
                    require(font["head"].created == font["head"].modified == manifest["source_date_epoch"] + 2082844800,
                            "font timestamp differs from deterministic epoch")
            count += check_font(entry, recorded, args, registry)
        except (ValueError, OSError, KeyError) as error:
            raise ValueError(f"{entry['key']}: {error}") from error
        print(f"PASS {entry['family']}: names, source metrics/layout, Human/AI UVS and ccmp, WOFF2, license and bundle")
    with zipfile.ZipFile(args.output / "textprov-utility-p9e.zip") as archive:
        expected = {"sources.json": manifest_data, "README.txt": (args.output / "README.txt").read_bytes()}
        for entry in entries:
            stem = f"textprov-{entry['key']}-utility-p9e"
            for name, filename in [(stem + ".ttf", stem + ".ttf"), (stem + ".woff2", stem + ".woff2"),
                                   ("OFL.txt", stem + "-OFL.txt"), ("README.txt", stem + "-README.txt")]:
                expected[entry["key"] + "/" + name] = (args.output / filename).read_bytes()
        require(set(archive.namelist()) == set(expected) and len(archive.namelist()) == len(expected), "aggregate bundle contents mismatch")
        require(all(archive.read(name) == data for name, data in expected.items()), "aggregate bundle bytes mismatch")
        require(archive.testzip() is None, "aggregate ZIP corruption")
    print(f"PASS all {len(entries)} families; {count * 2} declared variations checked on each shaping path")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(f"FAIL {error}") from error
