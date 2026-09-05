<div align="center">

# woekel works

**Less manual checking. Fewer loose ends. More room for the work that matters.**

Reusable Claude Code and Codex skills I build and run to make operations feel
lighter and reduce the need to remember every next step.

[![MIT License](https://img.shields.io/badge/license-MIT-111111.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/Python-3-3776AB.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-21%20passing-2E7D32.svg)](skills/repo-structure-audit/tests/)

</div>

## Start here

One skill so far: [**Repo Structure Audit**](skills/repo-structure-audit/). Use it
when a repository feels hard to navigate, full of duplicates, or risky to reorganize.
It reads your repo, scores it against ten principles, and proposes the safest
cleanup. It never moves or deletes anything.

To get value from the audit, you need its way of thinking. Here is the whole model in
four ideas.

### 1. Every fact has exactly one home

A fact is anything that can be true or false: a rule, a setting, a status, a decision.
It lives in one file. Every other file links there instead of repeating it. If you
must edit two files to keep one statement true, that statement has two homes, and one
of them is already drifting.

### 2. Files have jobs, not just types

| Kind | Job | Holds facts? | Examples |
|---|---|---|---|
| **Owner** | States a fact and keeps it correct | Yes | `STATUS.md`, `config.json`, code |
| **Router** | Points an agent to the right owner | No, only paths | `AGENTS.md`, `CLAUDE.md` |
| **Orientation** | Explains the repo to a person | Summary only | `README.md` |

Routers hold zero facts. A README is never a router and never the source of truth.

### 3. Ask five questions before placing anything

Who owns it? What job does it do? Who reads it? What authority does it have? What
lifecycle is it in? The answers decide the folder. The root is a map, not a drawer.

### 4. Active, generated, historical, and disposable must look different

If a machine can rebuild it, ignore it or mark it. If it was replaced, say so and keep
it findable. If it stopped being maintained, say that too. Cleanup should never be a
guess.

The audit turns these four ideas into ten scored principles, grouped as Navigability,
Ownership, Lifecycle, and Hygiene. The full lesson, the principle table, and what the
report looks like are in the
[skill README](skills/repo-structure-audit/README.md).

## How it works

```mermaid
flowchart LR
    A[Your repository] --> B[Read-only scan]
    B --> C[Evidence review]
    C --> D[Scored audit]
    D --> E[Cleanup plan<br/>when requested]
```

The scanner collects facts. The skill checks those facts against your repo's actual
purpose and conventions before it recommends anything. A notes-only repo is never
told to add `src/` and `tests/`.

## Install

Clone this repository, then copy the skill into the tool you use:

```bash
git clone https://github.com/kwoekel/woekel-works.git

# Claude Code
cp -R woekel-works/skills/repo-structure-audit ~/.claude/skills/

# Codex
cp -R woekel-works/skills/repo-structure-audit ~/.codex/skills/
```

Then ask in plain words: "Audit this repository's structure."

Python 3 and Git are the only requirements. The scanner uses the Python standard
library; no package install is needed.

## Why I built it

Good operations should make work easier to carry, not add another system to
remember. I build these tools for my own operating system first, then share the
parts that can help someone else work with less friction.

I'm Kierra Woekel. I bring 10+ years across marketing operations, strategic
partnerships, and community engagement to AI systems built for real business
operations.

## License

MIT — use it, adapt it, and ship what helps.
