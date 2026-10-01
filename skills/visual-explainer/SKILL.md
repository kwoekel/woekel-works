---
name: visual-explainer
description: "Explain concepts, workflows, systems, and changes through visuals, clear headings, and short bullets. Use for /explain, walkthroughs, visual explanations, or ADHD-friendly breakdowns. Skip simple facts and routine status updates."
---

# Visual Explainer

Make complex ideas easy to see, scan, and understand. Support people who prefer
visual, ADHD-friendly explanations without assuming their expertise or needs.

## Presentation

Prefer concise explanations that are easy to scan.

- Use headings, bullets, whitespace, and visuals where they improve understanding.
- Let visuals carry relationships and detail; use prose to clarify what they cannot show.
- Include context, definitions, or examples when they help.
- Match the depth and structure to the content. Remove filler and repetition.

## Choose a visual

| To explain… | Use… |
|---|---|
| Parts, folders, or hierarchy | Annotated tree |
| Steps, routing, or decisions | Flow diagram |
| Options, differences, or mappings | Compact comparison table |
| A change | Before/after diagram or table |
| Events over time | Timeline |
| Quantities or trends | Chart with labeled units |

Use ASCII or Mermaid when supported. Use an interactive visual when exploring
scenarios benefits from it and the environment supports it. Choose a format
that renders clearly in the current interface.

Headings and bullets support the visual; they do not replace it when explaining
relationships or flow. Split wide or tangled visuals into small, labeled parts.
Do not add decorative visuals to a one-line answer.

## Keep it clear

- Use everyday words. Define unfamiliar terms briefly on first use.
- Label parts and connections so the visual can be understood on its own.
- Pair status symbols with text; never rely on color alone. Explain ambiguous
  symbols with a short legend, without listing ordinary tree connectors.
- Show relevant limits, uncertainty, or costs when they affect understanding.
- Avoid fixed emoji schemes, repeated takeaway headings, and unnecessary sections.

## Explain changes and choices

- Show what changes, where it fits, and its practical effect.
- Separate observed facts from recommendations; label unapproved changes
  **Proposed**.
- When a decision is needed, show concise options and meaningful tradeoffs in
  a small table or bullets. Prefer a choice control if available; otherwise
  ask a short question. Do not ask again for decisions already authorized.

## Using the skill

- `/explain [topic]`: explain the named topic visually.
- `/explain`: explain the current discussion visually.

## Where visuals belong

- **Active file:** when working on a file whose content would benefit from
  visuals, add them there beside the relevant content. Use a format the file
  supports and keep the edit within the current task.
- **Chat:** when no file is being worked on, or the explanation does not belong
  in that file, respond in chat.
- **Separate file:** create one only when asked to save or export. Use the
  requested destination or the project's output folder. Otherwise, use
  `docs/explainers/` at the verified Git root; outside a repository, ask where
  to save.
