# Reclamation plan for the TextProv proposal branch

Status: implementation plan, prepared for review. Repository deletion, site
replacement, publication, and Discussion updates have not been performed.

## Intended result

The active tree presents one coherent proposal for voice attribution. It contains
its model, desired behavior, encoding alternatives, open decisions, evidence, and
working SDK demonstrations. The SDKs retain their reserved package identities
and implemented experimental behavior; they do not define the proposal or settle
its open choices. The former v0.2 specification is removed.

`Voice0` remains unattributed ordinary Unicode text. Nonzero voices distinguish
sources; human/AI classification is optional metadata. No encoding, reference
scope, allocation, or copying guarantee becomes settled through this cleanup.
Musical controls provide a precedent for explicit begin/end scope; their musical
code points need not be adopted to evaluate that structure. These musical
controls are not deprecated.

Three read-only subagent audits informed this plan: repository content and
evidence, site dependencies, and GitHub Discussions. The coordinating review
resolves their findings into the target below.

## Target tree

```text
README.md                         Concept, status, reading order, demonstration
LICENSE
.gitignore
.github/workflows/checks.yml      Proposal links, site build, demo checks
.github/workflows/pages.yml       Deliberate site publication

docs/model.md                     Semantics and abstract representation
docs/requirements.md              Desired behavior and evaluation criteria
docs/decisions.md                 Open choices; established Voice0 decision
docs/evaluation.md                Observations, limitations, evaluation plan
docs/encodings/README.md          Candidate comparison and status
docs/encodings/vs.md              Bounded current experiment and collision
docs/encodings/additive-pua.md    Private suffix and reference-payload options
docs/encodings/annotations.md     Interlinear base/annotation structure
docs/encodings/tags.md            Modern tags and historical language tagging
docs/encodings/run-delimiters.md  Paired versus stateful scope; musical precedent
docs/encodings/other-controls.md  Bidi, ZWJ, combining marks, excluded areas
docs/proposals/unicode.md         Possible standardized mechanism

site/index.html                  Proposal introduction and homepage toggle
site/proposal.template.html      Full proposal presentation
site/build-proposal.js           Renders canonical proposal Markdown
site/app.js                      Homepage initialization
site/provenance.js               Toggle controller
site/styles.css
site/demo/                       Marked samples and site-specific demo tests
site/package.json
site/package-lock.json
site/vite.config.js
site/README.md

python/                          Working Python SDK demonstration
ruby/                            Working Ruby SDK demonstration
js/                              Working JavaScript SDK and site renderer
experiments/baseline/                  Current demo mapping, shared fixtures, notes
ucd/                             Segmentation data needed by SDK demonstrations
tools/gen_grapheme_tables.py      Reproducible shared SDK table generation
```

The tree is a responsibility map, not a requirement to create each file exactly
as named. Tests and notices accompany retained code. `site/proposal.html` is a
generated build artifact. Python, Ruby, and JavaScript remain working examples
with their reserved package names and package metadata. The site imports the
JavaScript SDK rather than copying its runtime into a second implementation.
Shared experimental mappings and fixtures live under `experiments/baseline/`; SDK tests
and generation tools are updated to those paths. External metadata and newly standardized characters remain visible
in the candidate index and relevant linked documents.

This plan is a temporary coordination artifact. Its completion record can live
in the implementing task or commit description; it does not need to become a
permanent additional proposal guide.

## Content disposition

