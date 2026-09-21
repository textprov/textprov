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

The source fonts map U+E0102 to a legacy unknown glyph. TextProv v1 assigns
that selector to mixed, so this mapping is deliberately removed. These
subsets do not display mixed, edited, or unknown variants. Use the JavaScript
reader to display all five states.

Human variants look plain. AI variants have a sawtooth underline. HarfBuzz
shaping was checked for both subsets; this is not a guarantee for every
browser or platform. A browser can load a webfont yet ignore its variation
selector mappings. The website's local-font example uses local() only and
never falls back to downloading a webfont.

Installation
------------

Unzip a download and install the TTF using your operating system's font
manager. Select the matching family in your editor, then open
../samples/marked-text.txt as UTF-8. Reload the homepage to try its
local-font example. Local font access may be restricted by browser
privacy settings.

Family names:

- Maryheather TextProv Demo P+
- Zilla Slab TextProv Demo P+
- Agave Mono TextProv Demo P+   (single-width cells + icons, best for IDEs)
- Agave TextProv Demo P+        (fixed-width text, double-width icons,
                                 the terminal-friendly default)
- Agave Propo TextProv Demo P+  (proportional text)

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
