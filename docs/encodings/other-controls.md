# Other controls and Unicode areas

## Bidirectional scope controls

Status: comparison candidate with active layout effects. `U+2066 LRI`,
`U+2067 RLI`, and `U+2068 FSI` open isolates terminated by `U+2069 PDI`.
The older embeddings and overrides (`U+202A–U+202E`) use `U+202C PDF`.
These families have distinct scope rules; PDF and PDI are not interchangeable.
Their semantics and boundary handling are defined by
[UAX #9](https://www.unicode.org/reports/tr9/).

They scope directional processing, not source attribution. A TextProv convention
would require an additional reference encoding and recognition scheme. It could
change punctuation placement, ordering, and surrounding text even when all
controls are invisible. Genuine bidi controls must survive extraction. Evaluation
includes mixed Arabic/Hebrew/Latin text, nested isolates, unmatched controls,
paragraph boundaries, and copying into a different directional context.

## Other areas considered

These areas do not supply a private annotation namespace. Assignment status and
encoding validity are separate from suitability for attribution.

| Area | Range or characters | Role and TextProv assessment |
| --- | --- | --- |
| Surrogates | `U+D800–U+DFFF` | UTF-16 surrogate code units encode supplementary scalars in pairs. Surrogates are not Unicode scalar values; lone surrogates are not valid Unicode interchange. Exclude as attribution characters. |
| Noncharacters | `U+FDD0–U+FDEF` and the last two values of each plane, including `U+FFFE/U+FFFF` | Permanently reserved, valid scalar values; their occurrence does not itself make Unicode encoding ill-formed. Useful as internal sentinels, without assigned textual meaning. They do not provide standardized public attribution semantics or PUA agreement. |
| BOM | `U+FEFF` | Marks encoding/byte order at stream boundaries; word joiner is strongly preferred for its older zero-width no-break-space use. Processing may consume it. Exclude as a generic attribution marker. |
| Specials reserved positions | Unassigned values in `U+FFF0–U+FFFF` | Reserved for assignment, not private use. A proposal may request new semantics and properties; exact placement is a separate allocation decision. See [annotations](annotations.md). |
| Interlinear annotations | `U+FFF9–U+FFFB` | Existing base/annotation structure; considered separately in the [annotation candidate](annotations.md), with receiver agreement and fallback limitations. |
| Object replacement | `U+FFFC` | Represents an embedded object in text. It does not inherently delimit attribution or carry a voice reference; object/protocol use would require explicit application conventions. |
| Replacement character | `U+FFFD` | Substitutes for unknown or unrepresentable input, including decoding errors. Using it as attribution would conflate errors and metadata; exclude as a marker. |
| Tags | Assigned tags in `U+E0000–U+E007F` | Current emoji-tag use and deprecated language-tagging precedent are evaluated in [tag candidates](tags.md); neither is a general private namespace. |

See [Unicode sections 23.6–23.9](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/)
and [Unicode conformance](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-3/).


See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
