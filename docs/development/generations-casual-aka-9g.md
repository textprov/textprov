---
# docs/development/generations-casual.md
---

# Document 2: TextProv Generational Marking, Plain-Language Guide

## What a mark records

Every character can carry one invisible mark. The mark records two things:

- **Origin:** who wrote the character originally (human, AI, mixed, edited, or unknown).
- **Generation:** how many times the character has been carried from one conversation into the next.

## Reading a mark

Every mark has the form **U+E01gs**:

- **g** is the generation (0–9).
- **s** is the origin.

In shorthand, use the last three hex digits. For example, `100` is human-written and never reused, and `131` is AI-written text passed along three times.

| Generation | human | ai | mixed | edited | unknown | 5–F |
|---|---|---|---|---|---|---|
| 0 | E0100 | E0101 | E0102 | E0103 | E0104 | reserved |
| 1 | E0110 | E0111 | E0112 | E0113 | E0114 | reserved |
| 2 | E0120 | E0121 | E0122 | E0123 | E0124 | reserved |
| 3 | E0130 | E0131 | E0132 | E0133 | E0134 | reserved |
| 4 | E0140 | E0141 | E0142 | E0143 | E0144 | reserved |
| 5 | E0150 | E0151 | E0152 | E0153 | E0154 | reserved |
| 6 | E0160 | E0161 | E0162 | E0163 | E0164 | reserved |
| 7 | E0170 | E0171 | E0172 | E0173 | E0174 | reserved |
| 8 | E0180 | E0181 | E0182 | E0183 | E0184 | reserved |
| 9 (9 or more) | E0190 | E0191 | E0192 | E0193 | E0194 | reserved |

## What happens when text is reused

Each time a transcript becomes input to a new conversation, every mark moves down one row (+16). The origin never changes.

Example: a human-written word passed through three conversations goes `100 → 110 → 120 → 130`.

At row 9 the count stops. **9 means "9 or more."**

## What it tells you, and what it doesn't

| Tells you | Doesn't tell you |
|---|---|
| The origin as first recorded | Whether that origin is true (it's a claim, not a check) |
| How many times the text was reused, up to 9 | Who passed it along, or the path it took |
| That the text came in from earlier material | Whether it was changed along the way (not yet decided) |

## How the space is divided

- **Rows 0–9 (E0100–E019F, 160 points):** the default grid.
- **Columns 5–F:** reserved for future origin types. Today's tools will still count generations correctly for these, without needing to know what they mean.
- **Rows A–E (E01A0–E01EF, 80 points):** reserved for alternate layouts. Each layout gets its own separate range, so a mark never depends on outside context to be read. This still holds after a snippet is copied out of its document.

## Compatibility

Row 0 is exactly today's marks. Text that is already marked counts as generation 0 with no changes.

## Still to decide

- How to mark reused text that someone then edits.
- How "mixed" is assigned, and what generation it gets.
- What to do with unmarked text that gets reused.
- How alternate layouts claim their ranges in rows A–E.