| Existing content | Action | Destination or reason |
| --- | --- | --- |
| `README.md` | Rewrite | Reading order and status; replace normative spec onboarding with concise SDK demo links; remove obsolete site caveats |
| `docs/proposal/model.md`, `requirements.md`, `decisions.md` | Move and edit links | Flatter `docs/` layout; retain agreed semantics and explicit open choices |
| `docs/proposal/encodings.md` | Split and reconcile | Candidate index plus focused documents; preserve alternatives without duplicating their full explanations |
| `docs/proposal/unicode.md` | Move | `docs/proposals/unicode.md` |
| `docs/proposal/demonstration.md` | Rewrite | `docs/evaluation.md`: distinguish observations from future measurements |
| `docs/adr/**`, `docs/development/**` | Extract selected evidence, then remove | Previous implementation decisions and operational advice do not govern the proposal |
| `docs/GOAL.md`, `MATURITY.md`, `SELECTORS-PUA-AND-INTERCHANGE.md`, `HTML-RENDERING.md`, `FONT-UTILITIES.md` | Extract selected evidence, then remove | Consolidate relevant substance; avoid parallel goals, maturity rules, and obsolete integration guides |
| `SPEC.md`, `CHANGELOG.md`, `genesis.md` | Remove | Historical material remains in previous revisions; necessary implemented rules are documented as experiments |
| `mapping.json`, `fixtures.json` | Relocate and reframe | `experiments/baseline/`; working SDK data and shared behavioral checks, not the proposal registry or conformance definition |
| `python/**`, `ruby/**`, `js/**` | Retain and reframe | Working SDK demos; keep package identities, code, necessary data, tests and licenses; rewrite READMEs and comments to explain experimental scope |
| `.claude/**`, `site/.claude` | Remove first | Automatic hooks inject old classifications and hidden selectors into new prose |
| `tools/gen_grapheme_tables.py`, `ucd/**` | Retain required sources and tooling | SDK demonstrations need reproducible segmentation tables; update moved-data paths and preserve source/version/notices |
| Other `tools/**`, `site/public/fonts/**` | Remove by default | Keep only a demonstrated SDK/evaluation dependency; font downloads and font builders are unnecessary for the homepage toggle |
| `.github/workflows/conformance.yml` | Replace | Checks validate proposal links, site, and working SDK demos; experimental behavioral agreement does not certify the proposal |
| `.gitignore`, `.gitattributes`, remaining configuration | Simplify | Retain SDK build/cache rules and remove unused font/tool rules; preserve notices and rules still needed |

No `archive/` subtree copies the obsolete repository into the active proposal.
Before removal, record verified immutable source revisions for historical links.
The former snapshot is `466e82cd7037fe2c8b3984ff0144e68492a09e7c`; the proposal
snapshot before reclamation is `40bcd4b`. Verify remote reachability before using
GitHub links to either revision. Cleanup does not require rewriting or
force-pushing Git history or choosing a new default branch.

## Evidence extraction before removal

| Evidence | Source | Preserve | Limit |
| --- | --- | --- | --- |
| Legitimate IVS decoded as attribution | `docs/development/encoding-recommendation.md` | `U+8FBB U+E0100`, reported `human` result, selector loss on stripping, tested revision and source citation | Historical observed failure; reproduce separately in the retained runtime before claiming the same execution result there |
| Browser rendering and selection | `docs/HTML-RENDERING.md` | 2026-09-11 system-font Chromium/WebKit measurements, sample, versions, selection counts | Selection strings, not a physical clipboard round-trip; scratchpad prototype, not fresh verification of packages |
| Editing and search lessons | `docs/development/dogfooding*.md`, related operational notes | Relevant reported effects of hidden marks, rewriting, attribution inference, token overhead, exact searching | Motivate evaluation; do not convert anecdotal reports into universal guarantees |
| General design constraints | ADRs 0002, 0009, 0010, 0014, 0017 | Code-point preservation during decoration, display/storage distinction, source reference versus identity, malformed input, segmentation version | Carry missing substance only; do not revive old decisions as binding choices |
| Font/shaper observations | Font and interchange guides | Only a concise comparison if it materially explains a current candidate trade-off | Distinguish earlier CoreText/format-14 results from rebuilt utility fonts; no font suite retained solely to preserve history |

