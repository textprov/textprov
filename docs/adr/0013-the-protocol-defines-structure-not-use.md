# 0013. The protocol defines structure and encoding; how labels are used is left open

Status: accepted. Date: 2026-09-30.

## Context

The consumers considered so far show labels to a person: spans, editor
decorations, a font. A second kind of consumer reads the labels itself, and
one case shows why that matters.

An operator's prompt to a model often mixes text they wrote with text copied
from model output: an earlier answer, another session, a generated plan. To
the model reading the prompt, all of it arrives as the operator's words. That
is a real problem. A model can end up treating its own earlier output as the
operator's instruction or as independent confirmation, and it has no basis
for weighing the two kinds of text differently when they conflict.

TextProv-encoded text gives the reader that basis. If copied model output
carries `ai` marks and the path preserves them, an agent or its harness can
tell the pasted passages from the operator's own writing. What it does next
is open. One option is weighting: for example, counting the operator's
unmarked text at 1.2 and `ai`-marked text at 0.9 when balancing a decision.
Others include attributing instructions to their source, or asking before
acting on a pasted plan.

Each of these needs integration work beyond the protocol, and none has been
tried. The realization prompted a review of the protocol's scope: should it
say how labels are to be used, or stay with structure and encoding?

## Decision

1. The protocol is a shared baseline. It defines the states, how they are
   encoded, and how they are decoded, so that every producer and consumer
   means the same thing by the same mark.
2. The protocol does not prescribe use. How a consumer acts on a state,
   including what it takes unmarked text to mean in its own context, is the
   consumer's to work out.
3. A program that reads labels is a consumer of decoder output like any
   other. The ordered `(state, text)` runs are the interface; no new role or
   decoder change is needed.
4. The in-band vocabulary stays kinds of origin
   ([ADR 0010](0010-contributor-identity-is-out-of-band.md)). It gains no
   entries that tell a reader what to do with the text.

## Reasons

- Agreement on structure is what makes different uses comparable. Two
  harnesses can weight `ai` text differently, or not weight it at all, and
  still exchange text and compare results, because the label says the same
  thing to both.
- The best use is not known yet. Fixing one in the specification would close
  off the experiments that would find it. A small, stable encoding leaves
  room to try weighting, attribution, review prompts, and uses nobody has
  thought of.
- Use depends on context the protocol cannot see: the model, the task, and
  what else the consumer knows about where text came from.
- This matches how the specification already treats producers and renderers.
  It does not say how a producer decides which state applies or how a
  renderer draws one. Consumers get the same freedom.

## Considerations for integrators

These are observations for anyone building this use, not requirements.

- The specification leaves the meaning of unmarked text to the consumer. A
  harness that reads unmarked text in a prompt as the operator's own is
  making that choice. It is worth knowing that text which was never marked
  and text whose marks were stripped look the same.
- A label is a claim
  ([cooperative standard](../development/voluntary-standards.md)). How much
  to rely on it depends on the path the text took.
- A selector is four bytes in UTF-8 and follows every marked cluster. A
  harness may prefer to decode and pass the runs to the model as structure
  rather than pass the raw selectors.
- The use depends on a producer at the model's output surface and on a copy
  path that preserves marks. Neither is established today.

## Consequences

- `SPEC.md` describes the consumer beside the roles and lists consumer
  behaviour under "Not specified". No algorithm, fixture, or registry entry
  changes, so the specification and registry versions stay 0.1.
- Uses can be built and compared in integrations without a specification
  change.
- If practice shows that consumers need a distinction the vocabulary lacks,
  and it is a kind of origin, it enters the registry as a state under the
  usual rules.

## Not measured

- Whether marks survive copying from a chat interface, pasting into a
  terminal or editor, and submission through a model API.
- The token cost of selector-encoded text under current tokenizers.
- Whether using labels this way improves a model's decisions.
