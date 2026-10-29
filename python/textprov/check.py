"""Forward-only provenance checks using document syntax protection profiles.

Correspondence infers retained text, not authorship. Singleton moves and
cumulative edits retain the documented ambiguities of the docs-site checker.
Syntax profiles are heuristics; this module does not validate document ASTs.
"""

from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher

from ._core import GENERATED_STATES, default_mapping, strip_marks
from ._encode import mark
from ._grapheme import segments
from .syntax import resolve_profile

MAPPING = default_mapping()
STATES = {value: key for key, value in MAPPING.selectors.items()}
# Smallest move threshold that excludes the reported one-cluster coincidence
# while still checking mark changes on two-cluster moves. Not a confidence score
# or a minimum for primary equal runs; see docs/TEXTPROV.md alignment limitations.
MIN_MOVE_CLUSTERS = 2


@dataclass
class Cluster:
    start: int
    end: int
    raw: str
    text: str
    state: str


def clusters(source):
    """Keep original encodings alongside offsets in the unmarked source."""
    result = []
    offset = 0
    for raw in segments(source):
        plain = strip_marks(raw)
        state = STATES.get(ord(raw[-1]))
        if len(raw) == 1 and ord(raw) in MAPPING.pua2base:
            state = MAPPING.pua2base[ord(raw)][1]
        result.append(Cluster(offset, offset + len(plain), raw, plain, state))
        offset += len(plain)
    return result


def correspondence(old, new):
    """Infer correspondence, not authorship, ignoring reflow whitespace.

    Exact encodings anchor the primary alignment; visible-text alignment in
    the gaps can pair even one coincidental cluster. A minimum there would
    also discard retained legacy bytes or hide changes to existing marks.
    Unique exact unmatched blocks are then paired as moves: mark changes are
    checked only at MIN_MOVE_CLUSTERS or above, while shorter blocks must keep
    identical bytes. Short moves and cumulative edits remain ambiguous; see
    docs/TEXTPROV.md for examples, historical exceptions, and follow-up scope.
    """
    a = [
        i for i, item in enumerate(old) if item.text and not item.text.isspace()
    ]
    b = [
        i for i, item in enumerate(new) if item.text and not item.text.isspace()
    ]
    # Prefer exact preserved encodings as anchors. Otherwise inserting an AI
    # copy before an identical human-labelled passage looks like relabelling.
    anchors = SequenceMatcher(
        None, [old[i].raw for i in a], [new[i].raw for i in b], autojunk=False
    )
    matches = {}
    old_gaps = defaultdict(list)
    new_gaps = defaultdict(list)

    def align(tag, i, j, k, l):
        if tag == "equal":
            # Keep singleton survivors (including their original encoding).
            # The unmatched-move threshold is unsafe for these primary runs.
            matches.update(zip(b[k:l], a[i:j]))
        else:
            if i < j:
                old_gaps[tuple(old[n].text for n in a[i:j])].append(a[i:j])
            if k < l:
                new_gaps[tuple(new[n].text for n in b[k:l])].append(b[k:l])

    for tag, i, j, k, l in anchors.get_opcodes():
        if tag == "equal":
            align(tag, i, j, k, l)
            continue
        visible = SequenceMatcher(
            None,
            [old[n].text for n in a[i:j]],
            [new[n].text for n in b[k:l]],
            autojunk=False,
        )
        for subtag, x, y, z, w in visible.get_opcodes():
            align(subtag, i + x, i + y, k + z, k + w)
    for key, old_blocks in old_gaps.items():
        new_blocks = new_gaps.get(key, [])
        if len(old_blocks) != 1 or len(new_blocks) != 1:
            continue
        pairs = list(zip(new_blocks[0], old_blocks[0]))
        # One cluster does not identify a passage: the y removed from "życia"
        # and the y written in "pomocy?" are a coincidence, not a move. Pair a
        # shorter block only when that keeps its exact bytes, so it can retain
        # legacy text but never report a relabelled or lost mark.
        if len(key) >= MIN_MOVE_CLUSTERS or all(
            new[n].raw == old[o].raw for n, o in pairs
        ):
            matches.update(pairs)
    return matches


def eligible(item, offsets):
    return (
        bool(item.text)
        and not item.text.isspace()
        and all(offset in offsets for offset in range(item.start, item.end))
    )


def check_text(before, after, *, profile="markdown", require_marks=True):
    """Return (line, column, message) problems at unmarked code-point offsets.

    Locations are one-based. Existing encodings must survive correspondence;
    removing marks from protected syntax is allowed as a repair. New prose
    requires one supported selector, unless require_marks is false, which
    allows unmarked/unsupported-origin prose but still rejects malformed new
    supported marks and changes to corresponding existing encodings.
    """
    old, new = clusters(before), clusters(after)
    matches = correspondence(old, new)
    plain = strip_marks(after)
    flags = list(resolve_profile(profile)(plain))
    if len(flags) != len(plain) or any(
        type(flag) is not bool for flag in flags
    ):
        raise ValueError("profile must return one bool per text code point")
    offsets = {
        offset for offset, protected in enumerate(flags) if not protected
    }
    problems = []
    for index, item in enumerate(new):
        message = None
        if index in matches:
            original = old[matches[index]]
            # Removing a mark from syntax (an aside fence, say) repairs it.
            repaired = (
                original.state
                and item.state is None
                and not eligible(item, offsets)
            )
            if original.raw != item.raw and not repaired:
                message = (
                    "changed or lost an existing mark"
                    if original.state
                    else "marked unchanged legacy text"
                )
        elif eligible(item, offsets):
            if item.state not in GENERATED_STATES:
                if require_marks:
                    message = "new prose cluster has no supported origin mark"
            elif item.raw != mark(item.text, state=item.state):
                message = "new prose cluster must have one selector mark"
        elif item.state or not item.text:
            message = (
                "new mark is outside eligible prose or attached to whitespace"
            )
        if message:
            line = plain.count("\n", 0, item.start) + 1
            column = item.start - plain.rfind("\n", 0, item.start)
            problems.append((line, column, message))
    return problems
