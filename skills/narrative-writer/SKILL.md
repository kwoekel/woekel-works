---
name: narrative-writer
description: Draft a written narrative of events for a custody evaluator, therapist, guardian ad litem, or attorney from the court timeline. Use when the user says "write my narrative", "draft the history for the evaluator", "statement of facts", "summarize what happened between X and Y", or needs a written account of a period.
---

# Narrative Writer

**Court folder:** `court/` below means whichever folder the user chose, recorded once as `court-folder:` in that folder's or the workspace's agent instructions. If unknown, ask once and record it. Never create a second one.

Turns the timeline into a calm, readable account that an evaluator or attorney can trust. Credibility comes from being factual, child-focused, and sourced.

> Organized draft for your attorney to review, not legal advice.

## Before writing, ask (one message)

1. Who is it for? (custody evaluator, guardian ad litem, therapist, attorney)
2. What period? (all, or dates)
3. Any page or word limit, or required format?
4. Anything they specifically asked about?

## Steps

1. **Read `court/timeline.md`.** If it's missing or out of date, suggest running Timeline Builder first.
2. **Select events:** all 🔴 and the 🟡 entries that show a pattern. Leave ⚪ out unless needed for context.
3. **Write in chronological order,** one paragraph per event or tightly linked cluster. Each paragraph ends with its sources in brackets, e.g. `[T-014; EVT-031; text 2023-05-04]`.
4. **Show patterns plainly:** "This was the fourth late exchange in six weeks [T-020, T-022, T-025, T-027]."
5. **Keep the children at the center:** what they experienced, how they responded, what the user did to protect their routine and wellbeing.
6. **Mark memory-only content:** "To the best of my recollection…" for anything tagged `recollection`.
7. **List open questions** at the end instead of filling gaps: "I don't have records for spring 2021. Do you have texts, emails, or someone who remembers?"
8. Save to `court/narratives/YYYY-MM-DD-[audience]-[period].md` and show the user a short summary.
9. **Run Proof Check** on the saved draft. Don't call it ready until it says **Ready for attorney review**. Until then, call it a draft and list what's open.
10. **Offer export to Word or PDF,** using whichever document tool the app has. If there is none, say so. Put the disclaimer at the top, then add two appendices:
    - **Source index:** every cited ID and source, with date, what it is, and where it lives.
    - **Timeline appendix:** the cited rows from `court/timeline.md`, unchanged.

    The Markdown stays the master. Make changes there and export again. If the user wants an export before Proof Check passes, mark its first page `Not yet proof-checked`.

## Project tracker

If a project tracker exists (`PROJECT.md` with Sections, Sources needed, Sources linked, Open questions, Last session), open from it when resuming and update it at the end of each session. Don't create one unasked.

## Tone rules

- First person, plain language, short sentences.
- Describe behavior, never diagnose or label ("the other parent arrived 90 minutes late," not "the other parent is a narcissist").
- No sarcasm, no adjectives that argue ("outrageous," "obviously").
- Acknowledge the user's own actions honestly; evaluators notice one-sided accounts.
- Never invent, merge, or embellish events. Never change what a quote says.

## Rules

- **Privacy.** Files stay in the user's own folder and their own private backup, and nothing is sent to anyone else. Reading a file sends its contents to the AI provider, so check the app's privacy settings and ask the attorney.
- **No unattended tidying.** Automated tidy or lint jobs may report, but must not merge, move, rename, or rewrite anything in the court folder. State it in the folder's agent instructions, under `court-folder:`: `automated-jobs: report only; never merge, move, rename, or rewrite anything here.`

## Output shape

```markdown
> Organized draft for your attorney to review, not legal advice.

# [Narrative title] — [period]
Prepared for: [audience] · Draft date: YYYY-MM-DD · Based on timeline vN

## Summary (3–5 sentences)
## Background (brief)
## Events
[chronological paragraphs with sources]
## Patterns
## Impact on the children
## What I'm asking for / concerns going forward (only if the user wants this section)
## Open questions and gaps
```

---
Source: structure follows the statement-of-facts variant of Anthropic's chronology skill (anthropics/claude-for-legal, Apache License 2.0): 🔴 and relevant 🟡 events, chronological prose, each paragraph cited. Child-impact focus and attribution standards from Case Forge (CaseForgeHq/family-court-strategist, MIT License).
