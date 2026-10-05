#!/usr/bin/env python3
"""Independent verifier for a CraftProof certificate.

Fetches /c/{code}/proof and re-checks everything locally: record hashes,
chain linkage, Ed25519 signatures and Merkle inclusion. Nothing here trusts
the server's own verdict — that is the point. Run it against a tampered
database and it fails exactly where the tampering happened.

    python3 verify_cli.py 54WSAD5U
    python3 verify_cli.py 54WSAD5U --api http://localhost:8002
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

from crypto_utils import canonical_json, sha256, verify
from merkle import MerkleTree
from record import GENESIS_HASH
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

OK = "  [PASS] "
BAD = "  [FAIL] "


def fetch_proof(api, code):
    url = f"{api.rstrip('/')}/c/{code}/proof"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Server returned {e.code} for {url}")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {url}: {e.reason}")


def verify_proof(doc):
    failures = []
    records = doc["records"]
    print(f"Certificate {doc['certificate_code']} — {len(records)} custody record(s)\n")

    prev_hash = GENESIS_HASH
    for rec in records:
        fields = rec["signed_fields"]
        seq = fields["seq_index"]
        print(f"Record {seq}: {fields['from_user_id']} -> {fields['to_name']}  ({fields['timestamp']})")

        # 1. Content integrity: re-hash the signed fields ourselves.
        recomputed = sha256(canonical_json(fields)).hex()
        if recomputed == rec["record_hash"]:
            print(OK + f"content hash  {recomputed[:16]}…")
        else:
            print(BAD + "content hash mismatch — this record was altered after signing")
            print(f"         stored:      {rec['record_hash']}")
            print(f"         recomputed:  {recomputed}")
            failures.append(f"record {seq}: content hash")

        # 2. Chain linkage: this record must name its predecessor.
        if fields["prev_hash"] == prev_hash:
            print(OK + "chain linkage")
        else:
            print(BAD + "chain linkage broken — a record was inserted, removed or reordered")
            failures.append(f"record {seq}: linkage")
        prev_hash = rec["record_hash"]

        # 3. Signature: the outgoing custodian signed this exact record hash.
        pub_hex = (rec.get("signer") or {}).get("public_key")
        if not pub_hex:
            print(BAD + "no public key published for the signer")
            failures.append(f"record {seq}: missing signer key")
        else:
            pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
            try:
                sig_ok = verify(pk, bytes.fromhex(rec["record_hash"]), bytes.fromhex(rec["signature"]))
            except ValueError:
                sig_ok = False
            if sig_ok:
                print(OK + f"Ed25519 signature by {rec['signer']['name']}")
            else:
                print(BAD + "signature does not verify against the signer's public key")
                failures.append(f"record {seq}: signature")

        # 4. Merkle inclusion in a published checkpoint (optional — a record
        #    can be genuine but not yet checkpointed).
        m = rec.get("merkle")
        if not m:
            print("  [ -- ] not yet included in a published checkpoint")
        elif MerkleTree.verify_proof(rec["record_hash"], [(p["hash"], p["side"]) for p in m["proof"]], m["root_hash"]):
            print(OK + f"Merkle inclusion in checkpoint #{m['batch_index']} (root {m['root_hash'][:16]}…)")
        else:
            print(BAD + f"Merkle proof does not reconstruct checkpoint #{m['batch_index']} root")
            failures.append(f"record {seq}: merkle inclusion")
        print()

    return failures


def main():
    ap = argparse.ArgumentParser(description="Independently verify a CraftProof certificate.")
    ap.add_argument("code", help="certificate code, e.g. 54WSAD5U")
    ap.add_argument("--api", default="http://localhost:8002", help="backend base URL")
    args = ap.parse_args()

    doc = fetch_proof(args.api, args.code.strip().upper())
    failures = verify_proof(doc)

    server = doc.get("server_verdict", {})
    print(f"Server said: {'verified' if server.get('verified') else 'NOT verified'}"
          + (f" ({server.get('reason')})" if server.get("reason") else ""))

    if failures:
        print(f"\nRESULT: NOT AUTHENTIC — {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("\nRESULT: AUTHENTIC — every hash, signature and checkpoint proof verified locally.")


if __name__ == "__main__":
    main()
