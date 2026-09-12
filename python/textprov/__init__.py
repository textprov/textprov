"""TextProv: put provenance marks in text, and read them back out.

    >>> import textprov
    >>> textprov.to_html("f\U000E0101")
    '<span class="prov prov-ai" data-prov="ai">f\U000E0101</span>'

    >>> textprov.mark("hi", state="ai") == "h\U000E0101i\U000E0101"
    True

The protocol is defined in SPEC.md; `mapping.json` is the code-point registry.
Marking text needs the registry and nothing else, so the producer lives here
too: `mark`, `mark_added`, and `convert`. Rendering marks in a *font* is a
separate job and needs a font toolchain; that producer-side renderer is the
`--provenance` option of the Nerd Fonts fork.
"""

from ._core import (
    CONTRACT_VERSION,
    GENERATED_STATES,
    RESERVED_STATES,
    Mapping,
    cluster_end,
    default_mapping,
    is_combining,
    load_mapping,
    runs,
    strip_marks,
    to_html,
)
from ._encode import convert, inspect, mark, mark_added

__all__ = [
    "CONTRACT_VERSION",
    "GENERATED_STATES",
    "RESERVED_STATES",
    "Mapping",
    "cluster_end",
    "convert",
    "default_mapping",
    "inspect",
    "is_combining",
    "load_mapping",
    "mark",
    "mark_added",
    "runs",
    "strip_marks",
    "to_html",
]

__version__ = "0.1.0"
