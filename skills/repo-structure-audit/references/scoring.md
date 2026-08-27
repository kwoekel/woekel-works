# Scoring and ranking

## Contents

- [Weights](#weights)
- [Deductions](#deductions)
- [Not applicable](#not-applicable)
- [Pending checks](#pending-checks)
- [Calculate totals](#calculate-totals)
- [Verdicts and bands](#verdicts-and-bands)
- [Action ranking](#action-ranking)
- [Repeat audits](#repeat-audits)

## Weights

| Group | Check | Points |
|---|---|---:|
| Navigability | C1 Entry point and navigability | 15 |
|  | C2 Naming consistency | 10 |
| Ownership | C3 Placement and smallest owner | 10 |
|  | C4 Project-folder threshold | 8 |
|  | C5 One source of truth | 7 |
| Lifecycle | C6 Lifecycle separation | 10 |
|  | C7 History and decisions | 8 |
|  | C8 Visible abandonment | 7 |
| Hygiene | C9 Configuration and credential exposure | 13 |
|  | C10 Git hygiene and artifacts | 12 |

## Deductions

Start each applicable check at full points. Deduct once for the overall condition, not per
file. Use only these steps:

| Deduct | Meaning |
|---:|---|
| 0% | Principle holds; deviations are deliberate and harmless |
| 20% | One low-consequence instance |
| 40% | Recurring pattern or one misleading instance |
| 60% | Principle is broadly absent |
| 80% | Absence already causes contradictions, wrong turns, or noisy operation |
| 100% | Principle is absent or the repository actively works against it |

Overrides:

- A verified tracked credential sets C9 to zero. Filename suspicion alone does not.
- No meaningful entry point caps C1 at 3/15.
- Do not calibrate toward an expected score distribution. Score only observed evidence.

## Not applicable

Mark a check N/A only when the profile cannot meaningfully exercise it. Redistribute its
points proportionally across the other checks in the same group so each resolved group still
totals 25. State the redistribution.

Cross-profile totals are directional, not a scientific comparison between unrelated
repository types.

## Pending checks

Pending means owner intent determines whether the check passes. Do not use it for choosing a
canonical copy, folder name, tool, or implementation.

When any check is pending, do not publish a single ordinary score out of 100. Report:

```text
Assessed: earned / available points = assessed percentage
Pending: check names and maximum points
Full-score range: earned to earned + pending maximum, out of 100
```

Example: resolved checks earn 61 of 86 available points and two unresolved checks total 14:

```text
Assessed: 61/86 (71%)
Full-score range: 61–75/100 pending C5 and C8
```

This range assumes pending checks can earn anywhere from zero to full points. Once the owner
answers, score those checks normally and publish the final total.

A deterministic duplicate is scored even when the canonical copy is unknown. An explicitly
marked archive is resolved and healthy. Hold a check only when the files cannot establish
whether a supposedly active or abandoned area is intentional.

## Calculate totals

Do not add scores manually. Encode each check as its earned percentage (`100`, `80`, `60`,
`40`, `20`, or `0`), `pending`, or `na`:

```bash
python3 <skill-dir>/scripts/calculate_score.py C1=80 C2=60 C3=100 C4=80 C5=40 \
  C6=80 C7=100 C8=pending C9=80 C10=60
```

Copy the assessed total, range/final score, and group lines exactly. The calculator performs
within-group N/A redistribution and excludes pending points from the assessed denominator.
Assign each underlying problem one primary deducted check so the same evidence is not counted
twice.

Common overlap defaults:

| Evidence | Primary deduction | Deduct another check only when… |
|---|---|---|
| Conflicting machine-readable values | C5 | C9 has a separate prose, credential, or environment-contract failure |
| Tracked or unignored generated artifact | C10 | C6 has other lifecycle ambiguity beyond Git tracking |
| Duplicate folders with naming variants | C5 | C2 shows a broader naming pattern beyond the duplicate |
| Dead route caused by an old name | C1 | C2 independently makes sibling names unpredictable |

## Verdicts and bands

| Verdict | Earned | Meaning |
|---|---:|---|
| 🟢 GREEN | ≥85% | Checked and clean |
| 🟡 YELLOW | 50–84% | Real drift, limited current cost |
| 🔴 RED | <50% | Current navigation, correctness, or maintenance cost |
| ⚪ N/A | — | Does not apply; explain why |
| ⏳ PENDING | — | Intent is required before scoring |

Apply total bands only after all checks are resolved:

| Score | Band |
|---:|---|
| 85–100 | Maintained |
| 70–84 | Solid |
| 50–69 | Drifting |
| 30–49 | Tangled |
| 0–29 | Unstructured |

## Action ranking

Use `recoverable points × multiplier` as a starting point, then apply safety and dependency
ordering.

| Multiplier | Issue |
|---:|---|
| 5× | Verified tracked credential |
| 4× | Missing entry point or confident dead route |
| 3× | Uncontrolled duplicate source, tracked build output, prose-derived configuration |
| 2× | Dead dependency tree, missing artifact ignore rule, scratch contamination, no Git |
| 1.5× | Overdue project owner or unmarked superseded material |
| 1× | Naming drift, confirmed disposable empty item, premature scaffolding |

Safety overrides arithmetic:

1. Rotate credentials first.
2. Run reference checks before moves.
3. Prefer cheap reversible corrections.
4. Never call a zero-byte or old authored file disposable without evidence.

## Repeat audits

Compare the newest prior audit with the current repository. Separate score movement caused by
repository changes from movement caused by rubric changes. Generated audit and plan files are
excluded from scanner facts and reference searches.
