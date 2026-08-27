# Restructure planning

Load only after Phase 1 when the user requests an exact plan.

## Resolve decisions

- Read the latest audit. Ask at most three unresolved intent questions at a time, with evidence
  and short choices.
- Accept owner answers as facts. Record declined and deferred work under **Out of scope**.
- Do not re-ask answered implementation choices.
- Recalculate pending checks with [scoring.md](scoring.md). State a final score only after all
  score-affecting intent is resolved.
- Do not change a finding's score because the owner selected a canonical copy, name, or tool.

## Use the review-first format

Use `assets/restructure-plan.template.md` in this order:

1. Status metadata
2. Why this plan
3. Decisions taken
4. Target structure
5. Ownership map, when ownership changes
6. Change map
7. Execution phases
8. Acceptance criteria
9. Out of scope

Keep the document dense and scannable:

- Limit **Why this plan** to concrete present-day costs.
- Put choices, mappings, and finding coverage in tables.
- Show only affected areas in the target tree.
- Use short labels in execution phases; omit narrative transitions and generic handoff prose.
- Do not repeat ground rules already enforced by the commands, verification, or rollback.

## Preserve the safety contract

Every execution phase must include:

| Field | Requirement |
|---|---|
| Covers | Finding and principle |
| Outcome | One plain-language consequence or end state |
| References | Exact checks and results |
| Commands | Runnable, quoted, real paths; no unresolved placeholders |
| Verify | Behavioral test, not file existence alone |
| Rollback | Recovery for this phase only |
| Rebuild | Required before removing an untracked rebuildable artifact |

Combine changes only when they share one outcome, verification boundary, and rollback. One
structural move remains independently reversible.

Resolve the root with `git rev-parse --show-toplevel`. Inspect status and stop if planned paths
overlap unrelated user changes. Never prescribe automatic stashing, destructive reset, or
broad recursive deletion. For non-Git targets, name a recoverable backup location before any
authored move and do not claim `git mv` is available.

Never infer that zero-byte, `.gitkeep`, generated-looking, or old authored material is safe to
delete. Confirm how rebuildable artifacts rebuild. Archive uncertain authored material;
recommend deletion only when the owner confirms it is obsolete.

## Order execution

1. Rotate exposed credentials; removal does not clean Git history.
2. Protect the starting state and unrelated changes.
3. Run reference checks before dependent moves.
4. Apply cheap, reversible corrections.
5. Perform structural moves one verification boundary at a time.
6. Apply disruptive conventions last.
7. Run real tests/builds, review status, and re-run the audit.

Every phase must leave the repository working. Separate score changes caused by implementation
from changes caused by a revised rubric.
