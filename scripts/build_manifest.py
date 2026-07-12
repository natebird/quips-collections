#!/usr/bin/env python3
"""Emit manifest.json for a release to stdout.

Usage:
    build_manifest.py VERSION       # VERSION without the leading 'v', e.g. 1.0.0

The manifest is the single mutable pointer the app reads at
https://data.quipsapp.com/latest/manifest.json to discover the current
version, then pins the immutable v<version> assets it names.
"""

import base64
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

BASE = "https://data.quipsapp.com"

# Standalone generated feeds published alongside the index (see scripts/build_*.py).
# Each is optional: listed in the manifest only when the file is present at release.
GENERATED_FEEDS = [
    ("recentlyAdded", "recently-added.json"),
    ("onThisDay", "on-this-day.json"),
    ("shortAndShareable", "short-and-shareable.json"),
    ("newsletterPicks", "newsletter-picks.json"),
]


def sri_hash(raw: bytes) -> str:
    """SRI-style sha256 of raw bytes: 'sha256-' + base64(digest).

    Same scheme as the per-collection contentHash written by
    scripts/compute_hashes.py, so a client verifies the index the same way it
    verifies a collection.
    """
    return "sha256-" + base64.b64encode(hashlib.sha256(raw).digest()).decode("ascii")


def main():
    if len(sys.argv) != 2:
        print("usage: build_manifest.py VERSION", file=sys.stderr)
        return 1
    version = sys.argv[1].lstrip("v")

    # Hash the index's raw bytes — the same bytes published as
    # v<version>/collections.json — so a client can compare indexHash against
    # its cached copy and skip the index fetch entirely when nothing changed.
    with open("collections.json", "rb") as f:
        index_raw = f.read()
    index = json.loads(index_raw)
    collections = index.get("collections", [])
    quote_count = sum(c.get("quoteCount", 0) for c in collections)

    base = f"{BASE}/v{version}"
    manifest = {
        "version": version,
        "releasedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "collectionCount": len(collections),
        "quoteCount": quote_count,
        "indexUrl": f"{base}/collections.json",
        "indexHash": sri_hash(index_raw),
        "indexBytes": len(index_raw),
        "bundleUrl": f"{base}/quips-collections-v{version}.zip",
    }

    # Generated feeds (Recently Added, On This Day, …). Same url/hash/bytes
    # contract as the index, so a client discovers and integrity-checks them
    # the same way, and skips a feed whose hash matches its cached copy.
    generated = {}
    for key, fname in GENERATED_FEEDS:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                raw = f.read()
            generated[key] = {
                "url": f"{base}/{fname}",
                "hash": sri_hash(raw),
                "bytes": len(raw),
            }
    if generated:
        manifest["generated"] = generated

    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
