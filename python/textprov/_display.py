"""The optional reveal stylesheet distributed with the package."""

from importlib.resources import files
import re

_VERSION_PROPERTY = re.compile(r'--prov-display-version:\s*"([^"]+)"')


def stylesheet():
    """Return the shared gradient-mist and dotted-underline CSS as UTF-8 text."""
    return files(__package__).joinpath("textprov.css").read_text(encoding="utf-8")


def display_version():
    """Return the reveal treatment version, ``YYYY-MM-DD.family``.

    The value is read from ``--prov-display-version`` in the packaged
    stylesheet, which is the single source for it. The scheme is described in
    docs/development/display-versions.md.
    """
    match = _VERSION_PROPERTY.search(stylesheet())
    if match is None:
        raise ValueError("packaged stylesheet declares no --prov-display-version")
    return match.group(1)
