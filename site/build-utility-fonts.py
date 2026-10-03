#!/usr/bin/env python3
"""Build reproducible, directly patched TextProv P9E utility fonts.

Install font-build-requirements.txt, then run this script. Sources and licenses
are pinned by URL and SHA-256 in utility-font-sources.json. --offline requires
those exact cached inputs. No Nerd Fonts or external font-patcher is involved.
"""

import argparse
import hashlib
import json
import os
import re
import time
import urllib.request
import zipfile
from pathlib import Path

import brotli
import fontTools
from fontTools import subset
from fontTools.otlLib.builder import buildLigatureSubstSubtable, buildLookup
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent, USE_MY_METRICS

SITE = Path(__file__).resolve().parent
VERSION = "1.000"
SELECTORS = {"human": 0xE0100, "ai": 0xE0101}
BASES = set(range(0x20, 0x100)) | set(range(0x2010, 0x2028)) | {0x20AC, 0x2122, 0x2212}
DEFAULT_EPOCH = 1790812800  # 2026-10-01 00:00:00 UTC; reproducible without env vars.


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def codepoint(value):
    return int(value.removeprefix("U+"), 16)


def pinned_input(entry, kind, cache, offline):
    filename = entry[f"{kind}_cache_file"]
    if Path(filename).name != filename:
        raise ValueError(f"invalid cache filename: {filename}")
    expected = entry[f"{kind}_sha256"]
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError(f"invalid SHA-256 for {filename}")
    path = cache / filename
    if not path.exists():
        if offline:
            raise ValueError(f"offline input missing: {path}")
        url = entry[f"{kind}_url"]
        if not url.startswith("https://"):
            raise ValueError(f"source URL must use HTTPS: {url}")
        request = urllib.request.Request(url, headers={"User-Agent": "TextProv-Utility-Font-Builder/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        if sha256(data) != expected:
            raise ValueError(f"download SHA-256 mismatch: {filename}")
        cache.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
    data = path.read_bytes()
    if sha256(data) != expected:
        raise ValueError(f"cached SHA-256 mismatch: {filename}; remove it and fetch again")
    return path, data


def rename(font, entry, protocol_version):
    family = entry["family"]
    legacy = "TextProv Propo Utility P9E" if entry["key"] == "proportional" else family
    postscript = re.sub(r"[^A-Za-z0-9]", "", family) + "-Regular"
    values = {
        1: legacy, 2: "Regular", 3: f"{VERSION};TextProv;{postscript}",
        4: family, 5: f"Version {VERSION}; TextProv {protocol_version}",
        6: postscript, 10: (
            "TextProv P9E utility font for development, debugging and demonstrations. "
            "Human U+E0100 uses the original outline; AI U+E0101 adds a sawtooth cue. "
            "Applications choose their own provenance presentation. "
            f"Direct FontTools derivative of {entry['upstream_family']}; no Nerd Fonts dependency."
        ), 16: family, 17: "Regular",
    }
    # Replace every locale/platform instance, avoiding old source identities.
    # ID 18 is the old Macintosh full name; WWS family/subfamily IDs are stale.
    font["name"].names = [record for record in font["name"].names
                            if record.nameID not in set(values) | {18, 21, 22}]
    for name_id, value in values.items():
        for platform, encoding, language in [(3, 1, 0x409), (0, 4, 0), (1, 0, 0)]:
            font["name"].setName(value, name_id, platform, encoding, language)


def empty_glyph():
    return TTGlyphPen(None).glyph()


def marker_glyph(advance, em, descent):
    width = max(8, round(advance * 0.74))
    left = round((advance - width) / 2)
    low = descent + max(8, round(em * 0.016))
    amplitude, thickness = max(8, round(em / 12)), max(5, round(em / 24))
    points = [(left + round(width * i / 4), low + (amplitude if i % 2 else 0))
              for i in range(5)]
    pen = TTGlyphPen(None)
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    for x, y in reversed(points):
        pen.lineTo((x, y + thickness))
    pen.closePath()
    return pen.glyph()


def append_ccmp(font, substitutions):
    """Add an independent ligature lookup without replacing upstream layout."""
    if "GSUB" not in font:
        table = font["GSUB"] = newTable("GSUB")
        table.table = otTables.GSUB()
        table.table.Version = 0x00010000
        for attribute, klass, records in [
            ("ScriptList", otTables.ScriptList, "ScriptRecord"),
            ("FeatureList", otTables.FeatureList, "FeatureRecord"),
            ("LookupList", otTables.LookupList, "Lookup"),
        ]:
            value = klass()
            setattr(value, records, [])
            setattr(value, records.replace("Record", "") + "Count", 0)
            setattr(table.table, attribute, value)
    table = font["GSUB"].table
    lookup_index = len(table.LookupList.Lookup)
    table.LookupList.Lookup.append(buildLookup([buildLigatureSubstSubtable(substitutions)]))
    table.LookupList.LookupCount = len(table.LookupList.Lookup)
    old_records = list(table.FeatureList.FeatureRecord)
    ccmp_indices = [i for i, record in enumerate(old_records) if record.FeatureTag == "ccmp"]
    if not ccmp_indices:
        record = otTables.FeatureRecord()
        record.FeatureTag = "ccmp"
        record.Feature = otTables.Feature()
        record.Feature.FeatureParams = None
        record.Feature.LookupListIndex = []
        record.Feature.LookupCount = 0
        ccmp_indices = [len(old_records)]
        old_records.append(record)
    # A shaper may choose just one ccmp feature per language. Augment every
    # existing instance rather than introducing an ignored duplicate feature.
    for index in ccmp_indices:
        feature = old_records[index].Feature
        feature.LookupListIndex.append(lookup_index)
        feature.LookupCount = len(feature.LookupListIndex)
    if not any(record.ScriptTag == "DFLT" for record in table.ScriptList.ScriptRecord):
        script_record = otTables.ScriptRecord()
        script_record.ScriptTag = "DFLT"
        script_record.Script = otTables.Script()
        script_record.Script.DefaultLangSys = otTables.LangSys()
        script_record.Script.DefaultLangSys.LookupOrder = None
        script_record.Script.DefaultLangSys.ReqFeatureIndex = 0xFFFF
        script_record.Script.DefaultLangSys.FeatureIndex = []
        script_record.Script.DefaultLangSys.FeatureCount = 0
        script_record.Script.LangSysRecord = []
        script_record.Script.LangSysCount = 0
        table.ScriptList.ScriptRecord.append(script_record)
        table.ScriptList.ScriptRecord.sort(key=lambda item: item.ScriptTag)
        table.ScriptList.ScriptCount = len(table.ScriptList.ScriptRecord)
    # Feature records must be sorted; remap all existing language references.
    order = sorted(range(len(old_records)), key=lambda i: old_records[i].FeatureTag)
    remap = {old: new for new, old in enumerate(order)}
    table.FeatureList.FeatureRecord = [old_records[i] for i in order]
    table.FeatureList.FeatureCount = len(order)
    for script_record in table.ScriptList.ScriptRecord:
        script = script_record.Script
        languages = [record.LangSys for record in script.LangSysRecord]
        if script.DefaultLangSys is not None:
            languages.append(script.DefaultLangSys)
        for language in languages:
            indices = list(language.FeatureIndex)
            if not any(i in ccmp_indices for i in indices + [language.ReqFeatureIndex]):
                indices.append(ccmp_indices[0])
            language.FeatureIndex = sorted(remap[i] for i in indices)
            language.FeatureCount = len(language.FeatureIndex)
            if language.ReqFeatureIndex != 0xFFFF:
                language.ReqFeatureIndex = remap[language.ReqFeatureIndex]


def patch(font, mapping):
    cmap = font.getBestCmap()
    supported = sorted(cp for cp in BASES if cp in cmap)
    marked = [cp for cp in supported if chr(cp).isprintable() and not chr(cp).isspace()]
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.layout_features = ["*"]
    options.glyph_names = True
    options.recalc_timestamp = False
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=supported)
    worker.subset(font)
    cmap = dict(font.getBestCmap())
    glyph_order = list(font.getGlyphOrder())
    glyf, hmtx = font["glyf"], font["hmtx"]
    em = font["head"].unitsPerEm
    descent = (font["OS/2"].sTypoDescender if font["OS/2"].fsSelection & 0x80
               else max(font["hhea"].descent, -font["OS/2"].usWinDescent))

    def add(name, glyph, metrics):
        glyf[name] = glyph
        hmtx[name] = metrics
        glyph_order.append(name)
        return name

    selector_glyphs = {selector: add(f"textprov.vs.{selector:05X}", empty_glyph(), (0, 0))
                       for selector in SELECTORS.values()}
    variants, strips = {}, {}
    for cp in marked:
        base = cmap[cp]
        if base in variants:
            continue
        advance, lsb = hmtx[base]
        if advance not in strips:
            strips[advance] = add(f"textprov.sawtooth.{advance}",
                                 marker_glyph(advance, em, descent), (0, 0))
        glyph = Glyph()
        glyph.numberOfContours = -1
        glyph.components = []
        for index, component_name in enumerate([base, strips[advance]]):
            component = GlyphComponent()
            component.glyphName, component.x, component.y = component_name, 0, 0
            component.flags = USE_MY_METRICS if index == 0 else 0
            glyph.components.append(component)
        variants[base] = add(f"textprov.ai.{base}", glyph, (advance, lsb))
    font.setGlyphOrder(glyph_order)
    for selector, glyph in selector_glyphs.items():
        cmap[selector] = glyph
    pua = {}
    for encoded, info in mapping["pua"].items():
        base = codepoint(info["base"])
        if info["provenance"] == "ai" and base in marked:
            value = codepoint(encoded)
            cmap[value] = variants[cmap[base]]
            pua[encoded] = info["base"]
    # Preserve source BMP cmaps and add a full Unicode cmap for supplementary PUA/VS.
    for table in font["cmap"].tables:
        if table.isUnicode() and table.format in (4, 12):
            table.cmap = {cp: glyph for cp, glyph in cmap.items()
                          if table.format == 12 or cp <= 0xFFFF}
    if not any(table.platformID == 3 and table.platEncID == 10 for table in font["cmap"].tables):
        table = CmapSubtable.newSubtable(12)
        table.platformID, table.platEncID, table.language = 3, 10, 0
        table.cmap = cmap
        font["cmap"].tables.append(table)
    table = CmapSubtable.newSubtable(14)
    table.platformID, table.platEncID, table.language = 0, 5, 0
    table.cmap = {}
    table.uvsDict = {
        SELECTORS["human"]: [(cp, cmap[cp]) for cp in marked],
        SELECTORS["ai"]: [(cp, variants[cmap[cp]]) for cp in marked],
    }
    font["cmap"].tables = [existing for existing in font["cmap"].tables if existing.format != 14] + [table]
    substitutions = {(cmap[cp], selector_glyphs[selector]): glyph
                     for selector, pairs in table.uvsDict.items() for cp, glyph in pairs}
    append_ccmp(font, substitutions)
    return supported, marked, pua


def write_zip(path, members, epoch):
    # Explicit metadata makes ZIPs independent of build paths, mtimes and umask.
    stamp = time.gmtime(max(315532800, min(epoch, 4354819198)))[:6]
    stamp = stamp[:5] + (stamp[5] // 2 * 2,)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for filename, data in sorted(members.items()):
            info = zipfile.ZipInfo(filename, date_time=stamp)
            info.create_system, info.external_attr = 3, 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)


def build(entry, args, mapping, epoch):
    source, _ = pinned_input(entry, "font", args.cache_dir, args.offline)
    _, license_text = pinned_input(entry, "license", args.cache_dir, args.offline)
    font = TTFont(source, recalcTimestamp=False)
    if "glyf" not in font or "fvar" in font:
        raise ValueError(f"expected a static TrueType glyf font: {source}")
    for tag in ("DSIG", "FFTM", "meta"):
        if tag in font:
            del font[tag]
    supported, marked, pua = patch(font, mapping)
    rename(font, entry, mapping["version"])
    font["head"].fontRevision = float(VERSION)
    font["head"].created = font["head"].modified = epoch + 2082844800
    stem = f"textprov-{entry['key']}-utility-p9e"
    outputs = {}
    for flavor, suffix in [(None, ".ttf"), ("woff2", ".woff2")]:
        font.flavor = flavor
        path = args.output / (stem + suffix)
        font.save(path, reorderTables=True)
        outputs[path.name] = sha256(path.read_bytes())
    description = (
        f"{entry['family']} (Regular)\nTextProv utility font version {VERSION}\n\n"
        "For development, debugging and demonstrations. AI U+E0101 adds a sawtooth\n"
        "cue; Human U+E0100 keeps the ordinary outline. Applications and websites\n"
        "choose their own visual interpretations of provenance. These cues are\n"
        "declarations, not proof of authorship or trust.\n\n"
        "Latin subset, with supported common punctuation. Spaces, controls and\n"
        "soft hyphen have no declared variation. Only Human and AI are TextProv\n"
        "states. Registry-allocated AI PUA aliases are included for\n"
        "compatibility; base character + selector is the canonical representation.\n"
        "Per-glyph advances and source line metrics are retained. Marked runs can\n"
        "shape differently from plain runs (for example kerning or ligatures).\n\n"
        f"Derived from {entry['upstream_family']}\nRepository: {entry['repository']}\n"
        f"Revision: {entry['revision']}\nSource: {entry['source_path']}\n"
        f"Source SHA-256: {entry['font_sha256']}\nLicense: {entry['license']} (see OFL.txt)\n"
        f"License source: {entry['license_url']}\nLicense SHA-256: {entry['license_sha256']}\n\n"
        "Patched directly with FontTools; independent of Nerd Fonts and font-patcher.\n"
        "Original copyright and license notices are retained in the font.\n"
    ).encode("utf-8")
    for suffix, data in [("-OFL.txt", license_text), ("-README.txt", description)]:
        path = args.output / (stem + suffix)
        path.write_bytes(data)
        outputs[path.name] = sha256(data)
    members = {stem + suffix: (args.output / (stem + suffix)).read_bytes()
               for suffix in (".ttf", ".woff2")}
    members.update({"OFL.txt": license_text, "README.txt": description})
    write_zip(args.output / (stem + ".zip"), members, epoch)
    outputs[stem + ".zip"] = sha256((args.output / (stem + ".zip")).read_bytes())
    return {
        **entry, "version": VERSION, "style": "Regular", "selectors": {name: f"U+{cp:05X}" for name, cp in SELECTORS.items()},
        "coverage": {"base": [f"U+{cp:04X}" for cp in supported],
                     "marked": [f"U+{cp:04X}" for cp in marked], "pua": pua},
        "outputs": outputs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sources", type=Path, default=SITE / "utility-font-sources.json")
    parser.add_argument("--cache-dir", type=Path, default=SITE / ".font-cache")
    parser.add_argument("--output", type=Path, default=SITE / "public/fonts/utility")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", DEFAULT_EPOCH))
    if epoch < 0:
        parser.error("SOURCE_DATE_EPOCH must be a nonnegative integer")
    entries = json.loads(args.sources.read_text())
    keys = [entry["key"] for entry in entries]
    if not entries or len(set(keys)) != len(keys) or any(not re.fullmatch(r"[a-z]+", key) for key in keys):
        parser.error("source entries need unique lowercase keys")
    mapping = json.loads((SITE.parent / "mapping.json").read_text())
    if {name: codepoint(mapping["variation_selectors"][name]) for name in SELECTORS} != SELECTORS:
        parser.error("registry Human/AI selectors differ from this builder")
    args.output.mkdir(parents=True, exist_ok=True)
    fonts = [build(entry, args, mapping, epoch) for entry in entries]
    manifest = {"version": VERSION, "protocol_version": mapping["version"],
                "source_date_epoch": epoch, "toolchain": {"fonttools": fontTools.__version__, "brotli": brotli.__version__},
                "source_manifest_sha256": sha256(args.sources.read_bytes()),
                "registry_sha256": sha256((SITE.parent / "mapping.json").read_bytes()), "fonts": fonts}
    manifest_data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (args.output / "sources.json").write_bytes(manifest_data)
    aggregate = {f"{entry['key']}/{name}": (args.output / filename).read_bytes()
                 for entry in entries for name, filename in [
                     (f"textprov-{entry['key']}-utility-p9e.ttf", f"textprov-{entry['key']}-utility-p9e.ttf"),
                     (f"textprov-{entry['key']}-utility-p9e.woff2", f"textprov-{entry['key']}-utility-p9e.woff2"),
                     ("OFL.txt", f"textprov-{entry['key']}-utility-p9e-OFL.txt"),
                     ("README.txt", f"textprov-{entry['key']}-utility-p9e-README.txt")]}
    aggregate["sources.json"] = manifest_data
    readme = (
        "TextProv Utility P9E fonts, version " + VERSION + "\n\n"
        "Development, debugging and demonstration adjuncts. Human U+E0100 keeps\n"
        "the original outline; AI U+E0101 adds a visible sawtooth cue. Applications\n"
        "choose their own provenance presentation. Cues declare provenance and\n"
        "do not authenticate authorship. These are Regular Latin subsets.\n\n"
        "Install each TTF in your operating system or use WOFF2 with @font-face.\n"
        "Base character + selector is canonical. Registry-allocated AI PUA aliases\n"
        "are available for compatibility. Only Human and AI are TextProv states.\n"
        "Source per-glyph advances and line metrics are retained; marked runs\n"
        "can shape differently (for example kerning or ligatures).\n\n"
        + "\n".join(f"{entry['family']} — derived from {entry['upstream_family']}" for entry in entries)
        + "\n\nEach family folder in the bundle contains its full original OFL.txt and\n"
        "README.txt with pinned source attribution. All source fonts and these\n"
        "derivatives are SIL Open Font License 1.1 fonts. Sources and output hashes\n"
        "are recorded in sources.json. Patches use FontTools directly and are\n"
        "independent of Nerd Fonts or its font-patcher.\n"
    ).encode("utf-8")
    (args.output / "README.txt").write_bytes(readme)
    aggregate["README.txt"] = readme
    write_zip(args.output / "textprov-utility-p9e.zip", aggregate, epoch)
    for font in fonts:
        print(f"{font['family']}: {len(font['coverage']['marked'])} Human/AI bases, {len(font['coverage']['pua'])} registry PUA aliases")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error
