import { expect, test } from 'claude-code/testing'

const setup = ($: any, on: any, answer: any, box = '') => {
  const seen: any = {}
  const cells: any = {}
  on('state.get', (_: any, e: any) => ({ value: cells[e.key] ?? { value: false, version: 0 } }))
  on('state.set', (_: any, e: any) => {
    const version = (cells[e.key]?.version ?? 0) + 1
    cells[e.key] = { value: e.value, version }
    return { value: { isSet: true, version } }
  })
  on('store.get', () => ({ value: undefined }))
  on('store.set', () => ({ value: undefined }))
  on('command.register', () => ({ value: { command: 'tidy' } }))
  on('session.start', (_: any, e: any) => ({ cwd: e.cwd }))
  on('prompt.read', () => ({ value: { text: box, cursor: 0 } }))
  on('model.complete', (_: any, e: any) => { seen.prompt = JSON.stringify(e); return { value: answer } })
  on('prompt.fill', (_: any, e: any) => { seen.fill = e.text; return { isFilled: true } })
  return seen
}

test('tidies typed text into the prompt box', async ($, on) => {
  const seen = setup($, on, { isAnswered: true, text: 'Goal: x\n', usage: {} })
  const r = await $.command.run({ command: 'tidy', args: 'messy thoughts' } as any)
  expect(seen.prompt).toContain('messy thoughts')
  expect(seen.fill).toBe('Goal: x')
  expect(r.text).toContain('Tidied')
})

test('empty input explains itself and calls no model', async ($, on) => {
  const seen = setup($, on, { isAnswered: true, text: 'no', usage: {} })
  const r = await $.command.run({ command: 'tidy', args: ' ' } as any)
  expect(seen.prompt).toBe(undefined)
  expect(r.text).toContain('Type your brain dump')
})

test('a failed call leaves the prompt box alone', async ($, on) => {
  const seen = setup($, on, { isAnswered: false, reason: 'empty-reply' }, 'draft')
  const r = await $.command.run({ command: 'tidy', args: '' } as any)
  expect(seen.fill).toBe(undefined)
  expect(r.text).toContain('unchanged')
})

test('the Tidy button tidies the prompt box', async ($, on) => {
  const seen = setup($, on, { isAnswered: true, text: 'Goal: y', usage: {} }, 'loose draft')
  on('ui.toast', () => ({ value: undefined }))
  const ui = await $.ui.mount({ plugin: 'tidy', component: 'AbovePrompt', surface: 'desktop', props: { hasSurvey: false, bodyColumns: 80 } } as any)
  await ui.press({ key: 'tidy' })
  expect(seen.fill).toBe('Goal: y')
  await ui.unmount()
})

test('the bar folds down and back', async ($, on) => {
  setup($, on, { isAnswered: true, text: 'x', usage: {} })
  const BAND = { plugin: 'tidy', component: 'AbovePrompt', surface: 'desktop', props: { hasSurvey: false, bodyColumns: 80 } } as any
  // The stand-in state doesn't redraw by itself, so each step mounts afresh.
  let ui = await $.ui.mount(BAND)
  await ui.press({ key: 'fold' })
  await ui.unmount()
  ui = await $.ui.mount(BAND)
  expect(await ui.find({ key: 'tidy' } as any)).toBeFalsy()
  await ui.press({ key: 'unfold' })
  await ui.unmount()
  ui = await $.ui.mount(BAND)
  expect(await ui.find({ key: 'tidy' } as any)).toBeTruthy()
  await ui.unmount()
})