`docs/evaluation.md` records known results with source revision, date, sample,
method, input/output code points where available, and limitations. The HTML
rendering guide says find-in-page was not measured, while ADR 0002 reports a
Chromium/WebKit `window.find('fork')` check and an absent-string control. Preserve
that conflict until the revision, method, and tested artifact are reconciled;
neither account establishes a physical clipboard round-trip. ADR 0009's editor
decoration option is unimplemented, not an observed result. Proposed
application tests occupy a separate section. Evidence unavailable in the
repository is explicitly identified; missing details are not invented.

## Working SDK demonstrations

Retain Python, Ruby, and JavaScript in their existing package directories,
including reserved package names, manifests, entry points, implemented features,
required data, licenses, and meaningful tests. Package versions describe the
executable experiments, not a versioned proposal standard. The cleanup does not
publish new packages or invent implementations of the voice-reference model.

Rewrite each SDK README to lead with its working-demo status, show a runnable
example, identify the implemented VS/classification and replacement-PUA behavior,
and link to the model, candidate profiles, and known collision. Remove claims
that the former specification governs the proposal. Implemented generation or
mapping rules may remain documented as experimental behavior when needed to use
the code; they are not reserved allocations or requirements of the proposal.

Keep shared fixtures and mapping data as explicit experiment assets. Update
Python/Ruby/JS checks, copied mappings, generation scripts, and relative references
together. Retain tests for implemented behavior and Unicode segmentation; remove
or rewrite tests tied to deleted automatic hooks and obsolete publication pages.
CI continues to run the SDK suites and checks shared data agreement, naming that
scope explicitly. No old URL, API, or file-path compatibility is required by this
reclamation plan; changes are guided by coherent working examples.

## Site reclamation

The homepage leads with the proposal and its unresolved choices, explains voices
and `Voice0`, and offers a short demonstration. The primary navigation contains
one GitHub repository link. Proposal details appear through content links and a
full proposal page generated from the canonical Markdown, rather than through a
second independently maintained specification.

The existing provenance toggle moves beside the homepage heading. It controls a
clearly identified, deliberately marked VS sample. Its legend names the actual
historical labels decoded by that implementation. It does not relabel those
states as implemented voice references or automatically classify newly written
proposal prose. Remove the separate homepage reveal controller so one toggle
owns display state.

The toggle needs `provenance.js`, its control markup, a marked
`[data-prov-document]` region, and the appropriate CSS. Without a region the
controller hides the button. Move useful legend styles from `spec.css` and scope
demo decoration to the sample. Ordinary proposal prose remains plain Unicode.
No custom font is required.

Remove `encoder.html`, font galleries/downloads, package installation and OS
clipboard instructions, and the normative spec page/template/scripts/styles.
Remove `/spec.html` entirely. No transition notice, redirect, or old-link
compatibility is needed. SDK installation and usage belong in the package
READMEs; the homepage can link to the working examples in its body.

Replace `build-spec.js` with proposal rendering. The build consumes a declared
ordered set of proposal docs, rewrites relative links, and handles headings and
anchors consistently. It does not parse specification versions, fixed selector
registries, or release metadata. Update package scripts, lockfile, and Vite inputs
together. Retain `marked` only if the chosen Markdown build uses it.

Keep the site's JavaScript SDK import and CSS dependency, updating paths only
where the experimental data layout changes. The module embeds registry and
segmentation tables and does not load the root mapping at runtime. Retain its
implemented behavior as a working example; constrain the homepage UI to the
small VS demonstration. Preserve segmentation source/version and required
notices. Shared runtime fixes belong in `js/`, not a copied site-only fork.

The Pages workflow currently deploys pushes to `main`, not this work branch.
Adjust watched paths to include canonical proposal docs and retained demo files.
Prepare build/deployment changes, but keep branch/default-branch migration and
live publication explicit. A local cleanup is not evidence that the public site
has changed.

## GitHub Discussions

The read-only audit found eight Discussions, all in Q&A, with no accepted answers
or locks. Seven are open with no comments. #14 is closed and has one comment.
These observations describe the audit; re-read each topic before applying edits.

