# Executable baseline experiment

These assets describe the implemented SDK demonstrations, not the proposal's
encoding registry or conformance standard. They retain experimental mapping
version `0.2`; fixture `experiment_version` records that baseline identifier.
Existing API names `SPEC_VERSION` and `specVersion` expose the same historical
identifier and do not version the proposal.

`mapping.json` maps two supplementary variation selectors to the classifications
`human` and `ai`. It also maps a limited set of replacement-PUA characters to
base characters labelled `ai`. That mode replaces base characters; it is not the
[additive-PUA candidate](../../docs/encodings/additive-pua.md).

Python and Ruby vendor identical mapping copies for standalone package use;
JavaScript embeds equivalent tables. Their checks compare these copies and
exercise shared `fixtures.json` cases. Those checks establish agreement between
these implementations, not Unicode endorsement or reliable attribution detection.

The decoder cannot distinguish legitimate variation sequences using these same
selectors. `U+8FBB U+E0100` is decoded as `human`, and stripping removes its real
glyph distinction. Do not apply the decoder automatically to arbitrary proposal
prose. See the [VS profile](../../docs/encodings/vs.md) and
[evaluation](../../docs/evaluation.md).

The demos do not implement the proposal's voice-reference semantics, dictionaries,
reference scope, or optional metadata. Their unmarked result is `None`, `nil`, or
`null`; the proposal's abstract model calls unattributed text `Voice0` without
adding a marker or assuming human origin.

Run checks from each package directory; see [Python](../../python/README.md),
[Ruby](../../ruby/README.md), and [JavaScript](../../js/README.md).
