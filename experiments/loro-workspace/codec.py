"""One-request bridge to the checkout's codec; no Chronicle or user configuration."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
from textprov import default_mapping, mark_chat, mark_document_edit, runs, segments


def decode(text):
    mapping = default_mapping()
    tokens = []
    for raw in segments(text):
        state, visible = runs(raw, strip=True, merge_whitespace=False)[0]
        # The experimental profile is explicit. Unsupported/stray selectors and
        # ambiguous multiple marks are refused rather than erased or guessed.
        selectors = [c for c in raw if 0xE0100 <= ord(c) <= 0xE01EF]
        if selectors and (len(selectors) != 1 or state is None or
                          ord(selectors[0]) not in mapping.selectors.values()):
            raise ValueError("unsupported, stray, or conflicting provenance selector")
        if any(0x100000 <= ord(c) <= 0x10FFFD and ord(c) not in mapping.pua2base for c in raw):
            raise ValueError("unsupported replacement-PUA character")
        if any(0xD800 <= ord(c) <= 0xDFFF for c in raw):
            raise ValueError("unpaired Unicode surrogate")
        tokens.append(dict(raw=raw, visible=visible, state=state))
    # Adjacent runs must form complete graphemes in the decoded editor text.
    if list(segments("".join(t["visible"] for t in tokens))) != [t["visible"] for t in tokens]:
        raise ValueError("attribution boundary splits a visible grapheme")
    return tokens


def operate(request):
    operation = request["operation"]
    if operation == "decode":
        return decode(request["text"])
    if operation == "edit":
        before, inserted, after = (request[k] for k in ("before", "inserted", "after"))
        # Validate even input that would be replaced, and pasted input, before
        # applying policy. Nothing is inferred from a Loro peer ID.
        for text in (before, request["removed"], inserted, after):
            decode(text)
        actor, destination = request["actor"], request["destination"]
        if actor not in ("human", "assistant") or destination not in ("chat", "draft"):
            raise ValueError("actor must be human/assistant and destination chat/draft")
        proposed = before + inserted + after
        if destination == "chat":
            proposed = before + mark_chat(inserted, "user" if actor == "human" else "assistant") + after
        elif actor == "assistant":
            proposed = mark_document_edit(before + request["removed"] + after, proposed)
        return decode(proposed)
    raise ValueError("unknown boundary operation")


if __name__ == "__main__":
    try:
        print(json.dumps({"result": operate(json.load(sys.stdin))}, ensure_ascii=True))
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
