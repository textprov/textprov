# Communicating about TextProv

This guide keeps project documentation, package metadata, and user interfaces
consistent about what TextProv does and does not establish.

## Core description

Use this definition when space permits:

> TextProv is an opt-in protocol for carrying producer-declared origin states in
> Unicode p󠄁r󠄁o󠄁s󠄁e󠄁. Participating tools can add, preserve, decode, and display states
> `human` a󠄁n󠄁d󠄁 `ai`.󠄁
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

## Marking scope

D󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁 T󠄁e󠄁x󠄁t󠄁P󠄁r󠄁o󠄁v󠄁 a󠄁s󠄁 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 c󠄁o󠄁m󠄁m󠄁u󠄁n󠄁i󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 p󠄁e󠄁o󠄁p󠄁l󠄁e󠄁.󠄁 S󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁
f󠄁i󠄁l󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁 e󠄁x󠄁c󠄁l󠄁u󠄁d󠄁e󠄁d󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁i󠄁r󠄁 e󠄁n󠄁t󠄁i󠄁r󠄁e󠄁t󠄁y󠄁,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁s󠄁,󠄁 d󠄁o󠄁c󠄁s󠄁t󠄁r󠄁i󠄁n󠄁g󠄁s󠄁,󠄁 a󠄁n󠄁d󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁
p󠄁r󠄁o󠄁s󠄁e󠄁 i󠄁n󠄁s󠄁i󠄁d󠄁e󠄁 t󠄁h󠄁e󠄁m󠄁.󠄁 A󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁e󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 d󠄁e󠄁v󠄁e󠄁l󠄁o󠄁p󠄁m󠄁e󠄁n󠄁t󠄁 w󠄁o󠄁r󠄁k󠄁f󠄁l󠄁o󠄁w󠄁s󠄁 a󠄁n󠄁d󠄁
v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 c󠄁o󠄁n󠄁t󠄁r󠄁o󠄁l󠄁.󠄁

C󠄁o󠄁d󠄁e󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁s󠄁 c󠄁a󠄁r󠄁r󠄁i󠄁e󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁i󠄁n󠄁 p󠄁r󠄁o󠄁s󠄁e󠄁 m󠄁a󠄁y󠄁 b󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁;󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁r󠄁e󠄁 n󠄁o󠄁t󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁d󠄁
t󠄁o󠄁 m󠄁a󠄁r󠄁k󠄁 t󠄁h󠄁e󠄁m󠄁.󠄁 K󠄁e󠄁e󠄁p󠄁 t󠄁h󠄁e󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁i󠄁o󠄁n󠄁 b󠄁e󠄁t󠄁w󠄁e󠄁e󠄁n󠄁 a󠄁 s󠄁n󠄁i󠄁p󠄁p󠄁e󠄁t󠄁'󠄁s󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁e󠄁d󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 a󠄁n󠄁d󠄁 i󠄁t󠄁s󠄁
s󠄁u󠄁i󠄁t󠄁a󠄁b󠄁i󠄁l󠄁i󠄁t󠄁y󠄁 f󠄁o󠄁r󠄁 d󠄁i󠄁r󠄁e󠄁c󠄁t󠄁 e󠄁x󠄁e󠄁c󠄁u󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 m󠄁e󠄁a󠄁n󠄁 h󠄁u󠄁m󠄁a󠄁n󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁.󠄁

T󠄁h󠄁e󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁e󠄁r󠄁 p󠄁r󠄁o󠄁c󠄁e󠄁s󠄁s󠄁e󠄁s󠄁 t󠄁e󠄁x󠄁t󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 r󠄁e󠄁c󠄁o󠄁g󠄁n󠄁i󠄁z󠄁i󠄁n󠄁g󠄁 l󠄁a󠄁n󠄁g󠄁u󠄁a󠄁g󠄁e󠄁s󠄁,󠄁 f󠄁i󠄁l󠄁e󠄁 r󠄁o󠄁l󠄁e󠄁s󠄁,󠄁 o󠄁r󠄁 s󠄁y󠄁n󠄁t󠄁a󠄁x󠄁.󠄁
A󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁s󠄁 e󠄁l󠄁i󠄁g󠄁i󠄁b󠄁l󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁e󠄁n󠄁t󠄁 b󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 i󠄁t󠄁.󠄁 D󠄁o󠄁 n󠄁o󠄁t󠄁 p󠄁r󠄁e󠄁s󠄁e󠄁n󠄁t󠄁
c󠄁o󠄁m󠄁m󠄁e󠄁n󠄁t󠄁-󠄁o󠄁n󠄁l󠄁y󠄁 o󠄁r󠄁 s󠄁t󠄁r󠄁i󠄁n󠄁g󠄁-󠄁o󠄁n󠄁l󠄁y󠄁 m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 a󠄁s󠄁 a󠄁n󠄁 e󠄁x󠄁c󠄁e󠄁p󠄁t󠄁i󠄁o󠄁n󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 s󠄁o󠄁u󠄁r󠄁c󠄁e󠄁-󠄁f󠄁i󠄁l󠄁e󠄁 b󠄁o󠄁u󠄁n󠄁d󠄁a󠄁r󠄁y󠄁.󠄁
S󠄁e󠄁e󠄁 t󠄁h󠄁e󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁'󠄁s󠄁 [m󠄁a󠄁r󠄁k󠄁i󠄁n󠄁g󠄁 s󠄁c󠄁o󠄁p󠄁e󠄁](../../SPEC.md#marking-scope).󠄁

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

Unmarked text does not default to `human`. O󠄁n󠄁l󠄁y󠄁 `human` a󠄁n󠄁d󠄁 `ai` a󠄁r󠄁e󠄁 d󠄁e󠄁f󠄁i󠄁n󠄁e󠄁d󠄁;󠄁
n󠄁o󠄁 m󠄁a󠄁r󠄁k󠄁 m󠄁e󠄁a󠄁n󠄁s󠄁 t󠄁h󠄁e󠄁 a󠄁b󠄁s󠄁e󠄁n󠄁c󠄁e󠄁 o󠄁f󠄁 a󠄁n󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 d󠄁e󠄁c󠄁l󠄁a󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 n󠄁o󠄁t󠄁 a󠄁 t󠄁h󠄁i󠄁r󠄁d󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁.󠄁

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
