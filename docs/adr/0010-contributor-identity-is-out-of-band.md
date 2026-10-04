# 0010. Marks carry state and generation; contributor identity stays out of band

Status: p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁.󠄁 D󠄁a󠄁t󠄁e󠄁:󠄁 2󠄁0󠄁2󠄁6󠄁-󠄁1󠄁0󠄁-󠄁0󠄁2󠄁.󠄁 R󠄁e󠄁v󠄁i󠄁s󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 a󠄁c󠄁c󠄁e󠄁p󠄁t󠄁e󠄁d󠄁 o󠄁n󠄁 2󠄁0󠄁2󠄁6󠄁-󠄁0󠄁9󠄁-󠄁1󠄁1󠄁,󠄁
w󠄁h󠄁i󠄁c󠄁h󠄁 a󠄁l󠄁l󠄁o󠄁w󠄁e󠄁d󠄁 o󠄁n󠄁l󠄁y󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 i󠄁n󠄁 b󠄁a󠄁n󠄁d󠄁.󠄁 I󠄁t󠄁s󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁 d󠄁e󠄁c󠄁i󠄁s󠄁i󠄁o󠄁n󠄁 i󠄁s󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁.󠄁
A󠄁m󠄁e󠄁n󠄁d󠄁e󠄁d󠄁 2󠄁0󠄁2󠄁6󠄁-󠄁1󠄁0󠄁-󠄁0󠄁3󠄁:󠄁 t󠄁h󠄁e󠄁 [f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁](../development/generations-formal-aka-9g.md)
i󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁i󠄁n󠄁g󠄁l󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁i󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 a󠄁n󠄁d󠄁 i󠄁t󠄁s󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁.󠄁 T󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 k󠄁e󠄁e󠄁p󠄁s󠄁 t󠄁h󠄁e󠄁
r󠄁e󠄁a󠄁s󠄁o󠄁n󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁d󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁s󠄁t󠄁a󠄁t󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁.󠄁

