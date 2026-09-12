# 0004. One fixture file defines decorator conformance

Status: accepted. Date: 2026-09-11.

Amended by [ADR 0011](0011-the-producer-is-text-processing.md): the fixture
also defines producer and conversion conformance.

## Context

The decorator will be ported to several languages. Independent
implementations drift unless they share a test.

## Decision

At the time, `src/glyphs/provenance/decorator/fixtures.json` in the Nerd Fonts
fork was the decorator conformance suite. Its canonical successor is this
repository's `fixtures.json`. A decoder conforms when `runs(input, options)`
equals the recorded runs for every case. The fixture is extended for each
breakage report and is never edited merely to fit an implementation.

## Evidence

The fixture was generated from the Python prototype and checked by hand. The
JavaScript prototype, written independently with `Intl.Segmenter`, passes all
18 original cases.

Three `merge_whitespace: false` cases were added on 2026-09-11, generated
from the shipped `bin/scripts/nfprov.py`. They exposed that the shipped
`css/nfprov.js` read only `mergeWhitespace`, so the earlier 18/18 result
had not exercised that option. The fixture now carries `contract_version`, and
runners compare both versions against the implementation. The shipped
JavaScript had its own runner,
`decorator/check_fixtures.mjs`; the prototype runners tested only the
prototypes.

## Consequences

- A port is one file plus a fixture runner.
- Grapheme segmentation differences between hosts surface as fixture failures
  rather than silent divergence.
