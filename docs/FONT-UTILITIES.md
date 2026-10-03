# TextProv Utility P9E fonts

TextProv Utility P9E fonts help developers inspect and debug provenance
encoding. They also provide demonstrations while applications integrate
TextProv. `P9E` is the shorthand for provenance; `Utility` identifies these
fonts as an adjunct to development work.

Applications and sites that display content have the context to choose useful
visual interpretations of the Unicode marks. They can show labels on demand,
use their own interface, or process provenance without displaying it. The
utility fonts provide one inspectable presentation of supported marks. Their
patterns are not requirements of the [TextProv protocol](../SPEC.md).

## Choose a family

Each family is a Regular static font, distributed as installable TrueType
(`.ttf`), webfont (`.woff2`), and a ZIP containing both formats, its license,
and a short README.

| TextProv family | Upstream design | Inspection use | Download |
| --- | --- | --- | --- |
| TextProv Sans Utility P9E | Source Sans 3 | Sans serif interface text | [Sans bundle](../site/public/fonts/utility/textprov-sans-utility-p9e.zip) |
| TextProv Serif Utility P9E | Source Serif 4 | Serif prose | [Serif bundle](../site/public/fonts/utility/textprov-serif-utility-p9e.zip) |
| TextProv Fixed Utility P9E | IBM Plex Mono | Fixed-width text and tabular comparisons | [Fixed bundle](../site/public/fonts/utility/textprov-fixed-utility-p9e.zip) |
| TextProv Mono Utility P9E | Source Code Pro | Monospaced code and terminal text | [Mono bundle](../site/public/fonts/utility/textprov-mono-utility-p9e.zip) |
| TextProv Proportional Utility P9E | Atkinson Hyperlegible | Proportional text with distinctive letterforms | [Proportional bundle](../site/public/fonts/utility/textprov-proportional-utility-p9e.zip) |

The [complete suite](../site/public/fonts/utility/textprov-utility-p9e.zip)
contains all five families with their notices and the generated build
manifest. Install a `.ttf` using your operating system's font installer, then
select its family in the application used for inspection. Some older font
menus show the Proportional family as **TextProv Propo Utility P9E**; its
legacy family-name field is shortened while its typographic family name
retains **TextProv Proportional Utility P9E**.

These categories overlap. Fixed and Mono both use fixed-width text, with
different underlying designs for comparison. Sans and Serif are proportional
fonts too. The suite supplies distinct debugging views, rather than defining
five mutually exclusive spacing classes.

## Rendering and coverage

The fonts contain TextProv's Human (`U+E0100`) and AI (`U+E0101`) selector
mappings. AI text uses a sawtooth strip below the baseline, within the font's
existing line metrics. Human text keeps the source outline, so a font view
alone cannot distinguish an explicit Human mark from unmarked text. Use a
TextProv decoder when you need that distinction or the complete state record.

The subset includes available glyphs in `U+0020`–`U+00FF`,
`U+2010`–`U+2027`, and the Euro, trademark, and minus signs. Selector variants
are added only for printable, non-whitespace base characters present in the
source. Whitespace, controls, and the soft hyphen are not decorated. H󠄁u󠄁m󠄁a󠄁n󠄁
a󠄁n󠄁d󠄁 A󠄁I󠄁 a󠄁r󠄁e󠄁 t󠄁h󠄁e󠄁 o󠄁n󠄁l󠄁y󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁d󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁.󠄁 S󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 a󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
h󠄁a󠄁v󠄁e󠄁 n󠄁o󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 m󠄁e󠄁a󠄁n󠄁i󠄁n󠄁g󠄁;󠄁 f󠄁o󠄁n󠄁t󠄁 c󠄁o󠄁v󠄁e󠄁r󠄁a󠄁g󠄁e󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁.󠄁 The
g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁e󠄁d󠄁 [build manifest](../site/public/fonts/utility/sources.json) records the actual
coverage of each build.

The builder adds a `cmap` format 14 variation-sequence table and `ccmp`
glyph-substitution rules. The second path allows text shapers to substitute a
supported base-plus-selector sequence through OpenType composition. It is a
font implementation choice; the private TextProv sequences are not
Unicode-registered variation sequences. The fonts also include the registry's
AI PUA mappings where the corresponding base glyph is present. They do not
allocate additional private code points.

Each decorated glyph keeps its base glyph's advance width. Inserting
selectors and substituting decorated glyphs can change kerning and ligature
formation across a marked run, so an entire shaped string need not match the
spacing of its unmarked source. This is a practical limitation of these
inspection fonts; fixed-width character advances alone do not establish
identical shaping of every text sequence.

A native CoreText test on macOS 27.2 (build 26B5091g), recorded on
2026-10-01, selected the decorated `A` for `A + U+E0101` in all five rebuilt
TrueType fonts. `A + U+E0100` and plain `A` selected the ordinary glyph; each
family retained the same character advance for those cases at 30 points. A
rendered comparison also showed visible AI patterns in the tested Latin and
punctuation samples.

The earlier P+ demo fonts used format 14 alone, and recorded CoreText tests
selected plain glyphs. Those results describe the legacy artifacts. The
utility suite's native CoreText result is scoped to the tested fonts, host,
and samples; consuming applications still need their own rendering tests.
Font-table checks and HarfBuzz shaping checks do not establish universal
editor or browser compatibility. Complex grapheme clusters, languages outside
the subset, application font fallback, and copy-and-paste paths need separate
integration testing. See the
[font and interchange guide](SELECTORS-PUA-AND-INTERCHANGE.md) for the legacy
CoreText evidence and why selectors remain the interchange form.

