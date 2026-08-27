# Structure Audit — {repo name} — {YYYY-MM-DD}

{No pending checks: **{n}/100 — {band}.**
Pending checks: **Assessed: {earned}/{available} points ({percent}%). Full-score range:
{minimum}–{maximum}/100 pending {checks}.** Never show an ordinary `{n}/100` headline while
pending.}

Read as: {profile}. {N/A checks and reason.}

{Scope, supplied purpose, governing conventions, and assumptions.}

{If a prior audit exists:}

## Since last audit

{Repository changes versus rubric/scoring changes. Generated reports are excluded from facts.}

Navigability  {earned}/{available}
Ownership     {earned}/{available}
Lifecycle     {earned}/{available}
Hygiene       {earned}/{available}

## Verdicts

| Principle | Verdict | Worst evidence |
|---|---|---|
| P1 Obvious entry point | 🟢/🟡/🔴/⚪/⏳ | … |
| P2 Consistent naming | … | … |
| P3 Smallest complete owner | … | … |
| P4 Project-folder threshold | … | … |
| P5 One source of truth | … | … |
| P6 Lifecycle separation | … | … |
| P7 Preserved history | … | … |
| P8 Visible abandonment | … | … |
| P9 Configuration discipline | … | … |
| P10 Git hygiene | … | … |

## What this costs today

{Two to four concrete consequences. Say plainly when nothing is currently costly.}

## What works

{One to three specific strengths worth preserving.}

## Structure now → recommended

{A compact annotated tree showing only affected areas and enough context to orient. Do not
include changes that depend on unanswered intent.}

## Findings

### F{n} · {title}

**Principle** — {P# Name and short rule.}

**Why it matters** — {Observable consequence, not a restatement.}

**In this repo** — {Paths and evidence. Never quote secret values.}

**Recommendation** — {Desired outcome; preserve documented repository constraints.}

**References checked** — {Exact searches and results.}

**Risk if wrong** — {Failure mode or “none found.”}

## Needs your call

{Only questions where intent decides whether a finding exists. Never ask which duplicate is
canonical here; uncontrolled duplication is already scored. Put naming and implementation
choices under “Decisions for the plan.” Maximum three questions.}

## Decisions for the plan

{Implementation choices that do not change the audit score, such as which duplicate becomes
canonical or whether independently owned projects should adopt workspace tooling.}

## Ranked next actions

{Highest leverage and safest first. Reference checks precede dependent moves.}

## Coverage and security limits

- {Unreadable, depth-pruned, opaque, or sampled paths.}
- {Whether a dedicated secret-content scan ran. Filename checks alone do not prove absence.}
- {Whether Git history, external schedules, symlinks, or deployment consumers were checked.}
