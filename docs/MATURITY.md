# TextProv maturity lifecycle

Each maturity stage defines the compatibility guarantees for a revision. The
maintainer changes its status through a short public release note using the
criteria below.

## Stages

| Stage | Guarantee |
| --- | --- |
| Draft | Specification behavior may change incompatibly. Pin an exact commit or immutable release tag. |
| Candidate | A revision is frozen for public review. It may be promoted, revised, or withdrawn to Draft. |
| Stable | Required specification behavior is immutable. Behavior changes require a new specification version. |
| Deprecated | Not recommended for new integrations. Existing documents and allocations keep their meaning. |

Published allocations remain protected at every stage under the
[registry stability rules](../SPEC.md#stability-rules).

## Promotion

**Draft → Candidate:**

- Pin the specification, registry, and fixtures to an exact commit or immutable
  tag, recording both specification and registry versions.
- Have one maintained implementation passing applicable fixture, producer, and
  vendored-registry checks.
- Resolve blocking ambiguities; document compatibility effects and known limits,
  including Unicode segmentation behavior.
- Announce the revision, feedback location, and review deadline.

**Candidate → Stable:**

- Allow at least **30 consecutive calendar days** of public review. Required
  behavior changes restart review; editorial corrections do not.
- Have one maintained implementation passing applicable conformance, property,
  and vendored-registry checks for the final revision.
- Resolve release blockers; record deferred findings and known limitations.

The qualifying implementation may be maintained by the specification's author.
External implementations and integration reports are optional. Record any
available external results; otherwise state that independent interoperability
is unverified.

At the review deadline, the maintainer chooses whether to promote, revise,
extend review with a new date, or withdraw. The release note records the date,
outcome, versions, revision, and links to test results and remaining limitations.

## Compatibility and retirement

- Implementations state their specification and registry versions, plus the tested
  revision during Draft and Candidate. Release snapshots remain available.
- Stable releases cannot return to Draft or Candidate. Required behavior changes,
  including bug fixes, need a new specification version and Candidate review.
- Editorial changes and new fixtures may clarify only existing requirements.
  Treat uncertain or disputed changes as behavioral.
- Registry versions advance independently. Additions preserve published meanings
  and document compatibility and test evidence; incompatible consumer behavior
  also requires a new specification version. Stable status applies to the registry
  revision reviewed for that release.
- Deprecation requires a notice for the release being retired, explaining the
  reason, any replacement, migration guidance, and support dates. Specifications,
  registries, and fixtures remain available. Package support is tracked separately
  from protocol maturity.

The [specification](../SPEC.md#versioning) states the current status.
