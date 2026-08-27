# {repo name} restructure plan — {YYYY-MM-DD}

**Status:** {ready / blocked by decisions}
**Companion:** `STRUCTURE-AUDIT-{YYYY-MM-DD}.md`
**Scope:** {whole repository / named area}
**Score:** {n}/100 ({band}){ or assessed range while checks remain pending}
**Coverage:** {n} approved · {n} declined · {n} deferred

---

## Why this plan

- {Concrete cost or risk from F#.}
- {Concrete cost or risk from F#.}
- {Omit generic rationale; use no more than four bullets.}

---

## Decisions taken

| Decision | Effect |
|---|---|
| {Owner-approved choice} | {What the plan will do} |
| {Deliberate exception} | {Constraint the executor must preserve} |

---

## Target structure

```text
{repo}/
├── {affected owner}/       {short annotation}
└── {affected area}/
    └── {planned path}      ← {current path}
```

{Show affected areas only. Omit this section when no structural layout changes.}

---

## Ownership map

| Question or subject | Canonical owner |
|---|---|
| {Fact, rule, implementation, or artifact} | `{path}` |

{Include only when the plan changes canonical ownership.}

---

## Change map

| # | Finding | Planned change | References | Risk |
|---|---|---|---|---|
| 1 | F{n} · P{n} {short title} | {End state} | {none / N, handled in phase N} | {low / medium / high} |

---

## Execution phases

### 1. {Imperative title}

**Covers:** F{n} · P{n} {name}

**Outcome:** {One sentence: consequence removed or end state created.}

**References:** {Exact search performed and result; name every reference handled here.}

**Assumes:** {shell/platform; omit when already stated for all phases.}

**Commands**

```bash
{Exact runnable commands with quoted real paths and no unresolved placeholders.}
```

**Verify**

```bash
{Behavioral test/build/check. File existence alone is insufficient for a move.}
```

**Rollback**

```bash
{Exact recovery for this phase alone; no destructive reset.}
```

{Before removing an untracked rebuildable artifact, add **Rebuild:** with its manifest and
exact rebuild command.}

### 2. {…}

{Repeat the same compact block. Keep each structural move independently verifiable and
reversible. Make the final phase run the repository's real tests/builds, review Git status,
and re-run the structure audit.}

---

## Acceptance criteria

- {Observable end state tied to F#.}
- {References updated and verified.}
- {Repository's actual tests/builds pass.}
- {Worktree contains only intended changes.}
- {New audit confirms no regression; separate repository improvement from rubric change.}

---

## Out of scope

| Finding | Call | Reason or revisit condition |
|---|---|---|
| F{n} {short title} | Declined — intentional | {Owner's reason} |
| F{n} {short title} | Deferred | {Condition for revisiting} |

{If none: `None.`}