| Existing Discussion | Replacement title | Questions and decision links |
| --- | --- | --- |
| [#13: marking scope](https://github.com/textprov/textprov/discussions/13) | Content scope: where should inline attribution be used? | Prose, source snippets, commit bodies/subjects, issues, review comments; search/parser consequences; eligibility responsibility. D09/D12 |
| [#14: meaning of human](https://github.com/textprov/textprov/discussions/14) | Source semantics: what does a voice reference attribute? | Contributor, submitter, quoted speaker, persona; observed activity versus authorship; optional classification. D03/D15. Reopen as unresolved |
| [#15: mixed versus ai](https://github.com/textprov/textprov/discussions/15) | Joint attribution: how should multiple contributions be represented? | One versus multiple references; separable contributions, quotations, paraphrases, rewrites; explicit attribution versus inference. D03 |
| [#16: editing reused text](https://github.com/textprov/textprov/discussions/16) | Editing: what attribution should survive insertion, deletion, and reuse? | Untouched, inserted, replaced, pasted text; unit versus paired/stateful scope; missing openers and orphan delimiters. D01/D07/D17 |
| [#17: mixed generations](https://github.com/textprov/textprov/discussions/17) | Optional history: should reuse and transformation metadata be in scope? | Whether history is needed; copy events versus transformations/derivation; optional metadata independent of reference meaning. D15 |
| [#18: unmarked reuse](https://github.com/textprov/textprov/discussions/18) | Voice0: how should unattributed text behave during copying and editing? | Preserve established absence meaning; entry into attributed runs; resets; missing dictionaries must not silently become Voice0. D07/D14/D17 |
| [#19: alternate generation layouts](https://github.com/textprov/textprov/discussions/19) | Encoding profiles: how are profiles recognized without collisions? | Context, versioning, escaping, unknown profiles; genuine IVS/emoji tags/unrelated PUA; private agreement versus standardization. D04–D06/D10/D11 |
| [#20: generation APIs and fixtures](https://github.com/textprov/textprov/discussions/20) | Evaluation: which application observations would distinguish the candidates? | Copying, editing, normalization, cursor, accessibility, search; recovery and preservation criteria; reproducible evidence. D01/D02/D08/D09 |

Each replacement opening post leads with the current proposal question and links
to the relevant published documents. No transition notice is needed. Remove
fixed selector-grid reservations, generation rules, assumed human defaults, and normative implementation instructions from the current
questions. Do not present eight historical opening posts in full as the new
agenda. Preserve original bodies and metadata in a rollback export before
editing; any historical source link used in a post must actually recover that
material. Historical opening-post text need not remain in the rewritten agenda.

The comment on #14 says that human meant a person wrote the text. Preserve it
unchanged, and explain in the new opening post that it answered the earlier
classification model. The proposal leaves source roles open and classification
optional. Reopening the thread does not endorse that historical comment as the
new model's resolution.

Add a short announcement introducing the proposal and linking the reading
order, open decisions, and bounded VS demonstration. Pin it if available. Add a
focused source-reference scope topic covering D13/D14: independent contexts both
using Voice1, merging/copied passages, and reference versus description survival.
This is a substantive gap in the former eight-topic agenda. Reuse an existing
matching topic if one appears before implementation.

Publish the proposal branch before linking newly moved documents from Discussions;
verify every branch-specific URL. Do not link to old `main/SPEC.md` or obsolete
`main/docs/development/` pages as the proposal's authority. Category restructuring
is unnecessary for this reset. The eight mapped topics remain open questions;
optional history is framed as a scope choice rather than a generation requirement.

Prepare exact replacement titles/bodies locally after the docs settle. Apply
updates individually, preserve discussion numbers and comments, re-read the
result, and record completion. No external messages or edits are part of this
plan-preparation task.

## Implementation sequence and agent ownership

| Phase | Owner | Concrete output | Dependency |
| --- | --- | --- | --- |
| 1. Remove obsolete automation and capture sources | Coordinator | Disable/remove old attribution hooks; record source revisions and evidence locations | None |
| 2. Reclaim canonical docs | Documentation agent | Target docs, extracted evidence, corrected links, disposition checklist | Phase 1 |
| 3. Reframe working SDKs | SDK agent | Package identities retained; usable demo READMEs; relocated data dependencies; SDK tests and generation tooling working | Canonical paths and experimental data layout from phase 2 |
| 4. Reclaim site | Site agent | Homepage toggle using JS SDK; proposal rendering; obsolete routes removed; working build | Agreed docs and SDK paths; can overlap phase 3 |
| 5. Remove obsolete tree and replace CI | Coordinator | Old docs/hooks/pages/font tooling removed; SDK checks retained; configs reconciled | Evidence capture and retained dependencies migrated |
| 6. Prepare Discussion replacements | Discussion agent | Current titles/bodies for all eight topics, reconciled with final docs | Phase 2; use an available slot after docs or SDK work |
| 7. Validate and review | Review agent and coordinator | Build/SDK/demo/link results, final tree audit, coverage and remote-edit checklist | Phases 2–6 |
| 8. Publish branch, update Discussions, then publish site deliberately | Coordinator | Publish the branch and verify doc URLs first; apply/re-read Discussion updates; track site deployment separately | Reviewed exact text and working site; publication scope settled |

The audits already used all three available subagent slots. During implementation,
documentation, SDK, and site agents own disjoint paths, with SDK data/layout
changes handed to the site agent. The Discussion agent owns only local drafts
and runs when a slot becomes available. The coordinator owns deletions, workflows, commits, and remote mutations. The
site agent owns site package scripts, lockfile, and Vite configuration; the coordinator owns repository-wide
configuration. Hand over the canonical path map before the site
agent updates imports. The SDK agent owns package directories, experimental
data, UCD sources, and required generators. Do not let agents independently
delete retained runtime, fixtures, or workflows. A final review checks cross-area
claims and dependencies.

Use coherent commits for documentation/evidence, SDK demos, site, and removals/CI.
Each commit includes coupled dependency changes so retained tests do not require
already deleted files. No package release, new encoding implementation, or change to open semantic
choices is bundled into reclamation. Existing SDK demonstrations remain working.

## Completion criteria

- README and homepage consistently say proposal, explain `Voice0`, and identify
  encoding and reference scope as unresolved.
- No competing normative v0.2 spec, ADR/development bulk, proposal-wide registry
  promises, generation reservations, font downloads, transition pages, or
  compatibility routes remain in active content.
- All three SDKs retain their package names and working demo examples. Their
  manifests, entry points, required data, generation tools, and behavioral tests
  agree with the revised layout; SDK documentation states experimental scope.
- Every discussed candidate remains findable. Musical delimiters are described
  as a scope precedent; obsolete assigned characters are not treated as free PUA.
- Human/AI labels and old selector values appear only in bounded historical
  SDK demo/profile/evidence descriptions, never as the proposal's universal taxonomy.
- Markdown links and generated site links/anchors resolve. Old routes are removed
  without redirects or transition notices.
- Site tests and production build pass. The toggle works by keyboard and on
  mobile, exposes correct accessibility state, handles blocked storage, and
  leaves underlying sample code points unchanged.
- Genuine IVS, emoji tags, ZWJ sequences, and unrelated PUA in ordinary proposal
  text are not passed through an experimental attribution decoder.
- Copy observations identify their actual method; DOM selection, real clipboard
  transport, and destination behavior are not conflated.
- CI checks docs, site, and SDK demos using the retained experimental mappings,
  fixtures, and segmentation data, with no deleted-hook/font/spec dependencies.
- A hidden-marker scan allows only explicit demonstration samples. Required
  licenses/notices remain attached to all retained code/data.
- All eight Discussion topics have a recorded outcome and verified update;
  historical comments remain intact. Unchanged or blocked remote work is reported.
- The local branch, GitHub Discussions, repository default branch, and published
  site each have separately reported status.
