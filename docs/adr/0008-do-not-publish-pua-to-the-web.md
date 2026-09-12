# 0008. Do not publish PUA-encoded text to the web

Status: proposed. Date: 2026-09-11.

## Context

PUA text renders under CoreText where selector text does not, which makes it
tempting as the iOS answer for pages that ship the P+ font.

## Proposal

Publish only the selector encoding and rely on the decorator (0001) for iOS.
PUA in the DOM is expected to break find-in-page, copy as PUA, and provide no
usable text to screen readers.

## Open

None of the three expected breakages were measured. This is reasoning, not
evidence.
