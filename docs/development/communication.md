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

## Experiments with programmatic consumers

[S󠄁P󠄁E󠄁C󠄁.󠄁m󠄁d󠄁](../../SPEC.md#application-use-non-normative) l󠄁e󠄁a󠄁v󠄁e󠄁s󠄁 a󠄁p󠄁p󠄁l󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁
p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁 t󠄁o󠄁 c󠄁o󠄁n󠄁s󠄁u󠄁m󠄁e󠄁r󠄁s󠄁.󠄁 A󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 h󠄁a󠄁r󠄁n󠄁e󠄁s󠄁s󠄁 c󠄁o󠄁u󠄁l󠄁d󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁 c󠄁o󠄁p󠄁i󠄁e󠄁d󠄁 A󠄁I󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁 a󠄁n󠄁d󠄁 u󠄁s󠄁e󠄁
t󠄁h󠄁e󠄁 r󠄁e󠄁s󠄁u󠄁l󠄁t󠄁i󠄁n󠄁g󠄁 r󠄁u󠄁n󠄁s󠄁 f󠄁o󠄁r󠄁 a󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 w󠄁e󠄁i󠄁g󠄁h󠄁t󠄁i󠄁n󠄁g󠄁,󠄁 o󠄁r󠄁 r󠄁e󠄁v󠄁i󠄁e󠄁w󠄁 p󠄁r󠄁o󠄁m󠄁p󠄁t󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁s󠄁e󠄁 a󠄁r󠄁e󠄁
i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 i󠄁d󠄁e󠄁a󠄁s󠄁,󠄁 n󠄁o󠄁t󠄁 d󠄁e󠄁m󠄁o󠄁n󠄁s󠄁t󠄁r󠄁a󠄁t󠄁e󠄁d󠄁 b󠄁e󠄁n󠄁e󠄁f󠄁i󠄁t󠄁s󠄁.󠄁

B󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 m󠄁a󠄁k󠄁i󠄁n󠄁g󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁s󠄁 a󠄁b󠄁o󠄁u󠄁t󠄁 s󠄁u󠄁c󠄁h󠄁 a󠄁n󠄁 i󠄁n󠄁t󠄁e󠄁g󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁,󠄁 m󠄁e󠄁a󠄁s󠄁u󠄁r󠄁e󠄁:󠄁

- W󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 s󠄁u󠄁r󠄁v󠄁i󠄁v󠄁e󠄁 c󠄁o󠄁p󠄁y󠄁i󠄁n󠄁g󠄁 f󠄁r󠄁o󠄁m󠄁 a󠄁 c󠄁h󠄁a󠄁t󠄁 i󠄁n󠄁t󠄁e󠄁r󠄁f󠄁a󠄁c󠄁e󠄁,󠄁 p󠄁a󠄁s󠄁t󠄁i󠄁n󠄁g󠄁 i󠄁n󠄁t󠄁o󠄁 a󠄁 t󠄁e󠄁r󠄁m󠄁i󠄁n󠄁a󠄁l󠄁
  o󠄁r󠄁 e󠄁d󠄁i󠄁t󠄁o󠄁r󠄁,󠄁 a󠄁n󠄁d󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 a󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 A󠄁P󠄁I󠄁.󠄁
- T󠄁h󠄁e󠄁 t󠄁o󠄁k󠄁e󠄁n󠄁 c󠄁o󠄁s󠄁t󠄁 o󠄁f󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁-󠄁e󠄁n󠄁c󠄁o󠄁d󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 c󠄁o󠄁m󠄁p󠄁a󠄁r󠄁e󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁d󠄁 r󠄁u󠄁n󠄁s󠄁 s󠄁u󠄁p󠄁p󠄁l󠄁i󠄁e󠄁d󠄁
  a󠄁s󠄁 s󠄁t󠄁r󠄁u󠄁c󠄁t󠄁u󠄁r󠄁e󠄁.󠄁
- W󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁e󠄁 c󠄁h󠄁o󠄁s󠄁e󠄁n󠄁 p󠄁o󠄁l󠄁i󠄁c󠄁y󠄁 i󠄁m󠄁p󠄁r󠄁o󠄁v󠄁e󠄁s󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 d󠄁e󠄁c󠄁i󠄁s󠄁i󠄁o󠄁n󠄁s󠄁.󠄁

T󠄁h󠄁e󠄁 w󠄁o󠄁r󠄁k󠄁f󠄁l󠄁o󠄁w󠄁 n󠄁e󠄁e󠄁d󠄁s󠄁 a󠄁 p󠄁r󠄁o󠄁d󠄁u󠄁c󠄁e󠄁r󠄁 a󠄁t󠄁 t󠄁h󠄁e󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁 s󠄁u󠄁r󠄁f󠄁a󠄁c󠄁e󠄁 a󠄁n󠄁d󠄁 a󠄁 p󠄁a󠄁t󠄁h󠄁 t󠄁h󠄁a󠄁t󠄁 p󠄁r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁s󠄁
m󠄁a󠄁r󠄁k󠄁s󠄁.󠄁 U󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 c󠄁a󠄁n󠄁 a󠄁l󠄁s󠄁o󠄁 b󠄁e󠄁 t󠄁e󠄁x󠄁t󠄁 w󠄁h󠄁o󠄁s󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁s󠄁 w󠄁e󠄁r󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁p󠄁p󠄁e󠄁d󠄁,󠄁 s󠄁o󠄁 t󠄁r󠄁e󠄁a󠄁t󠄁i󠄁n󠄁g󠄁
i󠄁t󠄁 a󠄁s󠄁 o󠄁p󠄁e󠄁r󠄁a󠄁t󠄁o󠄁r󠄁-󠄁w󠄁r󠄁i󠄁t󠄁t󠄁e󠄁n󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁s󠄁 a󠄁 s󠄁e󠄁p󠄁a󠄁r󠄁a󠄁t󠄁e󠄁 l󠄁o󠄁c󠄁a󠄁l󠄁 a󠄁s󠄁s󠄁u󠄁m󠄁p󠄁t󠄁i󠄁o󠄁n󠄁.󠄁 A󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 u󠄁s󠄁e󠄁s󠄁
f󠄁o󠄁u󠄁r󠄁 b󠄁y󠄁t󠄁e󠄁s󠄁 i󠄁n󠄁 U󠄁T󠄁F󠄁-󠄁8󠄁 p󠄁e󠄁r󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁;󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁 b󠄁e󠄁f󠄁o󠄁r󠄁e󠄁 m󠄁o󠄁d󠄁e󠄁l󠄁 s󠄁u󠄁b󠄁m󠄁i󠄁s󠄁s󠄁i󠄁o󠄁n󠄁 i󠄁s󠄁
o󠄁n󠄁e󠄁 o󠄁p󠄁t󠄁i󠄁o󠄁n󠄁 t󠄁o󠄁 e󠄁v󠄁a󠄁l󠄁u󠄁a󠄁t󠄁e󠄁.󠄁

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
