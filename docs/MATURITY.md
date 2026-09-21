# TextProv maturity lifecycle

Maturity states what implementers can rely on. Contract and registry versions
identify the rules and allocations in use; a version number alone does not
establish maturity. Package versions and package publication do not promote the
protocol.

The stages are **Draft → Candidate → Stable**, with **Deprecated** as a
retirement status. The maintainer approves each promotion in a public decision
record. Passing tests or reaching a review deadline does not automatically
promote a release.

## Stages and promises

| Stage | Promise | Entry | Exit |
| --- | --- | --- | --- |
| Draft | Contract behavior may change incompatibly. Published registry allocations remain reserved. Implementers pin an immutable revision. | A published specification identifies scope, versions, and unresolved questions. | The Candidate checklist is satisfied and promotion is recorded. |
| Candidate | A specific revision is frozen for interoperability review. No new features; only corrections from review. | The Candidate checklist is satisfied and a review notice is published. | The Stable checklist is satisfied and promotion is recorded. |
| Stable | Required contract behavior is immutable. Compatible registry extensions follow the registry rules; incompatible behavior requires a new contract version. | The Stable checklist is satisfied and promotion is recorded. | The release remains Stable unless explicitly deprecated. A successor does not automatically retire it. |
| Deprecated | Not recommended for new integrations. Existing documents and allocations retain their meaning. | A notice records the reason, successor if any, migration guidance, and implementation-support plans. | Terminal status. Specifications, registries, and fixtures remain available. |

A Stable release cannot return to Draft or Candidate to withdraw its guarantees.
A successor begins its own lifecycle. Stable already freezes required behavior,
so there is no separate Frozen or Final stage.

## Draft to Candidate

Promotion requires all of the following:

- **Immutable snapshot.** The specification, registry, and fixtures are tied to
  one commit or immutable release tag. The record identifies both versions and
  the exact revision.
- **Defined scope.** Intended release scope is complete. There are no known
  release-blocking ambiguities or contradictory requirements in encoding,
  decoding, production, conversion, or markup.
- **Conformance evidence.** At least two reference implementations pass their
  applicable fixture suites against the snapshot. Producer properties and
  vendored-registry checks pass where applicable. The evidence identifies the
  implementation revisions, commands, environments, and results.
- **Compatibility review.** Registry growth, older-consumer behavior, and the
  conditions requiring a new contract version are documented. Adding a state
  is not assumed compatible merely because it appends a registry entry.
- **Explicit boundaries.** Unsupported behavior and platform-dependent limits
  are documented. Unicode segmentation has either a supported baseline or
  explicit permitted differences and conformance limits; agreement on fixtures
  alone is not evidence of general equivalence.
- **Review notice.** A public notice identifies the candidate revision, review
  deadline, feedback location, and deliberately deferred work.

A release blocker is a finding that prevents satisfaction of these criteria or
of the Stable checklist. Other findings may be deferred with a recorded reason.

## Candidate to Stable

Promotion requires all of the following:

- At least **30 consecutive calendar days** of public review without a change
  to required behavior. A behavior correction produces a new candidate and
  restarts the review period. Editorial corrections are recorded and do not
  restart it.
- Passing conformance, property, and vendored-registry checks for the final
  candidate snapshot, as applicable to each implementation.
- At least **one end-to-end integration** demonstrating production, storage or
  copying, decoding, and rendering in a named environment. Its report records
  where marks survive and where they do not. It does not claim universal
  copy-and-paste preservation.
- At least **one external interoperability exercise** in which someone other
  than the maintainer implements or integrates from the specification and
  reports results and ambiguities. Two maintainer-written implementations are
  cross-language evidence, not independent interpretation.
- No unresolved release blockers. Known non-blocking limitations and their
  disposition are recorded.
- A dated public promotion decision linking the evidence and identifying the
  guarantees taking effect.

Two independently developed implementations are not required. An external
exercise is required; elapsed time without external feedback is not a substitute.
There is no deadline by which a Candidate must become Stable.

## Registry guarantees at every stage

The [registry stability rules](../SPEC.md#stability-rules) apply from the first
publication of an allocation, including Draft and Candidate:

- Published selector and PUA code points are never reassigned or removed.
- Formula-reserved code points are not assigned a conflicting meaning.
- Abandoned allocations may be documented as obsolete, but remain reserved and
  documented with their original meanings.
- Additions increment the registry version and append entries only.

Draft flexibility applies to contract behavior, not reuse of published code
points. Deprecation does not erase allocations or reinterpret old text.

## Revisions and conformance claims

The live specification and registry describe the current draft; their URLs are
not pinned artifacts. Every release snapshot remains available by its exact
commit or immutable tag.

An implementation states the contract and registry versions it implements.
During Draft and Candidate, it also identifies the immutable revision used for
conformance. The version pair alone does not distinguish draft revisions whose
behavior differs. Release identifiers such as `v0.1-draft.3` and `v0.1-rc.1`
identify snapshots; these are examples, not claims that those releases exist.
No revision identifier is added to the in-band encoding by this policy.

Contract and registry versions advance independently, but promotion records
identify the exact pair reviewed together. Stable status for a contract does
not automatically endorse a future registry revision. A later registry release
records its compatibility with supported contracts and evidence for that claim;
new behavior follows the Candidate review process before being called Stable.

## Changes after Stable

- Editorial corrections clarify wording without changing required behavior.
- Added fixtures express existing requirements; they do not introduce new ones
  under an unchanged Stable contract version.
- Changes to required behavior need a new contract version, even when described
  as bug fixes. The previous Stable snapshot remains available.
- Compatible registry extensions preserve published meanings and follow the
  registry rules. An extension requiring incompatible consumer behavior also
  requires a new contract version.
- Package maintenance and support lifetimes are separate from protocol maturity.
  A deprecation notice states any implementation-support dates explicitly;
  protocol deprecation alone promises neither continued package maintenance nor
  a particular support window.

## Decision records

The maintainer records each promotion or deprecation in a repository document
or release notice that remains available with the release. Each record includes:

- Stage, decision date, and maintainer approval.
- Contract version, registry version, and immutable snapshot revision.
- Checklist evidence, including test results, review dates, and integration
  reports where required.
- Resolved blockers, deferred findings, and known limitations.
- Guarantees taking effect, or deprecation reasons and migration/support plans.

The [specification](../SPEC.md#versioning) states the current status and links
to this policy. A status edit without the required evidence and decision record
is not a promotion.
