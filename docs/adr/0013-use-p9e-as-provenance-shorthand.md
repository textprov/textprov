# 0013. Use p9e and P9E as provenance shorthand

Status: accepted (naming convention). Date: 2026-09-30.

Font artifact and consumer-name migration remains pending.

## Context

Provenance-enabled fonts use `P+` in their names. The demo font builders assign
families such as `Maryheather TextProv Demo P+`, and the website's local-font
lookups refer to those names. Earlier records use `P+` to describe this font
rendering path.

TextProv provides a shared structure, encoding, and vocabulary that
applications can use in different ways. Fonts primarily support development,
debugging, and demonstrations; applications can also inspect provenance on
demand or use decoded states internally, including in agent prompt
integrations. A compact shorthand for provenance can apply across those uses.

The shorthand follows the style of `i18n`, `l10n`, and `a11y`. The selected
spelling is `p9e`: a project-defined mnemonic for provenance inspired by that
style, rather than a literal count of the letters omitted from the word.

## Decision

Use `p9e` as the compact shorthand for provenance, and `P9E` as its uppercase
form in font suffixes and other display labels. The two spellings have the
same meaning. Use the full word when introducing the shorthand to readers.

`P9E` succeeds `P+` as the suffix convention for newly named
provenance-enabled font variants. For example, a rebuilt demo font can use
`Maryheather TextProv Demo P9E` where the existing artifact uses
`Maryheather TextProv Demo P+`.

TextProv remains the protocol name. Repository and package names, public APIs,
CLI options, CSS classes, data attributes, registry states, and code-point
allocations keep their established identities. The shorthand describes
provenance; it does not prescribe how an application presents or uses it.

### Transition from P+

Existing font artifacts retain the names embedded in them until they are
rebuilt. Installation instructions, source filenames, build inputs, and
local-font lookups continue to use the actual names of those artifacts.

A font rename coordinates the font's naming metadata, generated bundles and
manifests, consumer lookups, and installation instructions. Consumers that
support both generations can recognize the old and new family names during
the transition. Changing a documentation label alone does not rename an
installed font; users may need to select the new family after installing it.

Historical ADRs and test reports retain `P+` when referring to the artifacts
and behavior they recorded. New explanations introduce `p9e` or `P9E`, with
`P+` identified as the earlier font suffix where the distinction matters.

## Alternatives considered

- Retain `P+`: preserves familiarity with the existing font variants, but keeps
  the shorthand tied to that rendering path.
- Use only the full word `provenance`: remains useful for introductions and
  explanations, but does not provide a compact suffix or label.

## Consequences

- Applications and font tooling share a compact term for provenance while
  keeping TextProv as the protocol identity.
- The letters-and-digit spelling is suitable for compact names and labels.
- Existing readers need an explicit connection between `P+` and `P9E`.
- Because `p9e` is a chosen mnemonic, documentation defines its meaning rather
  than presenting it as a strict numeronym calculation.
- Font migration requires coordinated build and consumer updates; this record
  establishes the naming convention and records that remaining work.

## Relationship to earlier decisions

This record supplements [ADR 0006's naming decision](0006-decorator-packages-and-repository.md#naming)
with a provenance shorthand. It preserves that record's protocol and package
identities and [ADR 0012's npm naming policy](0012-npm-namespace.md).

[ADR 0011](0011-the-producer-is-text-processing.md) establishes that a font is
a renderer. The new shorthand also applies to uses beyond font rendering,
consistent with the specification's
[application use discussion](../../SPEC.md#application-use-non-normative).
