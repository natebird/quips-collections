#!/usr/bin/env python3
"""Emit manifest.json for a release to stdout.

Usage:
    build_manifest.py VERSION       # VERSION without the leading 'v', e.g. 1.0.0

The manifest is the single mutable pointer the app reads at
https://data.quipsapp.com/latest/manifest.json to discover the current
version, then pins the immutable v<version> assets it names.
"""

import json
import sys
from datetime import datetime, timezone

BASE = "https://data.quipsapp.com"


def main():
    if len(sys.argv) != 2:
        print("usage: build_manifest.py VERSION", file=sys.stderr)
        return 1
    version = sys.argv[1].lstrip("v")

    with open("collections.json", encoding="utf-8") as f:
        index = json.load(f)
    collections = index.get("collections", [])
    quote_count = sum(c.get("quoteCount", 0) for c in collections)

    base = f"{BASE}/v{version}"
    manifest = {
        "version": version,
        "releasedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "collectionCount": len(collections),
        "quoteCount": quote_count,
        "indexUrl": f"{base}/collections.json",
        "bundleUrl": f"{base}/quips-collections-v{version}.zip",
    }
    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
