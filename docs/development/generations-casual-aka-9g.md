---
# docs/development/generations-casual.md
---

# Document 2: TextProv Generational Marking, Plain-Language Guide

S󠄁t󠄁a󠄁t󠄁u󠄁s󠄁:󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁,󠄁 n󠄁o󠄁n󠄁-󠄁n󠄁o󠄁r󠄁m󠄁a󠄁t󠄁i󠄁v󠄁e󠄁.󠄁 G󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁 a󠄁n󠄁d󠄁 a󠄁l󠄁t󠄁e󠄁r󠄁n󠄁a󠄁t󠄁e󠄁 l󠄁a󠄁y󠄁o󠄁u󠄁t󠄁s󠄁 (󠄁s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁)󠄁
a󠄁r󠄁e󠄁 n󠄁o󠄁t󠄁 p󠄁a󠄁r󠄁t󠄁 o󠄁f󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 v󠄁e󠄁r󠄁s󠄁i󠄁o󠄁n󠄁 0󠄁.󠄁2󠄁.󠄁 T󠄁h󠄁i󠄁s󠄁 g󠄁u󠄁i󠄁d󠄁e󠄁 d󠄁e󠄁s󠄁c󠄁r󠄁i󠄁b󠄁e󠄁s󠄁 t󠄁h󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁,󠄁
n󠄁o󠄁t󠄁 b󠄁e󠄁h󠄁a󠄁v󠄁i󠄁o󠄁r󠄁 r󠄁e󠄁q󠄁u󠄁i󠄁r󠄁e󠄁d󠄁 o󠄁f󠄁 c󠄁u󠄁r󠄁r󠄁e󠄁n󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁.󠄁

## What a mark records

Every character can carry one invisible mark. The mark records two things:

- **Origin:** who wrote the character originally (󠄁h󠄁u󠄁m󠄁a󠄁n󠄁 o󠄁r󠄁 A󠄁I󠄁)󠄁.
- **Generation:** how many times the character has been carried from one conversation into the next.

## Reading a mark

Every mark has the form **U+E01gs**:

- **g** is the generation (0–9).
- **s** is the origin.

In shorthand, use the last three hex digits. For example, `100` is human-written and never reused, and `131` is AI-written text passed along three times.

| Generation | human (󠄁0󠄁)󠄁 | a󠄁i󠄁 (󠄁1󠄁)󠄁 | 2󠄁–󠄁F󠄁 |
|---|---|---|---|
| 0 | E0100 | E0101 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 1 | E0110 | E0111 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 2 | E0120 | E0121 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 3 | E0130 | E0131 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 4 | E0140 | E0141 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 5 | E0150 | E0151 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 6 | E0160 | E0161 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 7 | E0170 | E0171 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 8 | E0180 | E0181 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |
| 9 (9 or more) | E0190 | E0191 | u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 /󠄁 reserved |

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
- **Columns 2󠄁–󠄁F󠄁:󠄁** u󠄁n󠄁a󠄁l󠄁l󠄁o󠄁c󠄁a󠄁t󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 r󠄁e󠄁s󠄁e󠄁r󠄁v󠄁e󠄁d󠄁 f󠄁o󠄁r󠄁 f󠄁u󠄁t󠄁u󠄁r󠄁e󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 t󠄁y󠄁p󠄁e󠄁s󠄁;󠄁 n󠄁o󠄁n󠄁e󠄁 a󠄁r󠄁e󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁e󠄁d󠄁.󠄁 U󠄁n󠄁d󠄁e󠄁r󠄁 t󠄁h󠄁i󠄁s󠄁 p󠄁r󠄁o󠄁p󠄁o󠄁s󠄁a󠄁l󠄁,󠄁 a󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁 t󠄁h󠄁e󠄁s󠄁e󠄁 c󠄁o󠄁l󠄁u󠄁m󠄁n󠄁s󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 a󠄁s󠄁s󠄁i󠄁g󠄁n󠄁i󠄁n󠄁g󠄁 t󠄁h󠄁e󠄁m󠄁 a󠄁n󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 m󠄁e󠄁a󠄁n󠄁i󠄁n󠄁g󠄁.󠄁
- **Rows A–E (E01A0–E01EF, 80 points):** reserved for alternate layouts. Each layout gets its own separate range, so a mark never depends on outside context to be read. This still holds after a snippet is copied out of its document.

## Compatibility

Row 0 is exactly today's marks. Text that is already marked counts as generation 0 with no changes.

## Still to decide

- How to mark reused text that someone then edits.
- H󠄁o󠄁w󠄁 t󠄁o󠄁 r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁 r󠄁e󠄁u󠄁s󠄁e󠄁 o󠄁f󠄁 u󠄁n󠄁m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 t󠄁e󠄁x󠄁t󠄁 o󠄁u󠄁t󠄁 o󠄁f󠄁 b󠄁a󠄁n󠄁d󠄁 w󠄁i󠄁t󠄁h󠄁o󠄁u󠄁t󠄁 i󠄁n󠄁v󠄁e󠄁n󠄁t󠄁i󠄁n󠄁g󠄁 a󠄁n󠄁 o󠄁r󠄁i󠄁g󠄁i󠄁n󠄁 c󠄁l󠄁a󠄁i󠄁m󠄁.󠄁
- How alternate layouts claim their ranges in rows A–E.
