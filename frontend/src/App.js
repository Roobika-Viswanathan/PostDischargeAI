import { useEffect, useState } from 'react'
import { health } from './api'
import PatientLookup from './components/PatientLookup'
import ChatTimeline from './components/ChatTimeline'

export default function App() {
  const [ready, setReady] = useState(false)
  const [patient, setPatient] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    health().then(() => setReady(true)).catch(() => setError('Backend not reachable'))
  }, [])

  if (!ready) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Medical AI Assistant</h2>
        {error ? <div role="alert" style={{ color: 'crimson' }}>{error}</div> : <div>Loading...</div>}
      </div>
    )
  }

  return (
    <div style={{ fontFamily: 'system-ui, Segoe UI, Arial, sans-serif' }}>
      <Header />
      {!patient ? (
        <PatientLookup onResolved={setPatient} />
      ) : (
        <ChatTimeline patient={patient} onReset={() => setPatient(null)} />
      )}
      <Footer />
    </div>
  )
}

function Header() {
  return (
    <header style={{ padding: 12, borderBottom: '1px solid #eee', display: 'flex', gap: 12, alignItems: 'center' }}>
      <img src="/src/assets/logo.svg" alt="Logo" width={28} height={28} />
      <strong>Medical AI Assistant</strong>
      <span style={{ fontSize: 12, color: '#666' }}>Post-Discharge (Nephrology) POC</span>
    </header>
  )
}

function Footer() {
  return (
    <footer style={{ padding: 12, borderTop: '1px solid #eee', fontSize: 12, color: '#666', textAlign: 'center' }}>
      This is an AI assistant for educational purposes only. Not medical advice.
    </footer>
  )
}


