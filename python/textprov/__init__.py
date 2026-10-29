# python/textprov/__init__.py

"""TextProv: put provenance marks in text, and read them back out.

    >>> import textprov
    >>> textprov.to_html("f\U000e0101", display="exact")
    '<span class="prov prov-ai" data-prov="ai">f\U000e0101</span>'

    >>> textprov.mark("hi", state="ai") == "h\U000e0101i\U000e0101"
    True

This package implements the experimental VS/classification and replacement-PUA
baseline. Its mapping does not allocate characters for the voice-attribution
proposal. See experiments/baseline/README.md and python/README.md.
"""

from ._core import (
    GENERATED_STATES,
    SPEC_VERSION,
    UNICODE_VERSION,
    Mapping,
    default_mapping,
    load_mapping,
    runs,
    segments,
    strip_marks,
    to_html,
)
from ._display import display_version, stylesheet
from ._encode import convert, inspect, mark, mark_added

__all__ = [
    "GENERATED_STATES",
    "SPEC_VERSION",
    "UNICODE_VERSION",
    "Mapping",
    "check_text",
    "clusters",
    "convert",
    "correspondence",
    "default_mapping",
    "inspect",
    "load_mapping",
    "mark",
    "mark_added",
    "mark_chat",
    "mark_chat_parts",
    "mark_document",
    "mark_document_edit",
    "runs",
    "segments",
    "strip_marks",
    "display_version",
    "stylesheet",
    "to_html",
]

from ._version import __version__


def mark_chat(text, role, scope="prose"):
    """Apply the chat speaker policy at the selected scope, preserving marks."""
    from .marking import mark_chat as operation

    return operation(text, role, scope=scope)


def mark_chat_parts(parts, role, scope="prose"):
    """Mark complete chat text across parts, retaining their original boundaries."""
    from .marking import mark_chat_parts as operation

    return operation(parts, role, scope=scope)


def mark_document(text, profile="markdown"):
    """Mark new AI document prose while preserving marks and protected syntax."""
    from .marking import mark_document as operation

    return operation(text, profile=profile)


def mark_document_edit(old_text, new_text, profile="markdown"):
    """Mark AI document changes and carry unchanged existing marks."""
    from .marking import mark_document_edit as operation

    return operation(old_text, new_text, profile=profile)


def clusters(source):
    """Return graphemes with original encodings, states, and unmarked offsets."""
    from .check import clusters as operation

    return operation(source)


def correspondence(old, new):
    """Map new cluster indices to old ones using preservation correspondence."""
    from .check import correspondence as operation

    return operation(old, new)


def check_text(before, after, *, profile="markdown", require_marks=True):
    """Check preservation and new prose coverage at one-based text locations."""
    from .check import check_text as operation

    return operation(
        before, after, profile=profile, require_marks=require_marks
    )
