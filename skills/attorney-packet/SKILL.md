---
name: attorney-packet
description: Prepare a one-page update for the user's family-law attorney, track attorney communications and costs, and on request draft a motion-prep packet (statement of facts plus exhibit list). Use when the user says "prep for my lawyer call", "attorney update", "what should I ask my lawyer", "track my legal bills", "is my lawyer following up", or "motion prep".
---

# Attorney Packet

**Court folder:** `court/` below means whichever folder the user chose, recorded once as `court-folder:` in that folder's or the workspace's agent instructions. If unknown, ask once and record it. Never create a second one.

Makes every attorney conversation shorter, cheaper, and more useful, and keeps a record of what was promised and what happened.

> Organized draft for your attorney to review, not legal advice.

## Mode 1: Attorney update (default)

1. Read `court/timeline.md`, recent entries in `court/incidents/` and `court/communications/`, and the last packet in `court/attorney/` (if any).
2. Write `court/attorney/YYYY-MM-DD-update.md`, **one page max**:

```markdown
> Organized draft for your attorney to review, not legal advice.

# Update for [attorney] — YYYY-MM-DD
## Since our last contact (YYYY-MM-DD)
- [3–6 bullets, each ending with its timeline ID in brackets]
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

**Flag gently** (as questions to raise, not accusations) if: promised follow-ups didn't happen, deadlines are close with no action, the user felt rushed to agree, advice seems to conflict with the evidence the user has, or bills include work the user doesn't recognize. Suggest how to raise it with the attorney first.

## Mode 3: Motion prep (when the user says "motion prep")

1. Ask what the motion is about and the period it covers. Don't choose legal arguments; that's the attorney's job.
2. Draft `court/attorney/motion-prep-YYYY-MM-DD.md`:
   - **Statement of facts,** under a `## Statement of facts` heading: chronological prose built from relevant 🔴 and 🟡 timeline entries, each paragraph ending with its sources in brackets.
   - **Exhibit list:** numbered, with description, date, and file location for every cited source.
   - **Gaps:** facts the motion seems to need that aren't documented.
   - **Questions for the attorney.**
3. Mark legal points `[verify with attorney]`. Never cite statutes or cases from memory.

## Before calling an update or motion-prep packet ready

1. **Run Proof Check** on the saved file. Don't call it ready until it says **Ready for attorney review**. Until then, call it a draft and list what's open.
2. **Offer export to Word or PDF,** using whichever document tool the app has. If there is none, say so. Put the disclaimer at the top, then add two appendices (the one-page limit doesn't count them):
   - **Source index:** every cited ID and source, with date, what it is, and where it lives.
   - **Timeline appendix:** the cited rows from `court/timeline.md`, unchanged.

   The Markdown stays the master. Make changes there and export again. If the user wants an export before Proof Check passes, mark its first page `Not yet proof-checked`.

## Project tracker

If a project tracker exists (`PROJECT.md` with Sections, Sources needed, Sources linked, Open questions, Last session), open from it when resuming and update it at the end of each session. Don't create one unasked.

## Rules

- Never invent facts, dates, or legal rules.
- Keep `> Organized draft for your attorney to review, not legal advice.` at the top of every file this skill writes, including the log, costs, and exports.
- Never contact the attorney or send anything. Drafts only.
- **Privacy.** Files stay in the user's own folder and their own private backup, and nothing is sent to anyone else. Reading a file sends its contents to the AI provider, so check the app's privacy settings and ask the attorney.
- **No unattended tidying.** Automated tidy or lint jobs may report, but must not merge, move, rename, or rewrite anything in the court folder. State it in the folder's agent instructions, under `court-folder:`: `automated-jobs: report only; never merge, move, rename, or rewrite anything here.`

---
Sources: attorney communication log, cost tracking, advice assessment, and red flags adapted from Case Forge's Lawyer Accountability skill (CaseForgeHq/family-court-strategist, MIT License, © Kyle Fischer), rewritten for US terms. Statement-of-facts method adapted from Anthropic's chronology skill (anthropics/claude-for-legal, Apache License 2.0).