> **S󠄁t󠄁a󠄁t󠄁e󠄁-󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁r󠄁r󠄁e󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 (󠄁2󠄁0󠄁2󠄁6󠄁-󠄁1󠄁0󠄁-󠄁0󠄁3󠄁)󠄁:󠄁** T󠄁h󠄁e󠄁 f󠄁i󠄁v󠄁e󠄁-󠄁s󠄁t󠄁a󠄁t󠄁e󠄁 v󠄁o󠄁c󠄁a󠄁b󠄁u󠄁l󠄁a󠄁r󠄁y󠄁 i󠄁n󠄁
> t󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 i󠄁s󠄁 s󠄁u󠄁p󠄁e󠄁r󠄁s󠄁e󠄁d󠄁e󠄁d󠄁.󠄁 `mixed`,󠄁 `edited`,󠄁 a󠄁n󠄁d󠄁 `unknown` p󠄁r󠄁e󠄁d󠄁a󠄁t󠄁e󠄁 t󠄁h󠄁e󠄁
> g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 a󠄁n󠄁d󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁s󠄁 a󠄁n󠄁d󠄁 a󠄁r󠄁e󠄁 o󠄁b󠄁s󠄁o󠄁l󠄁e󠄁t󠄁e󠄁,󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁t󠄁a󠄁i󠄁n󠄁e󠄁d󠄁 a󠄁s󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁s󠄁
> o󠄁r󠄁 n󠄁a󠄁m󠄁e󠄁d󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁i󠄁r󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 `U+E0102`–󠄁`U+E0104`,󠄁 s󠄁t󠄁a󠄁y󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 a󠄁r󠄁e󠄁
> n󠄁e󠄁v󠄁e󠄁r󠄁 r󠄁e󠄁a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁.󠄁 C󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁 g󠄁u󠄁i󠄁d󠄁a󠄁n󠄁c󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 `human` a󠄁n󠄁d󠄁 `ai`.󠄁
> I󠄁n󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁,󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 0󠄁 a󠄁n󠄁d󠄁 1󠄁 n󠄁a󠄁m󠄁e󠄁 t󠄁h󠄁o󠄁s󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁;󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 2󠄁–󠄁4󠄁
> a󠄁r󠄁e󠄁 n󠄁e󠄁v󠄁e󠄁r󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 5󠄁–󠄁F󠄁 a󠄁r󠄁e󠄁 u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁
> a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁 m󠄁e󠄁a󠄁n󠄁i󠄁n󠄁g󠄁s󠄁.󠄁 I󠄁t󠄁s󠄁 1󠄁6󠄁0󠄁-󠄁p󠄁o󠄁i󠄁n󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁
> t󠄁h󠄁e󠄁r󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 h󠄁a󠄁s󠄁 2󠄁0󠄁 n󠄁a󠄁m󠄁e󠄁d󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁/󠄁g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁m󠄁b󠄁i󠄁n󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 n󠄁o󠄁t󠄁 5󠄁0󠄁;󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁
> h󠄁a󠄁s󠄁 t󠄁w󠄁o󠄁 n󠄁a󠄁m󠄁e󠄁d󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 n󠄁o󠄁t󠄁 f󠄁i󠄁v󠄁e󠄁.󠄁 T󠄁h󠄁e󠄁 o󠄁l󠄁d󠄁 a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 c󠄁a󠄁p󠄁a󠄁c󠄁i󠄁t󠄁y󠄁 c󠄁o󠄁u󠄁n󠄁t󠄁s󠄁,󠄁
> c󠄁o󠄁n󠄁s󠄁e󠄁q󠄁u󠄁e󠄁n󠄁c󠄁e󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁e󠄁r󠄁-󠄁d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 e󠄁x󠄁a󠄁m󠄁p󠄁l󠄁e󠄁s󠄁 b󠄁e󠄁l󠄁o󠄁w󠄁 a󠄁r󠄁e󠄁 h󠄁i󠄁s󠄁t󠄁o󠄁r󠄁i󠄁c󠄁a󠄁l󠄁,󠄁 n󠄁o󠄁t󠄁
> c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 g󠄁u󠄁i󠄁d󠄁a󠄁n󠄁c󠄁e󠄁.󠄁 G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁n󠄁d󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁
> n󠄁o󠄁n󠄁-󠄁n󠄁o󠄁r󠄁m󠄁a󠄁t󠄁i󠄁v󠄁e󠄁;󠄁 t󠄁h󠄁e󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁 d󠄁e󠄁c󠄁i󠄁s󠄁i󠄁o󠄁n󠄁 i󠄁s󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁.󠄁 S󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁 c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁
> [s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁](../../SPEC.md#states) a󠄁n󠄁d󠄁
> [g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁](../development/generations-formal-aka-9g.md).󠄁

## Context

A mark is one code point after a grapheme cluster. I󠄁n󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 i󠄁t󠄁
i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁f󠄁i󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 o󠄁f󠄁 t󠄁h󠄁a󠄁t󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁:󠄁 h󠄁u󠄁m󠄁a󠄁n󠄁,󠄁 A󠄁I󠄁,󠄁 m󠄁i󠄁x󠄁e󠄁d󠄁,󠄁 e󠄁d󠄁i󠄁t󠄁e󠄁d󠄁,󠄁 o󠄁r󠄁 u󠄁n󠄁k󠄁n󠄁o󠄁w󠄁n󠄁
(󠄁`mapping.json` `variation_selectors`,󠄁 `U+E0100`–󠄁`U+E0104`)󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 h󠄁a󠄁s󠄁
n󠄁o󠄁 i󠄁n󠄁-󠄁b󠄁a󠄁n󠄁d󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁;󠄁 t󠄁h󠄁e󠄁 c󠄁o󠄁n󠄁s󠄁u󠄁m󠄁e󠄁r󠄁 d󠄁e󠄁c󠄁i󠄁d󠄁e󠄁s󠄁 w󠄁h󠄁a󠄁t󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 m󠄁e󠄁a󠄁n󠄁s󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁
p󠄁r󠄁o󠄁t󠄁o󠄁c󠄁o󠄁l󠄁 t󠄁a󠄁k󠄁e󠄁s󠄁 n󠄁o󠄁 position on it.

T󠄁w󠄁o󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁s󠄁k󠄁 w󠄁h󠄁a󠄁t󠄁 e󠄁l󠄁s󠄁e󠄁 a󠄁 m󠄁a󠄁r󠄁k󠄁 c󠄁o󠄁u󠄁l󠄁d󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁.󠄁

- **I󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁.󠄁** C󠄁o󠄁u󠄁l󠄁d󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁c󠄁o󠄁l󠄁 n󠄁a󠄁m󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁o󠄁r󠄁s󠄁 i󠄁n󠄁s󠄁t󠄁e󠄁a󠄁d󠄁:󠄁 H󠄁1󠄁,󠄁 H󠄁2󠄁,󠄁 A󠄁I󠄁1󠄁,󠄁
  A󠄁I󠄁2󠄁,󠄁 a󠄁n󠄁d󠄁 s󠄁o󠄁 o󠄁n󠄁?󠄁
- **G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁** C󠄁o󠄁u󠄁l󠄁d󠄁 a󠄁 m󠄁a󠄁r󠄁k󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 h󠄁o󠄁w󠄁 m󠄁a󠄁n󠄁y󠄁 t󠄁i󠄁m󠄁e󠄁s󠄁 a󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 h󠄁a󠄁s󠄁 b󠄁e󠄁e󠄁n󠄁
  r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁d󠄁,󠄁 t󠄁h󠄁a󠄁t󠄁 i󠄁s󠄁,󠄁 t󠄁a󠄁k󠄁e󠄁n󠄁 f󠄁r󠄁o󠄁m󠄁 o󠄁n󠄁e󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁'󠄁s󠄁 t󠄀r󠄀a󠄀n󠄀s󠄀c󠄀r󠄀i󠄀p󠄀t󠄀 i󠄀n󠄀t󠄀o󠄀 t󠄀h󠄀e󠄀
  i󠄀n󠄀p󠄀u󠄀t󠄀 o󠄀f󠄀 t󠄁h󠄁e󠄁 n󠄁e󠄁x󠄁t󠄁?󠄁 T󠄁e󠄁x󠄁t󠄁 t󠄁h󠄁a󠄁t󠄁 h󠄁a󠄁s󠄁 p󠄁a󠄁s󠄁s󠄁e󠄁d󠄁 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁
  s󠄁e󠄁v󠄁e󠄁r󠄁a󠄁l󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁w󠄁i󠄁s󠄁e󠄁 l󠄁o󠄁o󠄁k󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁 a󠄁s󠄁 t󠄁e󠄁x󠄁t󠄁 w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 l󠄁a󠄁s󠄁t󠄁
  o󠄁n󠄁e󠄁.󠄁

| L󠄁a󠄁y󠄁e󠄁r󠄁 | C󠄁a󠄁p󠄁a󠄁c󠄁i󠄁t󠄁y󠄁 | U󠄁s󠄁e󠄁d󠄁 b󠄁y󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 |
| --- | --- | --- |
| Selectors `U+E0100`–`U+E01EF` | 2󠄁4󠄁0󠄁 (󠄁`VS1`–󠄁`VS16` a󠄁r󠄁e󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁'󠄁s󠄁)󠄁 | 1󠄁6󠄁0󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁,󠄁 5󠄁0󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁m󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁e󠄁d󠄁;󠄁 8󠄁0󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 |
| P󠄁U󠄁A󠄁 p󠄁l󠄁a󠄁n󠄁e󠄁 1󠄁6󠄁 | a󠄁l󠄁l󠄁 (󠄁`PUA_AI(cp) = 0x100000 + cp` r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 p󠄁l󠄁a󠄁n󠄁e󠄁 f󠄁o󠄁r󠄁 A󠄁I󠄁)󠄁 | g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 o󠄁n󠄁l󠄁y󠄁 |
| F󠄁o󠄁n󠄁t󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁s󠄁 | 3󠄁 v󠄁a󠄁r󠄁i󠄁a󠄁n󠄁t󠄁s󠄁 p󠄁e󠄁r󠄁 b󠄁a󠄁s󠄁e󠄁 | n󠄁o󠄁n󠄁e󠄁 n󠄁e󠄁w󠄁;󠄁 a󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁 1󠄁4󠄁 c󠄁m󠄁a󠄁p󠄁 m󠄁a󠄁p󠄁s󠄁 s󠄁e󠄁v󠄁e󠄁r󠄁a󠄁l󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 t󠄁o󠄁 o󠄁n󠄁e󠄁 v󠄁a󠄁r󠄁i󠄁a󠄁n󠄁t󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁 |
| M󠄁a󠄁r󠄁k󠄁s󠄁 a󠄁 r󠄁e󠄁a󠄁d󠄁e󠄁r󠄁 c󠄁a󠄁n󠄁 t󠄁e󠄁l󠄁l󠄁 a󠄁p󠄁a󠄁r󠄁t󠄁 | 3󠄁 (󠄁b󠄁a󠄁r󠄁,󠄁 s󠄁a󠄁w󠄁t󠄁o󠄁o󠄁t󠄁h󠄁,󠄁 n󠄁o󠄁n󠄁e󠄁)󠄁 | u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 w󠄁h󠄁i󠄁l󠄁e󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 s󠄁h󠄁a󠄁r󠄁e󠄁s󠄁 i󠄁t󠄁s󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁 |
| D󠄁e󠄁c󠄁o󠄁r󠄁a󠄁t󠄁o󠄁r󠄁,󠄁 `data-prov`,󠄁 C󠄁S󠄁S󠄁 | u󠄁n󠄁b󠄁o󠄁u󠄁n󠄁d󠄁e󠄁d󠄁 | unbounded |

I󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁 f󠄁a󠄁i󠄁l󠄁s󠄁 t󠄁w󠄁o󠄁 t󠄁e󠄁s󠄁t󠄁s󠄁.󠄁 F󠄁i󠄁r󠄁s󠄁t󠄁,󠄁 a󠄁 n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁e󠄁d󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁o󠄁r󠄁 i󠄁s󠄁 a󠄁n󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁,󠄁 n󠄁o󠄁t󠄁 a󠄁
p󠄁r󠄁o󠄁p󠄁e󠄁r󠄁t󠄁y󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁 T󠄁h󠄁e󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁 t󠄁h󠄁a󠄁t󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁f󠄁i󠄁e󠄁s󠄁 A󠄁I󠄁2󠄁 c󠄁a󠄁n󠄁n󠄁o󠄁t󠄁 f󠄁i󠄁t󠄁 i󠄁n󠄁 a󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁
a󠄁n󠄁d󠄁 w󠄁o󠄁u󠄁l󠄁d󠄁 h󠄁a󠄁v󠄁e󠄁 t󠄁o󠄁 l󠄁i󠄁v󠄁e󠄁 o󠄁u󠄁t󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁.󠄁 S󠄁e󠄁c󠄁o󠄁n󠄁d󠄁,󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁t󠄁o󠄁c󠄁o󠄁l󠄁'󠄁s󠄁 v󠄁a󠄁l󠄁u󠄁e󠄁 i󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁
a󠄁 m󠄁a󠄁r󠄁k󠄁 i󠄁s󠄁 s󠄁e󠄁l󠄁f󠄁-󠄁d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁d󠄁 s󠄁u󠄁r󠄁v󠄁i󠄁v󠄁e󠄁s󠄁 c󠄁o󠄁p󠄁y󠄁 a󠄁n󠄁d󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁.󠄁 A󠄁n󠄁 o󠄁r󠄁d󠄁i󠄁n󠄁a󠄁l󠄁 s󠄁l󠄁o󠄁t󠄁 l󠄁o󠄁s󠄁e󠄁s󠄁
t󠄁h󠄁a󠄁t󠄁 a󠄁t󠄁 t󠄁h󠄁e󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 b󠄁o󠄁u󠄁n󠄁d󠄁a󠄁r󠄁y󠄁:󠄁 A󠄁I󠄁2󠄁 i󠄁n󠄁 o󠄁n󠄁e󠄁 f󠄁i󠄁l󠄁e󠄁 i󠄁s󠄁 n󠄁o󠄁t󠄁 A󠄁I󠄁2󠄁 i󠄁n󠄁 a󠄁n󠄁o󠄁t󠄁h󠄁e󠄁r󠄁.󠄁

G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 p󠄁a󠄁s󠄁s󠄁e󠄁s󠄁 b󠄁o󠄁t󠄁h󠄁.󠄁 I󠄁t󠄁 i󠄁s󠄁 a󠄁 p󠄁r󠄁o󠄁p󠄁e󠄁r󠄁t󠄁y󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁'󠄁s󠄁 p󠄁a󠄁t󠄁h󠄁,󠄁 n󠄁o󠄁t󠄁 o󠄁f󠄁 a󠄁 p󠄁e󠄁r󠄁s󠄁o󠄁n󠄁,󠄁
a󠄁n󠄁d󠄁 i󠄁t󠄁 m󠄁e󠄁a󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁 t󠄁h󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁:󠄁 a󠄁 w󠄁o󠄁r󠄁d󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁d󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁 t󠄁i󠄁m󠄁e󠄁s󠄁 i󠄁s󠄁
g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 3󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁v󠄁e󠄁r󠄁 i󠄁t󠄁 i󠄁s󠄁 p󠄁a󠄁s󠄁t󠄁e󠄁d󠄁.󠄁

## Decision

1. **A󠄁 m󠄁a󠄁r󠄁k󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁s󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁n󠄁d󠄁 a󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 n󠄁o󠄁t󠄁h󠄁i󠄁n󠄁g󠄁 e󠄁l󠄁s󠄁e󠄁.󠄁** I󠄁t󠄁 m󠄁a󠄁y󠄁 n󠄁o󠄁t󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁
   a󠄁n󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁:󠄁 a󠄁 p󠄁a󠄁r󠄁t󠄁i󠄁c󠄁u󠄁l󠄁a󠄁r󠄁 a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁,󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁,󠄁 s󠄁e󠄁s󠄁s󠄁i󠄁o󠄁n󠄁,󠄁 o󠄁r󠄁 a󠄁c󠄁c󠄁o󠄁u󠄁n󠄁t󠄁.󠄁
2. **L󠄁a󠄁y󠄁o󠄁u󠄁t󠄁.󠄁** T󠄁h󠄁e󠄁 [f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁](../development/generations-formal-aka-9g.md)
   d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁,󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 o󠄁p󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 c󠄁o󠄁n󠄁f󠄁o󠄁r󠄁m󠄁a󠄁n󠄁c󠄁e󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁.󠄁
   I󠄁n󠄁 o󠄁u󠄁t󠄁l󠄁i󠄁n󠄁e󠄁:󠄁 a󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁 o󠄁f󠄁 1󠄁6󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 b󠄁y󠄁 1󠄁0󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁,󠄁 w󠄁h󠄁o󠄁s󠄁e󠄁
   g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 8󠄁0󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁s󠄁 f󠄁o󠄁r󠄁
   s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁.󠄁 A󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁s󠄁 a󠄁n󠄁 a󠄁l󠄁t󠄁e󠄁r󠄁n󠄁a󠄁t󠄁e󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁 i󠄁t󠄁s󠄁 o󠄁w󠄁n󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁
   r󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 W󠄁h󠄁e󠄁r󠄁e󠄁 t󠄁h󠄁i󠄁s󠄁 o󠄁u󠄁t󠄁l󠄁i󠄁n󠄁e󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 d󠄁i󠄁f󠄁f󠄁e󠄁r󠄁,󠄁 t󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁
   s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 g󠄁o󠄁v󠄁e󠄁r󠄁n󠄁s󠄁.󠄁
3. **E󠄁v󠄁e󠄁r󠄁y󠄁 m󠄁a󠄁r󠄁k󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁s󠄁 i󠄁t󠄁s󠄁e󠄁l󠄁f󠄁.󠄁** N󠄁o󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 m󠄁a󠄁y󠄁 d󠄁e󠄁p󠄁e󠄁n󠄁d󠄁 o󠄁n󠄁 c󠄁o󠄁n󠄁t󠄁e󠄁x󠄁t󠄁 o󠄁u󠄁t󠄁s󠄁i󠄁d󠄁e󠄁
   t󠄁h󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁,󠄁 b󠄁e󠄁c󠄁a󠄁u󠄁s󠄁e󠄁 a󠄁 c󠄁o󠄁p󠄁i󠄁e󠄁d󠄁 s󠄁u󠄁b󠄁s󠄁t󠄁r󠄁i󠄁n󠄁g󠄁 l󠄁o󠄁s󠄁e󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 c󠄁o󠄁n󠄁t󠄁e󠄁x󠄁t󠄁.󠄁 A󠄁n󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
   m󠄁a󠄁y󠄁 a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁 w󠄁i󠄁t󠄁h󠄁 f󠄁e󠄁w󠄁e󠄁r󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 t󠄁h󠄁a󠄁n󠄁 t󠄁h󠄁e󠄁 g󠄁r󠄁i󠄁d󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁s󠄁.󠄁 T󠄁h󠄁a󠄁t󠄁 f󠄁r󠄁e󠄁e󠄁d󠄁o󠄁m󠄁 s󠄁t󠄁o󠄁p󠄁s󠄁 a󠄁t󠄁
   a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁i󠄁n󠄁g󠄁.󠄁 A󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 e󠄀v󠄀e󠄀r󠄀y󠄀 s󠄀t󠄀a󠄀t󠄀e󠄀,󠄀 i󠄀n󠄀c󠄀l󠄀u󠄀d󠄀i󠄀n󠄀g󠄀 o󠄀n󠄀e󠄀s󠄀 i󠄀t󠄀 d󠄀o󠄀e󠄀s󠄀
   n󠄀o󠄀t󠄀 k󠄁n󠄁o󠄁w󠄁,󠄁 a󠄁n󠄁d󠄁 s󠄁a󠄁t󠄁u󠄁r󠄁a󠄁t󠄁e󠄁s󠄁 o󠄁n󠄁l󠄁y󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 9󠄁 (󠄁P󠄁7󠄁 a󠄁n󠄁d󠄁 C󠄁3󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁
   s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁)󠄁.󠄁 A󠄁 t󠄁o󠄁o󠄁l󠄁 t󠄁h󠄁a󠄁t󠄁 s󠄁a󠄁t󠄁u󠄁r󠄁a󠄁t󠄁e󠄁d󠄁 a󠄀t󠄀 g󠄀e󠄀n󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀 3󠄀 w󠄀o󠄀u󠄀l󠄀d󠄀 w󠄀r󠄀i󠄀t󠄀e󠄀 3󠄀 f󠄀o󠄀r󠄀
   t󠄀e󠄀x󠄀t󠄀 r󠄀e󠄀g󠄀u󠄀r󠄀g󠄀i󠄀t󠄀a󠄀t󠄀e󠄀d󠄀 f󠄀i󠄀v󠄀e󠄀 t󠄁i󠄁m󠄁e󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 a󠄁 r󠄁e󠄁a󠄁d󠄁e󠄁r󠄁 w󠄁o󠄁u󠄁l󠄁d󠄁 t󠄁a󠄁k󠄁e󠄁 3󠄁 a󠄁s󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁
   (󠄁C󠄁o󠄁r󠄁o󠄁l󠄁l󠄁a󠄁r󠄁y󠄁 4󠄁.󠄁1󠄁)󠄁.󠄁 A󠄁 c󠄁o󠄁a󠄁r󠄁s󠄁e󠄁r󠄁 s󠄁c󠄁a󠄁l󠄁e󠄁 i󠄁s󠄁 a󠄀 s󠄀t󠄀r󠄀i󠄀d󠄀e󠄀 i󠄀n󠄀 t󠄀h󠄀e󠄀 r󠄀e󠄀s󠄀e󠄀r󠄀v󠄀e󠄀d󠄀 r󠄀a󠄀n󠄀g󠄀e󠄀.󠄀
4. **R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁i󠄁n󠄁g󠄁 i󠄀s󠄀 a󠄀 s󠄀e󠄀p󠄀a󠄀r󠄀a󠄀t󠄀e󠄀 o󠄀p󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀 f󠄀r󠄀o󠄀m󠄀 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁.󠄁** E󠄁a󠄁c󠄁h󠄁 t󠄁i󠄁m󠄁e󠄁 a󠄁
   t󠄁r󠄁a󠄁n󠄁s󠄁c󠄁r󠄁i󠄁p󠄁t󠄁 b󠄁e󠄁c󠄁o󠄁m󠄁e󠄁s󠄁 i󠄁n󠄁p󠄁u󠄁t󠄁 t󠄁o󠄁 a󠄁 n󠄁e󠄁w󠄁 c󠄁o󠄁n󠄁v󠄁e󠄁r󠄁s󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁
   m󠄁a󠄁r󠄁k󠄁 g󠄁o󠄁e󠄁s󠄁 u󠄁p󠄁 b󠄁y󠄁 o󠄁n󠄁e󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 P󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 r󠄁u󠄁l󠄁e󠄁 3󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁
   s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 w󠄁h󠄁i󠄁c󠄁h󠄁 k󠄁e󠄁e󠄁p󠄁s󠄁 a󠄁n󠄁 e󠄁x󠄁i󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁,󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁 g󠄁o󠄁v󠄁e󠄁r󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁
   (󠄁C󠄁3󠄁 a󠄁n󠄁d󠄁 C󠄁4󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁)󠄁.󠄁 T󠄁h󠄁e󠄁 e󠄁a󠄁r󠄁l󠄁i󠄁e󠄁r󠄁 n󠄁a󠄁m󠄁e󠄁,󠄁 c󠄁a󠄁r󠄁r󠄁y󠄁i󠄁n󠄁g󠄁,󠄁 h󠄁i󠄁d󠄁
   t󠄁h󠄁a󠄁t󠄁 t󠄁h󠄁i󠄁s󠄁 i󠄁s󠄁 a󠄁n󠄁 o󠄁p󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 i󠄁t󠄁s󠄁 o󠄁w󠄁n󠄁.󠄁
5. **P󠄁U󠄁A󠄁 i󠄁s󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 o󠄁n󠄁l󠄁y󠄁.󠄁** P󠄁U󠄁A󠄁 r󠄁e󠄁m󠄁a󠄁i󠄁n󠄁s󠄁 a󠄁n󠄁 a󠄁d󠄁j󠄁u󠄁n󠄁c󠄁t󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁 f󠄁o󠄁r󠄁
   c󠄁o󠄁m󠄁p󠄁a󠄁t󠄁i󠄁b󠄁i󠄁l󠄁i󠄁t󠄁y󠄁 w󠄁i󠄁t󠄁h󠄁 f󠄁o󠄁n󠄁t󠄁 w󠄁o󠄁r󠄁k󠄁f󠄁l󠄁o󠄁w󠄁s󠄁.󠄁 A󠄁 m󠄁a󠄁r󠄁k󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 1󠄁 o󠄁r󠄁 l󠄁a󠄁t󠄁e󠄁r󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁
   P󠄁U󠄁A󠄁 f󠄁o󠄁r󠄁m󠄁.󠄁 A󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 t󠄁h󠄁a󠄁t󠄁 m󠄁e󠄁e󠄁t󠄁s󠄁 a󠄁 P󠄁U󠄁A󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁s󠄁 i󠄁t󠄁 t󠄀o󠄀 b󠄀a󠄀s󠄀e󠄀
   p󠄀l󠄀u󠄀s󠄀 s󠄀e󠄀l󠄀e󠄀c󠄀t󠄀o󠄀r󠄀,󠄀 a󠄀s󠄀 [S󠄁P󠄁E󠄁C󠄁.󠄁m󠄁d󠄁](../../SPEC.md#algorithm)
   d󠄁o󠄁e󠄁s󠄁 f󠄁o󠄁r󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁n󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 (󠄁C󠄁7󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁)󠄁.󠄁
6. **I󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁,󠄁 w󠄁h󠄁e󠄁n󠄁 w󠄁a󠄁n󠄁t󠄁e󠄁d󠄁,󠄁 i󠄁s󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁d󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 b󠄁a󠄁n󠄁d󠄁** by the container: an
   attribute on a wrapping element in HTML, a header line or sidecar in plain
   text, a field in an editor's metadata. The protocol does not define that
   channel.
7. **P󠄁e󠄁r󠄁-󠄁c󠄁o󠄁n󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁o󠄁r󠄁 s󠄁l󠄁o󠄁t󠄁s󠄁,󠄁 i󠄁f󠄁 e󠄁v󠄁e󠄁r󠄁 n󠄁e󠄁e󠄁d󠄁e󠄁d󠄁 i󠄁n󠄁 b󠄁a󠄁n󠄁d󠄁,󠄁 a󠄁r󠄁e󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁** i󠄁n󠄁 t󠄁h󠄁e󠄁
   r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 E󠄁a󠄁c󠄁h󠄁 s󠄁l󠄁o󠄁t󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 n󠄁a󠄁m󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 i󠄁t󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁s󠄁 t󠄁o󠄁;󠄁 a󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁
   t󠄁h󠄁a󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 s󠄁l󠄁o󠄁t󠄁 o󠄁r󠄁d󠄁i󠄁n󠄁a󠄁l󠄁,󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁
   c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁e󠄁r󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁s󠄁 w󠄁h󠄁a󠄁t󠄁 a󠄁n󠄁 o󠄁r󠄁d󠄁i󠄁n󠄁a󠄁l󠄁 m󠄁e󠄁a󠄁n󠄁s󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 6󠄁.󠄁 N󠄁o󠄁t󠄁h󠄁i󠄁n󠄁g󠄁 i󠄁s󠄁
   s󠄁c󠄁h󠄁e󠄁d󠄁u󠄁l󠄁e󠄁d󠄁.󠄁

## Options considered for varying the layout

| A󠄁p󠄁p󠄁r󠄁o󠄁a󠄁c󠄁h󠄁 | S󠄁e󠄁l󠄁f󠄁-󠄁d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁i󠄁n󠄁g󠄁 | C󠄁o󠄁s󠄁t󠄁 |
| --- | --- | --- |
| F󠄁i󠄁x󠄁e󠄁d󠄁 g󠄁r󠄁i󠄁d󠄁;󠄁 a󠄁n󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁 a󠄁 s󠄁u󠄁b󠄁s󠄁e󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 | Y󠄁e󠄁s󠄁 | S󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 c󠄁a󠄁n󠄁n󠄁o󠄁t󠄁 b󠄁e󠄁 t󠄁r󠄁a󠄁d󠄁e󠄁d󠄁 f󠄀o󠄀r󠄀 g󠄀e󠄀n󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀s󠄀 b󠄀e󠄀y󠄀o󠄀n󠄀d󠄀 t󠄀h󠄀e󠄀 g󠄀r󠄀i󠄀d󠄀 |
| D󠄁i󠄁s󠄁j󠄁o󠄁i󠄁n󠄁t󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁s󠄁 (󠄁t󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁,󠄁 a󠄁n󠄁d󠄁 e󠄁a󠄁c󠄁h󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁n󠄁 i󠄁t󠄁s󠄁 o󠄁w󠄁n󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 r󠄁a󠄁n󠄁g󠄁e󠄁)󠄁 | Y󠄁e󠄁s󠄁 | U󠄁s󠄁e󠄁s󠄁 u󠄁p󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁 |
| I󠄁n󠄁-󠄁b󠄁a󠄁n󠄁d󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 m󠄀a󠄀r󠄀k󠄀e󠄀r󠄀 a󠄀t󠄀 t󠄀h󠄀e󠄀 s󠄀t󠄀a󠄀r󠄀t󠄀 o󠄀f󠄀 a󠄀 r󠄀u󠄀n󠄀 | P󠄁a󠄁r󠄁t󠄁l󠄁y󠄁 | L󠄀o󠄀s󠄀t󠄀 w󠄀h󠄀e󠄀n󠄀 a󠄀 s󠄀u󠄀b󠄀s󠄀t󠄀r󠄀i󠄀n󠄀g󠄀 i󠄀s󠄀 c󠄀o󠄀p󠄀i󠄀e󠄀d󠄀 |
| O󠄁u󠄁t󠄁-󠄁o󠄁f󠄁-󠄁b󠄁a󠄁n󠄁d󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 | N󠄁o󠄁 | L󠄀o󠄀s󠄀t󠄀 w󠄀h󠄀e󠄀n󠄀 a󠄀 s󠄀u󠄀b󠄀s󠄀t󠄀r󠄀i󠄀n󠄀g󠄀 i󠄀s󠄀 c󠄀o󠄀p󠄀i󠄀e󠄀d󠄀 |

T󠄁h󠄁e󠄁 d󠄁e󠄁c󠄁i󠄁s󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁m󠄁b󠄁i󠄁n󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 f󠄁i󠄁r󠄁s󠄁t󠄁 t󠄁w󠄁o󠄁.󠄁

T󠄁h󠄁e󠄁 g󠄁r󠄁i󠄁d󠄁 i󠄁s󠄁 1󠄁6󠄁 w󠄁i󠄁d󠄁e󠄁 s󠄁o󠄁 t󠄁h󠄁a󠄁t󠄁 a󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 r󠄁e󠄁a󠄁d󠄁s󠄁 d󠄁i󠄁r󠄁e󠄁c󠄁t󠄁l󠄁y󠄁 i󠄁n󠄁 h󠄁e󠄁x󠄁:󠄁 t󠄁h󠄁e󠄁 l󠄁a󠄁s󠄁t󠄁 d󠄁i󠄁g󠄁i󠄁t󠄁
i󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 o󠄁n󠄁e󠄁 b󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 i󠄁t󠄁 i󠄁s󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 T󠄁h󠄁e󠄁 b󠄁l󠄁o󠄁c󠄁k󠄁 h󠄁o󠄁l󠄁d󠄁s󠄁 e󠄁x󠄁a󠄁c󠄁t󠄁l󠄁y󠄁
1󠄁5󠄁 r󠄁o󠄁w󠄁s󠄁 o󠄁f󠄁 1󠄁6󠄁.󠄁 G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁,󠄁 s󠄁o󠄁 t󠄁e󠄁x󠄁t󠄁 a󠄁l󠄁r󠄁e󠄁a󠄁d󠄁y󠄁
m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 n󠄁e󠄁e󠄁d󠄁s󠄁 n󠄁o󠄁 m󠄁i󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 C󠄁a󠄁p󠄁p󠄁i󠄁n󠄁g󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁t󠄁 9󠄁 k󠄁e󠄁e󠄁p󠄁s󠄁 t󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁
s󠄁i󠄁n󠄁g󠄁l󠄁e󠄁 d󠄁e󠄁c󠄁i󠄁m󠄁a󠄁l󠄁 d󠄁i󠄁g󠄁i󠄁t󠄁 a󠄁n󠄁d󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁s󠄁 f󠄁i󠄁v󠄁e󠄁 r󠄁o󠄁w󠄁s󠄁 f󠄁r󠄁e󠄁e󠄁 f󠄁o󠄁r󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁
t󠄁h󠄁e󠄁m󠄁s󠄁e󠄁l󠄁v󠄁e󠄁s󠄁.󠄁 S󠄁a󠄁t󠄁u󠄁r󠄁a󠄁t󠄁i󠄁n󠄁g󠄁 b󠄁e󠄁l󠄁o󠄁w󠄁 9󠄁 w󠄁a󠄁s󠄁 c󠄁o󠄁n󠄁s󠄁i󠄁d󠄁e󠄁r󠄁e󠄁d󠄁 a󠄁s󠄁 a󠄁 w󠄁a󠄁y󠄁 t󠄁o󠄁 v󠄁a󠄁r󠄁y󠄁 t󠄁h󠄁e󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁 a󠄁n󠄁d󠄁
r󠄁e󠄁j󠄁e󠄁c󠄁t󠄁e󠄁d󠄁,󠄁 b󠄁e󠄁c󠄁a󠄁u󠄁s󠄁e󠄁 a󠄁 r󠄁e󠄁a󠄁d󠄁e󠄁r󠄁 c󠄁o󠄁u󠄁l󠄁d󠄁 n󠄁o󠄁 l󠄁o󠄁n󠄁g󠄁e󠄁r󠄁 t󠄁a󠄁k󠄁e󠄁 a󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 b󠄁e󠄁l󠄁o󠄁w󠄁 9󠄁 a󠄁s󠄁
e󠄁x󠄁a󠄁c󠄁t󠄁.󠄁

## Evidence

The capacity table w󠄁a󠄁s󠄁 f󠄁i󠄁r󠄁s󠄁t󠄁 r󠄁e󠄁a󠄁d󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 o󠄁n󠄁 2󠄁0󠄁2󠄁6󠄁-󠄁0󠄁9󠄁-󠄁1󠄁1󠄁:󠄁 `mapping.json`
version 0.1, `font-patcher` glyph generation (three variants per base plus mark
glyphs), and `css/nfprov.js`. The decorator is table driven in both
languages, so the software cost of a new state is one registry entry; the
font cost is one glyph per base; the visual cost is a stroke pattern a reader
must distinguish at 12 to 14 px. None of those budgets holds identities.

Slots were checked for cost without being built: 16 slot selectors use z󠄁e󠄁r󠄁o󠄁
n󠄁e󠄁w󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁s󠄁,󠄁 b󠄁e󠄁c󠄁a󠄁u󠄁s󠄁e󠄁 a󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁 1󠄁4󠄁 c󠄁m󠄁a󠄁p󠄁 m󠄁a󠄁y󠄁 m󠄁a󠄁p󠄁 s󠄁e󠄁v󠄁e󠄁r󠄁a󠄁l󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁
v󠄁a󠄁r󠄁i󠄁a󠄁n󠄁t󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁.󠄁 T󠄁h󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁o󠄁w󠄁s󠄁 r󠄁e󠄁l󠄁y󠄁 o󠄁n󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁 m󠄁a󠄁p󠄁p󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁d󠄁 h󠄁a󠄁v󠄁e󠄁 n󠄁o󠄁t󠄁 b󠄁e󠄁e󠄁n󠄁
b󠄁u󠄁i󠄁l󠄁t󠄁 e󠄁i󠄁t󠄁h󠄁e󠄁r󠄁.󠄁

## Consequences

- `human`, `ai`, `mixed`, `edited`, and `unknown` remain the complete s󠄁t󠄁a󠄁t󠄁e󠄁
  set. `edited` and `unknown` are proposed: their selectors are allocated in the
  registry but no producer emits them yet and no font renders them.
- A󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 r󠄁e󠄁a󠄁d󠄁s󠄁 b󠄁o󠄁t󠄁h󠄁 v󠄁a󠄁l󠄁u󠄁e󠄁s󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 a󠄁l󠄁o󠄁n󠄁e󠄁 (󠄁D󠄁e󠄁f󠄁 2󠄁.󠄁2󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁
  f󠄁o󠄁r󠄁m󠄁a󠄁l󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁)󠄁.󠄁 A󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 t󠄁h󠄁a󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 k󠄁n󠄁o󠄁w󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁 r󠄁e󠄁a󠄁d󠄁s󠄁 i󠄁t󠄁s󠄁
  g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 F󠄁o󠄁r󠄁 a󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 w󠄁h󠄁o󠄁s󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁,󠄁 i󠄁t󠄁
  r󠄁e󠄁p󠄁o󠄁r󠄁t󠄁s󠄁 a󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 v󠄁a󠄁l󠄁u󠄁e󠄁,󠄁 n󠄁o󠄁t󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁.󠄁
- T󠄁h󠄁e󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁'󠄁s󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁,󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁,󠄁 m󠄁a󠄁r󠄁k󠄁u󠄁p󠄁,󠄁 c󠄁o󠄁n󠄁f󠄁o󠄁r󠄁m󠄁a󠄁n󠄁c󠄁e󠄁
  f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁.󠄁 T󠄁h󠄁e󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 s󠄁t󠄁i󠄁l󠄁l󠄁 o󠄁p󠄁e󠄁n󠄁 a󠄁r󠄁e󠄁 l󠄁i󠄁s󠄁t󠄁e󠄁d󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁
  s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁
  [g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁a󠄁l󠄁 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁](../../SPEC.md#generational-marking-proposed-non-normative).󠄁
- A󠄁 f󠄁o󠄁n󠄁t󠄁 t󠄁h󠄁a󠄁t󠄁 r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁s󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 n󠄁e󠄁e󠄁d󠄁s󠄁 a󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁 1󠄁4󠄁 e󠄁n󠄁t󠄁r󠄁y󠄁 p󠄁e󠄁r󠄁 b󠄁a󠄁s󠄁e󠄁 p󠄁e󠄁r󠄁
  s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁.󠄁 T󠄁h󠄁e󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁 g󠄁r󠄁o󠄁w󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁 t󠄁h󠄁e󠄁 n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁 o󠄁f󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 e󠄁v󠄁e󠄁n󠄁 t󠄁h󠄁o󠄁u󠄁g󠄁h󠄁 t󠄁h󠄁e󠄁 g󠄁l󠄁y󠄁p󠄁h󠄁
  c󠄁o󠄁u󠄁n󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁.󠄁
- A page that wants per-contributor colour styles by container, not by
  mark. The decorator's `data-prov` stays a state name.
- E󠄁v󠄁e󠄁r󠄁y󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 b󠄁l󠄁o󠄁c󠄁k󠄁 c󠄁a󠄁n󠄁 f󠄁o󠄁r󠄁m󠄁 a󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁e󠄁r󠄁e󠄁d󠄁 i󠄁d󠄁e󠄁o󠄁g󠄁r󠄁a󠄁p󠄁h󠄁i󠄁c󠄁 v󠄁a󠄁r󠄁i󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
  s󠄁e󠄁q󠄁u󠄁e󠄁n󠄁c󠄁e󠄁 w󠄁i󠄁t󠄁h󠄁 a󠄁 H󠄁a󠄁n󠄁 b󠄁a󠄁s󠄁e󠄁.󠄁 T󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁s󠄁 5󠄁0󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁s󠄁 i󠄁n󠄁s󠄁t󠄁e󠄁a󠄁d󠄁 o󠄁f󠄁 5󠄁,󠄁
  w󠄁h󠄁i󠄁c󠄁h󠄁 w󠄁i󠄁d󠄁e󠄁n󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 e󠄁x󠄁p󠄁o󠄁s󠄁u󠄁r󠄁e󠄁,󠄁 t󠄁r󠄁a󠄁c󠄁k󠄁e󠄁d󠄁 i󠄁n󠄁
  [i󠄁s󠄁s󠄁u󠄁e󠄁 #󠄁2󠄁0󠄁](https://github.com/delano/nerd-fonts/issues/20).
- M󠄁a󠄁r󠄁k󠄁s󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 1󠄁 o󠄁r󠄁 l󠄁a󠄁t󠄁e󠄁r󠄁 h󠄁a󠄁v󠄁e󠄁 n󠄁o󠄁 P󠄁U󠄁A󠄁 f󠄁o󠄁r󠄁m󠄁.󠄁 H󠄁o󠄁w󠄁 t󠄁h󠄁e󠄁y󠄁 r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁 u󠄁n󠄁d󠄁e󠄁r󠄁
  C󠄁o󠄁r󠄁e󠄁T󠄁e󠄁x󠄁t󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁t󠄁 b󠄁e󠄁e󠄁n󠄁 c󠄁h󠄁e󠄁c󠄁k󠄁e󠄁d󠄁.󠄁 T󠄁h󠄁e󠄁 e󠄁a󠄁r󠄁l󠄁i󠄁e󠄁r󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 o󠄁f󠄁 t󠄁h󠄁i󠄁s󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 s󠄁a󠄁i󠄁d󠄁 t󠄁h󠄁a󠄁t󠄁
  c󠄁o󠄁n󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁o󠄁r󠄁 s󠄁l󠄁o󠄁t󠄁s󠄁 w󠄁o󠄁u󠄁l󠄁d󠄁 r󠄁e󠄁a󠄁c󠄁h󠄁 C󠄁o󠄁r󠄁e󠄁T󠄁e󠄁x󠄁t󠄁 o󠄁n󠄁l󠄁y󠄁 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 t󠄁h󠄁e󠄁 `ccmp` r󠄁o󠄁u󠄁t󠄁e󠄁 i󠄁n󠄁
  [i󠄁s󠄁s󠄁u󠄁e󠄁 #󠄁2󠄁4󠄁](https://github.com/delano/nerd-fonts/issues/24);󠄁 t󠄁h󠄁a󠄁t󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁t󠄁
  b󠄁e󠄁e󠄁n󠄁 v󠄁e󠄁r󠄁i󠄁f󠄁i󠄁e󠄁d󠄁 f󠄁o󠄁r󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁o󠄁w󠄁s󠄁.󠄁
- Copy and paste carries state and g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 a󠄁n󠄁d󠄁 d󠄁r󠄁o󠄁p󠄁s󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁t󠄁y󠄁.󠄁 T󠄁h󠄁a󠄁t󠄁 i󠄁s󠄁 b󠄁y󠄁
  design.

## Related: document-level defaults

The same principle answers whether text can declare "unmarked here means
mixed" or "unmarked here means AI". It can, but only out of band and only as
a statement about the container.

- In band there is no code point for a default, and there will not be one. A
  default marker would have to persist until the next marker, which
  [`CRITERIA.md`](https://github.com/delano/nerd-fonts/blob/main/src/glyphs/provenance/CRITERIA.md)
  rejects because a partial copy would carry the wrong state or none. Unmarked
  text has no in-band state wherever it lands.
- Out of band a container may declare a default, for example an attribute on
  the wrapping element in HTML. Presentation may style unmarked text inside
  it accordingly. The decorator does not read it: runs with no state stay
  `null`, so the declaration is lost on copy exactly as identity is.
- The useful case is a document that is mostly AI with human edits marked
  explicitly. That works today by marking the AI text and leaving the human
  edits unmarked, or by marking both. Declaring a default instead saves
  bytes and loses the property that every character answers for itself.
  The protocol prefers the marks.
