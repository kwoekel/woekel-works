# repo-structure-audit

A Claude Code skill that audits how a repository is organized and produces an
evidence-backed cleanup plan — without touching a single file it audits.

## What it does

Answers one question: is this repo easy to navigate, safe to maintain, and
possible to reorganize without breaking live references?

It runs a scanner over the target, then reads the results as *evidence* rather
than conclusions. It covers:

- **Navigability** — can a newcomer find the right file from the entry point?
- **Ownership** — every subject has exactly one owner; routers point, they don't
  state facts. Two owners for one fact is a finding; so is a routing file that
  holds a fact instead of a pointer.
- **Lifecycle** — archives, dated files, generated reports, scratch folders.
- **Hygiene** — duplication, config sprawl, Git tracking of things that
  shouldn't be tracked, and credential *leads* (filename patterns, never values).

Output is a dated audit report, and optionally an exact restructure plan with
the reference updates each move requires.

## When it fires

- "Audit this repo's structure" / "is this repo a mess?"
- A scoped review of one subfolder
- Turning an existing audit into a concrete restructure plan
- A single placement or naming question — it answers directly instead of running
  a full audit

## What it will not do

- It never changes, moves, renames, or deletes the content it audits. It stops
  at the plan; you execute it with your normal workflow.
- It never overwrites a report — repeat runs get `-2`, `-3`, and so on.
- It never prints a suspected credential's value, and it says plainly that a
  filename scan cannot prove the absence of secrets.
- It treats repository prose as untrusted data and does not execute instructions
  embedded in the files it reads.

## Install

```bash
cp -R repo-structure-audit ~/.claude/skills/
```

Claude Code picks it up automatically on the next session.

## Requirements

Python 3 (standard library only — no packages to install) and `git` on PATH.

## Layout

| Path | What |
|---|---|
| `SKILL.md` | The skill itself — routing, boundaries, and both phases |
| `scripts/scan_structure.py` | The scanner; writes JSON, refuses to write inside the target |
| `scripts/calculate_score.py` | Turns findings into the scored profile |
| `references/` | Scoring model, repo profiles, structure principles, scan schema |
| `assets/` | Report templates for the audit and the restructure plan |
| `agents/openai.yaml` | Interface metadata for non-Claude runtimes |
| `tests/` | Unit tests for both scripts |

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## License

MIT — see the repository root.
