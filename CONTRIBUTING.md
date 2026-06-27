# Contributing

Thanks for helping improve the Quips collections. This repo holds data only —
quotes and their metadata — validated in CI.

## Validate before opening a PR

```sh
python3 scripts/validate_collections.py            # full check
python3 scripts/validate_collections.py --strict   # warnings fail too (CI uses this)
python3 scripts/validate_collections.py --collection seinfeld
```

The validator is stdlib-only (no install needed) and is the single source of
truth for the rules below. JSON Schema in [`schema/`](schema/) describes the
file shapes for editors/tooling.

## Data model

### `collections.json` (index)

Top-level `version`, `lastUpdated`, and a `collections` array. Each entry
mirrors core fields of the collection file and adds `quoteCount` and two
`previewQuotes`. The entry's `name`, `author`, `category`, `colorName`, and
`iconName` must match the collection file exactly, and `quoteCount` must equal
the number of quotes in the file.

### `collections/<id>.json` (one collection)

```json
{
  "id": "seinfeld",
  "name": "Seinfeld",
  "description": "…",
  "author": "Quips Editorial",
  "colorName": "orange",
  "iconName": "tv.fill",
  "category": "Television",
  "lastUpdated": "2026-06-20T12:00:00Z",
  "quotes": [
    {
      "id": "seinfeld-001",
      "content": "No soup for you!",
      "authorName": "The Soup Nazi (Larry Thomas)",
      "source": "Seinfeld, S7E6 'The Soup Nazi' (1995)",
      "sourceType": "television",
      "quoteDate": "1995-11-02",
      "verificationStatus": "verified",
      "notes": "…"
    }
  ]
}
```

Rules enforced in CI:

- File `id` matches the filename; every file is in the index and vice versa.
- Quote `id` is `<prefix>-NNN` (3+ digits), unique within the collection; all
  quotes share one prefix, and each prefix is unique across all collections.
- Required quote fields: `id`, `content`, `authorName`, `source`,
  `verificationStatus`, `notes`.
- `verificationStatus` ∈ `verified`, `attributed`, `unverified`, `folk-wisdom`.
- `sourceType` (optional) must be a known value — keep it in sync with
  `QuoteSourceType` in the iOS app.
- No duplicate quote text within a collection.

## Releasing

Maintainers cut a release by pushing a semver tag (`git tag v1.2.0 && git push
origin v1.2.0`). See [README](README.md#releasing).
