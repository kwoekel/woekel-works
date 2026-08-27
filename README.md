# woekel-works

Claude Code skills, agents, and automations I build and use to eliminate manual
ops work — the kind that eats hours, causes errors, and doesn't scale.

I'm Kierra Woekel. My background is marketing and operations — strategic
partnerships, community engagement, and ops — and I use that lens to design
automation that solves real business problems. Everything here is something I
actually run.

## What's inside

| Folder | What it is |
|---|---|
| `skills/` | Claude Code skills — drop-in capabilities you can install and use |

### Skills

| Skill | What it does |
|---|---|
| [`repo-structure-audit`](skills/repo-structure-audit/) | Audits a repository's organization and produces an evidence-backed cleanup plan — navigation, ownership, duplication, archives, generated files, config, and Git hygiene. |

## Using a skill

Copy the skill folder into `~/.claude/skills/` and Claude Code picks it up
automatically:

```bash
git clone https://github.com/kwoekel/woekel-works.git
cp -R woekel-works/skills/repo-structure-audit ~/.claude/skills/
```

Each skill has its own README with what it does, when it fires, and anything it
needs installed.

## License

MIT — use it, change it, ship it.
