# Genesis

Textprov began with a recurring frustration: technical work was being governed by text whose provenance had become unclear. Claims were repeated as established facts, tentative choices were treated as settled policy, and decisions about shipping were allowed to block the experiments needed to make those decisions.

The immediate trigger was the phrase **“security promise.”** It was used to justify a design choice during work with Claude Fable. When challenged, the phrase had no authoritative source.

> Where did the term “security promise” come from?

Nowhere real. ADR-0013 said only that compaction **“bounds locally reconstructible deleted content”** and that, with peers, the honest claim is **“this device forgot and asked its peers to do the same.”** It said nothing about rungs or a promise that history was “bounded by one rung.”

That latter phrase first appeared in commit `ba11581` on 2026-08-28, *Rework ADR-0025 to argue where history dies*. It was placed in quotation marks as though it referred to an existing claim, then argued against. An agent copied it into a delivery note, and it was repeated again as “today’s security promise.” Through repetition, an unsupported phrase acquired the appearance of provenance.

The correction removed all three occurrences from ADR-0025 and restored the actual language of ADR-0013:

- Compaction bounds locally reconstructible deleted content.
- A block’s history never outlives its page, never survives a shed, and never crosses a key frame to another device.
- Ratification must state that bound directly and amend ADR-0013 in its Decision section.

The concrete design question could then be asked without the invented premise: should a page forget its edit history at expiry, deletion, a deliberate shed, the size budget, and the sync ceremony—or at every rung change and hold top-up?

## The broader failure

The invented “security promise” was the straw that broke the camel’s back, but it was not the only problem. The same failure mode appeared in planning work.

A plan turned too many **conditions for shipping** into **conditions for starting**. An ADR said thresholds should be chosen **“before freezing the adapter.”** That was interpreted as *before implementing the adapter*. Those are not the same requirement. An evaluation implementation was needed to produce the measurements that could settle the thresholds.

Several distinctions had been lost:

- **Evaluation was confused with release.** Dependency review, licensing, UI policy, and corpus evaluation were serialized even though synthetic or public inputs could be used before processing user text or distributing the feature.
- **The riskiest surface set the burden for every surface.** Automatic paste carried greater false-positive and editing risks than a user-requested language suggestion, but its requirements were allowed to delay learning whether the shared detection gate worked at all.
- **Proposals were presented as unanswered questions.** Default-off behavior, strict UTF-8 handling, and uncolored unsupported labels were concrete provisional choices. They could bound an experiment without being mistaken for final release policy.
- **Avoiding persistence was mistaken for resolving product intent.** A session-only rendering choice may simplify implementation, but forgetting a deliberately selected language still requires an argument when the product tenets say a document should reopen in the state in which it was left.

The right next step was not another policy meeting. It was an executable, non-shipping experiment: evaluate against the recorded registry artifact, use synthetic or public text, keep thresholds configurable, retain ranked results, and measure precision, useful-code coverage, confusion cases, and local resource costs. Those results could then inform the production adapter and the surfaces safe enough to ship.

## Why textprov

These incidents shared a root problem: the text no longer made clear what was sourced, inferred, proposed, decided, or still unknown. Once those categories blurred, unsupported language could become a premise and unresolved policy could become a false prerequisite.

Textprov came from the conviction that there had to be a better way to work with evolving technical text—one that preserves where claims came from, keeps provisional choices visibly provisional, and distinguishes **“start measuring now”** from **“approved to ship.”**

The originating Claude conversation is preserved in [this artifact](https://claude.ai/code/artifact/b39b6c4c-0e7b-4dbb-9e28-d9f1c7ab5acb).
