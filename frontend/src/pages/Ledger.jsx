import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Stamp, RefreshCw } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export default function Ledger() {
  const [checkpoints, setCheckpoints] = useState(null)
  const [publishing, setPublishing] = useState(false)
  const [message, setMessage] = useState('')

  const load = async () => {
    try {
      const res = await fetch(`${API}/ledger/checkpoints`)
      if (res.ok) setCheckpoints(await res.json())
      else setCheckpoints([])
    } catch { setCheckpoints([]) }
  }

  useEffect(() => { load() }, [])

  const publish = async () => {
    setPublishing(true)
    setMessage('')
    try {
      const res = await fetch(`${API}/ledger/checkpoint`, { method: 'POST' })
      const data = await res.json()
      if (res.ok) {
        setMessage(data.new
          ? `Checkpoint #${data.batch_index} published, sealing ${data.record_count} entries.`
          : `Nothing new since checkpoint #${data.batch_index} — the ledger is already up to date.`)
        load()
      } else {
        setMessage(data.detail || 'Could not publish a checkpoint.')
      }
    } catch {
      setMessage('Cannot reach the server.')
    }
    setPublishing(false)
  }

  const formatDate = (ts) => {
    if (!ts) return ''
    const d = new Date(ts.includes('T') ? ts : ts.replace(' ', 'T') + 'Z')
    if (isNaN(d)) return ts
    return d.toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div style={{ maxWidth: '760px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Public Checkpoints</h2>
      <p style={{ color: 'var(--color-muted)', fontFamily: 'var(--font-sans)', fontSize: '0.95rem', lineHeight: 1.7 }}>
        Every so often, CraftProof seals every certificate entry recorded so far into a single
        short fingerprint and publishes it here. Once a checkpoint is published, none of the
        entries it covers can be quietly changed — not even by us. If a single letter of a single
        entry were edited, its checkpoint would no longer match.
      </p>

      <div style={{ display: 'flex', gap: '0.8rem', alignItems: 'center', flexWrap: 'wrap', margin: '1.5rem 0' }}>
        <button className="btn btn-sm" onClick={publish} disabled={publishing}>
          <Stamp size={14} style={{ verticalAlign: '-2px', marginRight: '0.4rem' }} />
          {publishing ? 'Publishing…' : 'Publish a checkpoint'}
        </button>
        <button className="btn btn-outline btn-sm" onClick={load}>
          <RefreshCw size={14} style={{ verticalAlign: '-2px', marginRight: '0.4rem' }} />
          Refresh
        </button>
      </div>

      {message && (
        <div className="detail-section" style={{ marginBottom: '1.5rem' }}>{message}</div>
      )}

      {checkpoints === null && (
        <p style={{ color: 'var(--color-faint)' }}>Loading checkpoints…</p>
      )}

      {checkpoints && checkpoints.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: 'var(--color-faint)' }}>
          <p>No checkpoints published yet.</p>
          <p style={{ fontSize: '0.9rem' }}>Publish the first one to seal every entry recorded so far.</p>
        </div>
      )}

      {checkpoints && checkpoints.map(cp => (
        <div key={cp.batch_index} className="card" style={{ padding: '1.3rem 1.5rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Checkpoint #{cp.batch_index}</h3>
            <span style={{ fontFamily: 'var(--font-sans)', fontSize: '0.82rem', color: 'var(--color-faint)' }}>
              {formatDate(cp.created_at)}
            </span>
          </div>
          <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.88rem', color: 'var(--color-muted)', margin: '0.5rem 0 0.7rem' }}>
            Seals {cp.record_count} certificate {cp.record_count === 1 ? 'entry' : 'entries'}.
          </p>
          <code className="hash" title="The published fingerprint for this checkpoint">{cp.root_hash}</code>
        </div>
      ))}

      <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.88rem', color: 'var(--color-faint)', marginTop: '2rem' }}>
        Curious how this works? Read <Link to="/how-it-works">how verification works</Link>.
      </p>
    </div>
  )
}
