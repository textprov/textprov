Earlier TextProv demos (family naming updated to P9E)
====================================================

The new TextProv Utility P9E set lives in utility/. These older subsets remain
available at their existing URLs. Their cmap-14-only behavior differs from the
new utility fonts; see utility/README.txt for the development/debugging set.

Output family names now use P9E. Historical source input filenames below use
P+ because those are the actual upstream files used by these legacy builders.
The old Agave Propo variant has fixed-width Latin text; only its icon-width
mode was proportional. Use TextProv Proportional Utility P9E for a genuinely
variable-width text comparison.

TextProv example fonts
======================

These regular-weight demo subsets come from https://github.com/delano/nerd-fonts:

- patched-fonts/maryheather/webfonts/MaryheatherNerdFontPropoP+-Regular.woff2
- patched-fonts/zilla/webfonts/ZillaSlabNerdFontPropoP+-Regular.woff2
- temp/agave-pplus/AgaveNerdFontMonoP+-Regular.ttf
- temp/agave-pplus/AgaveNerdFontP+-Regular.ttf
- temp/agave-pplus/AgaveNerdFontPropoP+-Regular.ttf

sources.json records the source file hashes and output family names.

Copyright and licences
----------------------

Maryheather derives from Merriweather:
Copyright 2016 The Merriweather Project Authors (sorkintype@gmail.com),
with Reserved Font Name "Merriweather".
See maryheather-OFL.txt for the complete SIL Open Font License 1.1.
The modified family uses Maryheather rather than the reserved name.

Zilla Slab:
Copyright 2017, The Mozilla Foundation.
See zilla-OFL.txt for the complete SIL Open Font License 1.1.

Agave (three variants: Mono, fixed-width, Propo):
Copyright 2013-2026 The agave Project Authors
(https://github.com/blobject/agave).
See agave-OFL.txt for the complete SIL Open Font License 1.1.

Nerd Fonts patching attribution and licence: NERD-FONTS-LICENSE.txt.
The font software is not covered by the website code's MIT licence.
Redistribute the font licence notices with the fonts. Each ZIP includes them.

Scope and compatibility
-----------------------

These subsets retain U+0020 through U+00FF where present in the source and
variation selectors U+E0100 (Human) and U+E0101 (AI). Nerd Fonts icons and
private-use encodings are excluded. They are not full replacement fonts.

The source fonts contain a legacy non-TextProv U+E0102 mapping, which is
deliberately removed. Human and AI are the only TextProv provenance states.
Use the JavaScript reader to display their labels without a font.

Human variants look plain. AI variants have a sawtooth underline. HarfBuzz
shaping was checked for both subsets; this is not a guarantee for every
browser or platform. A browser can load a webfont yet ignore its variation
s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 m󠄁a󠄁p󠄁p󠄁i󠄁n󠄁g󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁 w󠄁e󠄁b󠄁s󠄁i󠄁t󠄁e󠄁'󠄁s󠄁 r󠄁e󠄁a󠄁d󠄁e󠄁r󠄁 r󠄁e󠄁v󠄁e󠄁a󠄁l󠄁s󠄁 l󠄁a󠄁b󠄁e󠄁l󠄁s󠄁 i󠄁n󠄁d󠄁e󠄁p󠄁e󠄁n󠄁d󠄁e󠄁n󠄁t󠄁l󠄁y󠄁 o󠄁f󠄁
f󠄁o󠄁n󠄁t󠄁 r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁i󠄁n󠄁g󠄁.󠄁

Installation
------------

Unzip a download and install the TTF using your operating system's font
manager. Select the matching family in your editor, then open
../samples/marked-text.txt a󠄁s󠄁 U󠄁T󠄁F󠄁-󠄁8󠄁.󠄁 P󠄁a󠄁s󠄁t󠄁e󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁p󠄁l󠄁e󠄁 i󠄁n󠄁t󠄁o󠄁 t󠄁h󠄁e󠄁 h󠄁o󠄁m󠄁e󠄁p󠄁a󠄁g󠄁e󠄁
r󠄁e󠄁a󠄁d󠄁e󠄁r󠄁 t󠄁o󠄁 i󠄁n󠄁s󠄁p󠄁e󠄁c󠄁t󠄁 i󠄁t󠄁s󠄁 l󠄁a󠄁b󠄁e󠄁l󠄁s󠄁 i󠄁n󠄁d󠄁e󠄁p󠄁e󠄁n󠄁d󠄁e󠄁n󠄁t󠄁l󠄁y󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁e󠄁d󠄁 f󠄁o󠄁n󠄁t󠄁.󠄁

Family names:

- Maryheather TextProv Demo P9E
- Zilla Slab TextProv Demo P9E
- Agave Mono TextProv Demo P9E   (fixed-width Latin text)
- Agave TextProv Demo P9E        (fixed-width Latin text)
- Agave Propo TextProv Demo P9E  (fixed-width Latin text; historical source
                                 variant name, not a proportional-text font)

The WOFF2 files are for embedding on a web page via CSS @font-face.

The three Agave variants are Latin subsets of a monospaced code font, so
they are the ones to install in an editor or terminal for TextProv
kick-the-tires. Maryheather and Zilla Slab are prose fonts.

Rebuild
-------

From site/, with Python, fonttools and brotli installed:

python3 build-demo-fonts.py /path/to/nerd-fonts   # Maryheather + Zilla
python3 build-agave-fonts.py /path/to/nerd-fonts  # Agave P+ trio

Both scripts subset their sources, rename the family, keep only U+E0100
(Human) and U+E0101 (AI) selectors, and package licences with each ZIP.
build-agave-fonts.py reads raw TTFs from temp/agave-pplus/; build the
Agave P+ trio there first via the nerd-fonts pipeline.
