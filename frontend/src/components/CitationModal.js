import { useEffect } from 'react'

export default function CitationModal({ open, onClose, citations }) {
  useEffect(() => {
    function onEsc(e) { if (e.key === 'Escape') onClose?.() }
    if (open) window.addEventListener('keydown', onEsc)
    return () => window.removeEventListener('keydown', onEsc)
  }, [open, onClose])

  if (!open) return null
  return (
    <div role="dialog" aria-modal="true" style={backdrop} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>
        <h3>Source Citations</h3>
        {(!citations || citations.length === 0) && <div>No citations.</div>}
        <ul>
          {citations?.map((c, idx) => (
            <li key={idx}>
              {c.section ? <strong>{c.section}</strong> : 'Reference'} {c.page ? `(p. ${c.page})` : ''}
              {typeof c.score === 'number' ? ` • score: ${c.score.toFixed(3)}` : ''}
            </li>
          ))}
        </ul>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  )
}

const backdrop = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center'
}
const modal = {
  width: 'min(90vw, 560px)', background: 'white', borderRadius: 8, padding: 16
}


