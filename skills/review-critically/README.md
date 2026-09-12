# Review Critically

A Claude Code and Codex skill for independent, evidence-led review of plans,
documents, designs, workflows, and other artifacts.

It checks whether the work solves the real problem—not whether it merely looks
complete or follows familiar conventions. Findings distinguish what was observed,
inferred, externally benchmarked, and still unknown.

## Use it when

- you want a skeptical second opinion or gap analysis;
- a plan needs to be tested against its intended outcome;
- an established approach may be hiding assumptions or trade-offs;
- current standards or external evidence materially affect the conclusion.

This is not a proofreading skill. It reviews the approach, evidence, risks,
alternatives, and success test.

## Run it

Ask in plain words:

```text
Review this plan critically against the problem it is meant to solve.
```

Or invoke it directly in Codex:

```text
$review-critically Review the attached proposal.
```

## What you get back

The review leads with a direct conclusion, then covers what holds up, ranked gaps,
missing perspectives, relevant external benchmarks, credible alternatives, and the
smallest useful next steps.

The skill remains read-only. It does not rewrite or implement the artifact unless
you make a separate request.

## Install

```bash
git clone https://github.com/kwoekel/woekel-works.git

# Claude Code
cp -R woekel-works/skills/review-critically ~/.claude/skills/

# Codex
cp -R woekel-works/skills/review-critically ~/.codex/skills/
```

## License

MIT.
