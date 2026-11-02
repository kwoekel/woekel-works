# Share Shield

A Claude Code mod that blurs secrets and personal info in the chat while your
screen is being shared or recorded. It turns on by itself when sharing starts
and off when it ends.

## Install

At the prompt of a Claude Code terminal session:

```
/plugin install share-shield --marketplace kwoekel/woekel-works
```

From a shell:

```bash
claude plugin install share-shield --marketplace kwoekel/woekel-works
```

In the desktop app: click + next to the prompt box, then Plugins, Add
marketplace with `kwoekel/woekel-works`, then Add plugin.

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
