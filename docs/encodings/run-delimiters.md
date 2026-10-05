# Run-delimiter architecture

Status: architecture alternatives; no delimiter characters selected.

Inclusion records a design possibility, not a claim that an assigned character
already permits that use. Deprecated characters remain assigned with their
historical meaning; deprecation does not release them for private allocation.
A proposal can request reconsideration or new attribution semantics, with
compatibility evidence and a standards decision still needed.

Run syntax and code-point choice are separate decisions. A profile can define
paired delimiters, a prefix that sets state until changed, or repeated unit
references. Each needs a voice-reference payload; a begin/end pair alone carries
no source identity. Nested versus non-nested scope, paragraph boundaries, resets
to `Voice0`, and recovery from malformed input remain open. A copied interior
fragment may need newly synthesized delimiters or state to retain attribution.

## Private-use begin/end markers


Private agreement can define PUA begin/end markers, reference payloads, and
resets, as well as suffixes. This is a separate candidate from per-unit marking.
Ordinary Unicode processing does not automatically give such characters nesting,
attachment, invisibility, or word-boundary behavior. A profile needs recognition,
escaping, delimiter balancing, and rules for literal PUA text and partial copying.

Existing private registries or font assignments do not establish a universal PUA
word-bracketing protocol. This proposal makes no claim that ConScript, SIL, or
NLP pipelines share one. A specific precedent needs its own documented mapping,
license or agreement, and demonstrated behavior before serving as evidence.

Illustrative syntax is `TP_BEGIN(reference) + text + TP_END`. A stateful
alternative uses `TP_SET(reference) + text` until a new setting or reset.
These placeholders express structure without allocating code points.

## Musical begin/end precedent

Status: structural precedent and possible repurposing proposal, not an accepted
TextProv encoding. The four pairs are BEGIN/END BEAM, TIE, SLUR, and PHRASE;
they delimit musical notation. They are assigned
format controls and are **not deprecated** in Unicode 17. See
[Western musical symbols](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-21/)
and the [Deprecated property](https://www.unicode.org/Public/17.0.0/ucd/PropList.txt).

Their paired structure is relevant to run annotations, but their musical meaning
remains active. An attribution adaptation needs a reference payload, a means to
distinguish real musical notation, and a standards basis for changed semantics.
Default-ignorable display does not ensure retention by editors or sanitizers.
Evaluation includes genuine music, incomplete pairs, nesting, and interior copies.

## Deprecated stateful formatting toggles

Status: historical stateful precedent and possible revival proposal. The three
pairs are INHIBIT/ACTIVATE SYMMETRIC SWAPPING (`206A/206B`), INHIBIT/ACTIVATE
ARABIC FORM SHAPING (`206C/206D`), and NATIONAL/NOMINAL DIGIT SHAPES
(`206E/206F`). Unicode
retains them as deprecated characters; they have not been removed.

Their non-nesting on/off model suggests attribution state changes, rather than
balanced nested brackets. It still lacks voice-reference syntax. A proposed
adaptation needs rules for defaults, resets, legacy content, and receivers that
ignore or discard these controls. Their historical rendering purposes cannot
simply be presumed inert in every implementation. See
[Unicode section 23.3](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-23/).

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
