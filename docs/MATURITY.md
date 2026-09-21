# TextProv maturity lifecycle

Maturity defines what implementers can rely on. Contract and registry versions
identify the rules and allocations in use, but do not establish maturity.
Publishing a package also does not promote the protocol.

The lifecycle is **Draft → Candidate → Stable**. **Deprecated** is a retirement
status. Every promotion or deprecation requires a public maintainer decision;
tests and elapsed review time do not cause promotion automatically.

## Stages

| Stage | Guarantee |
| --- | --- |
| Draft | Contract behavior may change incompatibly. Published registry allocations remain reserved. Implementers must pin an immutable revision. |
| Candidate | One revision is frozen for interoperability review. Only review-driven corrections are allowed. |
| Stable | Required contract behavior is immutable. Incompatible changes require a new contract version. |
| Deprecated | The release is not recommended for new integrations, but existing documents and allocations keep their meaning. Specifications, registries, and fixtures remain available. |

A Stable release cannot return to Draft or Candidate. A successor starts its own
lifecycle and does not automatically deprecate an earlier release.

## Draft to Candidate

Promotion requires:

- An immutable commit or release tag covering the specification, registry, and
  fixtures, with the contract and registry versions recorded.
- Complete release scope, with no known blocking ambiguities or contradictions.
- At least two reference implementations passing applicable fixture, producer,
  and vendored-registry checks. Evidence records revisions, commands,
  environments, and results.
- Documented compatibility effects for registry growth, older consumers, and
  changes that require a new contract version.
- Documented unsupported behavior and platform limits. Unicode segmentation
  must define a baseline or permitted differences and conformance limits.
- A public notice identifying the candidate revision, review deadline, feedback
  location, and deferred work.

A release blocker prevents one of these requirements or a Stable requirement
from being met. Other findings may be deferred with a recorded reason.

## Candidate to Stable

Promotion requires:

- At least **30 consecutive calendar days** of public review with no change to
  required behavior. A behavior change creates a new candidate and restarts the
  review period; recorded editorial changes do not.
- Passing applicable conformance, property, and vendored-registry checks for the
  final candidate.
- One end-to-end integration covering production, storage or copying, decoding,
  and rendering in a named environment. Its report records where marks survive
  and where they do not.
- One interoperability exercise by someone other than the maintainer, with
  reported results and ambiguities. Two maintainer-written implementations do
  not satisfy this requirement.
- No unresolved release blockers, plus a record of non-blocking limitations.
- A dated public decision linking the evidence and stating the guarantees that
  take effect.

Independently developed implementations are not required, but external review
is. A Candidate has no deadline for promotion.

## Registry guarantees

The [registry stability rules](../SPEC.md#stability-rules) apply from an
allocation's first publication:

- Published selector and PUA code points are never removed or reassigned.
- Formula-reserved code points never receive conflicting meanings.
- Obsolete allocations remain reserved with their original meanings.
- Additions append entries and increment the registry version.

Draft flexibility applies to contract behavior, not published allocations.
Deprecation does not erase allocations or reinterpret existing text.

## Revisions and conformance

Live specification and registry URLs are not pinned artifacts. Each release
snapshot must remain available by exact commit or immutable tag.

An implementation states its contract and registry versions. During Draft and
Candidate, it also states the immutable revision tested. Contract and registry
versions advance independently, and each promotion records the exact pair
reviewed together.

A Stable contract does not automatically endorse later registry revisions.
Those revisions must document compatibility and evidence. New behavior must
complete Candidate review before it is called Stable.

## Changes after Stable

- Editorial changes may clarify but not alter required behavior.
- New fixtures may express only existing requirements.
- Any required behavior change needs a new contract version, including a bug
  fix that changes behavior. The previous Stable snapshot remains available.
- Compatible registry extensions preserve published meanings. Extensions that
  require incompatible consumer behavior also need a new contract version.
- Package maintenance and support periods are separate from protocol maturity.
  A deprecation notice must state any support dates explicitly.

## Decision records

Each promotion or deprecation record must remain available with the release and
include:

- The stage, date, and maintainer approval.
- Contract and registry versions and the immutable revision.
- Required evidence, including tests, review dates, and integration reports.
- Resolved blockers, deferred findings, and known limitations.
- The guarantees taking effect, or the reason for deprecation and any successor,
  migration guidance, and support plan.

The [specification](../SPEC.md#versioning) states the current status and links
to this policy. Changing that status without the required evidence and decision
record is not a promotion.
