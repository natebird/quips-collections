# Changelog

All notable changes to the Quips collections data are documented here.

Versioning is semantic and scoped to the data:
- **patch** (`x.y.Z`) — quotes added to or edited within existing collections.
- **minor** (`x.Y.0`) — one or more new collections.
- **major** (`X.0.0`) — a breaking change to the data shape or schema.

Each released version is tagged `vX.Y.Z`; pushing the tag builds `dist/`, publishes
the GitHub Release, and uploads to `data.quipsapp.com`. The section for a version is
used verbatim as that release's notes.

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
