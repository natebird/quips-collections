# Changelog

All notable changes to the Quips collections data are documented here.

Versioning is semantic and scoped to the data:
- **patch** (`x.y.Z`) — quotes added to or edited within existing collections.
- **minor** (`x.Y.0`) — one or more new collections.
- **major** (`X.0.0`) — a breaking change to the data shape or schema.

Each released version is tagged `vX.Y.Z`; pushing the tag builds `dist/`, publishes
the GitHub Release, and uploads to `data.quipsapp.com`. The section for a version is
used verbatim as that release's notes.

## [Unreleased]
### Changed
Recoloured 23 collections so each token matches what the collection is actually
about. Some assignments were plainly wrong for the subject — Edgar Allan Poe was
a bright purple, Jane Austen a highlighter yellow, Zen wisdom purple, Johnny Cash
("the man in black") blue — and the palette was also badly unbalanced: 31 of 83
collections were amber or blue while six of Palette 2.0's sixteen tokens (rose,
lime, sky, indigo, violet, gray) were unused entirely. Notable moves: Poe, Stoic
wisdom, Zen wisdom, Battlestar Galactica and Johnny Cash to `gray`; Jane Austen,
Studio Ghibli and Leadership & Vision to `sky`; Great Poems, Rumi, Self-Compassion
and Marriage & Weddings to `rose`; Star Wars to `yellow` (the opening crawl);
Oscar Wilde to `green` (the green carnation); Sikh Wisdom to `orange` (saffron).
Every token is now in use and the largest bucket is 11 rather than 16. Only
`colorName` / `colorLightHex` / `colorDarkHex` changed — no quote, name, icon or
category was touched. Per-collection `contentHash`/`bytes` recomputed.

## [1.11.1] - 2026-08-08
### Changed
Normalised author initials to one house style — a period and a space between
each initial (`J. R. R. Tolkien`, not `J.R.R. Tolkien`), following Chicago 10.12
and the existing `C. S. Lewis` collection name. Five authors were spelled two
ways across collections, which `build_search_index.py` had been folding at build
time and reporting; the roster was correct but the underlying data disagreed
with itself.

17 values in 6 files: 12 `authorName` (A. A. Milne ×3, E. B. White ×2,
C. S. Lewis ×2, J. K. Rowling ×2, J. R. R. Tolkien ×3), plus 2 `source` and 3
`notes` where the same names appear in prose. No quote `content` was touched.

**Not a consumer-visible change.** The published roster already merged these,
so every author's `quoteCount` and `collectionCount` is unchanged
(C. S. Lewis 38, A. A. Milne 4, J. K. Rowling 4, J. R. R. Tolkien 4,
E. B. White 3); `authorCount` stays 941. What changes is that
`build_search_index.py` now reports no collisions and no roster entry carries a
`variants` array. Per-collection `contentHash`/`bytes` are updated in
`collections.json`, so progressive-download clients will refetch the six
affected collections.

## [1.11.0] - 2026-08-08
### Added
Two new published artifacts, both discovered through `latest/manifest.json` with
the existing `url`/`hash`/`bytes` contract:

- **`search-index.json`** — every quote in the dataset (2,711) flattened for
  search, plus the author roster derived from them (941, with spelling variants
  folded). The index ships only two `previewQuotes` per collection — about 6% of
  the corpus — so quote- and author-level search could not be answered from it
  without downloading all 83 collection files. ~1 MB raw, ~186 KB gzipped;
  consumers should fetch it lazily on first search. Named at the **top level** of
  the manifest as `searchIndex` rather than inside `generated`, because
  `generated` is a map of renderable shelves and this is not one.
- **`featured-collections.json`** — one featured collection per ISO week, each
  with a quote and an editorial note, built from the new committed
  `featured-schedule.json`. Every scheduled week is published and the client picks
  the one containing today, so the file is deterministic and independent of when a
  release is cut. Presentation is not duplicated: join `collectionId` to
  `collections.json`.

### Changed
- `scripts/build_manifest.py` publishes both, and gained an `ANCILLARY_ASSETS`
  list for assets that are published like a feed but are not one.
- The release workflow regenerates both before building `dist/`, and both the
  release and the PR validation workflows now gate on
  `scripts/build_featured.py --check` — a scheduled week that names a renamed or
  deleted collection fails CI instead of shipping as a blank week.
- PR validation now also *runs* every feed builder and the manifest builder, not
  just the validators. A change that breaks a builder used to pass CI and fail at
  release time, after the tag was already pushed.

