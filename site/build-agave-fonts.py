"""Build TextProv demo subsets of Agave P+ (Mono, fixed-width, Propo).

The Agave P+ variants are shipped as raw TTFs (no upstream WOFF2, no ZIP), so
this script operates on the on-disk TTFs directly. It renames the family,
strips the legacy U+E0102 mapping (source's "unknown" glyph, which collides
with TextProv v1's `mixed`), keeps U+E0100/U+E0101, and emits TTF + WOFF2 +
ZIP bundles alongside the Maryheather and Zilla assets.

Requires fonttools and brotli. Run:

  python3 build-agave-fonts.py /path/to/nerd-fonts

Expects /path/to/nerd-fonts/temp/agave-pplus/AgaveNerdFont{Mono,,Propo}P+-Regular.ttf
and /path/to/nerd-fonts/patched-fonts/Agave/LICENSE.
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

source = Path(sys.argv[1])
target = Path(__file__).parent / "public" / "fonts"
agave_dir = source / "temp" / "agave-pplus"
fonts = [
    ("agave-mono",  "Agave Mono",         "AgaveNerdFontMonoP+-Regular.ttf"),
    ("agave-fixed", "Agave",              "AgaveNerdFontP+-Regular.ttf"),
    ("agave-propo", "Agave Propo",        "AgaveNerdFontPropoP+-Regular.ttf"),
]
manifest = []
for stem_prefix, display, filename in fonts:
    original = agave_dir / filename
    font = TTFont(original)
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=list(range(0x20, 0x100)) + [0xE0100, 0xE0101])
    worker.subset(font)
    family = display + " TextProv Demo P+"
    postscript = display.replace(" ", "") + "TextProvDemoPPlus"
    names = {
        1: family,
        2: "Regular",
        3: family + " 1.0",
        4: family,
        6: postscript,
        16: family,
        17: "Regular",
    }
    for record in font["name"].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    tables = [t for t in font["cmap"].tables if t.format == 14]
    assert len(tables) == 1
    assert set(tables[0].uvsDict) == {0xE0100, 0xE0101}
    for selector in (0xE0100, 0xE0101):
        assert any(
            cp == ord("A") and glyph
            for cp, glyph in tables[0].uvsDict[selector]
        )
    stem = stem_prefix + "-textprov-demo"
    for flavor, extension in [(None, ".ttf"), ("woff2", ".woff2")]:
        font.flavor = flavor
        font.save(target / (stem + extension))
    license_text = (source / "patched-fonts" / "Agave" / "LICENSE").read_bytes()
    (target / "agave-OFL.txt").write_bytes(license_text)
    nerd_license = (source / "LICENSE").read_bytes()
    (target / "NERD-FONTS-LICENSE.txt").write_bytes(nerd_license)
    with zipfile.ZipFile(
        target / (stem + ".zip"), "w", zipfile.ZIP_DEFLATED
    ) as bundle:
        for name in [
            stem + ".ttf",
            stem + ".woff2",
            "agave-OFL.txt",
            "NERD-FONTS-LICENSE.txt",
        ]:
            bundle.write(target / name, name)
    manifest.append(
        {
            "source": str(original.relative_to(source)),
            "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
            "family": family,
            "selectors": ["U+E0100", "U+E0101"],
        }
    )

sources_path = target / "sources.json"
existing = json.loads(sources_path.read_text()) if sources_path.exists() else []
existing = [e for e in existing if not e["family"].startswith("Agave ")]
existing.extend(manifest)
sources_path.write_text(json.dumps(existing, indent=2) + "\n")
