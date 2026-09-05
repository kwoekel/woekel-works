# Structure principles

Use principles as the reason for findings; treat implementations as ecosystem-dependent.

**Guiding convention:** every subject in the ownership map has exactly one owner; agent
routers hold zero facts. `AGENTS.md` and `CLAUDE.md` are the primary agent routers.
`README.md` explains the repository to people; it is never a router or canonical
owner. P3 places the owner, P5 keeps it singular, and P1 keeps agent routers pointing rather
than asserting.

## Contents

- [Mental model](#mental-model)
- [P1 Obvious entry point](#p1--obvious-entry-point)
- [P2 Consistent naming](#p2--consistent-naming)
- [P3 Smallest complete owner](#p3--smallest-complete-owner)
- [P4 Project-folder threshold](#p4--project-folder-threshold)
- [P5 One source of truth](#p5--one-source-of-truth)
- [P6 Lifecycle separation](#p6--lifecycle-separation)
- [P7 Preserved history](#p7--preserved-history)
- [P8 Visible abandonment](#p8--visible-abandonment)
- [P9 Configuration discipline](#p9--configuration-discipline)
- [P10 Git hygiene](#p10--git-hygiene)

## Mental model

A repository is a boundary of ownership and history. Classify items by owner, purpose,
audience, authority, and lifecycle—not by file type or whether a human or AI created them.

```text
repository
├── human orientation what is this? (`README.md` when needed)
├── agent routes      where are governing sources? (`AGENTS.md`, `CLAUDE.md`)
├── active work        what does it produce or operate?
├── configuration      what controls behavior?
├── documentation      what must people understand?
├── generated output   what can a machine recreate?
└── history            what happened previously?
```

## P1 · Obvious entry point

**Rule:** A cold human can understand the repository, and an agent can reach governing
sources and active work, without searching.

Evidence of failure:

- No meaningful human orientation where the repository needs one.
- `AGENTS.md` or `CLAUDE.md` names missing paths or omits obviously active owners.
- In a multi-project repository, sampled projects have no local orientation.
- Three plausible artifacts cannot be reached through names alone—the clickable-tree test.

Do not require a README for a single self-explanatory file or a package already explained by
its parent documentation. A confident wrong agent route costs more than a missing route.

## P2 · Consistent naming

**Rule:** Names are predictable within each ownership boundary.

Look for three or more sibling styles, inconsistent dates, or near-identical names that cause
duplicate creation. Tool names, language conventions, and deliberate `_archive`-style markers
are exceptions. Consistency within a project matters more than enforcing one style across
unrelated ecosystems.

## P3 · Smallest complete owner

**Rule:** Information lives in the smallest area that completely owns it.

| Scope | Home |
|---|---|
| Repository-wide | Root or a root-owned area |
| One project/service/topic | Inside that owner |
| Shared by real consumers | A clearly named shared owner |
| Produced by one, consumed elsewhere | Source with producer; expose a documented interface |

Loose root files, buried global rules, and “shared” areas used by one project are leads. The
root should act as a map, not satisfy an arbitrary item limit.

An agent router that states a fact instead of pointing to its owner is a P3 finding: the fact
now has two homes and drifts silently. Score it here, not twice under P5. A README that
duplicates canonical detail is also misplaced, but remains human documentation rather than
becoming a router.

## P4 · Project-folder threshold

**Rule:** A folder becomes a project when the work has its own identity and lifecycle.

Signals include a distinct outcome, multiple related artifacts, independent status or
decisions, repeatable automation, or the ability to work inside it without understanding the
whole repository. Flag both overdue ownership and premature empty scaffolding.

`src/`, tests, scripts, config, docs, and assets are vocabulary, not a checklist. Follow the
profile and ecosystem. Independent projects in one repository do not automatically require
workspace tooling; integration claims and shared dependencies determine that need.

## P5 · One source of truth

**Rule:** Maintain a fact or implementation in one authoritative place; other locations point
to it or declare derivation.

Evidence includes conflicting config values, active/archive copies that both look current,
uncontrolled duplicate helpers or documents, and repeated guidance without precedence.
Byte-identical files establish copying but not the correct consolidation. Score the duplicate
finding now; ask which copy is canonical as a planning decision.

Generated copies are healthy when direction, source, and regeneration are explicit.

## P6 · Lifecycle separation

**Rule:** Authored, generated, historical, and disposable material are visibly distinct.

```text
Can it be recreated?
├── yes → usually ignore or rebuild; document exceptions
└── no
    ├── meaningful deliverable → retain with its owner
    └── uncertain/temporary → confirm before archive or removal
```

Leads include committed build output, caches in authored areas, runtime logs beside durable
documents, and deliverables stranded from their producer. Do not prescribe `tmp/` or another
folder name when repository policy defines a different lifecycle. A zero-byte file is not
automatically disposable; it may be a sentinel or intentional placeholder.

## P7 · Preserved history

**Rule:** Important decisions and superseded material remain findable and clearly historical.

Git, local archives, decision records, and dated audits are common implementations. Findings
include no recoverable history where loss matters, unmarked superseded material, project
audits far from their owner, or long-lived work represented by meaningless history alone.

Do not require formal decision logs for small projects. Archive uncertain authored material;
recommend deletion only after the owner confirms it has no continuing value.

## P8 · Visible abandonment

**Rule:** Anything no longer maintained says so; nothing dead presents itself as current.

Evidence includes a stated cadence contradicted by content dates, documentation for missing
workflows, or apparently active folders whose purpose implies maintenance but stopped.
Reference material is not stale merely because it is old. Explicitly retired content in a
clearly named archive passes this principle and does not require an owner question.
Live compatibility references may block a move, but they do not make the retirement marker
ambiguous; record them under reference risk or ownership instead of holding P8 pending.

Modification times are weak evidence. When the scanner reports clustered mtimes, use content
dates, dated filenames, and Git history or leave the check pending.

## P9 · Configuration discipline

**Rule:** Values controlling behavior are machine-readable; credentials are stored securely.

Findings include automation scraping values from prose, conflicting settings, or verified
credential material in tracked files. Documentation explaining configuration is healthy;
instruction files can legitimately be prose-as-behavior.

Do not prescribe `.env`, `.env.example`, or any particular secret/config convention against a
repository's governing policy. Require a documented environment contract in whatever safe
form that repository supports. Filename candidates are leads only. A dedicated redacted
secret scan is required before claiming the repository contains no embedded secrets.

Use P5 as the primary deduction for conflicting machine-readable values. Deduct P9 separately
only when another failure exists, such as prose being parsed as config, an unsafe credential,
or an undocumented environment contract.

## P10 · Git hygiene

**Rule:** Version control tracks authored decisions and intentional products, not accidental
machine output.

Findings include tracked rebuildable artifacts, missing applicable ignore rules, noisy runtime
output, abandoned dependency trees with manifests, and artifacts from an otherwise unused
ecosystem. Use `git check-ignore` semantics and `git ls-files`; presence alone is insufficient.

Lockfiles and documented vendored dependencies are not findings. Directories such as
`vendor/`, `build/`, `out/`, `env/`, and `target/` are ambiguous across ecosystems; the
scanner leaves them opaque, so confirm their role before recommending removal.
