# CraftProof — Landing Page Design Brief

*For the UI/UX designer. Everything you need to design the landing page is in
this document — no codebase knowledge required.*

---

## 1. What CraftProof is (one paragraph)

CraftProof lets artisans — potters, woodworkers, jewelers, painters — create a
tamper-proof **digital certificate of authenticity** for a handmade piece.
Each certificate gets a **QR code sticker** that goes on the physical object.
When the piece is sold to a gallery, and then to a customer, each handover is
cryptographically recorded. Anyone can scan the QR with their phone and
instantly see: *who made it, its full ownership history, and a
"Verified Authentic" seal* that cannot be faked or quietly edited.

The problem it solves: collectors of handmade goods currently have no way to
verify authenticity or provenance beyond "trust me." CraftProof makes trust
**checkable** — in about five seconds, with a phone camera.

## 2. Who it's for

| Audience | What they do | What they care about |
|---|---|---|
| **Makers** (primary signup) | Register pieces, print QR tags, hand off to galleries | Being recognized as the true maker; protecting their name from fakes |
| **Galleries / shops** (secondary signup) | Hold inventory, sell to customers | Offering proof of authenticity without paperwork |
| **Buyers / the public** (no signup, ever) | Scan a QR on an item they own or are about to buy | A quick, trustworthy answer: "is this real?" |

The landing page must speak to all three, but its two conversion goals are:
**makers sign up**, and **anyone verifies a piece**. Everything else is
supporting.

## 3. The Golden Rule (this is the brand)

> **Users never see the words "hash," "signature," "blockchain," "crypto," or
> "Merkle" anywhere in the product.** They see: "Verified ✓",
> "Certificate", "Ownership History", "Sealed in the public ledger". All the
> cryptography happens invisibly underneath.

The landing page must obey this too. Words like *tamper-proof*, *can't be
faked or edited*, and *publicly checkable* are fine. Words like *blockchain*
and *cryptographic* are not. If a phrase sounds like a crypto startup, cut it.
The vibe is craft studio, not fintech.

## 4. The one job of the landing page

A stranger should understand the product in **under 10 seconds** and be able
to do one of two things immediately:

1. **Verify a piece** — enter a code like `AB12CD34` (they'd normally scan a
   QR, but the web offers a code lookup box).
2. **Join as a maker or gallery** — one clear signup path.

Current headline (keep the sentiment, make it beautiful):
> **"Authenticity you can hold."**
> CraftProof lets you prove a handmade piece is genuine, and see its full
> ownership history — from the maker's hands to yours.

## 5. What's already built (so you know what we have to show)

- A working app: makers register pieces → each gets a QR + certificate code →
  transfers are recorded → anyone can open the public certificate page.
