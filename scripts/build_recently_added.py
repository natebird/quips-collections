#!/usr/bin/env python3
"""Generate recently-added.json — a standalone "Recently Added" collection of
the N most recently added quotes across all collections.

Recency comes straight from the data: every quote carries an `addedAt` timestamp
(see scripts/backfill_added_at.py and the add-quotes skill). A quote whose
`addedAt` equals its collection's `addedAt` arrived when the collection was
created — those are excluded, so a brand-new collection's bulk import doesn't
swamp the feed. The rest are sorted newest-first and the top N are kept.

This file is intentionally NOT registered in collections.json and lives outside
collections/: it reuses other collections' quote ids/text, which would violate
the one-prefix-per-collection and cross-collection-uniqueness rules enforced by
validate_collections.py.

Output is deterministic (lastUpdated = the newest included quote's addedAt), so
re-running with no new quotes produces no diff. Stdlib only.

Usage: build_recently_added.py [--root ROOT] [--limit N] [--out PATH]
"""

import argparse
import json
import os
import sys

# Presentation for the generated collection (new-palette color; see the token
# migration in scripts/migrate_colors.py).
META = {
    "id": "recently-added",
    "name": "Recently Added",
    "author": "Quips Editorial",
    "colorName": "sky",
    "colorLightHex": "#1F9ED4",
    "colorDarkHex": "#45C2FC",
    "iconName": "sparkles",
    "category": "Featured",
    "generated": True,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--out", default=None, help="output path (default: <root>/recently-added.json)")
    args = ap.parse_args()

    coll_dir = os.path.join(args.root, "collections")
    files = sorted(fn for fn in os.listdir(coll_dir) if fn.endswith(".json"))

    # (addedAt, collection_id, quote) for every quote added *after* its
    # collection's creation — i.e. an incremental addition, not part of a
    # newly added collection's initial batch.
    events = []
    for fn in files:
        data = json.load(open(os.path.join(coll_dir, fn), encoding="utf-8"))
        cid, created = data["id"], data.get("addedAt")
        for q in data.get("quotes", []):
            added = q.get("addedAt")
            if added and added != created:
                events.append((added, cid, q))

    # Newest first; tie-break by quote id for stable, deterministic ordering.
    events.sort(key=lambda e: (e[0], e[2].get("id", "")), reverse=True)
    picked = events[: args.limit]

    quotes = [{**q, "sourceCollection": cid} for _, cid, q in picked]
    newest = picked[0][0] if picked else ""

    collection = {
        **META,
        "description": (
            f"The {len(quotes)} most recently added quotes across the Quips "
            "collections, excluding quotes introduced with brand-new collections."
        ),
        "lastUpdated": newest,
        "quotes": quotes,
    }

    out = args.out or os.path.join(args.root, "recently-added.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {len(quotes)} quote(s) to {out} (newest added {newest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
