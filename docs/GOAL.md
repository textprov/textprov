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
the states visible. The client-side implementation also requires JavaScript
and `Intl.Segmenter`; server-rendered spans do not require client-side
JavaScript. See [HTML rendering](HTML-RENDERING.md) for integration boundaries
and the original prototype measurements.

## Non-goals

- Defining a visual style. The contract defines classes and an attribute; CSS
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
[specification](../SPEC.md#markup) for the markup contract.

[ADR 0006](adr/0006-decorator-packages-and-repository.md#remaining-work)
records remaining package work and the requirement to turn a breakage report
into a fixture before another port. It also proposes a browser extension for
pages whose authors cannot add a decorator pass; that extension does not exist.
[ADR 0009](adr/0009-editor-decoration-apis.md) proposes editor decorations that
leave the buffer unchanged. That path has not been prototyped.
