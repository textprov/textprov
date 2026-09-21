# TextProv as a cooperative standard

TextProv is an opt-in protocol. It gives participating tools a shared way to
encode, preserve, decode, and display origin declarations in Unicode text. It
does not force a producer to add a label, an intermediary to preserve one, or a
consumer to trust one.

This is a design boundary, not an omitted enforcement feature:

> TextProv standardizes the transport of origin declarations; it does not verify
> those declarations.

## What cooperation means

A TextProv workflow has four independent steps:

```text
integration decides → producer marks → transport preserves → consumer interprets
```

The protocol defines how a producer encodes a state and how a consumer decodes
it. It does not establish:

- how the integration chose the state;
- whether the declaration is honest or accurate;
- whether intermediate software preserved every mark;
- whether the consumer should trust or act on the declaration.

A false declaration can be correctly encoded. A valid decoder can report that
declaration without endorsing it.

## Marks are data, not verdicts

A mark can be useful without being authoritative. A consumer may display it,
include it in an audit log, or use it in a workflow whose participants have
agreed on how labels are assigned. Decoding establishes only which declaration
is present.

The protocol itself assigns no evidentiary weight to a marked state:

- `human` is not proof that a person wrote the text;
- `ai` is not the result of AI detection;
- an absent mark is not evidence of human authorship;
- a mark says nothing about quality, accuracy, or trustworthiness.

Applications may present marked and unmarked text differently, but any decision
that depends on accurate authorship needs evidence outside TextProv. The source
and handling of a declaration determine its credibility, not its code point.

TextProv marks are closer to in-band annotations than to security credentials.
Their rendering can resemble styling, but the marks carry machine-readable
states even when no visual style is applied.

## Why an advisory protocol can still help

Many common standards create value by making intent or metadata interoperable
without proving that the declaration is true:

- [`robots.txt`](https://www.rfc-editor.org/rfc/rfc9309.html) declares crawler
  preferences but is not access control.
- A canonical link declares a preferred URL; a consumer can accept or ignore it.
- [SPDX license expressions](https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/)
  standardize licensing declarations without proving that a license applies.
- Semantic Versioning standardizes how maintainers communicate compatibility;
  the version number cannot enforce compatible behavior.
- RSS and Atom let publishers expose feeds that participating readers can
  discover and consume.

These conventions are useful because honest participants benefit from a small,
shared vocabulary and predictable processing. TextProv makes the same trade:
low adoption cost and portability among cooperating tools, without enforcement.

## Stripping and false declarations

Any text processor can add, remove, or change a TextProv mark. This creates two
expected failure modes:

1. **Stripping:** a mark is removed deliberately or by software that does not
   preserve the relevant Unicode code points.
2. **False declaration:** a producer encodes a state that does not describe the
   actual workflow.

TextProv does not attempt to distinguish either case from an accurate
cooperative declaration. In particular, unmarked text remains unmarked; a
consumer must not silently reinterpret it as `human`.

This limitation reduces the protocol's suitability for adversarial decisions,
but it does not remove its value in cooperative editing, disclosure, and data
processing workflows.

## Relationship to authenticated provenance

Cryptographic provenance systems can bind claims to content, identify a signer,
and provide tamper evidence. TextProv does none of those things. It addresses a
narrower problem: keeping local origin states attached to character sequences.

The approaches can be combined. A signed document or authenticated transport
may protect text that contains TextProv marks. The surrounding system
authenticates the document or sender; TextProv remains the annotation format.
A copied passage does not inherit the original document's authenticated status
merely because its TextProv marks remain.

See the [protocol specification](../../SPEC.md) for normative behavior and the
[communication guide](communication.md) for language that preserves this trust
boundary.
