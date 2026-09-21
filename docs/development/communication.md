# Communicating about TextProv

This guide keeps project documentation, package metadata, and user interfaces
consistent about what TextProv does and does not establish.

## Core description

Use this definition when space permits:

> TextProv is an opt-in protocol for carrying producer-declared origin states in
> Unicode text. Participating tools can add, preserve, decode, and display states
> such as `human`, `ai`, and `mixed`.
>
> A TextProv mark records what a producer declares; it does not prove who wrote
> the text or how it was created. Anyone can add, remove, or change a mark.
> Unmarked text means only that no TextProv declaration is present.

For a shorter description:

> TextProv is an opt-in protocol for keeping origin declarations in Unicode
> text. It does not detect or verify where text came from.

Use this concise statement when explaining the trust boundary:

> **TextProv standardizes the transport of origin declarations; it does not
> verify those declarations.**

## Package summary

Use the existing package-registry summary:

> **Label AI output down to the character, directly in ordinary Unicode text.**

This summary describes the primary operation without claiming detection or
verification. Pair it with the trust-boundary sentence in longer package
listings and introductory documentation.

## Explain the lifecycle

Use this model to show where responsibility lies:

```text
integration decides → producer marks → transport preserves → consumer interprets
```

TextProv standardizes the encoding and decoding mechanics. It does not
standardize:

- how an integration decides which state applies;
- whether a producer's declaration is honest or correct;
- whether intermediate systems preserve a mark;
- whether a consumer trusts or acts on a declaration.

Keep these concepts separate:

- **Conforming mark:** encoded according to the TextProv specification.
- **Declared state:** the state assigned by the producer.
- **Accurate declaration:** a factual assessment outside the protocol.
- **Authenticated declaration:** a declaration protected by an external
  authentication mechanism.

A false declaration can still be conformingly encoded.

## Preferred terminology

Prefer:

- producer-declared state
- origin declaration
- origin label
- in-band annotation
- cooperative protocol
- participating producer
- participating consumer
- add, preserve, decode, or display a mark
- conforming encoding

Avoid or qualify:

- carries its own provenance
- knows where it came from
- says whether a human or machine wrote it
- detects AI-generated text
- verified provenance
- authentic
- trusted
- proof
- survives copy and paste

Instead of an unconditional survival claim, say:

> Marks can pass through Unicode-preserving copy, paste, and plain-text storage.

This wording accounts for sanitizers, normalization, unsupported software, and
deliberate removal.

## Describe marked and unmarked text

Use language that reports a declaration without endorsing it:

- `Producer-declared: AI`
- `Marked as AI-generated`
- `Declared human`
- `No TextProv declaration`

Do not say:

- `AI detected`
- `Verified human`
- `Authentic`
- `Trusted source`

Unmarked text does not default to `human`. An explicit `unknown` state is also
different from no mark: one is a declaration and the other is the absence of a
declaration.

A mark does not express a judgment about the text's quality, accuracy, safety,
or trustworthiness. Do not use shields, verification checkmarks, or
security-badge styling unless a separate system provides the corresponding
security property.

If an authenticated container is available, display the two dimensions
separately:

```text
Declared state: AI
Declaration authentication: not available
```

Do not collapse origin state and authentication into one status.

## Position TextProv alongside other standards

### `robots.txt`

[RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html) states that its rules are
not access authorization. The comparison is useful because both protocols
coordinate cooperating participants without preventing non-cooperation.

Do not overextend the analogy: crawler preferences and origin declarations have
different uses and risks. The shared point is the protocol boundary, not an
identical threat model.

### SPDX

[SPDX license expressions](https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/)
provide identifiers, syntax, and parsing rules for licensing declarations. A
valid expression does not itself prove that the declared license applies.
TextProv similarly standardizes vocabulary and encoding rather than factual
correctness.

### C2PA

[C2PA](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)
distinguishes assertions, signed claims, validation, and trust decisions.
TextProv implements only an in-band annotation layer and can coexist with a
system that provides stronger guarantees.

| Capability | TextProv | C2PA |
| --- | --- | --- |
| Origin assertions | Yes | Yes |
| Content binding | No | Yes |
| Signing credential | No | Yes |
| Digital signatures | No | Yes |
| Tamper evidence | No | Yes |
| Trust decision | Consumer-defined | Consumer-defined from validation and policy |

A signed document or authenticated transport may protect text containing
TextProv marks. That external system authenticates the document or sender;
TextProv remains the annotation format. A copied passage does not retain the
source document's authenticated status merely because its marks remain.

### W3C PROV

[W3C PROV](https://www.w3.org/TR/prov-overview/) represents information that can
support assessments of quality, reliability, or trustworthiness. TextProv is
narrower: it has no agents, activities, derivation graph, contributor identity,
or complete history. Describe it as an **in-band origin-annotation protocol**
when that distinction matters.

## Documentation order

Introduce TextProv in this order:

1. One-sentence definition.
2. Immediate declaration-not-proof boundary.
3. A concrete use case.
4. Cooperative lifecycle.
5. What the protocol standardizes.
6. What it does not establish.
7. Encoding and implementation details.
8. Relationship to authenticated provenance systems.

This order lets a new reader understand the purpose and trust boundary before
encountering Unicode or rendering details.
