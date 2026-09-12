# Goal

Let page authors show provenance-marked text without requiring readers to
install a font and without changing the producer. A decorator detects marks in
text, wraps marked runs in HTML spans, and lets CSS display the state.

## When to use a decorator

A provenance font can display marks only when the reader has that font and a
compatible text shaper. A decorator works on any page whose author controls the
HTML or DOM, and needs nothing from the reader. See
[HTML-RENDERING.md](HTML-RENDERING.md) for the measurements behind this
approach.

## Non-goals

- Defining a visual style. The contract defines classes and an attribute; CSS
  is an integration choice.
- Adding marks to text. That is the producer's job, which lives in this
  repository too but is a separate role (ADR 0011); a decorator only reads.
- Inferring provenance from text that has no marks.

## What comes next

[ADR 0006](adr/0006-decorator-packages-and-repository.md) sets the package
order: JavaScript first, then Python, then Ruby, with one breakage report
turned into a fixture case before each new port. A browser extension is the
proposed route for pages whose author cannot add a decorator pass; it does not
exist. Editor decoration APIs are [ADR 0009](adr/0009-editor-decoration-apis.md).