### Notes
`scripts/build_search_index.py` reports author-name spelling collisions it had to
fold — currently five, all initials spacing (`C. S. Lewis` / `C.S. Lewis`,
`J.R.R. Tolkien` / `J. R. R. Tolkien`, and three more). The folding keeps the
published roster correct; normalising the underlying `authorName` values in the
collection files is still worth doing separately.

## [1.10.0] - 2026-08-08
Notes backfilled after the fact: this version was tagged without a CHANGELOG
section, so its GitHub Release shipped with the workflow's fallback body.

### Added
- **Avatar: The Last Airbender** (41 quotes) — the 83rd collection.
- 17 quotes across 12 existing collections: Great Poems and Great Scientists
  (3 each), Founding Fathers (2), and one each to Civil Rights Voices, Cosmos &
  Space, Dystopian Fiction, First Lines, Great Speeches, Grit & Perseverance,
  Literary Classics, On Leadership, and Resilience & Grit. Several are
  misattribution corrections carrying their real origin — the "Darwin" adaptability
  line to Leon C. Megginson (1963), "this too shall pass" to Lincoln (1859).
- Quote Unquote issues 16–18 recorded in `published-quotes.json` (Megginson,
  Lincoln, Frost). Hand-written issue references were dropped from the collection
  files in favour of that one record.

The dataset goes from 82 collections / 2,653 quotes to 83 / 2,711.

### Changed
Sourcing audit continued through 113 quotes in 11 runs, completing Bhagavad Gita
and Bible Wisdom and working through Bob Dylan and Champion's Mindset. Four
substantive fixes:
- `dylan-014` — restored a truncated quote. The stored text ended at "I welcome
  them with open arms," dropping the punchline about his bank account that is the
  point of the joke.
- `champ-008` — sourced to *The Mamba Mentality: How I Play* (2018), replacing a
  vague, undated "c. 2016 remarks" citation.
- `champ-019` — sentence order restored to match the original essay.
- `dylan-026` — downgraded to `unverified`. The *Chronicles* citation is doubtful
  on the attribution axis, not merely the wording one: the book's actual passage
  reads differently, and some sources trace this wording to the 1985 *Biograph*
  notes instead.

