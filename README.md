# TextProv: a proposal for voice attribution in text

TextProv explores how text can retain attribution to distinct voices when
passages are copied between applications, including through plain-text workflows.
A voice distinguishes a source within an attribution context: a person, software
system, quoted speaker, or another defined source.

**Status: proposal under discussion.** No permanent encoding is selected and no
new Unicode characters are assigned by this project. A variation-selector (VS)
demonstration illustrates one experimental mechanism, with known limitations.

## The idea

```text
TextUnit + VoiceReference → AttributedUnit
```

Here, `+` means association, not necessarily character concatenation. A text unit
may contain several Unicode characters. Attribution is supplied by a person or
application; it neither detects a speaker nor proves authorship.

`Voice1`, `Voice2`, and `Voice3` illustrate distinct sources, not reserved labels.
Several people or assistants can have distinct voices. Human/AI classification,
source descriptions, and verified identity are optional information separate
from the reference.

`Voice0` represents unattributed text, including ordinary Unicode text without
added markers. It implies no human/AI classification and no common source
identity. An anonymous source with a distinct reference differs from absent
attribution.

The central design objective is that a copied interior passage retains its
attribution without requiring every intermediate application to understand
TextProv. Reference scope, source-context portability, and the minimum copying
outcome remain open: `Voice1` in two unrelated documents need not identify the
same source. Display, editing, recognition, and interoperability require
separate evaluation.

## Read the proposal

| Document | Role |
| --- | --- |
| [Model](docs/model.md) | Semantics and abstract representation |
| [Requirements](docs/requirements.md) | Desired behavior and evaluation criteria |
| [Encoding candidates](docs/encodings/README.md) | Experimental VS, private-use, annotation, tag, run, and external options |
| [Open decisions](docs/decisions.md) | Choices and evidence needed |
| [Unicode proposal direction](docs/proposals/unicode.md) | Possible standardized function, properties, and allocation process |
| [Evaluation](docs/evaluation.md) | Historical observations, limitations, and planned measurements |

## Demonstration

The [homepage source](site/index.html) includes a provenance toggle for a
deliberately marked VS sample. Ordinary rendering generally shows the underlying
text without a special font; the toggle uses a decoder and CSS to expose the
sample's historical human/AI classifications. It does not implement voice
references, source dictionaries, or optional attribution metadata.

The VS experiment collides with legitimate Unicode variation sequences. Its
useful rendering and attachment properties are evidence to evaluate, not a
private Unicode namespace or a selected permanent encoding. See the
[experimental profile](docs/encodings/vs.md) and [recorded collision](docs/evaluation.md#variation-sequence-collision).

The website is generated from the proposal documents and contains the bounded
demonstration. Build instructions are in [site/README.md](site/README.md).

## Working SDK demonstrations

The [Python](python/README.md), [Ruby](ruby/README.md), and
[JavaScript](js/README.md) SDKs remain working experiments for the historical
human/AI classifications and limited replacement-PUA mode. Their guides include
checkout examples, APIs, and test commands. The homepage uses the JavaScript
SDK for its deliberately marked sample. These SDKs do not implement voice
references or define the proposal's eventual encoding.

For a Python example, run from the repository root:

```sh
PYTHONPATH=python python3 -c 'import textprov; marked = textprov.mark("hello", state="ai"); print(textprov.runs(marked)); assert textprov.strip_marks(marked) == "hello"'
```

Restrict decoding and stripping to intentional experiments: genuine variation
sequences can be misclassified or altered. [Baseline test data](experiments/baseline/README.md)
describes the executable experiment rather than proposal conformance.

## Project status and license

This proposal has an independent Git history. No permanent encoding or proposal
conformance specification is selected; working SDKs demonstrate the earlier
experimental profile.

Project code is MIT licensed; see [LICENSE](LICENSE). Retained third-party data
or code carry their own notices alongside the relevant files.
