#!/usr/bin/env python3
"""Populate the database with a believable demo: makers, galleries, and
pieces walked through their full journey, so a demo never starts empty.

    python3 seed.py           # add demo data alongside whatever exists
    python3 seed.py --reset   # wipe the database first

Every account is created with password 'craftproof123'.
"""
import argparse
import os
import random
import string
import sys
from datetime import datetime, timedelta, timezone

from auth import get_password_hash
from core import create_checkpoint
from crypto_utils import generate_keypair, pubkey_to_hex, sign
from database import DB_PATH, get_db, init_db
from record import CustodyRecord, GENESIS_HASH
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

PASSWORD = "craftproof123"

MAKERS = [
    ("Meera Krishnan", "meera@example.com"),
    ("Tomas Hald", "tomas@example.com"),
    ("Aisha Rahman", "aisha@example.com"),
]
SELLERS = [
    ("Priya Nair", "priya@example.com", "Kalakriti Gallery"),
    ("Daniel Okoro", "daniel@example.com", "Northlight Craft Studio"),
]
PIECES = [
    (0, "Hand-thrown ceramic vase", "Stoneware clay, ash glaze",
     "Thrown on a kick wheel and wood-fired over three days.", 2, "Elena Fischer"),
    (0, "Speckled tea bowl set", "Stoneware clay, tenmoku glaze",
     "A set of four bowls, each slightly different by hand.", 1, None),
    (1, "Walnut serving board", "Black walnut, food-safe oil",
     "Cut from a single storm-felled walnut in Jutland.", 2, "Marcus Webb"),
    (1, "Oak three-legged stool", "White oak, hand-cut joinery",
     "Green-wood joinery, no screws or glue.", 0, None),
    (2, "Silver filigree earrings", "Sterling silver",
     "Drawn and twisted by hand using traditional filigree technique.", 2, "Ravi Menon"),
]


def create_user(conn, name, email, role, shop_name=None):
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        return existing["id"]
    sk, pk = generate_keypair()
    sk_hex = sk.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, email, password_hash, role, shop_name, public_key, encrypted_privkey) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, get_password_hash(PASSWORD), role, shop_name, pubkey_to_hex(pk), sk_hex),
    )
    return c.lastrowid


def signing_key(conn, user_id):
    row = conn.execute("SELECT encrypted_privkey FROM users WHERE id = ?", (user_id,)).fetchone()
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(row["encrypted_privkey"]))


def append_record(conn, piece_id, seq_index, from_user_id, to_user_id, to_name, note, prev_hash, when):
    rec = CustodyRecord(piece_id, seq_index, from_user_id, to_user_id, to_name, note, prev_hash,
                        timestamp=when.isoformat())
    rec_hash = rec.compute_hash()
    sig = sign(signing_key(conn, from_user_id), bytes.fromhex(rec_hash)).hex()
    conn.execute(
        "INSERT INTO custody_records (piece_id, seq_index, from_user_id, to_user_id, to_name, note, timestamp, prev_hash, record_hash, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (piece_id, seq_index, from_user_id, to_user_id, to_name, note, rec.timestamp, prev_hash, rec_hash, sig),
    )
    return rec_hash


def unique_code(conn):
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not conn.execute("SELECT 1 FROM pieces WHERE certificate_code = ?", (code,)).fetchone():
            return code


def seed():
    conn = get_db()
    try:
        maker_ids = [create_user(conn, n, e, "maker") for n, e in MAKERS]
        seller_ids = [create_user(conn, n, e, "seller", shop) for n, e, shop in SELLERS]
        conn.commit()

        now = datetime.now(timezone.utc)
        created = []

        for maker_idx, title, materials, story, hops, buyer in PIECES:
            maker_id = maker_ids[maker_idx]
            code = unique_code(conn)
            c = conn.cursor()
            c.execute(
                "INSERT INTO pieces (certificate_code, title, description, materials, made_by, current_owner_id) VALUES (?, ?, ?, ?, ?, ?)",
                (code, title, story, materials, maker_id, maker_id),
            )
            piece_id = c.lastrowid

            made_on = now - timedelta(days=random.randint(40, 120))
            prev = append_record(conn, piece_id, 0, maker_id, maker_id, "Self", "Piece created",
                                 GENESIS_HASH, made_on)
            seq, holder, when = 1, maker_id, made_on

            if hops >= 1:  # maker -> gallery
                gallery_id = random.choice(seller_ids)
                when += timedelta(days=random.randint(5, 25))
                prev = append_record(conn, piece_id, seq, holder, gallery_id, None,
                                     "Delivered to the gallery in person", prev, when)
                conn.execute("UPDATE pieces SET current_owner_id = ? WHERE id = ?", (gallery_id, piece_id))
                seq, holder = seq + 1, gallery_id

            if hops >= 2 and buyer:  # gallery -> named buyer, who needs no account
                when += timedelta(days=random.randint(3, 30))
                prev = append_record(conn, piece_id, seq, holder, None, buyer,
                                     "Sold in store", prev, when)
                conn.execute("UPDATE pieces SET current_owner_id = NULL WHERE id = ?", (piece_id,))

            created.append((code, title, hops))

        conn.commit()
    finally:
        conn.close()

    checkpoint = create_checkpoint()

    print(f"Seeded {len(MAKERS)} makers, {len(SELLERS)} galleries, {len(created)} pieces.")
    print(f"All accounts use the password: {PASSWORD}\n")
    for email, in [(e,) for _, e in MAKERS] + [(e,) for _, e, _ in SELLERS]:
        print(f"  login: {email}")
    print("\nCertificates:")
    for code, title, hops in created:
        stage = ["still with the maker", "in a gallery", "sold to a customer"][hops]
        print(f"  /c/{code}  {title}  ({stage})")
    if checkpoint:
        print(f"\nPublished checkpoint #{checkpoint['batch_index']} over {checkpoint['record_count']} records")
        print(f"  root: {checkpoint['root_hash']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed CraftProof with demo data.")
    ap.add_argument("--reset", action="store_true", help="delete the existing database first")
    args = ap.parse_args()

    if args.reset:
        confirm = input(f"Delete {DB_PATH} and all its data? [y/N] ").strip().lower()
        if confirm != "y":
            sys.exit("Aborted.")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    seed()
