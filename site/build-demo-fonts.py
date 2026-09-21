"""Build Latin-text demo subsets from the provenance Nerd Fonts fork.

Requires fonttools and brotli. Run: python3 build-demo-fonts.py /path/to/nerd-fonts
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
fonts = [
    (
        "maryheather",
        "Maryheather",
        "MaryheatherNerdFontPropoP+-Regular",
        "merriweather.zip",
        "Merriweather-1.582/OFL.txt",
    ),
    (
        "zilla",
        "Zilla Slab",
        "ZillaSlabNerdFontPropoP+-Regular",
        "zilla.zip",
        "zilla-slab/LICENSE",
    ),
]
manifest = []
for folder, display, filename, archive, license_path in fonts:
    root = source / "patched-fonts" / folder
    original = root / "webfonts" / (filename + ".woff2")
    font = TTFont(original)
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    worker = subset.Subsetter(options=options)
    # The source's E0102 is a legacy unknown glyph, not TextProv 0.1 mixed.
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
    stem = folder + "-textprov-demo"
    for flavor, extension in [(None, ".ttf"), ("woff2", ".woff2")]:
        font.flavor = flavor
        font.save(target / (stem + extension))
    with zipfile.ZipFile(root / archive) as upstream:
        license_text = upstream.read(license_path)
    (target / (folder + "-OFL.txt")).write_bytes(license_text)
    nerd_license = (source / "LICENSE").read_bytes()
    (target / "NERD-FONTS-LICENSE.txt").write_bytes(nerd_license)
    with zipfile.ZipFile(
        target / (stem + ".zip"), "w", zipfile.ZIP_DEFLATED
    ) as bundle:
        for name in [
            stem + ".ttf",
            stem + ".woff2",
            folder + "-OFL.txt",
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
(target / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n")
