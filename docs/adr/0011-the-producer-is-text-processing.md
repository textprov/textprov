# 0011. The producer is text processing, and a font is a renderer

Status: accepted. Date: 2026-09-12.

## Context

ADR 0006 split the protocol from the Nerd Fonts fork and drew the line as
"producer stays, consumer moves". The marker — `do_mark`, `do_mark_added`,
`do_convert` — stayed in the fork, and this repository's README said producing
marked text was out of scope.

That line was drawn in the wrong place, and it was drawn there because the
producer and one renderer happened to live in the same repository.

`font-patcher --provenance` does not produce marked text. It patches a font so
that already-marked text *displays* its marks. It is a renderer, and it sits
beside the other two: HTML spans (ADR 0001) and editor decoration APIs
(ADR 0009). It is the only one that needs a font toolchain, which is why it
lives in a font repository.

The marker, meanwhile, is 90 lines of text processing over the registry. It
imports `json` and `unicodedata`. It has no font dependency, no build step, and
nothing to do with Nerd Fonts. Leaving it in a font-patcher fork meant the
protocol repository could define marks that nothing in it could produce, and
that anyone wanting to mark text had to clone a font project to get a text
utility. It also made producer conformance unfalsifiable: the README claimed a
producer conformed when a decoder "reproduced its intent", which is not a test.

## Decision

The producer lives here, in the `textprov` Python package: `mark`,
`mark_added`, `convert`, and `inspect`, with a CLI (`python3 -m textprov`,
or the `textprov` entry point) covering mark, mark-added, convert, strip,
render, and inspect.

`SPEC.md` gains a Producer section stating the four properties a producer must
hold — one mark per cluster, never mark whitespace, idempotence, and that
`strip` returns the original text — and says that how a producer decides which
state applies is the integration's problem, not the protocol's.

`fixtures.json` gains `producer_cases` and `convert_cases` beside the decoder
`cases`. Recorded cases alone cannot cover the input space, so the reference
suite also tests the four properties directly. This is additive: the decoder
contract did not change, so the contract version stays 1. An implementation
that only reads marks ignores the new arrays.

The role vocabulary in `SPEC.md` is now producer, decoder, renderer, where
rendering covers markup, editor decorations, and a font's own variants.

## What this leaves in the fork

`font-patcher --provenance`, `bin/scripts/test-provenance.py` (it needs
`fontTools` and a built font), the font-build ADRs 0005 and 0007, and the
example and rollout material. The fork's `bin/scripts/nfprov.py` keeps working
as a downstream copy until this package is published; after that it is a
renderer's repository with no protocol code in it.

## Consequences

- Once the package is published, a user who wants to mark text installs one
  package with no dependencies.
- Producer conformance is defined by fixtures and required properties, not a
  claim.
- The Nerd Fonts fork is one renderer among three, which is what it always was.
- The JavaScript package still reads marks only. A browser producer would need
  a reason to exist; a DOM decorator does not imply one.
