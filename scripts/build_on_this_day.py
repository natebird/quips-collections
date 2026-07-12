#!/usr/bin/env python3
"""Generate on-this-day.json — quotes grouped by the calendar day they were
said or written.

Only quotes with a full `YYYY-MM-DD` quoteDate qualify (approximate dates like
`c. 1969` or `YYYY-MM` have no day). Each is filed under its `MM-DD` key, so the
app renders "On This Day" by indexing `days[<today MM-DD>]` — one deterministic
artifact, regenerated only when the data changes, no per-day snapshots.

Like the other generated feeds this file is standalone: NOT registered in
collections.json and outside collections/, because it reuses other collections'
quote ids/text. Stdlib only.

Usage: build_on_this_day.py [--root ROOT] [--out PATH]
"""

import argparse
import json
import os
import re
import sys

FULL_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

META = {
    "id": "on-this-day",
    "name": "On This Day",
    "author": "Quips Editorial",
    "colorName": "amber",
    "colorLightHex": "#E2A520",
    "colorDarkHex": "#FBB620",
    "iconName": "calendar",
    "category": "Featured",
    "generated": True,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    coll_dir = os.path.join(args.root, "collections")
    files = sorted(fn for fn in os.listdir(coll_dir) if fn.endswith(".json"))

    days = {}
    newest = ""
    total = 0
    for fn in files:
        data = json.load(open(os.path.join(coll_dir, fn), encoding="utf-8"))
        cid = data["id"]
        for q in data.get("quotes", []):
            qd = str(q.get("quoteDate", ""))
            if not FULL_DATE.match(qd):
                continue
            days.setdefault(qd[5:], []).append({**q, "sourceCollection": cid})
            newest = max(newest, q.get("addedAt", ""))
            total += 1

    # Deterministic: days in calendar order, quotes within a day oldest-first.
    ordered = {}
    for mmdd in sorted(days):
        ordered[mmdd] = sorted(days[mmdd], key=lambda q: (q.get("quoteDate", ""), q.get("id", "")))

    collection = {
        **META,
        "description": (
            "Quotes said or written on each calendar day. Index into `days` by "
            "today's MM-DD (e.g. \"07-04\") to show that day's quotes."
        ),
        "lastUpdated": newest,
        "days": ordered,
    }

    out = args.out or os.path.join(args.root, "on-this-day.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {total} quote(s) across {len(ordered)} day(s) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
