import { useState } from 'react'
import { lookupPatient } from '../api'

export default function PatientLookup({ onResolved }) {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await lookupPatient(name)
      setResult(res)
      if (res.status === 'ok' && res.matches?.length === 1) {
        onResolved(res.matches[0])
      }
    } catch (err) {
      setError('Lookup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: 16 }}>
      <h2>Find Your Discharge Report</h2>
      <p style={{ fontSize: 12, color: '#555' }}>
        This is an AI assistant for educational purposes only. Not a substitute for medical advice.
      </p>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8 }}>
        <input
          aria-label="Full name"
          placeholder="Enter your full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ flex: 1, padding: 10 }}
        />
        <button disabled={loading || !name} type="submit">{loading ? 'Searching...' : 'Search'}</button>
      </form>
      {error && <div role="alert" style={{ color: 'crimson', marginTop: 8 }}>{error}</div>}

      {result && (
        <div style={{ marginTop: 16 }}>
          {result.status === 'not_found' && <div>No patient found.</div>}
          {result.status === 'multiple' && (
            <div>
              <div>Multiple matches found. Please refine:</div>
              <ul>
                {result.matches.map((m, idx) => (
                  <li key={idx}><button onClick={() => onResolved(m)}>{m.patient_name}</button></li>
                ))}
              </ul>
            </div>
          )}
          {result.status === 'ok' && result.matches?.length === 1 && (
            <div style={{ marginTop: 8 }}>
              <h3>Summary</h3>
              <SummaryCard report={result.matches[0]} />
              <button style={{ marginTop: 12 }} onClick={() => onResolved(result.matches[0])}>Continue to Chat</button>
            </div>
          )}
        </div>
      )}
    </div>
  )}

function SummaryCard({ report }) {
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
      <div><strong>Diagnosis:</strong> {report.diagnosis}</div>
      <div><strong>Medications:</strong> {report.medications?.join(', ')}</div>
      <div><strong>Dietary:</strong> {report.dietary_restrictions?.join(', ')}</div>
      <div><strong>Follow-up:</strong> {report.follow_up_instructions?.join('; ')}</div>
      <div><strong>Warnings:</strong> {report.warning_signs?.join('; ')}</div>
      <div><strong>Discharge:</strong> {report.discharge_instructions?.join('; ')}</div>
    </div>
  )
}


