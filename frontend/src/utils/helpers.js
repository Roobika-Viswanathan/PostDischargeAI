export function formatCitationLabel(c) {
  const parts = []
  if (c.section) parts.push(String(c.section))
  if (c.page) parts.push(`p. ${c.page}`)
  return parts.length ? `[${parts.join('; ')}]` : ''
}

export function estimateConfidence(citations) {
  // If distance is provided, map inversely to confidence
  if (!citations || citations.length === 0) return 0.5
  const distances = citations
    .map(c => (typeof c.score === 'number' ? c.score : null))
    .filter(v => v !== null)
  if (distances.length === 0) return 0.6
  const d = Math.min(...distances)
  // distance ~ 0 (best), ~1+ (worse). Map to 0.6..0.95
  const conf = 0.95 - Math.min(0.35, Math.max(0, d) * 0.25)
  return Math.max(0.5, Math.min(0.98, conf))
}

