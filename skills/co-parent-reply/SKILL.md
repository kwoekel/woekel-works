---
name: co-parent-reply
description: Draft a calm reply to a message from the co-parent (text, email, or co-parenting app), and offer to log the incoming message. Use when the user pastes a message from the other parent, says "help me respond", "what do I say back", or "draft a reply to him/her".
---

# Co-Parent Reply Helper

In a high-conflict case, every message may end up in front of a judge. This skill drafts replies that are short, calm, and protect the user, and it never sends them.

> Organized draft for your attorney to review, not legal advice.

## Steps

1. **Read the incoming message.** Separate what actually needs an answer (dates, pickups, school, medical, money) from provocation, accusations, and bait.
2. **Check for red flags first.** If the message mentions court, lawyers, a change to custody or the schedule, relocation, threats, or the children's safety, say so at the top: "This one may be worth showing your attorney before replying." Still offer a holding reply ("I received your message and will respond by [day].").
3. **Draft one reply using BIFF:**
   - **Brief:** a few sentences. Long replies give more to argue with.
   - **Informative:** only facts and logistics about the kids.
   - **Friendly:** a neutral, polite opening or close. No sarcasm.
   - **Firm:** clear answer, clear next step, no opening for more debate.
4. **Don't:** defend her character, answer every accusation, apologize for things she didn't do, make admissions, discuss the case, or mention the other parent's behavior. If an accusation is false and must be addressed, one line: "I disagree with that description."
5. **Offer a second, shorter version** if the first is more than 4 sentences.
6. **Save** the incoming message and the draft to `court/replies/YYYY-MM-DD-short-title.md`.
7. **Offer to log it** as a communication with the Incident Log skill (especially if it's tagged 🔴 or 🟡).

## Output

```markdown
> Draft only. Not sent.

**What needs an answer:** [1–3 bullets]
**What to ignore:** [bait, in neutral words]
**Attorney flag:** none | [reason]

**Draft reply:**
> ...

**Shorter version:**
> ...
```

## Rules

- **Never send.** The user copies and sends it herself.
- Write in the user's voice, plain and neutral. No legal jargon.
- If the user's own draft is angry, don't lecture. Offer a calmer version side by side.

---
Source: BIFF response method (Brief, Informative, Friendly, Firm) from Bill Eddy, High Conflict Institute. Written for this kit; communication logging matches the Case Forge communication template (CaseForgeHq/family-court-strategist, MIT License).
