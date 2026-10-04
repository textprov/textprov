# TextProv: a proposal for voice attribution in text

TextProv explores how text can retain attribution to distinct voices when
passages are copied between applications, including through plain-text workflows.
A voice identifies a source within an attribution context: a person, software
system, quoted speaker, or another defined source. The proposal separates
attribution meaning from the mechanism used to encode it.

**Status: proposal under discussion.** No permanent encoding is selected and no
new Unicode characters are assigned by this project. The retained
variation-selector (VS) implementation is an experimental demonstration.

## The idea

```text
TextUnit + VoiceReference → AttributedUnit
```

Here, `+` means association, not necessarily character concatenation. A text unit
may contain several Unicode characters. Attribution is supplied by a person or
application; it neither detects a speaker nor proves authorship.

Illustrative voices might be `Voice1` for an author, `Voice2` for a quoted
participant, and `Voice3` for an assistant. These are example references, not
reserved labels. `Voice0` represents unattributed text, including ordinary
Unicode text without added markers. It implies no human/AI classification and
no common source identity. Multiple people or assistants can have distinct voices.
Human/AI classification, source descriptions, and verified identity are optional
information separate from the attribution reference.

The central design objective is that a copied interior passage retains its
attribution without requiring every intermediate application to understand
TextProv. Reference scope and the portability of source descriptions remain
open: `Voice1` from two unrelated documents need not identify the same source.
Whether an encoding meets that objective with acceptable display, editing,
and interoperability remains a question for evaluation.

## Read the proposal

| Document | Role |
| --- | --- |
| [Model](docs/proposal/model.md) | Concept, semantics, and abstract representation |
| [Requirements](docs/proposal/requirements.md) | Desired outcomes and evaluation criteria |
| [Encoding candidates](docs/proposal/encodings.md) | VS, additive PUA, annotations, and new-character proposals |
| [Open decisions](docs/proposal/decisions.md) | Choices, evidence needed, and decision status |
| [Unicode proposal direction](docs/proposal/unicode.md) | Possible standardization request, separate from private experiments |
| [Demonstration and evaluation](docs/proposal/demonstration.md) | Existing implementation, limitations, and measurement plan |

These documents define the proposal framing. Existing specifications, mappings,
fixtures, architecture records, and package documentation describe the retained
experimental baseline. Their implementation choices and compatibility statements
do not settle the proposal's open decisions.

## Existing demonstration

The VS demonstration stores labels in text that ordinary renderers generally
display without a special font. A TextProv decoder interprets or displays the
baseline human/AI classifications. It does not implement the proposed voice
references. Copying and editing depend on the application and preservation of
the marked sequence.

The VS profile has a documented collision with legitimate Unicode variation
sequences. Its display and attachment behavior are useful experimental evidence;
they do not establish a private Unicode namespace or permanent encoding.
See the [encoding assessment](docs/development/encoding-recommendation.md).

Retained code: [Python](python/README.md), [Ruby](ruby/README.md),
[JavaScript](js/README.md), and [website source](site/README.md).
The [baseline specification](SPEC.md), [mapping](mapping.json), and
[fixtures](fixtures.json) describe the experiment. The website and generated
specification pages retain the baseline presentation; they have not been
rewritten as the proposal.

## Branch provenance

This proposal starts a separate Git history. The demonstration snapshot comes
from commit `466e82cd7037fe2c8b3984ff0144e68492a09e7c`; that commit is a documentary
reference, not a parent of this branch. Earlier history remains on existing
repository branches.

## License

Project code is MIT licensed; see [LICENSE](LICENSE). Bundled fonts retain their
own licenses, including the SIL Open Font License 1.1. See the
[font licensing guide](docs/FONT-UTILITIES.md#licensing-and-attribution).
