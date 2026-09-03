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

| Tool | Use it when | What you get |
| --- | --- | --- |
| [**Repo Structure Audit**](skills/repo-structure-audit/) | A repository feels hard to navigate, duplicated, or risky to reorganize | An evidence-backed audit and, when requested, a reference-safe cleanup plan |

The audit is read-only. It examines navigation, ownership, lifecycle, generated
files, configuration, and Git hygiene without moving or deleting the repository
it reviews.

## How it works

```mermaid
flowchart LR
    A[Your repository] --> B[Read-only scan]
    B --> C[Evidence review]
    C --> D[Scored audit]
    D --> E[Cleanup plan<br/>when requested]
```

The scanner collects facts. The skill checks those facts against the repository's
actual purpose and rules before it makes a recommendation.

## Install

Clone this repository, then copy the skill into the tool you use:

```bash
git clone https://github.com/kwoekel/woekel-works.git

# Claude Code
cp -R woekel-works/skills/repo-structure-audit ~/.claude/skills/

# Codex
cp -R woekel-works/skills/repo-structure-audit ~/.codex/skills/
```

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