## Rebuild the suite

Run these commands from the repository root with Python 3.10 or newer,
required by the pinned fontTools version. The first build needs network access
to fetch the pinned upstream fonts and their licenses. Use an isolated
environment for the build dependencies:

```sh
python3 -m venv .venv-fonts
.venv-fonts/bin/python -m pip install -r site/font-build-requirements.txt
.venv-fonts/bin/python site/build-utility-fonts.py
.venv-fonts/bin/python site/check-utility-fonts.py --strict
```

[The source manifest](../site/utility-font-sources.json) pins the upstream
revision, font URL, license URL, and SHA256 checksums for each source. The
builder verifies downloads and cached inputs against those hashes, then writes
the suite to `site/public/fonts/utility/`. Sources and licenses are cached in
`site/.font-cache/`; the Python environment and source cache are local build
inputs. The checker also requires those cached originals and licenses; it
never fetches them. In a fresh checkout, run the builder with network access
before checking the bundled outputs.

Once the cache is populated, rebuild without network access:

```sh
.venv-fonts/bin/python site/build-utility-fonts.py --offline
.venv-fonts/bin/python site/check-utility-fonts.py --strict
```

Use `--cache-dir PATH` on both scripts to choose another cache, and
`--output PATH` on both to build and check another output directory.
`--sources PATH` selects another source manifest. An offline build requires every pinned font
and license in the cache; it fails on missing inputs or checksum mismatches.
Use each script's `--help` for its current options.

The output contains flat files named `textprov-{type}-utility-p9e.ttf`,
`.woff2`, and `.zip`, with matching `-OFL.txt` and `-README.txt` files. The
generated `sources.json` identifies build sources, coverage, and output
hashes. `textprov-utility-p9e.zip` packages the full suite. These files can be
served by the website or repackaged with their accompanying notices.

The checker validates font metadata and mappings, preserved glyph advances,
decoration geometry, bundles and notices, and exact shaping of supported
base-plus-selector sequences. It also checks f󠄁a󠄁l󠄁l󠄁b󠄁a󠄁c󠄁k󠄁 f󠄁o󠄁r󠄁 u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁
s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁.󠄁 I󠄁t󠄁s󠄁 strict checks use HarfBuzz through the pinned `uharfbuzz` dependency. Confirm
the application's actual rendering separately when adopting a utility font.

## Licensing and attribution

The project code is [MIT licensed](../LICENSE). The utility fonts and their
derivatives are licensed under the **SIL Open Font License 1.1 (OFL)**, rather
than the repository's code license. All five sources permit modification and
redistribution under OFL, including embedding and bundling. Each distributed
font must retain its upstream copyright and license, derivatives stay under
OFL, and the font software may not be sold by itself.

| Upstream source at the pinned revision | License | Reserved font name |
| --- | --- | --- |
| [Source Sans 3](https://github.com/adobe-fonts/source-sans/tree/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e) | [Adobe OFL notice](https://raw.githubusercontent.com/adobe-fonts/source-sans/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/LICENSE.md) | Source |
| [Source Serif 4](https://github.com/adobe-fonts/source-serif/tree/80d3f8894c09c937bebfa9011247d2e1c79fd6f4) | [Adobe OFL notice](https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/LICENSE.md) | Source |
| [IBM Plex Mono](https://github.com/IBM/plex/tree/763c36ef9117782905ae010056dfbe8fd2653a25) | [IBM OFL notice](https://raw.githubusercontent.com/IBM/plex/763c36ef9117782905ae010056dfbe8fd2653a25/LICENSE.txt) | Plex |
| [Source Code Pro](https://github.com/adobe-fonts/source-code-pro/tree/803b7e23ec97ae58b6232ea76519a76d428ba268) | [Adobe OFL notice](https://raw.githubusercontent.com/adobe-fonts/source-code-pro/803b7e23ec97ae58b6232ea76519a76d428ba268/LICENSE.md) | Source |
| [Atkinson Hyperlegible](https://github.com/googlefonts/atkinson-hyperlegible/tree/1cb311624b2ddf88e9e37873999d165a8cd28b46) | [Braille Institute OFL notice](https://raw.githubusercontent.com/googlefonts/atkinson-hyperlegible/1cb311624b2ddf88e9e37873999d165a8cd28b46/OFL.txt) | None declared |

The TextProv names replace the upstream primary font names to respect reserved
names. Copyright, license metadata, and the verbatim notices remain with the
fonts; renaming does not imply that TextProv designed the underlying typefaces
or that their upstream authors endorse these modifications. The per-font
READMEs identify the source and the added TextProv rendering behavior.

## Earlier demo fonts

The Maryheather, Zilla Slab, and Agave demos are rebuilt with embedded
`TextProv Demo P9E` names. Their existing download filenames remain available
so existing links continue to resolve. Those artifacts retain their legacy
format 14 shaping design and are distinct from this new utility suite.
Installed older copies may still show `P+`; select the actual family present
on your system. [ADR 0013](adr/0013-use-p9e-as-provenance-shorthand.md) records
the naming transition. Historical ADRs and rendering reports keep `P+` when
referring to the artifacts they measured.
