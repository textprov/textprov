# 0006. Protocol repository and ecosystem packages

Status: accepted. Date: 2026-09-11. Accepted: 2026-09-12.

## Context

The decorator has implementations in more than one language. ADR 0004 makes the
shared fixture the conformance test. The protocol material and the reference
implementations that consume it were held inside a Nerd Fonts fork, beside the
font patcher that produces marked text. Producer and consumer have different
audiences, different release cadences, and different dependencies: the patcher
needs FontForge and builds fonts, while a decorator is a few hundred lines of
text processing with no dependencies at all.

## Decision

The protocol lives in its own repository, `textprov/textprov`, which owns the
specification, the canonical registry, the fixture, and the reference
implementations. The fork keeps everything that builds or verifies fonts.

### Naming

Open until 2026-09-12. `nfprov` could not be the protocol name: the protocol is
not font-specific and must not imply a Nerd Fonts affiliation. `prov` was
rejected as the public name because it collides with an existing GitHub
organisation, an unrelated npm package, and PyPI's `prov`, an active W3C PROV
data-model library; that collision would make the protocol hard to find and
easy to confuse with the W3C standard.

| Role | Name |
| --- | --- |
| Protocol and specification | TextProv, `SPEC.md` |
| GitHub organisation and repository | `textprov/textprov` |
| JavaScript package | `@textprov/decorator` |
| Python package and import | `textprov` |
| Ruby gem (not yet published) | `textprov` |
| CSS class prefix and data attribute | `prov`, `data-prov` |

The class prefix stays `prov`. Changing it would break every stylesheet already
written against the shipped decorator, and the prefix is a local CSS name, not a
discovery surface: nobody searches a package index for a class. The repository,
organisation, and package names carry the identity instead. A consumer that
wants a different prefix passes the option; `data-prov` does not move with it.

`nfprov` remains the in-fork Python tool name for the encoder and font
workflow, where it is correctly scoped.

### What moved

- `SPEC.md`, written for this repository. The contract existed only as the
  fork's `DECORATOR.md`, which described a decorator rather than a protocol;
  the specification now covers states, both encodings, the registry and its
  stability rules, vendoring, the decoder, and the markup.
- One canonical `mapping.json`, replacing two byte-identical copies.
- `fixtures.json`, the conformance suite of ADR 0004.
- `js/textprov.js` and `js/textprov.css`, from `css/nfprov.js` and
  `css/nfprov.css`.
- `python/textprov`, the shared core and renderer from `bin/scripts/nfprov.py`:
  `load_mapping`, `is_combining`, `cluster_end`, the run splitter, the HTML
  renderer, and the decorator form of `strip`.
- Fixture runners for both implementations.
- `docs/GOAL.md`, `docs/HTML-RENDERING.md`, and ADRs 0001–0004, 0006, and
  0008–0010.

### What stayed in the fork

- `font-patcher` and its `--provenance` option.
- `bin/scripts/test-provenance.py`, which verifies built fonts and needs
  `fontTools`.
- The encoder operations in `bin/scripts/nfprov.py`: `do_mark`,
  `do_mark_added`, and `do_convert`, plus `do_inspect` as diagnostic tooling.
- ADR 0005 (serving the font as a woff2 subset) and ADR 0007 (reaching variants
  under CoreText through a `ccmp` ligature). Both are font-build decisions. ADR
  numbering is shared across the two repositories, so a number appears in one
  or the other, never both.
- Fork-specific material: its README, `zed-about.md`, examples, `ROLLOUT.txt`,
  and prototype screenshots.

### Test ownership

The earlier wording of this record required that test ownership be explicit
before any file moved. The fork's `selftest` had no direct coverage of
`cluster_end` or `to_html`; both were reached only through the encoder round
trips and the fixture loop, which would have left the moved code untested.
Direct tests were added first, then moved here as
`python/tests/test_conformance.py`. The fork's `selftest` keeps the mark and
convert round trips, which test the encoder it still owns.

### Vendoring

Each package vendors the registry and no package depends on another. A browser
script cannot load JSON synchronously, so `js/textprov.js` embeds the tables the
registry reduces to — the selector table, the allocated PUA ranges, and the
mapping version — and exposes them as `textprov.mapping`. The Python package
ships a copy of `mapping.json` inside the package directory. Each test suite
compares its copy to the canonical file on every run, so drift fails the build.
The JavaScript runner also asserts the two registry rules that the embedding
relies on: `PUA_AI(cp) = 0x100000 + cp`, and published entries are never
reassigned or removed.

## Remaining work

1. Publish `@textprov/decorator`. The DOM decorator and stylesheet are here; a
   rehype plugin and a markdown-it plugin are not written.
2. Wait for one breakage report and add its case to `fixtures.json` before
   starting another port.
3. Publish `textprov` on PyPI.
4. Publish a Ruby gem with a kramdown hook for Jekyll and GitHub Pages, then
   test it in a real site.
5. Have the fork consume the published Python package instead of its vendored
   copy of the shared core, and read the registry from the package rather than
   `src/glyphs/provenance/mapping.json`. Until then the fork's copies are
   downstream duplicates of the files here, and this repository is canonical.

Every package exposes `runs` and either `to_html` or `decorate`. The only
options are `strip`, `merge_whitespace`, and a class prefix.

A browser extension based on the client-side decorator is the proposed route
for pages whose author cannot add a decorator pass. It does not exist.

No domain has been registered and no trademark clearance has been done for the
name.
