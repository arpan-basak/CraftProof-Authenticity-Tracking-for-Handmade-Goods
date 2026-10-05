#!/usr/bin/env python3
"""Tests for the cryptographic engine, including the attacks it must catch.

Runs standalone (no pytest needed):

    python3 test_crypto.py

Each test builds a real chain in a throwaway database, then tries to forge it.
"""
import os
import sys
import tempfile

# Point every module at a scratch database before they import it.
_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="craftproof-test-"), "test.db")
os.environ["CRAFTPROOF_DB"] = _TMP_DB

from crypto_utils import canonical_json, generate_keypair, sha256, sign, verify
from database import get_db, init_db
from merkle import MerkleTree, leaf_hash
from record import CustodyRecord, GENESIS_HASH
from core import verify_chain_detailed, create_checkpoint, get_inclusion_proof
from cryptography.hazmat.primitives import serialization

init_db()


# ---------- helpers ----------

def make_user(name):
    sk, pk = generate_keypair()
    sk_hex = sk.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, email, password_hash, role, public_key, encrypted_privkey) VALUES (?, ?, ?, ?, ?, ?)",
        (name, f"{name}-{os.urandom(4).hex()}@test", "x", "maker",
         pk.public_bytes(encoding=serialization.Encoding.Raw,
                         format=serialization.PublicFormat.Raw).hex(), sk_hex),
    )
    conn.commit()
    uid = c.lastrowid
    conn.close()
    return uid, sk


def build_chain(hops=2):
    """A piece plus `hops` transfers, all correctly signed."""
    maker, maker_sk = make_user("maker")
    gallery, gallery_sk = make_user("gallery")
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO pieces (certificate_code, title, made_by, current_owner_id) VALUES (?, ?, ?, ?)",
        (os.urandom(4).hex().upper(), "Test piece", maker, maker),
    )
    piece_id = c.lastrowid

    def append(seq, from_id, sk, to_id, to_name, note, prev):
        rec = CustodyRecord(piece_id, seq, from_id, to_id, to_name, note, prev)
        h = rec.compute_hash()
        c.execute(
            "INSERT INTO custody_records (piece_id, seq_index, from_user_id, to_user_id, to_name, note, timestamp, prev_hash, record_hash, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (piece_id, seq, from_id, to_id, to_name, note, rec.timestamp, prev, h,
             sign(sk, bytes.fromhex(h)).hex()),
        )
        return h

    prev = append(0, maker, maker_sk, maker, "Self", "Piece created", GENESIS_HASH)
    if hops >= 1:
        prev = append(1, maker, maker_sk, gallery, None, "To the gallery", prev)
    if hops >= 2:
        prev = append(2, gallery, gallery_sk, None, "Walk-in buyer", "Sold", prev)
    conn.commit()
    conn.close()
    return piece_id


def db_exec(sql, params):
    conn = get_db()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


# ---------- primitives ----------

def test_canonical_json_is_order_independent():
    a = {"b": 2, "a": 1, "c": [3, 4]}
    b = {"c": [3, 4], "a": 1, "b": 2}
    assert canonical_json(a) == canonical_json(b)
    assert b" " not in canonical_json(a), "canonical form must not contain whitespace"


def test_record_hash_is_deterministic_and_sensitive():
    r1 = CustodyRecord(1, 0, 1, 1, "Self", "note", GENESIS_HASH, timestamp="2026-01-01T00:00:00+00:00")
    r2 = CustodyRecord(1, 0, 1, 1, "Self", "note", GENESIS_HASH, timestamp="2026-01-01T00:00:00+00:00")
    r3 = CustodyRecord(1, 0, 1, 1, "Self", "note!", GENESIS_HASH, timestamp="2026-01-01T00:00:00+00:00")
    assert r1.compute_hash() == r2.compute_hash()
    assert r1.compute_hash() != r3.compute_hash(), "a one-character edit must change the hash"
    assert len(r1.compute_hash()) == 64


def test_signature_round_trip_and_rejection():
    sk, pk = generate_keypair()
    other_sk, other_pk = generate_keypair()
    msg = sha256(b"a custody record")
    sig = sign(sk, msg)
    assert verify(pk, msg, sig)
    assert not verify(other_pk, msg, sig), "a different key must not verify"
    assert not verify(pk, sha256(b"a different record"), sig), "a different message must not verify"
    forged = bytearray(sig)
    forged[0] ^= 0x01
    assert not verify(pk, msg, bytes(forged)), "a flipped bit must not verify"


