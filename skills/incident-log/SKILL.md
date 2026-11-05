---
name: incident-log
description: Log a co-parenting or custody incident, or a message from the co-parent, as a dated evidence entry in the court folder. Use when the user says "log this", "add an incident", "this just happened", "save this text/email", shares a voice note or transcript about something that happened, or pastes a screenshot or message from the other parent.
---

# Incident Log

**Court folder:** `court/` below means whichever folder the user chose, recorded once as `court-folder:` in that folder's or the workspace's agent instructions. If unknown, ask once and record it. Never create a second one.

Capture what happened while it's fresh, in a format that holds up later. One entry per event, saved as plain markdown so any AI app or person can read it.

> Organized draft for your attorney to review, not legal advice.

## Where entries go

- Incidents: `court/incidents/YYYY-MM-DD-short-title.md`
- Messages and emails with the co-parent: `court/communications/YYYY-MM-DD-short-title.md`
- Also add a one-line row to `court/incident-log.md` (the index): `| date | ID | type | title | tag | file |`. Create it if missing.

## Steps

1. **Take in what the user shares.** Voice note, transcript, typed description, screenshot, email, or pasted text. If it's a voice note or transcript, keep the user's own words in a quote block before tidying anything.
2. **Ask only what's missing, max 3 short questions:** when did it happen (exact or approximate), who was there, were the kids present or affected. Don't interrogate. If the user is upset, log what you have and mark the rest `[to fill in later]`.
3. **Pick the next ID.** Incidents use `EVT-###`, communications use `COM-###` (check the index for the last number).
4. **Write the entry** using the template below.
5. **Match to the custody order.** If a custody/parenting order is in the court folder, name the specific term the event may relate to (quote the section). If there's no order on file, write `Order term: [unknown, add custody order to court folder]`. Never guess what an order says.
6. **Offer next steps,** in one line: draft an email or reply (use the Co-Parent Reply skill), add to the timeline, or flag for the attorney. For a bulk import, use the Source Map skill.

## Template — incident

```markdown
---
date: YYYY-MM-DD            # when it happened
date_precision: exact | approximate | recollection
logged: YYYY-MM-DD HH:MM    # when this entry was made
type: incident
event_id: EVT-###
people: []
children_present: yes | no | unknown
issue: []                   # e.g. schedule, pickup, communication, safety, school, medical
order_term: ""
source_file: ""
reliability: primary | secondary | recollection
tag: 🔴 | 🟡 | ⚪
---

> Organized draft for your attorney to review, not legal advice.

# [Short factual title]

## In my words
> [the user's original words, unedited]

## What happened
Who, what, when, where. Facts only. Describe behavior, not motives or diagnoses.

## Evidence
| Evidence | Where it lives | Strength |
|---|---|---|
| | | ★★★ / ★★☆ / ★☆☆ |

## Impact on the children
What the kids saw, heard, or experienced, and any change afterwards. Write "not observed" if none.

## Custody-order term
[quoted section, or "unknown"]

## Follow-up
- [ ]
```

## Template — communication

Same frontmatter with `type: communication`, `event_id: COM-###`, plus:

```markdown
> Organized draft for your attorney to review, not legal advice.

## Details
| From | To | Method (text / email / app / call) | Date and time |
|---|---|---|---|

## Exact content
> [verbatim text; never paraphrase a quote]

## Response sent
[what was sent back, or "none yet"]

## Pattern
Does this repeat something already logged? Link the earlier IDs.
```

## Rules

- **Never edit or delete a past entry.** Corrections go in a new entry: `Correction to EVT-###: ...`.
- **Never invent facts or fill gaps.** Mark uncertain details `approximate` or `my recollection`.
- **Quotes are exact,** with who said it, to whom, and where it came from.
- **Tags:** 🔴 possible order violation or safety concern, 🟡 part of a pattern, ⚪ background. If unsure, use the lower tag and note `[check tag]`.
- **Never send anything.** Drafts only.
- **Privacy.** Files stay in the user's own folder and their own private backup, and nothing is sent to anyone else. Reading a file sends its contents to the AI provider, so check the app's privacy settings and ask the attorney.
- **No unattended tidying.** Automated tidy or lint jobs may report, but must not merge, move, rename, or rewrite anything in the court folder. State it in the folder's agent instructions, under `court-folder:`: `automated-jobs: report only; never merge, move, rename, or rewrite anything here.`
- **Be gentle.** The user may be logging something painful. Keep questions short and don't comment on the other parent's character.

---
Sources: entry templates adapted from Case Forge's incident and communication templates (CaseForgeHq/family-court-strategist, MIT License, © Kyle Fischer). Attribution rules (who said it, to whom, per whose account) from Case Forge's methodology.