- The **public certificate page** is the product's crown jewel: a big green
  **"✓ VERIFIED AUTHENTIC"** badge, the piece's story, and a vertical
  **ownership timeline** ("Crafted by Meera Krishnan → Transferred to Kalakriti
  Gallery → Transferred to Jonathan Price") with "✓ Confirmed by [name]" on
  each step. If a record was tampered with, the badge turns into a red
  **"⚠ WARNING: ALTERED RECORD"** and the exact altered step is flagged.
- A public **Checkpoints** page (the "public ledger") and a plain-English
  **How it works** page.

**Real URLs you can play with right now:**

- Landing: https://craftproof-frontend.onrender.com
- A live verified certificate: https://craftproof-frontend.onrender.com/c/KOODE0LL
- How it works: https://craftproof-frontend.onrender.com/how-it-works
- Ledger: https://craftproof-frontend.onrender.com/ledger

(Note: the demo database resets on redeploy, so a code from the screenshots
may not resolve on the live site — the *pages* and their design are what
matter. The local screenshots in `docs/screenshots/` show real data.)

**Ready-made screenshots** (in this repo, `docs/screenshots/`) you may use in
the design as "real product" imagery:

- `13-certificate-verified.png` — the verified certificate page (hero material)
- `16-certificate-tampered.png` — the red tamper warning (great "what if
  someone fakes it?" visual)
- `06-piece-card-qr-tag.png` — a QR tag as the maker sees it
- `03-maker-dashboard.png`, `09-gallery-dashboard.png` — the two studio views

## 6. Content blocks we'd like (in rough priority order)

1. **Hero** — headline + subline + a strong visual. The most compelling
   hero visual is the **certificate page itself** (green seal + timeline),
   ideally presented as a tilted card or phone mockup next to a physical
   object (a pot, a chair) to sell the physical↔digital link. The QR sticker
   on the object → phone → certificate is the story to tell in one image.
2. **Verify box** — the "Verify a Piece" card: one monospace input
   (`e.g. AB12CD34`) + "Verify Certificate" button. Keep it on the landing
   page itself; it's the fastest route to the wow moment. Also say: "Scan the
   QR code on the item with your phone — no app needed."
3. **How it works in 3 steps** — plain language, e.g.:
   1. *The maker registers the piece* → gets a QR certificate to attach.
   2. *Every handover is confirmed and recorded* — maker → gallery → you.
   3. *Anyone can check it, forever* — scan the code, see the whole history,
      sealed so it can't be quietly altered.
4. **A "see a real certificate" visual** — embed or link an annotated mock of
   the verified certificate page. This is the product.
5. **The tamper story** — a short "What if someone fakes the history?"
   section showing the red altered-record state. This is CraftProof's
   differentiator: the system *catches* edits and shows it publicly.
6. **For makers / For galleries** — two audience cards with 2–3 benefit
   bullets each and a signup CTA ("Join CraftProof").
7. **Trust explainer** — one honest paragraph, plain language:
   > "Every time a piece changes hands, the person handing it over digitally
   confirms it — a tamper-proof mark that can't be forged or edited after the
   fact. All confirmations are also sealed into a public ledger, so even
   CraftProof can't quietly alter a piece's history without it being
   detectable."
8. **Footer** — links: How it works · Checkpoints · Sign up · (MIT license).

Do **not** invent pricing sections, testimonials, or feature grids — there is
no billing and no fake quotes in a student/demo project. Keep it honest:
it's a working product you can try right now.

## 7. Design system already in the app (match or deliberately improve it)

The app has a quiet, editorial, "artisan studio" aesthetic. The landing page
should feel like the same brand — you may elevate it, but don't rebrand.

**Colors** (CSS variables already in the app):

| Token | Value | Use |
|---|---|---|
| `--color-ink` | `#1a1814` | Primary text, solid buttons |
| `--color-text` | `#2c2925` | Body text |
| `--color-muted` | `#5f5a50` | Secondary text |
| `--color-faint` | `#8c887e` | Tertiary text |
| `--color-border` | `#e0ddd5` | Hairlines, card borders |
| `--color-surface` | `#fcfbf9` | Page background (warm off-white) |
| `--color-card` | `#ffffff` | Cards |
| `--color-accent` | `#f5f4f0` | Subtle panel background |
| `--color-success` / bg / border | `#2e7d32` / `#e8f5e9` / `#c8e6c9` | The green verified seal |
| `--color-error` / bg / border | `#c62828` / `#ffebee` / `#ffcdd2` | The red tamper warning |

No brand accent color exists yet — if you introduce one (e.g. a terracotta or
indigo), please specify it as a variable and keep it restrained.

**Typography:**

- Display/headings: **Playfair Display** (serif, italic available) —
  "CraftProof" wordmark is Playfair italic bold.
- UI/body: **Inter** (sans) — buttons, forms, labels, timeline.
- Codes/hashes: system monospace, letterspaced (certificate codes look like
  `AB12CD34`).
- Current scale is modest (h1 ≈ 2.8rem). The landing page may go bigger.

**Existing components** (reusable): cards with 8px radius and hairline border,
solid ink buttons with uppercase 0.85rem Inter labels (letterspacing 1px),
outline buttons, green/red status badges, the vertical timeline, monospace
"hash" code blocks. Full CSS: `frontend/src/index.css` in the repo.

**Illustration/photography direction:** warm paper tones, real craft
materials (clay, wood, silver), generous whitespace, hairline rules — think
gallery placard / letterpress, not SaaS gradient. Subtle is better than loud.

## 8. Tone of voice

- **Quiet confidence.** Workshop, not hype. Short sentences.
- Honest about what it does and doesn't do ("try it right now" is fine).
- Plain language a non-technical collector immediately gets.

## 9. Deliverables we need

1. Desktop (1440) **and** mobile (390) comps of the landing page.
2. A component spec: hero, verify card, step cards, audience cards, footer —
   with colors, type sizes, spacing tied to the tokens above.
3. The hero visual concept (we'll build it in CSS/SVG where possible; photo
   mockups welcome as references).
4. Any new tokens (accent color) documented for `index.css`.

## 10. Technical constraints

- Single React page (`Landing.jsx`) + CSS we'll add to `index.css`; no heavy
  libraries. Animation: subtle CSS only (fade/rise on scroll at most).
- Keep the verify input functional (navigates to `/c/CODE`) and keep real
  links: `/signup`, `/login`, `/how-it-works`, `/ledger`, and a live
  certificate link if the demo data is seeded.
- Responsive: the verify card and hero must stack cleanly at 768px.
- Accessibility: contrast ≥ WCAG AA, focus styles on the input/buttons,
  semantic headings.
