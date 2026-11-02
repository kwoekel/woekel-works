// Process names (lowercase) that only run while the screen is shared or recorded.
export const CAPTURE_PROCESSES: Record<string, string> = {
  cpthost: 'Zoom screen share',
  screencaptureui: 'macOS screen recording',
  screencapture: 'macOS screen recording',
  obs: 'OBS',
  obs64: 'OBS',
}

// Names the first capture process found in `ps -axo comm=` output, or null.
export const detectCapture = (psOutput: string, extra: string[] = []): string | null => {
  const running = new Set(
    psOutput.split('\n').map(line => (line.trim().split('/').pop() ?? '').toLowerCase()),
  )
  for (const [name, label] of Object.entries(CAPTURE_PROCESSES)) {
    if (running.has(name)) return label
  }
  return extra.find(name => running.has(name.toLowerCase())) ?? null
}
