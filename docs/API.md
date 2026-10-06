# CraftProof Public API

Every certificate is readable over a simple JSON API so other websites, marketplaces
and gallery tools can verify authenticity without scraping. Verification endpoints are
open — no API key or account needed. Write endpoints use bearer-token auth.

Interactive docs: `https://craftproof-backend.onrender.com/docs` · raw schema: `/openapi.json`

## Base URL

```
https://craftproof-backend.onrender.com
```

## Verify a certificate

```
GET /api/verify/{code}
```

Plain-language verdict plus the full ownership history. `authentic: false` comes with a
human-readable `reason` when any record fails its integrity checks.

```bash
curl https://craftproof-backend.onrender.com/api/verify/KOODE0LL
```

```json
{
  "certificate_code": "KOODE0LL",
  "authentic": true,
  "reason": null,
  "piece": { "title": "Speckled tea bowl set", "maker": "Meera Krishnan", "..." : "..." },
  "current_holder": "Kalakriti Gallery",
  "history": [
    { "date": "2026-08-14T10:32:11.428706+00:00", "event": "Created by Meera Krishnan", "note": "Piece created" },
    { "date": "2026-09-02T09:10:03.117420+00:00", "event": "Meera Krishnan → Kalakriti Gallery", "note": "Delivered to the gallery in person" }
  ],
  "ledger": { "records": 2, "anchored": 2 },
  "verify_url": "/c/KOODE0LL"
}
```

## Full detail

| Endpoint | What it returns |
|---|---|
| `GET /c/{code}` | Complete certificate with per-record integrity checks, as the public page renders it |
| `GET /c/{code}/proof` | Signed fields, record hashes, Ed25519 signatures, signer public keys, Merkle inclusion proofs |
| `GET /ledger/checkpoints` | Published Merkle checkpoints sealing the record history |

## Writing data

Authenticate like the web app does, then call the same endpoints the dashboard uses:

```bash
TOKEN=$(curl -s -X POST https://craftproof-backend.onrender.com/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"meera@example.com","password":"craftproof123"}' \
  | jq -r .access_token)

curl -X POST https://craftproof-backend.onrender.com/pieces \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Handwoven wool scarf","materials":"Merino wool, natural dye"}'
```

## Embedding

Certificate URLs are stable public pages — point a QR code or an authenticity badge at
`https://craftproof-frontend.onrender.com/c/{code}`, or fetch `/api/verify/{code}` and render
your own verdict. CORS is open to all origins for the public endpoints.
