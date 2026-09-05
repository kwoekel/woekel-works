# Repo Structure Audit — {repo name} — {YYYY-MM-DD}

{One sentence: overall state, highest-cost problem, and safest first move.}

{No pending checks: **{n}/100 — {band}.**
Pending checks: **Assessed: {earned}/{available} points ({percent}%). Full-score range:
{minimum}–{maximum}/100 pending {checks}.** Never show an ordinary `{n}/100` headline while
pending.}

## What: Current State

- **Profile:** {profile and evidence}.
- **Scope:** {target, supplied purpose, governing conventions, and assumptions}.
- **N/A:** {checks and reason, or “None”}.

| Lens | Score |
|---|---:|
| Navigability | {earned}/{available} |
| Ownership | {earned}/{available} |
| Lifecycle | {earned}/{available} |
| Hygiene | {earned}/{available} |

### Seriousness by principle

| Principle | Seriousness | Strongest evidence |
|---|---|---|
| P1 Obvious entry point | 🟢 Clear / 🟡 Watch / 🔴 Fix / ⚪ N/A / ⏳ Needs your call | … |
| P2 Consistent naming | … | … |
| P3 Smallest complete owner | … | … |
| P4 Project-folder threshold | … | … |
| P5 One source of truth | … | … |
| P6 Lifecycle separation | … | … |
| P7 Preserved history | … | … |
| P8 Visible abandonment | … | … |
| P9 Configuration discipline | … | … |
| P10 Git hygiene | … | … |

### What works

{One to three specific strengths worth preserving.}

{If a prior audit exists:}

### Since last audit

{Repository changes versus rubric or scoring changes. Generated reports are excluded from
facts.}

## So What: What This Affects

{List only the two to four highest-cost consequences, most serious first. Name what may break,
duplicate, become misleading, or get lost. Say plainly when nothing is currently costly.}

### Evidence behind the findings

#### F{n} · {title} — {🟡 Watch / 🔴 Fix / ⏳ Needs your call}

**Current** — {P# Name. Repository paths and evidence. Never quote secret values.}

**Impact** — {Observable consequence in one or two sentences; do not restate the principle.}

**Proposal** — {Desired outcome; preserve documented repository constraints.}

**Safety** — {Exact reference searches and results. State the risk if wrong, or “None found.”}

{Repeat only for findings that affect the score, require a decision, or support a proposed
change. Do not repeat the same evidence in multiple findings.}

## Now What: Proposed Changes

> **Proposed — not reviewed.** This audit recommends changes; it does not approve or
> implement them.

### Before and After Proposed Changes

{Show only affected areas and enough context to orient. Keep annotations short enough for two
columns. Do not include changes that depend on unanswered intent.}

<table>
<tr>
<th>Current</th>
<th>After Proposed Changes</th>
</tr>
<tr>
<td><pre>
{affected current tree
with [KEEP], [FIX], [DUPLICATE],
[AUTHORED], or [GENERATED] notes}
</pre></td>
<td><pre>
{affected proposed tree
with [OWNER], [ROUTER], [HUMAN],
[MOVE], or [KEEP] notes}
</pre></td>
</tr>
</table>

**Tree key:** `OWNER` canonical home · `ROUTER` `AGENTS.md` or `CLAUDE.md`, pointers only ·
`HUMAN` explanatory `README.md` · `MOVE` reference check required · `KEEP` no change

### Ranked changes

| Order | Proposed change | Why this order | Safety check |
|---:|---|---|---|
| 1 | … | … | … |

{Rank by leverage and reversibility. Reference checks precede dependent moves.}

### Needs your call

{Only questions where intent decides whether a finding exists. Never ask which duplicate is
canonical here; uncontrolled duplication is already scored. Maximum three questions.}

### Choices for an implementation plan

{Choices that do not change the audit score, such as which duplicate becomes canonical. Do
not imply that an audit recommendation is approved.}

### Coverage and security limits

- {Unreadable, depth-pruned, opaque, or sampled paths.}
- {Whether a dedicated secret-content scan ran. Filename checks alone do not prove absence.}
- {Whether Git history, external schedules, symlinks, or deployment consumers were checked.}
