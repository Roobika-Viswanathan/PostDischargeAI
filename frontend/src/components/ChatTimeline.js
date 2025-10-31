import { useEffect, useRef, useState } from 'react'
import { chatSession, fetchAgentLogs } from '../api'
import { estimateConfidence, formatCitationLabel } from '../utils/helpers'
import CitationModal from './CitationModal'
import ConfidenceMeter from './ConfidenceMeter'
import AgentHandOffGraph from './AgentHandOffGraph'

export default function ChatTimeline({ patient, onReset }) {
  const [sessionId, setSessionId] = useState(null)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [showCitations, setShowCitations] = useState(false)
  const [lastCitations, setLastCitations] = useState([])
  const [handoff, setHandoff] = useState('')
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function sendMessage(text) {
    if (!text) return
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: text }])
    try {
      const res = await chatSession({ session_id: sessionId, message: text, patient_name: patient?.patient_name })
      setSessionId(res.session_id)
      setMessages((m) => [...m, { role: 'assistant', agent: res.agent, content: res.response, citations: res.citations }])
      setLastCitations(res.citations || [])
      setHandoff(res.handoff || '')
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', agent: 'system', content: 'Error contacting server.' }])
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  async function exportLogs() {
    try {
      const blob = await fetchAgentLogs(true)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'agent_audit.ndjson'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch {}
  }

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Chat</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setShowCitations(true)} disabled={!lastCitations?.length}>View Citations</button>
          <button onClick={exportLogs}>Download Logs</button>
          <button onClick={onReset}>Change Patient</button>
        </div>
      </div>

      <div style={{ fontSize: 12, color: '#555', marginBottom: 8 }}>
        Patient: <strong>{patient?.patient_name}</strong> • Diagnosis: {patient?.diagnosis}
      </div>

      <AgentHandOffGraph handoff={handoff} />

      <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, minHeight: 280 }}>
        {messages.map((m, idx) => (
          <MessageBubble key={idx} data={m} />
        ))}
        <div ref={endRef} />
      </div>

      <form onSubmit={(e) => { e.preventDefault(); sendMessage(input) }} style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <input
          aria-label="Ask a question"
          placeholder="Ask a follow-up or report a symptom..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1, padding: 10 }}
        />
        <button disabled={loading || !input} type="submit">{loading ? 'Sending...' : 'Send'}</button>
      </form>

      <CitationModal open={showCitations} citations={lastCitations} onClose={() => setShowCitations(false)} />
    </div>
  )
}

function MessageBubble({ data }) {
  const isUser = data.role === 'user'
  const style = {
    margin: '6px 0',
    display: 'flex',
    justifyContent: isUser ? 'flex-end' : 'flex-start'
  }
  const bubble = {
    maxWidth: '75%',
    padding: 10,
    borderRadius: 8,
    background: isUser ? '#e3f2fd' : '#f1f8e9',
    border: '1px solid #ddd'
  }

  const label = data.agent === 'clinical' ? 'Clinical AI' : data.agent === 'receptionist' ? 'Receptionist' : 'System'
  const conf = data.citations ? estimateConfidence(data.citations) : null
  const inlineCites = (data.citations || []).slice(0, 3).map(formatCitationLabel).filter(Boolean).join(' ')

  return (
    <div style={style}>
      <div style={bubble}>
        {!isUser && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: 12, padding: '2px 6px', borderRadius: 999, background: '#eee' }}>{label}</span>
            {conf !== null && <ConfidenceMeter value={conf} />}
          </div>
        )}
        <div style={{ whiteSpace: 'pre-wrap' }}>{data.content}</div>
        {!isUser && inlineCites && (
          <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>{inlineCites}</div>
        )}
      </div>
    </div>
  )
}


