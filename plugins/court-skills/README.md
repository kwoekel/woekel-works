# Court Skills

Five skills for a parent in a custody or co-parenting case. They turn scattered texts,
emails, voice notes, and memories into an organized record that an attorney or custody
evaluator can trust. Everything is saved as plain markdown in a `court` folder, so any
AI app (Claude, Codex, ChatGPT) or person can read it.

| Skill | What it does | Say something like |
|---|---|---|
| [Incident Log](skills/incident-log/SKILL.md) | Logs an incident or co-parent message as a dated evidence entry | "log this", "this just happened" |
| [Timeline Builder](skills/timeline-builder/SKILL.md) | Builds one sourced timeline, tags what matters, lists gaps | "update my timeline" |
| [Narrative Writer](skills/narrative-writer/SKILL.md) | Drafts a calm, child-focused, cited narrative for an evaluator or attorney | "draft the narrative for the evaluator" |
| [Co-Parent Reply](skills/co-parent-reply/SKILL.md) | Drafts brief, firm replies to the other parent. Never sends | "help me reply to this" |
| [Attorney Packet](skills/attorney-packet/SKILL.md) | One-page attorney update, attorney log and costs, motion-prep packet | "prep for my lawyer call", "motion prep" |

They pair well with Case Forge's Evidence Review and Analyse Document skills
([CaseForgeHq/family-court-strategist](https://github.com/CaseForgeHq/family-court-strategist)).

## Install

Claude Code:

```
/plugin install court-skills --marketplace kwoekel/woekel-works
```

Or copy single skills:

```bash
cp -R woekel-works/plugins/court-skills/skills/<skill-name> ~/.claude/skills/   # Claude Code
cp -R woekel-works/plugins/court-skills/skills/<skill-name> ~/.codex/skills/    # Codex
```

## Ground rules built into every skill

- Organized drafts for an attorney to review, not legal advice.
- Never sends an email or message. Drafts only.
- Never invents facts. Uncertain dates are marked approximate or recollection.
- Past entries are never edited. Corrections are added as new entries.
- Files stay local.

## Credits

- Incident and communication templates, attribution standards, and the attorney log are
  adapted from Case Forge by Kyle Fischer
  ([CaseForgeHq/family-court-strategist](https://github.com/CaseForgeHq/family-court-strategist), MIT License).
- The timeline and statement-of-facts method is adapted from Anthropic's chronology skill
  ([anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal), Apache License 2.0),
  with law-firm steps removed.
- The reply method is BIFF (Brief, Informative, Friendly, Firm) from Bill Eddy, High Conflict Institute.
