"""TextProv: read in-band text provenance marks and render them as markup.

    >>> import textprov
    >>> textprov.to_html("f\U000E0101")
    '<span class="prov prov-ai" data-prov="ai">f\U000E0101</span>'

The protocol is defined in SPEC.md; `mapping.json` is the code-point registry.
This package is the decoder and renderer only. Adding marks to text is the
producer's job, not this package's.
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

__all__ = [
    "CONTRACT_VERSION",
    "GENERATED_STATES",
    "RESERVED_STATES",
    "Mapping",
    "cluster_end",
    "default_mapping",
    "is_combining",
    "load_mapping",
    "runs",
    "strip_marks",
    "to_html",
]

__version__ = "0.1.0"
