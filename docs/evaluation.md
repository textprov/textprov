# Demonstration and evaluation

Status: historical observations, bounded VS demonstration, and proposed evaluation.
No additive-PUA or voice-reference encoding is implemented. No new application
transport measurements are claimed by this documentation cleanup.

## Demonstration

The homepage uses the retained JavaScript SDK decoder and CSS to expose a deliberately marked
VS sample without a special font. The experimental human/AI classifications are
not the proposal's voice-reference model. See the [VS profile](encodings/vs.md).
Only sample text enters that decoder; proposal prose remains ordinary Unicode.

## Historical observations

The observations below were reported by the earlier project. Source paths refer
to immutable snapshot `466e82cd7037fe2c8b3984ff0144e68492a09e7c`; unavailable raw
artifacts or uncertain methods are identified rather than reconstructed.

### Variation-sequence collision

The earlier assessment reports this result from the Python implementation:

```text
Input:         U+8FBB U+E0100
runs():        state = human
strip_marks(): U+8FBB
```

The input is a legitimate Japanese ideographic variation sequence, with no
TextProv producer involved. Attribution is invented and stripping loses the
glyph distinction. The assessment does not record a separate tested code SHA;
the immutable source snapshot contains that report, not a new reproduction.
The retained SDKs were also checked directly on 2026-10-04, as recorded below.
[historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/development/encoding-recommendation.md)

### Current SDK collision reproduction

Checked 2026-10-04 against the retained checkout using `PYTHONPATH=python python3`
and Node `require("./js/textprov.js")`. Both identify baseline API 0.2 and use
Unicode 17.0.0 segmentation tables. No SDK encoding behavior was changed during
reclamation.

| API | Result for `U+8FBB U+E0100` |
| --- | --- |
| Python `runs` | `human`, original two code points retained |
| Python `strip_marks` | `U+8FBB` only |
| JavaScript `runs` | `human`, original two code points retained |
| JavaScript `runs` with `strip: true` | `human`, `U+8FBB` only |

This reproduces the recognition and glyph-selection loss defect in both current
SDKs. It does not measure browser rendering or clipboard transport. The baseline
API identifier is distinct from package version and proposal status.

### Browser rendering and selection

Reported 2026-09-11 on macOS (Darwin 27), Playwright Chromium build 1243 and
WebKit 26.5 build 2358, with system fonts and no provenance font. A scratchpad
prototype used two paragraphs from an external producer example, converted to
selector form containing 322 selectors. The raw scratchpad and sample are not
part of this repository.

| Observation | Chromium | WebKit |
| --- | --- | --- |
| Server/client run results identical | yes | yes |
| Decorated spans from selector input | 7 | 7 |
| Width of `T + U+E0101` minus `T` | 0 px | 0 px |
| Selectors in server-rendered selection | 322 | 322 |
| Selectors in client-rendered selection | 322 | 322 |
| Selectors in then-PUA-decoded selection | 0 | 0 |

The prototype then decoded replacement PUA to bare base characters. Its later
base-plus-selector implementation was not measured by this table. Results concern
DOM selection strings, not a physical clipboard round-trip. They do not verify
current packages, Firefox, real iOS, accessibility, or destination behavior.
[historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/HTML-RENDERING.md)

### Search: conflicting historical accounts

ADR 0002 reports `window.find('fork')` matching the interleaved marked word in
Chromium and WebKit on 2026-09-11, with an absent-string control and the full
marked selection returned. The HTML-rendering report lists find-in-page as
unverified. These accounts conflict; the raw experiment is unavailable here.
Retain the limited reported result and the conflict, and repeat the named test
before making a current browser-search claim. Neither account verifies exact
search in editors, repository search, or indexing.
[historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/adr/0002-retain-selectors-in-span-text.md)

### Editing and processing lessons

Earlier hook reports describe prompt submission being classified as human even
when pasted text or scripted prompts had another origin; rewritten lines and
short quotations could receive overly broad AI labels. Marks also increased
reported token costs and prevented literal phrase matches in ordinary exact
search. These are reported effects of a particular automatic classification
adapter, not measurements establishing all applications' behavior.

They motivate separate criteria for explicit attribution, preservation during
editing, search, and overhead. The adapter and its classification policy are
not part of the proposal.
[historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/development/dogfooding-known-limitations.md)

### Font rendering

Earlier format-14-only demonstration fonts reportedly used decorated glyphs on
tested HarfBuzz paths but plain glyphs on tested CoreText paths. A later utility
suite added `ccmp` substitutions; its guide records native CoreText success for
`A + U+E0101` in five rebuilt TrueType fonts on macOS 27.2 build 26B5091g,
2026-10-01, including equal individual-character advance at 30 points.

These concern different font artifacts and limited samples. They establish no
universal shaping, editor, complex-script, or clipboard behavior. Fonts are not
required for the retained homepage CSS demonstration; historical font artifacts
remain recoverable from the earlier snapshot.
[historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/SELECTORS-PUA-AND-INTERCHANGE.md), [historical source](https://github.com/textprov/textprov/blob/466e82cd7037fe2c8b3984ff0144e68492a09e7c/docs/FONT-UTILITIES.md)

## Proposed evaluation matrix


Candidates are evaluated with ordinary fonts and, separately, any aware renderer,
font, or editor. Samples include Latin prose, composed and decomposed accents,
emoji ZWJ and tag sequences, Hangul Jamo, registered ideographic variants, Arabic,
Hebrew, and unrelated PUA text.

Observations cover whole and interior passage copying, paste into an unaware
plain-text editor followed by copying again, cursor movement, backspace,
insertion, search, accessibility, and explicit NFC/NFD transformations. Recorded
code points and decoded annotations accompany application and platform versions.

Voice-reference experiments include plain Unicode text represented as `Voice0`
without mutation or assumed human origin, and anonymous nonzero sources kept
separate from unattributed text. They also cover documents reusing `Voice1`,
merging passages, copying without source dictionaries, anonymous sources, and
multiple sources of the same human/AI category. Results distinguish reference
survival, preservation of source distinctions, and access to source descriptions.

Tag-based experiments compare payload suffixes with stateful attribution runs.
They include genuine emoji tag sequences, copying a run without its opening tag,
concatenating runs, missing terminators, and resets to the abstract `Voice0` state.
No attribution semantics are inferred from the historical language-tagging use.

Run-delimiter experiments include PUA brackets, interlinear annotations, musical
pairs, deprecated toggles, and bidi scope controls. Samples preserve legitimate
ruby, music, bidi controls, joiners, and combining marks. Tests cover nesting,
unclosed scopes, paragraph boundaries, conversion to markup, and an interior
copy with its opening context omitted. ZWJ and combining-mark comparisons record
changes in shaping, normalization, segmentation, and underlying text. A transport
result does not itself establish sanctioned Unicode semantics.


## Recording results

Each observation records candidate/profile revision, application and platform
versions, sample, method, raw input/output code points, decoded references, and
limitations. Separate ordinary fonts from aware rendering and editor support.
DOM selection, clipboard transport, and destination interpretation are separate
steps. Screenshots document appearance rather than exact preservation.

The matrix above is future work. Historical observations and demonstration
regression checks do not establish preservation in arbitrary applications.
