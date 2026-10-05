import React from 'react'
import { Link } from 'react-router-dom'
import { PenLine, Link2, Stamp, ShieldAlert } from 'lucide-react'

const STEPS = [
  {
    icon: PenLine,
    title: 'The maker signs the piece into existence',
    body: `When an artisan registers a piece, they confirm it with a personal digital seal that
           only they can produce. Anyone can check the seal is genuine; nobody can imitate it.`,
  },
  {
    icon: Link2,
    title: 'Every handover is confirmed by the person letting it go',
    body: `A maker handing a piece to a gallery, or a gallery selling it to you, confirms that
           exact handover. Each confirmation is tied to the one before it, so the history reads
           as one unbroken thread — you cannot slip an entry in, remove one, or reorder them.`,
  },
  {
    icon: Stamp,
    title: 'The whole history is sealed into a public checkpoint',
    body: `Periodically every entry recorded so far is sealed into a single published fingerprint.
           After that, even CraftProof cannot quietly rewrite the past without the checkpoint
           refusing to match.`,
  },
  {
    icon: ShieldAlert,
    title: 'The certificate is re-checked every time it is opened',
    body: `Opening a certificate re-runs all of these checks from scratch. If anything at all has
           been altered, the green badge turns into a red warning that names the step that failed.`,
  },
]

export default function HowItWorks() {
  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>How verification works</h2>
      <p style={{ color: 'var(--color-muted)', fontFamily: 'var(--font-sans)', fontSize: '0.98rem', lineHeight: 1.75 }}>
        A certificate is only worth something if it cannot be faked or quietly edited later.
        Here is what stands behind the green "Verified Authentic" badge — in plain language.
      </p>

      <div style={{ margin: '2.5rem 0' }}>
        {STEPS.map(({ icon: Icon, title, body }, i) => (
          <div key={i} style={{ display: 'flex', gap: '1.2rem', marginBottom: '2rem', alignItems: 'flex-start' }}>
            <div style={{
              flexShrink: 0, width: '44px', height: '44px', borderRadius: '50%',
              background: 'var(--color-accent)', border: '1px solid var(--color-border)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-ink)'
            }}>
              <Icon size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.08rem', margin: '0.4rem 0 0.4rem' }}>{i + 1}. {title}</h3>
              <p style={{ margin: 0, fontFamily: 'var(--font-sans)', fontSize: '0.92rem', color: 'var(--color-muted)', lineHeight: 1.75 }}>
                {body}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="detail-section">
        <h4 style={{ marginTop: 0, marginBottom: '0.6rem' }}>What this does not promise</h4>
        <p style={{ margin: 0, lineHeight: 1.75 }}>
          CraftProof proves that a certificate's history is genuine and unaltered, and that each
          handover was confirmed by the person who made it. It cannot tell you that the physical
          object in your hands is the one the certificate describes — that link is the tag or
          sticker attached to the piece. Treat a certificate the way you would a signed receipt:
          strong evidence, honestly kept.
        </p>
      </div>

      <p style={{ fontFamily: 'var(--font-sans)', fontSize: '0.9rem', color: 'var(--color-faint)', marginTop: '2rem' }}>
        You can browse the published <Link to="/ledger">checkpoints</Link>, or
        {' '}<Link to="/">look up a certificate</Link> by its code.
      </p>
    </div>
  )
}
