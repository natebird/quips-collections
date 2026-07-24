# Changelog

All notable changes to the Quips collections data are documented here.

Versioning is semantic and scoped to the data:
- **patch** (`x.y.Z`) — quotes added to or edited within existing collections.
- **minor** (`x.Y.0`) — one or more new collections.
- **major** (`X.0.0`) — a breaking change to the data shape or schema.

Each released version is tagged `vX.Y.Z`; pushing the tag builds `dist/`, publishes
the GitHub Release, and uploads to `data.quipsapp.com`. The section for a version is
used verbatim as that release's notes.

## [1.9.1] - 2026-07-24
### Changed
Backfilled `quoteDate` on 123 of the 125 quotes that had none, across 22
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
