# Unicode segmentation data

`GraphemeBreakTest.txt` is Unicode 17.0.0's extended-grapheme-cluster
segmentation test file, copied unchanged from the
[Unicode Character Database](https://www.unicode.org/Public/17.0.0/ucd/auxiliary/GraphemeBreakTest.txt).
Each SDK runs its segmentation checks against this file and checks the version
against its vendored tables. This validates segmentation behavior, not the
TextProv proposal or the suitability of its experimental selector mapping.

`tools/gen_grapheme_tables.py` generates `python/textprov/_ucd.py`,
`ruby/lib/textprov/ucd.rb`, the generated block in `js/textprov.js`, and this test
file from Unicode's GraphemeBreakProperty, emoji-data, DerivedCoreProperties,
and GraphemeBreakTest files. To reproduce the current tables from the repository root:

```sh
python3 tools/gen_grapheme_tables.py --version 17.0.0
```

The generator downloads missing source files to `tools/.ucd/17.0.0`; an existing
source directory can be supplied with `--ucd DIR`. It rejects inconsistent
source versions. All three SDKs use the same tables so runtime Unicode versions
do not change the experiment's segmentation. Changing the Unicode version
requires rerunning the SDK checks and reviewing the generated differences.

Unicode data is © Unicode, Inc. and distributed under the
[Unicode License v3](https://www.unicode.org/license.txt). Generated table headers
record their data source and generator; retain those notices.
