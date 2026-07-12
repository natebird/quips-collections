# Guide: consuming the generated collections

**Audience:** agents working in the **Quips iOS app** and the **quipsapp.com
website** repos. This describes a new set of *generated collections* — standalone
JSON feeds the `quips-collections` data repo now publishes alongside
`collections.json`, so the client can show dynamic, cross-collection views
(Recently Added, On This Day, …) without deriving them on-device.

You do **not** need this data repo to implement consumption — everything about
the contract is below.

---

## 1. What these are

Three feeds, each a **single JSON document** served from the same versioned base
as the index (`https://data.quipsapp.com/v<version>/`):

| Feed | File | Shape | What it holds |
|------|------|-------|---------------|
| Recently Added | `recently-added.json` | collection-shaped (`quotes[]`) | 25 newest quotes added to existing collections |
| On This Day | `on-this-day.json` | **day-keyed** (`days{}`) | quotes grouped by the calendar day they were said |
| Newsletter Picks | `newsletter-picks.json` | collection-shaped (`quotes[]`) | collection quotes featured in the Quote Unquote newsletter |

**These are NOT in `collections.json`.** They reuse quotes (and their ids/text)
from the real collections, so they deliberately break the index's
one-prefix-per-collection / cross-collection-uniqueness rules. Treat them as
**read-only presentation feeds**: render them, link back to the real collection
via each quote's `sourceCollection`, but don't run the collection validator on
them and don't expect their ids to be globally unique.

---

## 2. Discovery — always via the manifest

`https://data.quipsapp.com/latest/manifest.json` gained a `generated` object.
**Do not hardcode feed URLs** — read them from here, the same way you read
`indexUrl` / `indexHash`:

```jsonc
{
  "version": "1.9.0",
  "indexUrl":  "https://data.quipsapp.com/v1.9.0/collections.json",
  "indexHash": "sha256-…",
  "generated": {
    "recentlyAdded":   { "url": "https://data.quipsapp.com/v1.9.0/recently-added.json",  "hash": "sha256-…", "bytes": 14036 },
    "onThisDay":       { "url": "https://data.quipsapp.com/v1.9.0/on-this-day.json",      "hash": "sha256-…", "bytes": 401445 },
    "newsletterPicks": { "url": "https://data.quipsapp.com/v1.9.0/newsletter-picks.json", "hash": "sha256-…", "bytes": 3242 }
  }
}
```

Each entry has the **exact same `url` / `hash` / `bytes` contract as the index**:

- `url` — an immutable, versioned URL (safe to cache forever).
- `hash` — SRI-style `sha256-<base64>` of the file's raw bytes. Verify after
  download; re-hash a cached copy to decide whether to refetch.
- `bytes` — content length, for progress/budgeting.

**A key may be absent** (a feed can be added later, or skipped). Iterate the
`generated` map; don't assume a fixed set. Fall back gracefully — a missing feed
just means "don't show that shelf."

### Fetch/cache algorithm (same as the index)

