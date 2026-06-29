#!/usr/bin/env python3
"""Fill in (or verify) per-collection contentHash + bytes in collections.json.

These fields turn the index into a manifest for *progressive downloads*: a
client fetches the lightweight collections.json once, compares each entry's
contentHash against its cached copy of collections/<id>.json, and re-downloads
only the collections that actually changed.

  contentHash  SRI-style sha256 of the collection file's raw bytes as served,
               formatted "sha256-<base64>". Doubles as a Subresource-Integrity
               value the client can verify after download.
  bytes        Byte length of the same file, so the client can show/limit
               download sizes.

The hash is over the file *exactly as it sits on disk* (the bytes the CDN
serves), so a re-hash after download must match. collections.json itself is
never hashed into itself — no chicken-and-egg.

Usage:
    compute_hashes.py [--root ROOT] [--check]

    --root   repo root containing collections.json (default: .)
    --check  don't write; exit 1 if any stored hash/bytes is missing or stale
             (use in CI, alongside validate_collections.py)

Writing is idempotent: a clean tree re-run produces no diff. Stdlib only.
Exit code 0 on success, 1 on failure (or on drift under --check).
"""

import argparse
import base64
import hashlib
import json
import os
import sys


def sri_hash(raw: bytes) -> str:
    """SRI-style sha256 of raw bytes: 'sha256-' + base64(digest)."""
    digest = hashlib.sha256(raw).digest()
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def main():
    ap = argparse.ArgumentParser(
        description="Fill in or verify per-collection contentHash + bytes in collections.json."
    )
    ap.add_argument("--root", default=".", help="repo root containing collections.json")
    ap.add_argument(
        "--check",
        action="store_true",
        help="verify only; exit 1 on missing/stale hashes (for CI)",
    )
    args = ap.parse_args()

    index_path = os.path.join(args.root, "collections.json")
    coll_dir = os.path.join(args.root, "collections")

    try:
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] cannot read {index_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] {index_path}: invalid JSON ({e})", file=sys.stderr)
        return 1

    entries = index.get("collections", [])
    errors = 0
    drift = 0

    for entry in entries:
        cid = entry.get("id")
        path = os.path.join(coll_dir, f"{cid}.json")
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"[ERROR] {cid}: missing file {path}")
            errors += 1
            continue

        want_hash = sri_hash(raw)
        want_bytes = len(raw)

        if args.check:
            if entry.get("contentHash") != want_hash:
                print(f"[STALE] {cid}: contentHash differs (run compute_hashes.py)")
                drift += 1
            if entry.get("bytes") != want_bytes:
                print(f"[STALE] {cid}: bytes {entry.get('bytes')} != {want_bytes}")
                drift += 1
        else:
            entry["contentHash"] = want_hash
            entry["bytes"] = want_bytes

    if errors:
        print(f"\n{errors} error(s)")
        return 1

    if args.check:
        if drift:
            print(f"\n{drift} stale field(s) across {len(entries)} collection(s)")
            return 1
        print(f"ok — {len(entries)} collection(s) up to date")
        return 0

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote contentHash + bytes for {len(entries)} collection(s) to collections.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
