# 0001. Render provenance marks as HTML spans, independent of the font

Status: accepted. Date: 2026-09-11.

> **S󠄁t󠄁a󠄁t󠄁e󠄁 g󠄁u󠄁i󠄁d󠄁a󠄁n󠄁c󠄁e󠄁 u󠄁p󠄁d󠄁a󠄁t󠄁e󠄁d󠄁 (󠄁2󠄁0󠄁2󠄁6󠄁-󠄁1󠄁0󠄁-󠄁0󠄁3󠄁)󠄁:󠄁** T󠄁h󠄁e󠄁 `unknown` s󠄁t󠄁y󠄁l󠄁i󠄁n󠄁g󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁d󠄁
> b󠄁e󠄁l󠄁o󠄁w󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁s󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 h󠄁i󠄁s󠄁t󠄁o󠄁r󠄁i󠄁c󠄁a󠄁l󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁t󠄁y󠄁p󠄁e󠄁,󠄁 n󠄁o󠄁t󠄁 t󠄁h󠄁e󠄁 c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 v󠄁o󠄁c󠄁a󠄁b󠄁u󠄁l󠄁a󠄁r󠄁y󠄁.󠄁
> O󠄁n󠄁l󠄁y󠄁 `human` a󠄁n󠄁d󠄁 `ai` a󠄁r󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁d󠄁.󠄁 T󠄁h󠄁e󠄁 s󠄁p󠄁a󠄁n󠄁-󠄁r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁i󠄁n󠄁g󠄁 d󠄁e󠄁c󠄁i󠄁s󠄁i󠄁o󠄁n󠄁 i󠄁s󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁;󠄁
> s󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁 [c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁 r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁i󠄁n󠄁g󠄁 g󠄁u󠄁i󠄁d󠄁e󠄁](../HTML-RENDERING.md).󠄁

## Context

Marked text is visible only with a provenance-enabled (P+) font and a shaper
that honours the font's format-14 character map. Mobile browsers do not let
readers install or override fonts, and every iOS browser shapes through
CoreText, which drops the selectors.

## Decision

A decorator pass finds marked runs in the text and wraps them in
`<span class="prov prov-STATE" data-prov="STATE">`. CSS styles the spans.
The producer and the in-band encoding are unchanged. At the time, the specification
was `src/glyphs/provenance/decorator/DECORATOR.md` in the Nerd Fonts fork; its
canonical successor is this repository's `SPEC.md`.

## Evidence

With Chromium and WebKit 26.5, the system font, and no P+ font, server-side
and client-side passes produced identical runs and visible marks. The
measurements were originally recorded in
`src/glyphs/provenance/decorator/HTML-RENDERING.md`; see this repository's
`docs/HTML-RENDERING.md` for the current record.

## Choosing a pass

Server-side for anything published: it needs no JavaScript and survives feeds
and readers, which strip scripts. Client-side for surfaces the author does not
own. Both emit the same markup and share one stylesheet, which is where the
sawtooth-for-ai and bar-for-unknown language from the font is reproduced.

## Consequences

- iOS and mobile are covered on pages the author controls.
- A DOM or HTML rewrite is required once; CSS alone cannot select code points.
- Whitespace merging between equal states is a view default, not protocol.
- Pages the author does not control are not covered. See 0009 and the
  browser-extension note in 0006.
