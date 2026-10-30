"""The optional reveal stylesheet distributed with the package."""

from importlib.resources import files
import re

_VERSION_PROPERTY = re.compile(r'--prov-display-version:\s*"([^"]+)"')


def stylesheet():
    """Return the shared gradient-mist and dotted-underline CSS as UTF-8 text."""
    return files(__package__).joinpath("textprov.css").read_text(encoding="utf-8")


def display_version():
    """Return the reveal treatment version, ``v<spec version>-<family>``.

    The value is read from the first ``--prov-display-version`` in the
    packaged stylesheet, which is the single source for it; a candidate
    version declares its own value only inside rules gated on the
    ``data-prov-display-version`` root attribute. The prefix is the spec
    (proposal) version the treatment was designed against: not the ``0.2``
    baseline experiment identifier in :data:`SPEC_VERSION` and not this
    package's version. The family names the visual model. The scheme is
    described in docs/development/display-versions.md.
    """
    match = _VERSION_PROPERTY.search(stylesheet())
    if match is None:
        raise ValueError("packaged stylesheet declares no --prov-display-version")
    return match.group(1)


def display_family():
    """Return the family part of :func:`display_version`."""
    return display_version().rsplit("-", 1)[1]
