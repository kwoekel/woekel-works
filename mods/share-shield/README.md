# Share Shield

A Claude Code mod that blurs secrets and personal info in the chat while your
screen is being shared or recorded. It turns on by itself when sharing starts
and off when it ends.

## Install

Paste these into the prompt box of a Claude Code session, one at a time (the first one is only needed once):

```
/plugin marketplace add kwoekel/woekel-works
```

```
/plugin install share-shield@woekel-works
```

Claude Code opens the plugin panel on the mod. Pick a scope, confirm, and
type `/reload-plugins` if it asks. Full steps: [Mods](../README.md).

Mods need Claude Code 2.1.287 or newer (2.1.286 in the desktop app). A mod runs
with your permissions, so read it before you install it.

## What it detects (macOS)

| Signal | Process |
|---|---|
| Zoom screen share | `CptHost` |
| macOS / QuickTime screen recording | `screencaptureui`, `screencapture` |
| OBS | `OBS` |

Google Meet, Teams and other browser sharing are not detected yet: use
`/shield on`. Add more process names in the mod's `extraProcesses` setting.

## What it blurs

API keys and tokens (Anthropic, OpenAI, GitHub, Slack, AWS, Google, Stripe),
JWTs, Bearer headers, private keys, passwords in URLs, `password=` and
`API_KEY=` style values, emails, phone numbers, SSNs and card numbers.

It covers Claude's chat: messages, tool calls, tool output, command output and
other mods' panes. Other apps on your screen are not touched.

## Controls

- `/shield on`, `/shield off`, `/shield auto` (default), `/shield status`
- **Show for this share** in the band above the prompt unblurs until that share ends.
