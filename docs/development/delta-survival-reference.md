# Delta marked-text survival reference

This reference preserves the sample used to check variation-selector transport
through Delta 0.23.0 (recording contract 8) on one Mac during the
2026-11-01 session. It is test input, not an attribution history.

## Sample

The block below preserves the original four-line sample, including its final
LF newline. “Safe to delete” was part of the temporary probe's original text;
it is retained here so the sample bytes stay reproducible.

```text
TextProv survival sample for the Delta test, 2026-11-01. Safe to delete.
IVS: 辻󠄀 (U+8FBB U+E0100) 葛󠄀 (U+845B U+E0100) 葛󠄁 (U+845B U+E0101)
Marked ai: D󠄁e󠄁l󠄁t󠄁a󠄁 󠄁k󠄁e󠄁e󠄁p󠄁s󠄁 󠄁t󠄁h󠄁e󠄁s󠄁e󠄁 󠄁m󠄁a󠄁r󠄁k󠄁s󠄁
Marked human: a󠄀n󠄀d󠄀 󠄀t󠄀h󠄀e󠄀s󠄀e󠄀 󠄀t󠄀o󠄀o󠄀
```

Expected UTF-8 size: **360 bytes**. Expected SHA-256 of the block content,
excluding the fences:

```text
dfe36ced6474f01bf88db15ec44b7fabe3f2c4e8fbb091183e03725be0753180
```

The `ai` line places U+E0101 after every character, including spaces; the
`human` line does the same with U+E0100. These are synthetic labels from the
[experimental variation-selector profile](../encodings/vs.md), not verified
human or AI authorship. The IVS line exercises Japanese variation sequences
that must remain unchanged, despite sharing selectors with the experiment.

## Observed results

These results describe the earlier session, not checks rerun for this commit.

| Check | Observation | Scope |
| --- | --- | --- |
| File transport | The sample and four marked docs matched byte for byte in a fresh checkout mounted from DeltaDB. The original sample also remained unchanged. | Same Mac and local Delta replica only. |
| Transcript export | `thread show` and `thread watch` each returned 227 marks; four marked command-output lines matched their source files exactly. | Command output, not a user-typed prompt. |
| Plain-word search | Plain queries for “simultaneous” and “declared” missed marked text; queries including the marks found it. An unmarked control word was found. | `thread search --scope visible` against the earlier thread. |

The first probe used a `.txt` filename, which this repository ignores. It was
not imported into Delta. Renaming it to `.md` allowed the sample to sync.

Not tested: server round-trip or second-device byte identity, desktop and web
rendering and clipboard preservation, a marked user prompt, or an agent edit
that should preserve marks on untouched text. Storage preservation alone does
not establish those behaviors.

## Verify the preserved sample

Run from the repository root with Python 3. This checks the embedded sample,
not Delta transport:

```sh
python3 - <<'PY'
import hashlib
from pathlib import Path

reference = Path("docs/development/delta-survival-reference.md").read_bytes()
sample = reference.split(b"```text\n", 1)[1].split(b"```\n", 1)[0]
assert len(sample) == 360
assert hashlib.sha256(sample).hexdigest() == (
    "dfe36ced6474f01bf88db15ec44b7fabe3f2c4e8fbb091183e03725be0753180"
)
print("Sample preserved: 360 bytes; SHA-256 matches.")
PY
```
