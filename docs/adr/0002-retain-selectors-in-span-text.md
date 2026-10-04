# 0002. Retain selectors inside span text so copy round-trips

Status: accepted. Date: 2026-09-11.

## Context

A reader may copy from a decorated page into an editor that has a P+ font.
The selectors are default-ignorable and render at zero width in every engine
tested.

## Decision

Span text keeps the original selectors. The optional `strip` setting removes
them for integrators that need plain text, at the cost of copy round-trip.
`strip` defaults to `false`.

## Evidence

Selecting the decorated sections in Chromium and WebKit yielded all 322
selectors present in the source, identical to the undecorated control. Width
of a letter plus selector equalled the bare letter in both engines.

Find-in-page was tested 2026-09-11 and the concern did not materialise.
`window.find('fork')` succeeds in both Chromium and WebKit against
`f<VS>o<VS>r<VS>k<VS>`, where the DOM text contains no literal `fork`
substring. The selection returned is the full interleaved range. A search for
an absent string returns false, so the match is not spurious. Both engines
ignore default-ignorable selectors when matching.

### PUA input

T󠄁h󠄁e󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁a󠄁l󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁t󠄁y󠄁p󠄁e󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁d󠄁 P󠄁U󠄁A󠄁 t󠄁o󠄁 b󠄁a󠄁r󠄁e󠄁 b󠄁a󠄁s󠄁e󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁s󠄁.󠄁 S󠄁e󠄁l󠄁e󠄁c󠄁t󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁a󠄁t󠄁
s󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 y󠄁i󠄁e󠄁l󠄁d󠄁e󠄁d󠄁 z󠄁e󠄁r󠄁o󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 s󠄁o󠄁 t󠄁h󠄁e󠄁 o󠄁r󠄁d󠄁i󠄁n󠄁a󠄁r󠄁y󠄁 t󠄁e󠄁x󠄁t󠄁 s󠄁u󠄁r󠄁v󠄁i󠄁v󠄁e󠄁d󠄁 b󠄁u󠄁t󠄁 i󠄁t󠄁s󠄁
p󠄁r󠄁o󠄁v󠄁e󠄁n󠄁a󠄁n󠄁c󠄁e󠄁 d󠄁i󠄁d󠄁 n󠄁o󠄁t󠄁.󠄁 B󠄁o󠄁t󠄁h󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁t󠄁y󠄁p󠄁e󠄁s󠄁 w󠄁e󠄁r󠄁e󠄁 t󠄁h󠄁e󠄁n󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 t󠄁o󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁 P󠄁U󠄁A󠄁 t󠄁o󠄁 b󠄁a󠄁s󠄁e󠄁
p󠄁l󠄁u󠄁s󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁s󠄁s󠄁e󠄁d󠄁 t󠄁h󠄁e󠄁 P󠄁U󠄁A󠄁 f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁 c󠄁a󠄁s󠄁e󠄁s󠄁.󠄁 T󠄁h󠄁o󠄁s󠄁e󠄁 f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁 p󠄁a󠄁s󠄁s󠄁e󠄁s󠄁 d󠄁i󠄁d󠄁 n󠄁o󠄁t󠄁
m󠄁e󠄁a󠄁s󠄁u󠄁r󠄁e󠄁 a󠄁 p󠄁h󠄁y󠄁s󠄁i󠄁c󠄁a󠄁l󠄁 c󠄁l󠄁i󠄁p󠄁b󠄁o󠄁a󠄁r󠄁d󠄁 r󠄁o󠄁u󠄁n󠄁d󠄁-󠄁t󠄁r󠄁i󠄁p󠄁.󠄁 T󠄁h󠄁e󠄁
[r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁i󠄁n󠄁g󠄁 g󠄁u󠄁i󠄁d󠄁e󠄁](../HTML-RENDERING.md#original-prototype-measurements) r󠄁e󠄁t󠄁a󠄁i󠄁n󠄁s󠄁
t󠄁h󠄁e󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁a󠄁l󠄁 m󠄁e󠄁a󠄁s󠄁u󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁;󠄁 [S󠄁P󠄁E󠄁C󠄁.󠄁m󠄁d󠄁](../../SPEC.md#algorithm) d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁 c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁
P󠄁U󠄁A󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁 b󠄁a󠄁r󠄁e󠄁-󠄁b󠄁a󠄁s󠄁e󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁 w󠄁h󠄁e󠄁n󠄁 `strip` i󠄁s󠄁 e󠄁n󠄁a󠄁b󠄁l󠄁e󠄁d󠄁.󠄁

## Consequences

- Plain-text clipboard carries the selector encoding into HarfBuzz hosts.
- Find-in-page is not a reason to strip. `strip` remains for integrators who
  need clean text for other reasons, such as a plain-text export.
- Measured in browser find-in-page only. Search in other consumers, such as
  editors, greps, and site search indexes, is untested and will not ignore
  the selectors unless it normalises them away.
- A physical paste into a P+ editor was not performed; only the selection
  string was read.