def test_merkle_proofs():
    leaves = [sha256(bytes([i])).hex() for i in range(7)]  # odd count, exercises duplication
    tree = MerkleTree(leaves)
    for i, leaf in enumerate(leaves):
        assert MerkleTree.verify_proof(leaf, tree.get_proof(i), tree.root), f"leaf {i} must prove"
    outsider = sha256(b"never recorded").hex()
    assert not MerkleTree.verify_proof(outsider, tree.get_proof(0), tree.root), \
        "a leaf that is not in the tree must not prove"


def test_merkle_leaf_and_node_prefixes_differ():
    """Domain separation: a leaf must never be confusable with an internal node."""
    h = sha256(b"x")
    assert leaf_hash(h) != sha256(h), "leaves must be prefixed before hashing"


# ---------- chain-level attacks ----------

def test_honest_chain_verifies():
    piece_id = build_chain()
    valid, reason, checks = verify_chain_detailed(piece_id)
    assert valid, f"an untouched chain must verify, got: {reason}"
    assert len(checks) == 3 and all(c["ok"] for c in checks)


def test_edited_note_is_caught():
    piece_id = build_chain()
    db_exec("UPDATE custody_records SET note = ? WHERE piece_id = ? AND seq_index = 0",
            ("FORGED: mass produced", piece_id))
    valid, reason, checks = verify_chain_detailed(piece_id)
    assert not valid and "content hash" in reason
    assert not checks[0]["content_ok"] and checks[1]["content_ok"], "only record 0 should fail"


def test_rewritten_buyer_name_is_caught():
    piece_id = build_chain()
    db_exec("UPDATE custody_records SET to_name = ? WHERE piece_id = ? AND seq_index = 2",
            ("Someone Else", piece_id))
    valid, reason, _ = verify_chain_detailed(piece_id)
    assert not valid and "content hash" in reason


def test_deleted_middle_record_breaks_linkage():
    piece_id = build_chain()
    db_exec("DELETE FROM custody_records WHERE piece_id = ? AND seq_index = 1", (piece_id,))
    valid, reason, _ = verify_chain_detailed(piece_id)
    assert not valid and "linkage" in reason, f"expected a linkage failure, got: {reason}"


def test_forged_record_with_matching_hash_fails_signature():
    """The strongest attack: an attacker who rewrites the row AND recomputes
    the hash still cannot produce the custodian's signature."""
    piece_id = build_chain()
    conn = get_db()
    r = conn.execute("SELECT * FROM custody_records WHERE piece_id = ? AND seq_index = 1", (piece_id,)).fetchone()
    forged = CustodyRecord(r["piece_id"], r["seq_index"], r["from_user_id"], r["to_user_id"],
                           "Counterfeit Gallery", "Fabricated handoff", r["prev_hash"],
                           timestamp=r["timestamp"])
    conn.execute(
        "UPDATE custody_records SET to_name = ?, note = ?, record_hash = ? WHERE id = ?",
        ("Counterfeit Gallery", "Fabricated handoff", forged.compute_hash(), r["id"]),
    )
    conn.commit()
    conn.close()

    valid, reason, checks = verify_chain_detailed(piece_id)
    assert not valid, "a re-hashed forgery must still be rejected"
    assert checks[1]["content_ok"], "the hash now matches the forged content, as expected"
    assert not (checks[1]["signature_ok"] and checks[2]["linkage_ok"]), \
        "the forgery must break the signature or the following record's linkage"


def test_checkpoint_proves_inclusion_and_excludes_outsiders():
    piece_id = build_chain()
    checkpoint = create_checkpoint()
    assert checkpoint and checkpoint["record_count"] >= 3

    conn = get_db()
    hashes = [r["record_hash"] for r in conn.execute(
        "SELECT record_hash FROM custody_records WHERE piece_id = ? ORDER BY seq_index", (piece_id,)).fetchall()]
    conn.close()

    for h in hashes:
        proof = get_inclusion_proof(h)
        assert proof and proof["included"], "every checkpointed record must prove inclusion"
        assert proof["root_hash"] == checkpoint["root_hash"]

    assert get_inclusion_proof(sha256(b"a record nobody ever made").hex()) is None


def test_checkpoint_root_changes_when_a_record_is_added():
    build_chain()
    first = create_checkpoint()
    build_chain()
    second = create_checkpoint()
    assert second["root_hash"] != first["root_hash"], "new records must change the published root"
    assert second["batch_index"] == first["batch_index"] + 1


# ---------- runner ----------

def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed.append((name, str(e) or "assertion failed"))
            print(f"  FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001 - a crash is a test failure too
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ERROR {name}: {type(e).__name__}: {e}")

    print(f"\n{len(tests) - len(failed)}/{len(tests)} passed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
