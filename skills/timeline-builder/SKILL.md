---
name: timeline-builder
description: Build or update the court-case timeline from logged incidents, communications, and any emails, texts, notes, or transcripts the user points to. Use when the user says "build my timeline", "update the timeline", "what happened when", "make a chronology", or needs a timeline for a specific period or person.
---

# Timeline Builder

The timeline is the spine everything else hangs on: the evaluator narrative, attorney updates, motions, and the visual timeline. This skill extracts dated events from sources, removes duplicates, tags what matters, and lists what's missing.

> Organized draft for your attorney to review, not legal advice.

## Inputs (in this order)

1. Files or paths the user gives in this session.
2. `court/incidents/` and `court/communications/` (entries made by the Incident Log skill).
3. Any connected sources she names: Gmail search, calendar, meeting transcripts, notes exports, text exports.
4. If coverage looks thin, say so and ask. **No silent supplement:** never fill gaps from web search or general knowledge.

## Steps

1. **Read each source and pull out dated events,** one line each:
   - Email or text: `[date] [sender] told [recipient] [what]`
   - Meeting or exchange: `[date] [who] [where] [what happened]`
   - Court or school event: `[date] [what happened]`
2. **Record how sure the date is:** `exact`, `approximate`, or `recollection`.
3. **De-dupe.** The same event in a text, an email, and a note is one event with three sources. Merge and list every source.
4. **Tag significance:**
   - 🔴 possible custody-order violation, safety concern, or a fact that would genuinely matter to a judge or evaluator
   - 🟡 part of a pattern, or useful context
   - ⚪ background
   Discipline: if everything is 🔴, nothing is. When in doubt, use 🟡 and add `[check tag]`.
5. **Contradictions:** if two sources disagree on a date or fact, keep both entries and flag them. Don't pick a winner.
6. **Write the outputs** (below). If a timeline already exists, read it first, add new events, bump the version, and list what changed.
7. **Confirm before finishing:** "Here's what I built. Scan the 🔴 entries. Anything I got wrong?"

## Outputs

`court/timeline.md`:

```markdown
> Organized draft for your attorney to review, not legal advice.

# Timeline

**Built:** YYYY-MM-DD · **Version:** vN · **Entries:** N (N 🔴 / N 🟡 / N ⚪) · **Sources:** N

| # | Date | Precision | Event | Tag | Children involved | Sources |
|---|---|---|---|---|---|---|
| T-001 | YYYY-MM-DD | exact | one factual sentence | 🔴 | yes/no | EVT-012, email 2024-03-02 "Pickup" |

## Key events (🔴 only)
### [date] — [title]
- What: one line
- Why it matters: one line
- Sources: list

## Contradictions
[entries where sources disagree]

## Gaps
- Date ranges with no records
- Things you'd expect to be documented but aren't
- Sources that couldn't be read this run

## Version history
- vN built YYYY-MM-DD from [sources]
```

`court/timeline.csv` (for the visual timeline / dashboard), columns:
`id,date,precision,title,tag,children_involved,lane,sources`

## Variants on request

- **Period:** only events between two dates.
- **Person:** only events involving a named person (teacher, therapist, co-parent's new partner).
- **Pattern:** only events with a given issue tag (e.g. every late pickup).

## Rules

- Every entry traces to a source. Facts the user states in chat are tagged `[user provided]`.
- Never invent events. Never resolve contradictions for the user.
- Don't state legal conclusions or deadlines unless they come from a document in the folder; otherwise tag `[verify with attorney]`.
- Keep it local.

---
Source: method adapted from Anthropic's chronology skill (anthropics/claude-for-legal, litigation-legal/skills/chronology, Apache License 2.0), with law-firm steps removed (matter intake, conflicts check, privilege gate, plaintiff/defense framing, Bates numbering) and a recollection/approximate date field added.
