#!/usr/bin/env python3
"""Generate new-collections.json — the N most recently published collections.

This exists because "what's new" has two different answers and only one of them
was published. recently-added.json answers it for *quotes*, and deliberately
excludes any quote that arrived with a brand-new collection so a 40-quote import
doesn't swamp a 25-item feed. The consequence is that adding a whole collection
— the largest thing that can happen to this dataset — produces no change in any
published feed at all. This file is the other answer: the collections
themselves, newest first, so a client can highlight them.

Recency comes from each collection's `addedAt` (when it was first published),
not `lastUpdated` (which moves every time a quote is edited). Entries are copied
from collections.json rather than the collection files: the index already
mirrors the presentation fields and carries previewQuotes, which is exactly what
a highlight card needs and avoids reading 85 files to build one small feed.

Note this is a *top-N*, not a time window — no wall-clock is consulted, so the
output is a pure function of the data and re-running with no new collections
produces no diff. Many collections share a backfilled `addedAt` (see
scripts/backfill_added_at.py), so entries deep in the list are ties broken by
id; the genuinely-new ones are at the top, which is the part worth rendering.

Unlike the quote feeds this is collection-shaped, so build_manifest.py names it
as an ancillary asset rather than in `generated` — a client iterating `generated`
to draw quote shelves must not meet a feed it cannot render.

Usage: build_new_collections.py [--root ROOT] [--limit N] [--out PATH]
"""

import argparse
import json
import os
import sys

# Presentation for the generated collection list, mirroring the other feeds'
# META blocks (new-palette color; see scripts/migrate_colors.py).
META = {
    "id": "new-collections",
    "name": "New Collections",
    "author": "Quips Editorial",
    "colorName": "lime",
    "colorLightHex": "#9EDB2A",
    "colorDarkHex": "#9DDC21",
    "iconName": "sparkles.rectangle.stack.fill",
    "category": "Featured",
    "generated": True,
}

# Copied verbatim from each index entry. Deliberately excludes contentHash and
# bytes: those describe a download, and a client that decides to fetch the
# collection reads them from the index, which is the one place they are kept
# current.
ENTRY_FIELDS = (
    "id",
    "name",
    "description",
    "quoteCount",
    "previewQuotes",
    "colorName",
    "colorLightHex",
    "colorDarkHex",
    "iconName",
    "category",
    "addedAt",
    "lastUpdated",
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--out", default=None, help="output path (default: <root>/new-collections.json)")
    args = ap.parse_args()

    index_path = os.path.join(args.root, "collections.json")
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)

    entries = index.get("collections", [])

    # Newest first; tie-break by id so a shared backfilled timestamp still
    # yields a stable, deterministic order.
    ordered = sorted(
        entries,
        key=lambda c: (str(c.get("addedAt", "")), str(c.get("id", ""))),
        reverse=True,
    )
    picked = ordered[: args.limit]

    collections = [{k: c[k] for k in ENTRY_FIELDS if k in c} for c in picked]
    newest = str(picked[0].get("addedAt", "")) if picked else ""

    feed = {
        **META,
        "description": (
            f"The {len(collections)} most recently published Quips collections, newest first."
        ),
        "lastUpdated": newest,
        "collections": collections,
    }

    out = args.out or os.path.join(args.root, "new-collections.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {len(collections)} collection(s) to {out} (newest added {newest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
