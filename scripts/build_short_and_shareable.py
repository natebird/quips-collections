#!/usr/bin/env python3
"""Generate short-and-shareable.json — the short quotes, ideal for widgets and
lock screens.

Includes every quote whose `content` is at most --max-length characters
(default 80), sorted shortest-first so the punchiest lines lead. Each quote
keeps its object plus a `sourceCollection` back-reference.

Standalone like the other generated feeds: NOT registered in collections.json
and outside collections/. Deterministic output. Stdlib only.

Usage: build_short_and_shareable.py [--root ROOT] [--max-length N] [--out PATH]
"""

import argparse
import json
import os
import sys

META = {
    "id": "short-and-shareable",
    "name": "Short & Shareable",
    "author": "Quips Editorial",
    "colorName": "lime",
    "colorLightHex": "#9EDB2A",
    "colorDarkHex": "#9DDC21",
    "iconName": "bolt.fill",
    "category": "Featured",
    "generated": True,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-length", type=int, default=80)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    coll_dir = os.path.join(args.root, "collections")
    files = sorted(fn for fn in os.listdir(coll_dir) if fn.endswith(".json"))

    picked = []
    newest = ""
    for fn in files:
        data = json.load(open(os.path.join(coll_dir, fn), encoding="utf-8"))
        cid = data["id"]
        for q in data.get("quotes", []):
            if len(q.get("content", "")) <= args.max_length:
                picked.append({**q, "sourceCollection": cid})
                newest = max(newest, q.get("addedAt", ""))

    # Shortest first; tie-break by id for stable, deterministic ordering.
    picked.sort(key=lambda q: (len(q.get("content", "")), q.get("id", "")))

    collection = {
        **META,
        "description": (
            f"Quotes of {args.max_length} characters or fewer — ideal for widgets "
            "and lock screens, shortest first."
        ),
        "maxLength": args.max_length,
        "lastUpdated": newest,
        "quotes": picked,
    }

    out = args.out or os.path.join(args.root, "short-and-shareable.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {len(picked)} quote(s) (<= {args.max_length} chars) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
