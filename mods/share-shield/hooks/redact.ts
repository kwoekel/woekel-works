// Masks secrets and personal details in text, keeping the text's shape.

const blot = (s: string) => '█'.repeat(Math.min(Math.max(s.length, 4), 16))

const luhn = (digits: string) => {
  let sum = 0
  for (let i = 0; i < digits.length; i++) {
    let d = Number(digits[digits.length - 1 - i])
    if (i % 2 === 1) {
      d *= 2
      if (d > 9) d -= 9
    }
    sum += d
  }
  return sum % 10 === 0
}

type Rule = [RegExp, (match: string, ...groups: string[]) => string]

const RULES: Rule[] = [
  // PEM private keys
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(-----END [A-Z ]*PRIVATE KEY-----|$)/g, () => '-----PRIVATE KEY ████████-----'],
  // Known token formats
  [/\b(?:sk|pk|rk)[-_](?:live|test|ant|proj)?[-_]?[A-Za-z0-9_-]{16,}/g, blot],
  [/\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})/g, blot],
  [/\bxox[abprs]-[A-Za-z0-9-]{10,}/g, blot],
  [/\b(?:AKIA|ASIA)[0-9A-Z]{16}\b/g, blot],
  [/\bAIza[0-9A-Za-z_-]{35}\b/g, blot],
  [/\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}/g, blot],
  [/\b(Bearer|Basic|Token)\s+[A-Za-z0-9._~+/=-]{12,}/g, (_, kind) => `${kind} ${blot('xxxxxxxxxxxx')}`],
  // Credentials inside URLs
  [/\b([a-z][a-z0-9+.-]*:\/\/)([^\s:/@]+):([^\s/@]+)@/gi, (_, scheme, user) => `${scheme}${user}:${blot('xxxx')}@`],
  // key = value secrets (env files, JSON, YAML, CLI flags)
  [
    /\b([A-Za-z0-9_.-]*(?:password|passwd|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|private[_-]?key|credential)s?[A-Za-z0-9_.-]*)(["']?\s*[:=]\s*["']?)([^\s"',;]{6,})/gi,
    (_, key, sep, value) => `${key}${sep}${blot(value)}`,
  ],
  // Personal details
  [/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, blot],
  [/\b\d{3}-\d{2}-\d{4}\b/g, blot],
  [/\b\d(?:[ -]?\d){12,18}\b/g, m => (luhn(m.replace(/\D/g, '')) ? blot(m) : m)],
  [/(?:\+\d{1,3}[\s.-]?)?\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b/g, blot],
]

export const redact = (text: string): string =>
  RULES.reduce((out, [pattern, fn]) => out.replace(pattern, fn as (m: string) => string), text)

// Redacts every string inside a value, keeping its structure and types.
export const redactDeep = <T>(value: T): T => {
  if (typeof value === 'string') return redact(value) as T
  if (Array.isArray(value)) return value.map(redactDeep) as T
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, redactDeep(v)])) as T
  }
  return value
}
