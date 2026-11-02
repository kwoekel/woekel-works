export type Mode = 'auto' | 'on' | 'off'

declare module 'claude-code' {
  interface PluginState {
    'share-shield': {
      mode: Mode
      detected: string | null
      pausedFor: string | null
    }
  }
}
