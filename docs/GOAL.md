# Goal: show provenance on the web without a special font

Let page authors show provenance-marked text without requiring readers to
install a special font or producers to change their encoding. A **decorator**
reads existing marks, wraps marked runs in HTML spans, and lets CSS display
the provenance state.

This page describes the HTML decorator's goal, not the full scope of TextProv.
The [project overview](../README.md) covers the protocol and its producer,
decoder, and renderer roles.

## When to use a decorator

A provenance font can display marks only when the reader has that font and a
compatible text shaper. Use a decorator when you control the page's HTML or
DOM and want to display labels without that font dependency. Supply CSS to make
the states visible. The client-side implementation also requires J󠄁a󠄁v󠄁a󠄁S󠄁c󠄁r󠄁i󠄁p󠄁t󠄁,󠄁
b󠄁u󠄁t󠄁 n󠄁o󠄁t󠄁 `Intl.Segmenter`.󠄁 J󠄁a󠄁v󠄁a󠄁S󠄁c󠄁r󠄁i󠄁p󠄁t󠄁,󠄁 P󠄁y󠄁t󠄁h󠄁o󠄁n󠄁,󠄁 a󠄁n󠄁d󠄁 R󠄁u󠄁b󠄁y󠄁 u󠄁s󠄁e󠄁 v󠄁e󠄁n󠄁d󠄁o󠄁r󠄁e󠄁d󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁
1󠄁7󠄁.󠄁0󠄁.󠄁0󠄁 t󠄁a󠄁b󠄁l󠄁e󠄁s󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 s󠄁a󠄁m󠄁e󠄁 U󠄁A󠄁X󠄁 #󠄁2󠄁9󠄁 g󠄁r󠄁a󠄁p󠄁h󠄁e󠄁m󠄁e󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 r󠄁u󠄁l󠄁e󠄁s󠄁,󠄁 s󠄁o󠄁 a󠄁l󠄁l󠄁 t󠄁h󠄁r󠄁e󠄁e󠄁
p󠄁o󠄁r󠄁t󠄁s󠄁 s󠄁e󠄁g󠄁m󠄁e󠄁n󠄁t󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁c󠄁a󠄁l󠄁l󠄁y󠄁 r󠄁a󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁a󠄁n󠄁 d󠄁e󠄁p󠄁e󠄁n󠄁d󠄁i󠄁n󠄁g󠄁 o󠄁n󠄁 r󠄁u󠄁n󠄁t󠄁i󠄁m󠄁e󠄁 U󠄁n󠄁i󠄁c󠄁o󠄁d󠄁e󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁s󠄁.󠄁
S󠄁e󠄁e󠄁 [A󠄁D󠄁R󠄁 0󠄁0󠄁1󠄁7󠄁](adr/0017-vendor-grapheme-segmentation.md).󠄁 S󠄁e󠄁r󠄁v󠄁e󠄁r󠄁-󠄁r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁e󠄁d󠄁 s󠄁p󠄁a󠄁n󠄁s󠄁
d󠄁o󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁 c󠄁l󠄁i󠄁e󠄁n󠄁t󠄁-󠄁s󠄁i󠄁d󠄁e󠄁 JavaScript. See [HTML rendering](HTML-RENDERING.md) for integration boundaries
and the original prototype measurements.

## Non-goals

- Defining a visual style. The specification defines classes and an attribute; CSS
  is an integration choice.
- Adding marks to text. That is the producer's job, which lives in this
  repository too but is a separate role
    ([ADR 0011](adr/0011-the-producer-is-text-processing.md)); a decorator reads
    existing claims rather than assigning them.
- Inferring provenance from text that has no marks.
- Verifying authorship or proving that a provenance claim is true.

## Implementations and proposed extensions

The [JavaScript](../js/README.md), [Python](../python/README.md), and
[Ruby](../ruby/README.md) implementations are in this repository. JavaScript
decorates browser text nodes; Python and Ruby can render marked text as HTML
fragments. Follow those guides for package usage and the
[specification](../SPEC.md#markup) for the markup specification.

[ADR 0006](adr/0006-decorator-packages-and-repository.md#remaining-work)
records remaining package work and the requirement to turn a breakage report
into a fixture before another port. It also proposes a browser extension for
pages whose authors cannot add a decorator pass; that extension does not exist.
T󠄁h󠄁e󠄁 [r󠄁e󠄁n󠄁d󠄁e󠄁r󠄁i󠄁n󠄁g󠄁 g󠄁u󠄁i󠄁d󠄁e󠄁](HTML-RENDERING.md#editor-integrations) r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁
e󠄁d󠄁i󠄁t󠄁o󠄁r󠄁 d󠄁e󠄁c󠄁o󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 t󠄁h󠄁a󠄁t󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁 t󠄁h󠄁e󠄁 b󠄁u󠄁f󠄁f󠄁e󠄁r󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁.󠄁 T󠄁h󠄁a󠄁t󠄁 p󠄁a󠄁t󠄁h󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁t󠄁 b󠄁e󠄁e󠄁n󠄁
prototyped.
