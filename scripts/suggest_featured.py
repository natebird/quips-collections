#!/usr/bin/env python3
"""Propose the next N weeks of the featured-collection rotation, and optionally
append them to featured-schedule.json.

The rotation's job is coverage: every collection should get a turn before any
collection gets a second one. New collections are added to the dataset regularly,
so a schedule picked once would keep re-featuring the same 82 and never reach
number 83 — which is why this is re-run on a schedule rather than solved once.

Ranking, in order:

  1. Fewest previous features — a collection that has never been featured always
     outranks one that has.
  2. Least recently featured, among equals.
  3. Larger collections first, so a week's feature has quotes to show.
  4. Collection id, so the result is deterministic and reviewable.

On top of that, two spacing rules the ranking alone can't express: a category may
not repeat within ``--category-gap`` consecutive weeks (a month of Faith
collections is a rut, not a rotation), and a seasonal candidate is preferred when
its season is the week being filled.

Seasonal hints are *hints*. The script marks candidates whose name, description,
or category matches the month's keywords and says so in its output; the editorial
judgment about whether a Christmas collection really belongs in the second week of
December belongs to whoever reviews the proposal. Stdlib only.

Usage:
    suggest_featured.py [--weeks N] [--root ROOT] [--from YYYY-MM-DD]
    suggest_featured.py --apply            # append the proposal to the schedule
    suggest_featured.py --json             # machine-readable proposal
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

SCHEDULE = "featured-schedule.json"

# Month → words that make a collection feel like it belongs in that month. Matched
# case-insensitively against a collection's name, description, and category. Kept
# short on purpose: a long list makes almost everything "seasonal", which is the
# same as nothing being seasonal.
SEASONAL = {
    1: ["new year", "resolution", "fresh start", "goal", "habit"],
    2: ["love", "romance", "relationship", "heart"],
    3: ["spring", "growth", "renewal"],
    4: ["nature", "poetry", "earth", "garden"],
    5: ["graduation", "commencement", "mother"],
    6: ["summer", "travel", "adventure", "father"],
    7: ["freedom", "independence", "america", "patriot"],
    8: ["sport", "olympic", "training", "discipline"],
    9: ["school", "learning", "teacher", "study", "football"],
    10: ["horror", "fear", "ghost", "halloween", "mystery"],
    11: ["gratitude", "thankful", "harvest", "family"],
    12: ["christmas", "winter", "holiday", "reflection", "year in review"],
}


def monday_of(d):
    """The Monday of the ISO week containing `d`."""
    return d - timedelta(days=d.weekday())


def load_json(path, default=None):
    if not os.path.exists(path) and default is not None:
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seasonal_match(collection, month):
    """Keywords for `month` that this collection's text mentions."""
    haystack = " ".join([
        collection.get("name", ""),
        collection.get("description", ""),
        collection.get("category", ""),
    ]).lower()
    return [kw for kw in SEASONAL.get(month, []) if kw in haystack]


def propose(collections, history, start_monday, weeks, category_gap):
    """Pick `weeks` collections starting at `start_monday`.

    `history` is the existing schedule's weeks, oldest first; it seeds both the
    feature counts and the recent-category window, so an appended run never
    repeats a category straight after the ones already scheduled.
    """
    by_id = {c["id"]: c for c in collections}

    counts = {c["id"]: 0 for c in collections}
    last_week = {}
    for entry in history:
        cid = entry.get("collectionId")
        if cid in counts:
            counts[cid] += 1
            last_week[cid] = max(last_week.get(cid, ""), entry.get("weekStart", ""))

    # Categories already spoken for in the tail of the existing schedule.
    recent = [by_id[e["collectionId"]]["category"]
              for e in history[-category_gap:]
              if e.get("collectionId") in by_id]

    picks = []
    for i in range(weeks):
        week_start = start_monday + timedelta(weeks=i)
        month = week_start.month

        ranked = sorted(
            collections,
            key=lambda c: (
                counts[c["id"]],
                last_week.get(c["id"], ""),
                -c.get("quoteCount", 0),
                c["id"],
            ),
        )

        # Prefer a seasonal candidate, but only from the front of the queue — a
        # Christmas collection that has already had three turns shouldn't jump
        # ahead of one that has had none. "The front" is everything tied on the
        # lowest feature count.
        floor = counts[ranked[0]["id"]]
        eligible = [c for c in ranked if counts[c["id"]] == floor]

        def allowed(c):
            return c.get("category") not in recent

        seasonal = [(c, seasonal_match(c, month)) for c in eligible if allowed(c)]
        seasonal = [(c, kw) for c, kw in seasonal if kw]

        if seasonal:
            choice, matched = seasonal[0]
            reason = f"seasonal: matches {', '.join(matched)} for {week_start:%B}"
        else:
            spaced = [c for c in ranked if allowed(c)]
            # Every remaining candidate shares a category with the recent window;
            # take the best-ranked one rather than leaving the week empty.
            choice = spaced[0] if spaced else ranked[0]
            times = counts[choice["id"]]
            reason = (
                "never featured" if times == 0
                else f"featured {times}x, last {last_week.get(choice['id'], 'unknown')}"
            )

        counts[choice["id"]] += 1
        last_week[choice["id"]] = week_start.isoformat()
        recent = (recent + [choice.get("category")])[-category_gap:]

        picks.append({
            "weekStart": week_start.isoformat(),
            "collectionId": choice["id"],
            "note": f"{choice['name']} — {reason}",
        })

    return picks


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--weeks", type=int, default=4, help="how many weeks to propose (default 4)")
    ap.add_argument("--from", dest="from_date", default=None,
                    help="first week to fill, YYYY-MM-DD (default: the week after the "
                         "last scheduled one, or this week if the schedule is empty)")
    ap.add_argument("--category-gap", type=int, default=3,
                    help="how many consecutive weeks must pass before a category repeats")
    ap.add_argument("--apply", action="store_true", help="append the proposal to the schedule")
    ap.add_argument("--json", dest="as_json", action="store_true", help="print the proposal as JSON")
    args = ap.parse_args()

    index = load_json(os.path.join(args.root, "collections.json"))
    collections = index.get("collections", [])

    sched_path = os.path.join(args.root, SCHEDULE)
    schedule = load_json(sched_path, default={"weeks": []})
    history = sorted(schedule.get("weeks", []), key=lambda w: w["weekStart"])

    if args.from_date:
        start = monday_of(datetime.strptime(args.from_date, "%Y-%m-%d").date())
    elif history:
        last = datetime.strptime(history[-1]["weekStart"], "%Y-%m-%d").date()
        start = last + timedelta(weeks=1)
    else:
        start = monday_of(date.today())

    picks = propose(collections, history, start, args.weeks, args.category_gap)

    if args.as_json:
        json.dump(picks, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        never = sum(1 for c in collections
                    if not any(w.get("collectionId") == c["id"] for w in history))
        print(f"{len(collections)} collections, {never} never featured, "
              f"{len(history)} week(s) already scheduled")
        print(f"proposing {len(picks)} week(s) from {start}:\n")
        for p in picks:
            print(f"  {p['weekStart']}  {p['collectionId']:<28} {p['note']}")

    if args.apply:
        schedule.setdefault("weeks", []).extend(picks)
        schedule["weeks"].sort(key=lambda w: w["weekStart"])
        with open(sched_path, "w", encoding="utf-8") as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\nappended {len(picks)} week(s) to {sched_path} "
              f"({len(schedule['weeks'])} total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