`champ-001` (Ali's ringside reaction) is flagged but unchanged — the "prettiest
thing that ever lived" clause could not be confirmed as part of that moment, and
no confirmed correct wording was found to fix it to.

## [1.9.1] - 2026-07-24
### Changed
Backfilled `quoteDate` on 124 of the 126 quotes that had none, across 22
collections. Where the quote is misattributed or has no primary source, the date
is that of the *earliest documented appearance* rather than the named speaker's
era, and every such quote's `notes` now says so:
- **Traced to a primary source** — see the seven verified below, plus `di-008`
  to Haskins's *Meditations in Wall Street* (1940) and `sci-018` to Teller in
  *LIFE* (1954).
- **Dated to a documented origin that is not the named author** — e.g. `di-027`
  "Lincoln" to a 1947 Stieglitz book advertisement, `lead-023` "Lincoln" to
  Ingersoll's 1883 address, `sc-021` "Twain" to Bovee (1857), `di-026` "Whitman"
  to an anonymous 1862 newspaper item, `grit-014` "Coolidge" to Munger (1881),
  `grit-025` "Bruce Lee" to Phillips Brooks (1886), `dream-028`/`di-023`
  "C. S. Lewis" to Les Brown (1992), `dream-019` "Walt Disney" to EPCOT's
  Horizons (1983).
- **Estimated** — the remainder carry a `c. YYYY` / decade-range / century value
  with a note stating the estimate's basis and that the full source is unverified.

This includes `di-012` (Henry Ford), whose date was cleared earlier in this
release cycle: the same note that cleared it pins the earliest documented
appearance to *Reader's Digest*, September 1947, so it is dated `c. 1947`.

Two traditional proverbs (`res-020` Japanese, `rest-028` Spanish) are left
undated: their origins are genuinely unfixable and no estimate would be honest.

Seven of the newly sourced quotes were then checked word-for-word against the
source text and promoted to `verificationStatus: "verified"`, with `source` and
`sourceType` replaced by the real citation:
- `sc-030` Booker T. Washington — *Up from Slavery* (1901), ch. 4
- `courage-022` C. S. Lewis — *The Screwtape Letters* (1942), Letter 29
- `lead-027` Martin Luther King Jr. — *Where Do We Go From Here* (1967), ch. 4
- `res-022` Robert Frost — Ray Josephs interview, *This Week Magazine*, 1954-09-05
- `grit-018` Marie Curie — letter to her brother Józef, 1894-03-18, printed in
  Eve Curie's *Madame Curie*
- `grit-023` Harriet Beecher Stowe — *Oldtown Folks* (1869), ch. 39, p. 507
- `courage-021` Ambrose Redmoon — 'No Peaceful Warriors!', *Gnosis* #21 (1991)

### Fixed
Two quotes carried the popular drift rather than what the author wrote. Both
are corrected to the source text (the only quote-text changes in this release):
- `grit-023` — the 1869 first edition reads "as **if** you could n't hold on…
  that's just the place and time that the tide 'll turn", spoken by the
  schoolmaster Jonathan Rossiter. The stored text had "as though" and had
  expanded every contraction.
- `courage-021` — Redmoon wrote "more important than **one's** fear". The
  circulating version drops the possessive that makes the judgment personal.

Reading the source texts also disproved two commonly repeated citations:
- `grit-018` is *not* in *Pierre Curie: With Autobiographical Notes* (1923),
  which is where it is usually placed — the words appear nowhere in that book.
  It is the 1894 letter above.
- `courage-023` Malala Yousafzai is *not* in her United Nations Youth Assembly
  address of 12 July 2013, though it is near-universally cited to it. That
  speech's nearest sentence is "I speak not for myself, but for those without a
  voice." The quote is dated `c. 2013` and stays unverified.
Still short of the bar and left `unverified`: `sci-018` (Bohr only via Teller's
secondhand account) and `di-008` (written by Henry Stanley Haskins but filed
under `authorName: "Ralph Waldo Emerson"`, so the attribution is the part that
is wrong).

No `authorName` changed.

## [1.9.0] - 2026-07-11
### Added
Two more generated collections, joining Recently Added, each published as a
standalone feed under `v<version>/` and listed in `manifest.json`'s new
`generated` block (url/hash/bytes, same contract as the index):
- **On This Day** (`on-this-day.json`) — quotes grouped by the calendar day they
  were said (`days` keyed by `MM-DD`); the client indexes by today's date. Only
  quotes with a full `YYYY-MM-DD` date qualify (~700 across ~222 days).
- **Newsletter Picks** (`newsletter-picks.json`) — collection quotes featured in
  the Quote Unquote newsletter, tagged with `newsletterIssue`.

Generators: `scripts/build_on_this_day.py`, `build_newsletter_picks.py` (plus the
existing `build_recently_added.py`). The generated feeds are **build artifacts** —
regenerated from the released data and uploaded by the release workflow, not
committed to the repo. `build_manifest.py` advertises every present feed, so
published feeds always match the release. The consumer contract is documented in
`docs/consuming-generated-collections.md`. All feeds are additive: a client that
ignores `manifest.generated` is unaffected.

## [1.8.0] - 2026-07-11
### Added
An `addedAt` timestamp (ISO-8601 UTC, like `lastUpdated`) on every collection and
every quote, recording when each first entered the dataset — distinct from a
quote's `quoteDate` (when it was *said*). This makes recency queryable from the
data itself instead of from git history, so dynamic collections like Recently
Added become a plain sort.

- Backfilled across all 82 collections and 2,648 quotes from git history
  (`scripts/backfill_added_at.py`). A collection's `addedAt` is its file's first
  commit; a quote's is the commit where its id first appears. Quotes added with a
  collection share that collection's `addedAt`. The field is mirrored into the
  `collections.json` index entries.
- Documented in `schema/{collection,index}.schema.json` (now required) and
  enforced by `scripts/validate_collections.py` (missing/malformed `addedAt`, or
  an index/file disagreement, fails `--strict` CI).
- The `add-quotes` and `add-collection` skills now stamp `addedAt` on new entries.

This is additive and forward-compatible: clients that don't read `addedAt` ignore it.

## [1.7.0] - 2026-07-10
### Changed
Migrated every collection's color to Quips Palette 2.0 (the app's regenerated
16-token OKLCH palette). For each of the 82 collections — in both `collections.json`
and its `collections/<id>.json` — `colorName` was remapped to a new token and two
fields were added next to it: `colorLightHex` and `colorDarkHex` (light/dark
appearance hex). Cross-platform clients use the hex pair; iOS prefers `colorName`
when present, so the change is forward-compatible and old clients keep working.

Token remaps applied: `gold`/`brown` → `amber`, `lemon` → `yellow`,
`mint` → `teal`, `forestGreen`/`mediumGreen` → `green`, `navyBlue`/`primaryBlue`
→ `blue`. `orange`, `purple`, `magenta`, `red`, `cyan` carried over unchanged.

