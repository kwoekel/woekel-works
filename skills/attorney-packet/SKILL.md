---
name: attorney-packet
description: Prepare a one-page update for the user's family-law attorney, track attorney communications and costs, and on request draft a motion-prep packet (statement of facts plus exhibit list). Use when the user says "prep for my lawyer call", "attorney update", "what should I ask my lawyer", "track my legal bills", "is my lawyer following up", or "motion prep".
---

# Attorney Packet

Makes every attorney conversation shorter, cheaper, and more useful, and keeps a record of what was promised and what happened.

> Organized draft for your attorney to review, not legal advice.

## Mode 1: Attorney update (default)

1. Read `court/timeline.md`, recent entries in `court/incidents/` and `court/communications/`, and the last packet in `court/attorney/` (if any).
2. Write `court/attorney/YYYY-MM-DD-update.md`, **one page max**:

```markdown
> Organized draft for your attorney to review, not legal advice.

# Update for [attorney] — YYYY-MM-DD
## Since our last contact (YYYY-MM-DD)
- [3–6 bullets, each with a timeline ID]
## Key incidents (🔴)
- [date] [one line] [T-### / EVT-###]
## Upcoming dates and deadlines
- [date] [what] (source: [document])
## My questions
1. ...
## Documents attached / available
| Exhibit | What it is | Where it lives |
|---|---|---|
## Open items from last time
- [ ] [what the attorney said they'd do] — status
```

3. Ask the user if there are questions or worries to add before finalizing.

## Mode 2: Attorney log (after each call, email, or meeting)

Append to `court/attorney/attorney-log.md` (never edit earlier rows):

| Date | Method | What was discussed | Advice given | What I was asked to do | What the attorney said they'd do | What actually happened next |
|---|---|---|---|---|---|---|

Also keep a costs table in `court/attorney/costs.md`: fee agreement terms, each invoice (date, amount, work described), running total vs. estimate.

**Flag gently** (as questions to raise, not accusations) if: promised follow-ups didn't happen, deadlines are close with no action, she felt rushed to agree, advice seems to conflict with the evidence she has, or bills include work she doesn't recognize. Suggest how to raise it with the attorney first.

## Mode 3: Motion prep (when the user says "motion prep")

1. Ask what the motion is about and the period it covers. Don't choose legal arguments; that's the attorney's job.
2. Draft `court/attorney/motion-prep-YYYY-MM-DD.md`:
   - **Statement of facts:** chronological prose built from relevant 🔴 and 🟡 timeline entries, each paragraph cited.
   - **Exhibit list:** numbered, with description, date, and file location for every cited source.
   - **Gaps:** facts the motion seems to need that aren't documented.
   - **Questions for the attorney.**
3. Mark legal points `[verify with attorney]`. Never cite statutes or cases from memory.

## Rules

- Never invent facts, dates, or legal rules.
- Never contact the attorney or send anything. Drafts only.
- Keep it local.

---
Sources: attorney communication log, cost tracking, advice assessment, and red flags adapted from Case Forge's Lawyer Accountability skill (CaseForgeHq/family-court-strategist, MIT License, © Kyle Fischer), rewritten for US terms. Statement-of-facts method adapted from Anthropic's chronology skill (anthropics/claude-for-legal, Apache License 2.0).
