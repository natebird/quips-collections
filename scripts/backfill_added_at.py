#!/usr/bin/env python3
"""One-shot backfill of `addedAt` timestamps across the collections dataset.

Every collection and every quote gets an `addedAt` (full ISO-8601 UTC timestamp,
matching `lastUpdated`) recording when it first entered this repo's git history.
This makes recency queryable from the data itself instead of from git — the
Recently Added collection (and future dynamic collections) become a plain sort.

Recency source: a quote's addedAt is the author date of the commit where its id
first appears; a collection's addedAt is its file's first commit. Quotes present
at a collection's creation share that collection's addedAt — which is exactly the
signal the generator uses to exclude "quotes from a newly added collection"
(quote.addedAt == collection.addedAt → arrived at creation).

Idempotent: an object that already has `addedAt` is left untouched, so re-runs
are no-ops and hand-authored values are never clobbered. Placement mirrors the
repo's conventions — collection addedAt sits just before `lastUpdated`; a quote's
is appended after its existing fields. Stdlib only.

Usage: backfill_added_at.py [--root ROOT] [--check]
    --check  don't write; exit 1 if any object is still missing addedAt
"""

import argparse
import json
import os
import subprocess
import sys

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"  # UTC, matches lastUpdated / the validator regex


def git(root, *args):
    # TZ=UTC + format-local makes --date render commit times in UTC with a Z.
    env = {**os.environ, "TZ": "UTC"}
    return subprocess.run(
        ["git", "-C", root, *args],
        capture_output=True, text=True, check=True, env=env,
    ).stdout


def quote_ids(blob):
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        return []
    return [q.get("id") for q in data.get("quotes", []) if q.get("id")]


def first_seen(root, rel_path):
    """Return (creation_date, {quote_id: first_appearance_date}) for a file by
    walking its commits oldest→newest and recording each id's debut."""
    log = git(root, "log", "--reverse",
              "--date=format-local:" + TS_FMT, "--format=%H|%ad",
              "--", rel_path).strip()
    commits = [line.split("|", 1) for line in log.splitlines()] if log else []
    seen = {}
    for sha, date in commits:
        for qid in quote_ids(git(root, "show", f"{sha}:{rel_path}")):
            seen.setdefault(qid, date)
    return (commits[0][1] if commits else None), seen


def insert_before(obj, key, value, before):
    """Return obj with key:value inserted just before `before` (or appended if
    `before` is absent). No-op if key already present, preserving order."""
    if key in obj:
        return obj
    out = {}
    for k, v in obj.items():
        if k == before:
            out[key] = value
        out[k] = v
    if key not in out:
        out[key] = value
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    coll_dir = os.path.join(args.root, "collections")
    files = sorted(fn for fn in os.listdir(coll_dir) if fn.endswith(".json"))

    coll_added = {}   # cid -> addedAt (for mirroring into the index)
    missing = 0

    for fn in files:
        cid = fn[:-5]
        rel = f"collections/{fn}"
        path = os.path.join(coll_dir, fn)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        needs = "addedAt" not in data or any(
            "addedAt" not in q for q in data.get("quotes", [])
        )
        if not needs:
            coll_added[cid] = data.get("addedAt")
            continue

        created, seen = first_seen(args.root, rel)
        data = insert_before(data, "addedAt", created or data.get("lastUpdated"), "lastUpdated")
        for q in data.get("quotes", []):
            if "addedAt" not in q and q.get("id"):
                q["addedAt"] = seen.get(q["id"], data["addedAt"])
        coll_added[cid] = data["addedAt"]

        if args.check:
            missing += 1
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")

    # Mirror the collection-level addedAt into the index entries.
    index_path = os.path.join(args.root, "collections.json")
    with open(index_path, encoding="utf-8") as f:
        index = json.load(f)
    entries = index.get("collections", [])
    idx_changed = False
    new_entries = []
    for e in entries:
        if "addedAt" not in e:
            if args.check:
                missing += 1
            e = insert_before(e, "addedAt", coll_added.get(e.get("id")), "lastUpdated")
            idx_changed = True
        new_entries.append(e)
    index["collections"] = new_entries

    if not args.check and idx_changed:
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
            f.write("\n")

    if args.check:
        if missing:
            print(f"{missing} object(s) missing addedAt (run backfill_added_at.py)")
            return 1
        print(f"ok — addedAt present on all collections/quotes")
        return 0

    print(f"backfilled addedAt across {len(files)} collection(s) + index")
    return 0


if __name__ == "__main__":
    sys.exit(main())
