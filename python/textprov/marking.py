"""Automatic chat classification and AI document edits.

Chat classification follows the speaker selected by the host. Existing marks
always survive; ordinary editor changes receive no marks from these functions
unless a caller explicitly submits them as an AI document edit.
"""

import json
import sys

from ._encode import mark
from .editing import remark


def _text(value):
    if not isinstance(value, str):
        raise ValueError("text must be a string")
    return value


def mark_chat(text, role):
    """Mark unmarked user chat human or assistant chat AI, preserving marks.

    This is a speaker policy, not an inference about pasted text's authorship.
    Code and Markdown receive the same chat classification as other text.
    """
    if role not in ("user", "assistant"):
        raise ValueError("chat role must be user or assistant")
    return mark(_text(text), state="human" if role == "user" else "ai")


def mark_document(text):
    """Mark new AI document prose, preserving supplied marks and Markdown code."""
    return mark_document_edit("", text)


def mark_document_edit(old_text, new_text):
    """Mark AI additions and replacements, carrying unchanged source marks.

    Uses the existing whole-line/whole-word editing alignment. Existing marks
    in supplied new passages survive. Unchanged raw text is carried from the
    original even when the writer omitted its selectors. Markdown syntax and
    code are protected by the same conservative rules as other document edits.
    No prompt matching or manual claims are required.
    """
    return remark(_text(old_text), _text(new_text), markdown=True,
                  carry=True, shingles=set(), preserve_new_marks=True)


def main(argv=None):
    """Read one JSON request and return its marked text for host adapters."""
    try:
        if argv:
            raise ValueError("supply the request as JSON on stdin")
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError("request must be an object")
        operation = request.get("operation")
        if operation == "mark-chat":
            result = mark_chat(request["text"], request["role"])
        elif operation == "mark-document":
            result = mark_document_edit(request.get("old_text", ""), request["text"])
        else:
            raise ValueError("operation must be mark-chat or mark-document")
        print(json.dumps({"text": result}, ensure_ascii=False))
        return 0
    except (KeyError, ValueError, TypeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