1. Fetch `latest/manifest.json` (short TTL — it's the one mutable pointer).
2. For each `generated` entry you support: if your cached copy's hash ==
   `entry.hash`, use the cache. Otherwise fetch `entry.url`, verify
   `sha256(bytes) == entry.hash`, then cache keyed by that hash.
3. Never fetch a `v<version>/…` URL expecting it to change — versioned assets are
   immutable.

---

## 3. The quote object

Inside every feed, each quote is a **superset of the normal collection quote**
(`id`, `content`, `authorName`, `source`, `quoteDate`, `verificationStatus`,
`sourceType`, `notes`, `addedAt`) plus feed annotations:

| Extra field | On | Meaning |
|-------------|----|---------|
| `sourceCollection` | all feeds | id of the real collection this quote lives in (join back to `collections.json`) |
| `newsletterIssue` | `newsletter-picks` only | Quote Unquote issue number this quote was featured in |

Decode leniently: unknown fields should be ignored, and consumers that already
have a quote DTO can reuse it, treating `sourceCollection` / `newsletterIssue` as
optional additions. Use `sourceCollection` to route a tap to the underlying
collection, and to de-duplicate (the same quote can appear in more than one feed).

---

## 4. Per-feed shape & rendering

### Recently Added — `recently-added.json`
Collection-shaped. `quotes[]` are newest-first (the array is already sorted;
`lastUpdated` = the newest quote's `addedAt`). Excludes quotes that arrived as
part of a brand-new collection, so it reads as "new *additions*," not "new
collections." Render as a "Recently Added" shelf.

```jsonc
{
  "id": "recently-added", "name": "Recently Added", "generated": true,
  "colorName": "sky", "colorLightHex": "#1F9ED4", "colorDarkHex": "#45C2FC",
  "iconName": "sparkles", "category": "Featured",
  "lastUpdated": "2026-07-09T12:40:13Z",
  "quotes": [ { "id": "sci-030", "content": "…", "sourceCollection": "great-scientists", "addedAt": "2026-07-09T12:40:13Z", … } ]
}
```

### On This Day — `on-this-day.json`  ⚠️ different shape
**No `quotes[]`.** Instead a `days` object keyed by **`"MM-DD"`**:

```jsonc
{
  "id": "on-this-day", "name": "On This Day", "generated": true,
  "iconName": "calendar", "category": "Featured",
  "days": {
    "01-15": [ { "id": "…", "content": "…", "quoteDate": "1929-01-15", "sourceCollection": "civil-rights-voices", … } ],
    "07-04": [ … ]
  }
}
```

To render "today": compute the user's **local** date, format `MM-DD`, and look up
`days["MM-DD"]`. Notes:
- **Missing key** = no quotes for that day → hide the shelf (many of the 366 days
  are absent; only ~222 are populated).
- Quotes within a day are oldest-first by `quoteDate`.
- Only quotes with a full `YYYY-MM-DD` date qualify; approximate dates (`c. 1969`)
  are excluded by construction.
- Decide your policy for **Feb 29** (`"02-29"` exists) on non-leap years — e.g.
  fall through to `03-01` or hide.

### Newsletter Picks — `newsletter-picks.json`
Collection-shaped. Each quote carries `newsletterIssue`. Render an "As seen in
Quote Unquote #N" badge and, if you surface the newsletter, deep-link to that
issue. Small (only quotes with a verified match in the collections appear —
currently 5; misattribution/paraphrase issues have no verified quote and are
intentionally omitted).

---

## 5. Integrity, caching, versioning — recap

- **Verify every feed's `hash`** before caching (`ContentHash` on iOS; the same
  SRI scheme as `indexHash` and per-collection `contentHash`).
- **Cache by hash**; skip refetch when the manifest hash is unchanged.
- Feeds are **versioned with the dataset** — they live under `v<version>/` and
  move together with `collections.json`. `latest/manifest.json` is the only thing
  you poll.
- Feeds are **additive and forward-compatible**: a client that ignores the
  `generated` block entirely still works exactly as before.

---

## 6. Implementation checklist

**iOS**
- [ ] Extend the manifest DTO with an optional `generated: [String: FeedRef]`
      (`FeedRef { url, hash, bytes }`); iterate it, don't hardcode keys.
- [ ] Reuse the existing quote DTO; add optional `sourceCollection` /
      `newsletterIssue`. Keep lenient decoding.
- [ ] Model On This Day separately (`days: [String: [Quote]]`) — it is *not*
      `quotes[]`.
- [ ] Verify each feed with `ContentHash` before caching; key cache by hash.
- [ ] Route taps through `sourceCollection` into the existing collection detail.

**Website (quipsapp.com)**
- [ ] After pinning `.data-version`, fetch `generated.*` from the manifest and
      render the shelves you support.
- [ ] Verify `hash`; treat versioned URLs as immutable (cache-control is already
      `immutable`).
- [ ] On This Day: index `days` by the visitor's local `MM-DD`.

---

## 7. Regenerating (data-repo side, for reference)

The feeds are produced by `scripts/build_recently_added.py`,
`build_on_this_day.py`, and `build_newsletter_picks.py`. They are **build
artifacts, not committed** to the repo — the release workflow regenerates all of
them from the released data and uploads them under `v<version>/`, so the published
feeds always match the released collections. Consumers never need to run these;
they only read the published JSON named in the manifest.
