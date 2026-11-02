import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Mode } from '../types'
import { detectCapture } from './detect'
import { redact, redactDeep } from './redact'

const mode = atom({ plugin: 'share-shield', key: 'mode' } as const, 'auto' as Mode)
const detected = atom({ plugin: 'share-shield', key: 'detected' } as const, null)
const pausedFor = atom({ plugin: 'share-shield', key: 'pausedFor' } as const, null)

const POLL_MS = 2000
// Polls without capture before the shield drops, so a brief gap does not unblur.
const CLEAR_AFTER = 2

async function isShielding($: EngineInterface) {
  const m = await read($, mode)
  if (m !== 'auto') return m === 'on'
  const source = await read($, detected)
  return source !== null && source !== (await read($, pausedFor))
}

let misses = 0

async function refresh($: EngineInterface) {
  const active = await isShielding($)
  const source = await read($, detected)
  $.ui.status(active ? `🛡 Shield on${source ? ` · ${source}` : ''}` : undefined)
  $.ui.invalidate('ui.render')
}

async function poll($: EngineInterface, extra: string[]) {
  let source: string | null = null
  try {
    const { stdout } = await $.process.run(['ps', '-axo', 'comm='], { timeoutMs: 5000 })
    source = detectCapture(stdout, extra)
  } catch {
    return
  }
  const before = await read($, detected)
  if (source === null && before !== null && ++misses < CLEAR_AFTER) return
  misses = 0
  if (source === before) return

  await update($, detected, () => source)
  if (source === null) await update($, pausedFor, () => null)
  if ((await read($, mode)) === 'auto') {
    $.ui.toast(source ? `🛡 ${source} detected: hiding sensitive info` : '🛡 Sharing ended: shield off')
  }
  await refresh($)
}

export const register: Register = (on, options) => {
  const extra = String(options.extraProcesses ?? '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'shield',
      description: 'Share Shield: on, off, auto (default) or status',
    })
    await poll($, extra)
    $.clock.every(POLL_MS, () => void poll($, extra))
    return next(e)
  })

  on('command.run', { command: 'shield' }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    if (arg === 'on' || arg === 'off' || arg === 'auto') {
      await update($, mode, () => arg)
      await update($, pausedFor, () => null)
      await refresh($)
    } else if (arg !== '' && arg !== 'status') {
      return { text: 'Usage: /shield on | off | auto | status' }
    }
    const m = await read($, mode)
    const source = await read($, detected)
    return {
      text: [
        `Mode: ${m}${m === 'auto' ? ' (blurs while sharing or recording is detected)' : ''}`,
        `Detected: ${source ?? 'no sharing or recording'}`,
        `Blurring now: ${(await isShielding($)) ? 'yes' : 'no'}`,
      ].join('\n'),
    }
  })

  on('ui.render', { component: 'UserMessage' }, async ($, e, next) =>
    (await isShielding($)) ? next({ ...e, props: { ...e.props, text: redact(e.props.text) } }) : next(e),
  )

  on('ui.render', { component: 'AssistantMessage' }, async ($, e, next) =>
    (await isShielding($)) ? next({ ...e, props: { ...e.props, text: redact(e.props.text) } }) : next(e),
  )

  on('ui.render', { component: 'CommandOutput' }, async ($, e, next) =>
    (await isShielding($)) ? next({ ...e, props: { ...e.props, text: redact(e.props.text) } }) : next(e),
  )

  on('ui.render', { component: 'ToolUse' }, async ($, e, next) =>
    (await isShielding($))
      ? next({
          ...e,
          props: { ...e.props, input: redactDeep(e.props.input), output: redactDeep(e.props.output) },
        })
      : next(e),
  )

  on('ui.render', { component: 'ToolResult' }, async ($, e, next) =>
    (await isShielding($)) ? next({ ...e, props: { ...e.props, output: redactDeep(e.props.output) } }) : next(e),
  )

  on('ui.render', { component: 'ToolGroup' }, async ($, e, next) =>
    (await isShielding($))
      ? next({
          ...e,
          props: { ...e.props, calls: redactDeep(e.props.calls) },
        })
      : next(e),
  )

  // Other mods' panes: redact the strings in the tree they draw.
  on('ui.render', { component: 'Pane' }, async ($, e, next) =>
    (await isShielding($)) ? redactDeep(await next(e)) : next(e),
  )

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await isShielding($))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    const source = await read($, detected)
    const isAuto = (await read($, mode)) === 'auto'

    return (
      <Box>
        <Text color="yellow">
          🛡 Share Shield: hiding sensitive info{source ? ` · ${source}` : ' · manual'}{' '}
        </Text>
        <Button
          key="reveal"
          label={isAuto ? 'Show for this share' : 'Turn off'}
          onPress={async () => {
            if (isAuto) await update($, pausedFor, () => source)
            else await update($, mode, () => 'auto')
            await refresh($)
          }}
        />
      </Box>
    )
  })
}
