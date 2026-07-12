#!/usr/bin/env python3
"""Generate newsletter-picks.json — collection quotes that have been featured in
the Quote Unquote newsletter ("As seen in Quote Unquote").

Cross-references published-quotes.json against the collections: a published
quote is matched to a collection quote when their normalized texts (lowercased,
alphanumerics only) contain one another. Matched collection quotes are emitted
with a `newsletterIssue` number and a `sourceCollection` back-reference. Not
every newsletter quote maps to a collection quote — many issues are about
misattributions/paraphrases with no verified entry in the dataset; those are
reported and skipped.

Standalone like the other generated feeds: NOT registered in collections.json
and outside collections/. Deterministic output. Stdlib only.

Usage: build_newsletter_picks.py [--root ROOT] [--out PATH]
"""

import argparse
import json
import os
import re
import sys
import unicodedata

META = {
    "id": "newsletter-picks",
    "name": "Newsletter Picks",
    "author": "Quips Editorial",
    "colorName": "violet",
    "colorLightHex": "#8839E9",
    "colorDarkHex": "#A174F0",
    "iconName": "envelope.fill",
    "category": "Featured",
    "generated": True,
}


def normalize(text):
    text = unicodedata.normalize("NFKD", text).lower()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text).split())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    coll_dir = os.path.join(args.root, "collections")
    files = sorted(fn for fn in os.listdir(coll_dir) if fn.endswith(".json"))

    # (collection_id, quote, normalized_content) for every quote.
    quotes = []
    for fn in files:
        data = json.load(open(os.path.join(coll_dir, fn), encoding="utf-8"))
        for q in data.get("quotes", []):
            quotes.append((data["id"], q, normalize(q.get("content", ""))))

    with open(os.path.join(args.root, "published-quotes.json"), encoding="utf-8") as f:
        published = json.load(f)

    picked, unmatched = [], []
    for p in published:
        pn = normalize(p.get("quote", ""))
        match = next((
            (cid, q) for cid, q, qn in quotes if pn and (pn in qn or qn in pn)
        ), None)
        if match:
            cid, q = match
            picked.append({**q, "sourceCollection": cid, "newsletterIssue": p.get("issueNumber")})
        else:
            unmatched.append(p.get("issueNumber"))

    # Deterministic: by issue number.
    picked.sort(key=lambda q: (q.get("newsletterIssue") or 0, q.get("id", "")))
    newest = max((q.get("addedAt", "") for q in picked), default="")

    collection = {
        **META,
        "description": (
            "Quotes from the collections that have been featured in the Quote "
            "Unquote newsletter, tagged with their issue number."
        ),
        "lastUpdated": newest,
        "quotes": picked,
    }

    out = args.out or os.path.join(args.root, "newsletter-picks.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {len(picked)} matched quote(s) to {out}; "
          f"{len(unmatched)} issue(s) with no collection quote: {sorted(filter(None, unmatched))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
