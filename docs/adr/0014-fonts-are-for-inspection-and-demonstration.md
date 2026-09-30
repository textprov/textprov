# 0014. P+ fonts are for inspection and demonstration, not everyday display

Status: accepted. Date: 2026-09-30.

## Context

A P+ font is a font patched to draw a variant glyph for a marked cluster, so
marked text shows its state wherever that font is used. It is one of three
renderers ([ADR 0011](0011-the-producer-is-text-processing.md)).

The font was the first renderer built, and its mark was being designed as if
people would read through it all day. That set a bar the font cannot clear
cheaply. The mark has to stay distinguishable at 12 to 14 px without tiring
the reader, there is room for about three distinguishable marks
([ADR 0010](0010-contributor-identity-is-out-of-band.md)), every typeface
needs its own build, the demo fonts cover `human` and `ai` only, and some
rendering systems ignore the selector mappings
([CoreText limitation](../SELECTORS-PUA-AND-INTERCHANGE.md#known-limitation-selector-glyphs-on-macos-coretext)).

What the font does that no other renderer does is reveal the encoding with no
TextProv-aware software at all. Install it, and any application that draws
text with it shows which clusters are marked.

## Decision

1. A P+ font has two purposes:
   - **Inspection.** It shows whether marks are present, and where, in any
     application. That serves people building and debugging producers,
     decoders, and integrations, and anyone checking whether a copy, paste,
     or storage path preserved the marks.
   - **Demonstration.** It shows what labelled text looks like before the
     applications people use support TextProv. In that sense it is a stopgap.
2. The expected way to read labels is an application's own interface: spans
   ([ADR 0001](0001-render-marks-as-html-spans.md)), editor decorations
   ([ADR 0009](0009-editor-decoration-apis.md)), or whatever presentation
   suits the tool. How and when an application shows a state is its decision,
   and most readers will not look at marks continuously.
3. The font's mark is judged as an inspection aid: visible and unambiguous
   when someone is looking for it. It does not need to be comfortable for
   sustained reading or to work as a general typographic design.

## Consequences

- The visual design of the font mark, including the sawtooth, blocks nothing
  in the protocol. Refining it is optional work.
- The font's gaps are limits of a development tool: no `mixed`, `edited`, or
  `unknown` variants, Latin-only coverage, one build per typeface, and
  renderer-dependent support. They are not protocol defects, and closing them
  ranks below the span and editor renderers.
- The font remains a conforming renderer. Its encoding guidance does not
  change: publish selectors, keep PUA to controlled font workflows
  ([ADR 0008](0008-do-not-publish-pua-to-the-web.md)).
- Documentation and the website present P+ fonts as a way to look at the
  encoding, not as how TextProv is meant to be experienced.
