export default function AgentHandOffGraph({ handoff }) {
  if (!handoff) return null
  return (
    <div style={{ fontSize: 12, color: '#555' }}>
      {handoff === 'receptionist->clinical' ? 'Routing to Clinical AI Agent...' : handoff}
    </div>
  )
}

