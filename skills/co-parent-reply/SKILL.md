---
name: co-parent-reply
description: Draft a calm reply to a message from the co-parent (text, email, or co-parenting app), and offer to log the incoming message. Use when the user pastes a message from the other parent, says "help me respond", "what do I say back", or "draft a reply".
---

# Co-Parent Reply Helper

**Court folder:** `court/` below means whichever folder the user chose, recorded once as `court-folder:` in that folder's or the workspace's agent instructions. If unknown, ask once and record it. Never create a second one.

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
4. **Don't:** defend the user's character, answer every accusation, apologize for things the user didn't do, make admissions, discuss the case, or mention the other parent's behavior. If an accusation is false and must be addressed, one line: "I disagree with that description."
5. **Offer a second, shorter version** if the first is more than 4 sentences.
6. **Save** the incoming message and the draft to `court/replies/YYYY-MM-DD-short-title.md`.
7. **Offer to log it** as a communication with the Incident Log skill (especially if it's tagged 🔴 or 🟡).

## Output

```markdown
> Organized draft for your attorney to review, not legal advice.

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

- **Never send.** The user copies and sends it.
- Write in the user's voice, plain and neutral. No legal jargon.
- If the user's own draft is angry, don't lecture. Offer a calmer version side by side.
- **Privacy.** Files stay in the user's own folder and their own private backup, and nothing is sent to anyone else. Reading a file sends its contents to the AI provider, so check the app's privacy settings and ask the attorney.
- **No unattended tidying.** Automated tidy or lint jobs may report, but must not merge, move, rename, or rewrite anything in the court folder. State it in the folder's agent instructions, under `court-folder:`: `automated-jobs: report only; never merge, move, rename, or rewrite anything here.`

---
Source: BIFF response method (Brief, Informative, Friendly, Firm) from Bill Eddy, High Conflict Institute. Written for this kit; communication logging matches the Case Forge communication template (CaseForgeHq/family-court-strategist, MIT License).
