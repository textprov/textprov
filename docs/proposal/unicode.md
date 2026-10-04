# Possible Unicode proposal

Status: discussion draft, not a submitted or accepted Unicode proposal.

## Proposed subject

A possible submission concerns a general text-origin annotation function:
semantics, attachment, and processing behavior. TextProv supplies a motivating
application and experimental evidence. Code-point values and suggested placement
in Specials are separate allocation questions.

## Case to establish

The case needs a stable function, independent community use, and plain-text
interchange need. It explains why existing mechanisms and higher-level protocols
are insufficient. Unicode's [submission guidance](https://sew.unicode.org/guidelines)
identifies usage, stability, interchange need, and proposed properties. Meeting
those criteria does not guarantee acceptance. The appropriate review route for
a new annotation function also needs confirmation.

Desired invisibility and attachment require explicit property and algorithm
analysis. Rendering, grapheme and word boundaries, bidi, joining, normalization,
and older implementations each need treatment. A fixed label repertoire and a
general annotation structure remain alternatives.

## Experiments and allocation

PUA provides a legitimate private-agreement mechanism for an experiment. The VS
baseline supplies evidence about useful display and attachment as well as
collisions. A PUA experiment is not a prerequisite for submission.

Suggested unassigned values are not used as private markers before assignment.
Submission or preliminary approval does not create a standardized encoding.
Private allocations and final Unicode allocations remain distinct; any migration
is documented explicitly.

## Unresolved question

Whether provenance belongs in Unicode characters or higher-level annotation
protocols is part of the substantive case. Available code space alone does not
answer it.
