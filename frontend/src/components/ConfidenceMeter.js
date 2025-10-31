export default function ConfidenceMeter({ value }) {
  const pct = Math.round((value || 0) * 100)
  const color = pct >= 85 ? '#2e7d32' : pct >= 70 ? '#f9a825' : '#c62828'
  return (
    <div aria-label="confidence" title={`Confidence: ${pct}%`} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ width: 120, height: 8, background: '#eee', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color }} />
      </div>
      <span style={{ fontSize: 12, color: '#555' }}>{pct}%</span>
    </div>
  )
}


