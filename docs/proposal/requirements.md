# Requirements for evaluation

Status: proposed requirements and acceptance criteria. No candidate is declared
to satisfy them in all applications.

## Goals

- Origin claims accompany copied interior passages through plain-text workflows.
- Underlying Unicode text remains recoverable without losing legitimate content.
- Cooperating implementations agree on label meanings and attachment.
- Encoding, display, interpretation, and authenticity remain distinct concerns.

## Non-goals

- Inferring authorship or detecting AI generation from text.
- Establishing authenticity or factual accuracy from a label alone.
- Assigning Unicode characters without the standardization process.
- Guaranteeing preservation through software that removes or rewrites markers.

## Functional criteria

- Extraction preserves original code points by default, including legitimate
  variation sequences, joiners, and unrelated private-use text.
- Recognition distinguishes protocol syntax from literal content under stated
  assumptions. Ambiguity for arbitrary input is explicit.
- Interior passage copying does not depend on distant document context under
  the profile's supported selection conditions.
- Missing, malformed, conflicting, or unknown markers do not silently establish
  an origin claim.
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
