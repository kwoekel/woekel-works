import { expect, test } from 'claude-code/testing'

const SECRET = 'my key is sk-ant-api03-abcdefghijklmnopqrstuvwx and mail jane@example.com'

const message = (surface: 'terminal' | 'desktop') =>
  ({
    plugin: 'share-shield',
    surface,
    component: 'AssistantMessage',
    requestId: 'm1',
    props: { text: SECRET, isFirstOfReply: true },
  }) as const

const start = async ($: any, on: any, ps: string) => {
  on('command.register', () => ({ value: { command: 'shield' } }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: ps, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  on('ui.render', ($: any, e: any) => {
    const { Text } = $.ui.resolve(e)
    return <Text>{e.props.text}</Text>
  })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
}

test('blurs secrets while Zoom is sharing', async ($, on) => {
  await start($, on, '/Applications/zoom.us.app/Contents/Frameworks/cpthost.app/Contents/MacOS/CptHost\n')
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount(message(surface))
    const row = await ui.find({ type: 'Text', text: /my key/ })
    expect(row?.text).not.toContain('sk-ant')
    expect(row?.text).not.toContain('jane@example.com')
    await ui.unmount()
  }
})

test('leaves text alone when nothing is sharing', async ($, on) => {
  await start($, on, '/usr/libexec/replayd\n')
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount(message(surface))
    expect((await ui.find({ type: 'Text', text: /my key/ }))?.text).toBe(SECRET)
    await ui.unmount()
  }
})

test('detects OBS by its macOS process name', async ($, on) => {
  await start($, on, '/Applications/OBS.app/Contents/MacOS/OBS\n')
  const ui = await $.ui.mount(message('desktop'))
  expect((await ui.find({ type: 'Text', text: /my key/ }))?.text).not.toContain('sk-ant')
  await ui.unmount()
})

test("blurs another mod's pane while sharing", async ($, on) => {
  await start($, on, 'CptHost\n')
  const ui = await $.ui.mount({
    plugin: 'share-shield',
    surface: 'desktop',
    component: 'Pane',
    requestId: 'other-pane',
    props: {
      text: SECRET,
      title: 'Other',
      isFocused: false,
      bodyColumns: 40,
      placement: 'dock',
      scroll: { offset: 0, bodyRows: 20 },
      view: {},
    },
  } as any)
  const row = await ui.find({ type: 'Text', text: /my key/ })
  expect(row?.text).not.toContain('jane@example.com')
  await ui.unmount()
})
