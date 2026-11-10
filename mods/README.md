# Mods

Mods change how Claude Code looks and behaves. These are mine. Each one has its
own copy-paste steps below. You paste them into the prompt box of a Claude Code
session (the Code tab in the Claude desktop app, or a terminal session).

## Before you start

- You need Claude Code 2.1.287 or newer. The Claude desktop app needs 2.1.286 or
  newer. To check, type `/status` in a Code session and read the **Claude Code** row.
- A mod runs with your permissions. Read a mod before you install it, and install
  only from people you trust. The code for each mod is in its folder here.

## Step 1: add my mods (once)

Paste this and press Enter:

```
/plugin marketplace add kwoekel/woekel-works
```

Claude Code replies `Successfully added marketplace: woekel-works`.

## Step 2: install the mod you want

Paste the line for that mod and press Enter. Claude Code opens the plugin panel
on that mod. Pick where to install it (**user** works in all your projects), and
confirm. If it says `Run /reload-plugins to apply.`, close the panel, or type
`/reload-plugins`.

### Share Shield

Blurs keys, passwords, emails, phone numbers and card numbers in the chat while
you share your screen or record it.

```
/plugin install share-shield@woekel-works
```

Zoom sharing, macOS screen recording and OBS switch it on by itself. In Google
Meet or Teams, type `/shield on`. More controls: [Share Shield](share-shield/).

### Tidy

Turns a messy brain dump into clear instructions in your prompt box. You read
it, edit it, then send it. Nothing sends until you do.

```
/plugin install tidy@woekel-works
```

Type or paste your brain dump, then click **✦ Tidy** above the prompt box or type
`/tidy`. More controls: [Tidy](tidy/).

## If a step doesn't work

- Type `/plugin`, open the **Marketplaces** tab and check that `woekel-works` is
  listed. Then open **Discover** and pick the mod from there.
- In the Claude desktop app, you can also click **+** next to the prompt box and
  choose **Add plugins** (or **Plugins**, then **Browse plugins**) to browse the
  mods from marketplaces you have already added.
- Type `/plugin`, open the **Installed** tab and check the mod is switched on.
- Still stuck? [Open an issue](https://github.com/kwoekel/woekel-works/issues).
