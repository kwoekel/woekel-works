# Tidy

A Claude Code mod that turns a messy brain dump into clear instructions in your
prompt box. You read it, edit it, then send it.

## Install

At the prompt of a Claude Code session:

```
/plugin install tidy --marketplace kwoekel/woekel-works
```

From a shell:

```bash
claude plugin install tidy --marketplace kwoekel/woekel-works
```

Mods need Claude Code 2.1.287 or newer (2.1.286 in the desktop app). A mod runs
with your permissions, so read this one before you install it.

## Use it

1. Type or paste your brain dump into the prompt box.
2. Click **✦ Tidy** above the prompt box, or type `/tidy`. You can also type
   `/tidy` followed by the text you want tidied.
3. The prompt box fills with the rewrite. Check it, edit it, then send it.

Tidy never sends anything for you. If you keep typing while it works, it leaves
your text alone and tells you to tidy again when you're ready.

## What it writes

Tidy asks Claude (Sonnet) to rewrite the dump with these sections, leaving out
any that have nothing in them:

- **Goal**: one sentence on what you want.
- **Steps**: a numbered list in the order the work should happen.
- **Keep in mind**: limits, preferences and things to avoid.
- **Finished when**: how you'll know it's done.
- **Still unclear**: questions the dump leaves open, including any conflicts.

It keeps your own words and every specific detail, and adds no facts, tools or
steps you didn't give. Each tidy is one model call on your plan.

## Controls

- **▾** folds the bar down to a small **▴ Tidy** tab. Click the tab to bring it
  back. Tidy remembers your choice.
