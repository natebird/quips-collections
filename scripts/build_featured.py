#!/usr/bin/env python3
"""Generate featured-collections.json — the weekly featured-collection rotation,
resolved from featured-schedule.json.

The schedule names a collection per ISO week; this turns each entry into
something a client can render without a second fetch: the week's date range, the
collection id to join on, and one quote to show. Editorial rationale (`note`)
rides along so the site and app can say *why* it's featured.

**Every** scheduled week is published, past ones included, and the client picks
the entry whose range contains today — the same contract as `on-this-day.json`,
and for the same reason. A feed built around "now" would differ every time it was
generated, so a regeneration with unchanged data would produce a diff, and the
week a reader sees would depend on when the release happened to be cut rather
than on what day it is.

Presentation (name, colour, icon, description) is deliberately **not** copied in.
Clients join to `collections.json` on `collectionId`, so a rename or a palette
change ships in one place and this file can never disagree with it.

Standalone like the other generated feeds: NOT registered in collections.json.
Deterministic. Stdlib only.

Usage:
    build_featured.py [--root ROOT] [--out PATH]
    build_featured.py --check      # verify the schedule without writing
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

META = {
    "id": "featured-collections",
    "name": "Featured Collections",
    "author": "Quips Editorial",
    "colorName": "jade",
    "colorLightHex": "#27A98A",
    "colorDarkHex": "#2BD1AA",
    "iconName": "star.fill",
    "category": "Featured",
    "generated": True,
}


def problems(weeks, by_id):
    """Everything wrong with the schedule, as a list of human-readable strings."""
    found = []
    seen = set()
    previous = None

    for entry in weeks:
        week = entry.get("weekStart", "")
        cid = entry.get("collectionId", "")
        try:
            start = datetime.strptime(week, "%Y-%m-%d").date()
        except ValueError:
            found.append(f"{week or '(missing weekStart)'}: not a YYYY-MM-DD date")
            continue

        if start.weekday() != 0:
            found.append(f"{week}: not a Monday (weeks start Monday)")
        if week in seen:
            found.append(f"{week}: scheduled more than once")
        seen.add(week)

        # A gap leaves a week with no feature — survivable (the client falls back)
        # but almost always a mistake in an append, so it is worth saying out loud.
        if previous and start != previous and start != previous + timedelta(weeks=1):
            found.append(f"{week}: gap — previous scheduled week was {previous}")
        previous = start

        if cid not in by_id:
            found.append(f"{week}: unknown collection '{cid}'")
            continue

        quote_id = entry.get("quoteId")
        if quote_id and quote_id not in by_id[cid]["quote_ids"]:
            found.append(f"{week}: quote '{quote_id}' is not in '{cid}'")

    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None,
                    help="output path (default: <root>/featured-collections.json)")
    ap.add_argument("--check", action="store_true",
                    help="validate the schedule and exit; write nothing")
    args = ap.parse_args()

    index = json.load(open(os.path.join(args.root, "collections.json"), encoding="utf-8"))
    coll_dir = os.path.join(args.root, "collections")

    by_id = {}
    for c in index.get("collections", []):
        path = os.path.join(coll_dir, f"{c['id']}.json")
        quotes = json.load(open(path, encoding="utf-8")).get("quotes", []) if os.path.exists(path) else []
        by_id[c["id"]] = {"index": c, "quotes": quotes, "quote_ids": {q["id"] for q in quotes}}

    schedule = json.load(open(os.path.join(args.root, "featured-schedule.json"), encoding="utf-8"))
    weeks = sorted(schedule.get("weeks", []), key=lambda w: w.get("weekStart", ""))

    found = problems(weeks, by_id)
    if found:
        for p in found:
            print(f"ERROR {p}", file=sys.stderr)
        print(f"{len(found)} problem(s) in featured-schedule.json", file=sys.stderr)
        return 1

    if args.check:
        print(f"featured-schedule.json OK — {len(weeks)} week(s), "
              f"{len({w['collectionId'] for w in weeks})} distinct collection(s)")
        return 0

    entries = []
    for entry in weeks:
        cid = entry["collectionId"]
        record = by_id[cid]
        start = datetime.strptime(entry["weekStart"], "%Y-%m-%d").date()

        # The week's quote: whichever the schedule names, else the collection's
        # first — a stable choice, and the one a reader meets at the top of the
        # collection anyway.
        quote = None
        if entry.get("quoteId"):
            quote = next(q for q in record["quotes"] if q["id"] == entry["quoteId"])
        elif record["quotes"]:
            quote = record["quotes"][0]

        published = {
            "weekStart": entry["weekStart"],
            "weekEnd": (start + timedelta(days=6)).isoformat(),
            "collectionId": cid,
        }
        if entry.get("note"):
            published["note"] = entry["note"]
        if quote:
            published["quote"] = {**quote, "sourceCollection": cid}
        entries.append(published)

    feed = {
        **META,
        "description": (
            "One featured collection per ISO week. Find the entry whose weekStart/"
            "weekEnd contains today; join collectionId to collections.json for the "
            "collection's name, colour, and icon."
        ),
        # The schedule's own horizon, not a build timestamp: what changes about this
        # file is which weeks it covers.
        "lastUpdated": entries[-1]["weekStart"] + "T00:00:00Z" if entries else "",
        "weekCount": len(entries),
        "weeks": entries,
    }

    out = args.out or os.path.join(args.root, "featured-collections.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if entries:
        print(f"wrote {len(entries)} week(s) to {out} "
              f"({entries[0]['weekStart']} → {entries[-1]['weekEnd']})")
    else:
        print(f"wrote an empty schedule to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