The `colorLightHex`/`colorDarkHex` fields were added to `schema/collection.schema.json`
and `schema/index.schema.json`, and the one-shot remap is scripted in
`scripts/migrate_colors.py` (idempotent; re-running is a no-op).

## [1.6.0] - 2026-07-07
### Added
New Sports collection:
- `michael-jordan` (52 quotes) — drawn entirely from primary sources: his books
  *I Can't Accept Not Trying* (1994) and *Driven from Within* (2005), the 1997
  Nike "Failure" commercial, his 2009 Basketball Hall of Fame induction speech,
  *The Last Dance* (2020), and the 2013 ESPN feature "Michael Jordan Has Not Left
  The Building."

## [1.5.0] - 2026-07-06
### Added
Two new Movies collections:
- `lego-movies` (27 quotes) — weighted toward *The Lego Ninjago Movie* and the
  Ninjago animated series, rounded out with *The Lego Movie*, *The Lego Batman
  Movie*, and *The Lego Movie 2*.
- `teen-movies` (31 quotes) — anchored by *10 Things I Hate About You* and
  *Mean Girls*, with *Clueless*, *Legally Blonde*, *The Breakfast Club*,
  *Ferris Bueller's Day Off*, *Napoleon Dynamite*, *Bring It On*, and *Easy A*.

12 quotes from *The Emperor's New Groove* added to `disney-animated`, and 6
quotes from *The Matrix Reloaded*, *Revolutions*, and *Resurrections* added to
`scifi-screen`.

3 quotes added to `money-investing` (Howard Marks, Nassim Taleb, Seth Klarman)
and 1 to `great-poems` (Emily Dickinson).

### Fixed
`bsg-004`'s Season 1 opening-narration quote was missing a sentence
("They look and feel human. Some are programmed to think they are human.")
that sets up the Season 1 sleeper-agent storyline. Restored the full text and
clarified the source as specifically the Season 1 title card.

## [1.4.1] - 2026-07-01
### Changed
Added a dedicated `game` `sourceType` (mirroring the new `QuoteSourceType.game`
case in the app) and migrated the five Video Games collections off the
`video` stand-in they'd been using:
- `iconic-game-lines`, `legend-of-zelda`, `rpg-wisdom`, `starcraft`, `warcraft`
  — 117 quotes moved from `sourceType: "video"` to `sourceType: "game"`.

## [1.2.1] - 2026-06-30
### Changed
Reviewed every collection's `previewQuotes` for duplication and fixed the overlaps:
- No author is now featured in more than one collection's previews, and no quote
  is reused as a preview across collections.
- `inspiration-daily` — replaced an Einstein preview (kept in `creative-minds`)
  with Wayne Gretzky's "You miss 100% of the shots you don't take."
- `literary-classics` — replaced a Jane Austen preview (kept in `jane-austen`)
  with Dickens's "It was the best of times, it was the worst of times."
- `first-lines` — replaced a Tolkien preview (kept in `fantasy-worlds`) with
  Camus's "Mother died today."
- `how-i-met-your-mother` — replaced a malformed preview that matched no stored
  quote with Marshall's "Lawyered!" (also diversifies the featured characters).

Every preview now matches a real, verified quote in its collection.

## [1.2.0] - 2026-06-27
### Added
Nine new literary collections (346 verified quotes), each sourced from primary texts.

Single-author deep dives:
- **Shakespeare** — 54 verified quotes from the plays and sonnets.
- **Oscar Wilde** — 49 verified quotes from the plays, novel, and essays.
- **Sherlock Holmes** — 43 verified quotes from Arthur Conan Doyle's canon.
- **Edgar Allan Poe** — 31 verified quotes from the poems and tales.
- **Jane Austen** — 37 verified quotes from the novels.

Theme-based:
- **Great Poems** — 33 verified lines of verse across 27 poets.
- **Dystopian Fiction** — 29 verified quotes from the classic dystopias.
- **Children's Literature** — 31 verified quotes from beloved children's books.
- **First Lines** — 39 verified opening sentences of famous novels.

### Changed
- Reordered the collection index so LDS General Conference is no longer pinned to
  the top, and grouped the new literary collections after Literary Classics.

## [1.1.0] - 2026-06-27
### Added
- **Star Wars** collection — 60 verified quotes from across the Skywalker saga
  (original trilogy, prequels, and sequels).
- **Battlestar Galactica** collection — 25 verified quotes.

## [1.0.0] - 2026-06-27
### Added
- Initial public release: 15 collections, 582 quotes, served from
  `data.quipsapp.com`.
