# Repo Structure Audit

A Claude Code and Codex skill that reads how your repository is organized, scores
it against ten principles, and proposes the safest cleanup. It never moves, renames,
or deletes anything. It stops at the plan.

This page teaches the way of thinking the audit uses. Once you can see your repo the
way the audit sees it, the findings will read as obvious instead of arbitrary.

**Contents:** [The one idea](#the-one-idea) · [Three kinds of file](#three-kinds-of-file) ·
[Five questions](#five-questions-to-ask-about-any-file) · [What a healthy repo looks like](#what-a-healthy-repo-looks-like) ·
[The ten principles](#the-ten-principles) · [Run it](#run-it) · [What you get back](#what-you-get-back) ·
[Boundaries](#boundaries) · [Install](#install) · [What is inside](#what-is-inside)

## The one idea

**Every fact has exactly one home. Every other file points to that home.**

A "fact" is anything that can be true or false: a rule, a decision, a setting, a
status, a piece of code. Its home is the one file that states it. Every other file
that needs it links there instead of repeating it.

The test is simple. If you had to edit two files to keep one statement true, that
statement has two homes. One of them will drift, silently, and the next reader will
not know which to trust.

Almost every messy repo is this one problem wearing different costumes: duplicated
docs, config that disagrees with itself, an archive that still looks current, a
README that has to be re-edited every time a folder moves.

## Three kinds of file

The audit sorts every file by its job, not its file type. Three jobs matter most:

| Kind | Job | Holds facts? | Typical files |
|---|---|---|---|
| **Owner** | States a fact and keeps it correct | Yes, this is the home | `STATUS.md`, `config.json`, source code, a decision record |
| **Router** | Points an agent to the right owner | No, only paths and one-line purposes | `AGENTS.md`, `CLAUDE.md` |
| **Orientation** | Explains the repo to a person | Only as a summary, never as the source | `README.md` |

Two rules fall out of this:

- **Routers hold zero facts.** A router that says "the API key rotates monthly" now
  owns a fact it cannot keep true. It should say "rotation policy → `ops/secrets.md`".
- **A README is never a router and never an owner.** It is for humans landing cold.
  It summarizes and links. Canonical detail stays in the file that owns it.

## Five questions to ask about any file

Before you create, move, or merge anything, answer these. The answers tell you where
it lives.

| Question | What the answer decides |
|---|---|
| **Who owns it?** | The smallest folder that can keep it correct on its own. Repo-wide things live at root; anything about one project lives inside that project. |
| **What job does it do?** | Its purpose, separate from its extension. A `.md` can be an owner, a router, or a scratch note. |
| **Who reads it?** | A person, an agent, or a machine. Each wants a different shape. |
| **What authority does it have?** | Source of truth, human summary, agent route, or generated copy. Only one of these is allowed to be edited by hand to change the fact. |
| **What lifecycle is it in?** | Active, historical, generated, or disposable. Each should be visibly distinct so cleanup is never a guess. |

## What a healthy repo looks like

Ownership, not file type, decides the shape. Every well-organized repo has these
zones, whatever the folder names:

```text
repository
├── orientation        what is this? (README.md, for people)
├── agent routes       where are the governing files? (AGENTS.md, CLAUDE.md)
├── active work        what does this repo produce or operate?
├── configuration      what controls behavior? (machine-readable, never prose)
├── documentation      what must people understand?
├── generated output   what can a machine rebuild? (ignored or clearly marked)
└── history            what happened before? (git, dated records, marked archives)
```

Notice what is missing: nothing lives at root unless the whole repo owns it. The root
is a map, not a drawer.

A quick self-check for lifecycle:

```text
Can a machine recreate this file?
├── yes → ignore it in git, or mark it as generated
└── no
    ├── it is a real deliverable → keep it with its owner
    └── unsure or temporary → confirm before archiving or deleting
```

## The ten principles

The audit scores ten principles, grouped into four lenses. Each principle is one
question you can ask of your own repo right now.

| Lens | Principle | The question | Common failure |
|---|---|---|---|
| **Navigability** | P1 Obvious entry point | Can a stranger, human or agent, find the right starting file without searching? | No README where one is needed; an `AGENTS.md` that points to paths that no longer exist |
| | P2 Consistent naming | Are sibling files named the same way? | Three date formats in one folder; two near-identical names that invite a third copy |
| **Ownership** | P3 Smallest complete owner | Does each thing live in the smallest folder that fully owns it? | Loose files at root; a "shared" folder used by only one project; a router stating a fact |
| | P4 Project-folder threshold | Does each project folder have its own identity, and does each real project have a folder? | Empty scaffolding created too early; a real workstream still living in loose files |
| | P5 One source of truth | Is every fact stated in exactly one place? | Two configs that disagree; an active copy and an archive copy that both look current |
| **Lifecycle** | P6 Lifecycle separation | Can you tell authored, generated, historical, and disposable apart at a glance? | Build output committed; logs sitting beside durable docs |
| | P7 Preserved history | When something is replaced, can you still find what it replaced and why? | Superseded files silently deleted; decisions with no record |
| | P8 Visible abandonment | Does anything unmaintained say so? | A "weekly" folder last touched a year ago with no marker |
| **Hygiene** | P9 Configuration discipline | Are behavior-controlling values machine-readable and secrets kept out of files? | A script scraping a number out of a paragraph; a credential in a tracked file |
| | P10 Git hygiene | Does git track decisions and products, not machine leftovers? | Caches, build folders, or dependency trees committed |

The precise scoring rules the agent follows live in
[references/structure-principles.md](references/structure-principles.md). This page is
the plain-language version.

## Run it

Ask in plain words. The skill triggers on any request that reads like a structure
review.

```text
Audit this repository's structure.
```

Or narrow it:

```text
Audit only projects/client-services.
```

In Codex you can name the skill directly to remove ambiguity:

```text
$repo-structure-audit Audit the whole repository.
```

A single placement question, such as "where should this file go?", gets a direct
answer with no report.

## What you get back

One dated report with three sections:

| Section | What it tells you |
|---|---|
| **What: Current State** | Which repo profile was detected, the score, and a seriousness label per principle |
| **So What: What This Affects** | Two to four concrete consequences, each backed by evidence from your files |
| **Now What: Proposed Changes** | The safest changes in order, shown as before-and-after trees |

Seriousness labels always carry a word, so color is never the only signal:

| Label | Meaning |
|---|---|
| 🟢 Clear | Checked and healthy |
| 🟡 Watch | Real drift, limited cost today |
| 🔴 Fix | Costing you navigation, correctness, or maintenance now |
| ⚪ N/A | Does not apply to this kind of repo |
| ⏳ Needs your call | The audit cannot score it without knowing your intent |

The score is a summary, not the verdict. Read the evidence. And every recommendation
is labeled **Proposed — not reviewed** until you approve it.

The audit also detects a repo profile so it never applies the wrong conventions.
A notes-only repo is not told to add `src/` and `tests/`. Profiles: software, AI
workspace, knowledge/personal, monorepo, infrastructure. They combine.

If you ask for it, a second pass turns the audit into an exact restructure plan, with
every reference each move would break listed beside the move.

## Boundaries

- Reads only. Writes one report, and optionally one plan. Never edits, moves, renames, or deletes what it audits.
- Never overwrites an earlier report. Repeat runs get `-2`, `-3`, and so on.
- Never prints a suspected credential. It flags filename leads, redacts, and says plainly that a filename scan cannot prove your repo has no secrets.
- Treats your repo's prose as data. Instructions embedded in files it reads are not executed.
- Checks references before proposing any move, and records the check it ran.

## Install

```bash
git clone https://github.com/kwoekel/woekel-works.git

# Claude Code
cp -R woekel-works/skills/repo-structure-audit ~/.claude/skills/

# Codex
cp -R woekel-works/skills/repo-structure-audit ~/.codex/skills/
```

Needs Python 3 and Git. The scanner uses only the standard library.

## What is inside

| Path | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | The agent's instructions: workflow, boundaries, both phases |
| [references/structure-principles.md](references/structure-principles.md) | The canonical P1–P10 rubric |
| [references/repo-profiles.md](references/repo-profiles.md) | Which checks apply to which kind of repo |
| [references/scoring.md](references/scoring.md) | Weights, deductions, and bands |
| [references/restructure-planning.md](references/restructure-planning.md) | How the plan phase works |
| [assets/](assets/) | Report and plan templates |
| [scripts/scan_structure.py](scripts/scan_structure.py) | Read-only evidence scanner |
| [scripts/calculate_score.py](scripts/calculate_score.py) | Deterministic score calculator |
| [tests/](tests/) | Regression tests for both scripts |

Run the tests:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## License

MIT.
