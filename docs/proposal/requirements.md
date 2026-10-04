# Requirements for evaluation

Status: proposed requirements and acceptance criteria. No candidate is declared
to satisfy them in all applications.

## Goals

- Source attribution accompanies copied interior passages through plain-text workflows.
- Underlying Unicode text remains recoverable without losing legitimate content.
- Cooperating implementations agree on reference semantics and attachment.
- Encoding, display, interpretation, and authenticity remain distinct concerns.

## Non-goals

- Inferring authorship, detecting speakers, or detecting AI generation from text.
- Establishing identity, authenticity, or factual accuracy from a reference alone.
- Assigning Unicode characters without the standardization process.
- Guaranteeing preservation through software that removes or rewrites markers.

## Functional criteria

- Ordinary Unicode text with no recognized attribution is represented as
  `Voice0` without inserting markers or assuming human origin.
- `Voice0` represents absent attribution, not a common source. Anonymous sources
  with distinct references remain distinguishable from unattributed text.
- Extraction preserves original code points by default, including legitimate
  variation sequences, joiners, and unrelated private-use text.
- Recognition distinguishes protocol syntax from literal content under stated
  assumptions. Ambiguity for arbitrary input is explicit.
- Interior passage copying does not depend on distant document context under
  the profile's supported selection conditions.
- Copying and merging distinguish reference preservation from preservation of
  source distinctions and descriptions. The minimum guarantee remains open.
- Missing, malformed, conflicting, or unknown markers do not silently establish
  an attribution.
- Normalization is an explicit policy. Offset units and hash inputs identify
  the representation to which they apply.

## Qualities under evaluation

Unobtrusive fallback display, cluster attachment, cursor movement, shaping,
search, accessibility, storage overhead, and editing robustness are separate
criteria. Their priority and acceptable trade-offs remain [open](decisions.md).

## Evidence required for a profile decision

Application and platform versions accompany observations. Recorded input and
output code points establish transport preservation; screenshots establish
appearance only. Measurements distinguish default behavior from behavior with
a font, decoder, or editor integration. Counterexamples and unsupported paths
remain part of the result.
