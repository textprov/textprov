# 0009. Editor decoration APIs as a third consumer path

Status: proposed. Date: 2026-09-11.

## Context

Editors cannot have their buffers rewritten with spans. They expose decoration
APIs that attach a class to a range at paint time: VS Code
`TextEditorDecorationType`, CodeMirror decorations.

## Proposal

Port the run detection defined in `SPEC.md` to an editor extension that drives
the decoration API. This would cover CoreText editors without relying on
format-14 font substitution and would provide three consumer paths: the P+
font for HarfBuzz hosts, spans for the web, and decorations for editors with
an extension API.

## Open

Not prototyped. Whether Zed exposes a usable decoration API is unknown.
