# Adding a blog post to the prototype

Every article page on this site is generated. Nothing is hand-written HTML, which
is why the spacing, the hero, the "Keep reading" cards and the donate block are
identical on all of them. To add a post you edit one data file and run three
commands.

## The short version

1. Add one entry to `data/articles.json`.
2. Run:

```
python3 tools/gen_articles.py         # builds article-<slug>.html
python3 tools/gen_articles_index.py   # its tile on articles.html and the pillar pages
python3 tools/sync.py                 # header and footer
```

3. Commit and push.

## The entry

```json
{
 "slug": "planning-for-fire-season-starts-in-the-garden",
 "title": "Planning for Fire Season Starts in the Garden",
 "eyebrow": "Story",
 "date": "November 2025",
 "place": "",
 "pillar": "heal",
 "standfirst": "One sentence that sits under the headline in the hero.",
 "hero": "https://fnpw.org.au/wp-content/uploads/2025/11/7-1024x576.jpg",
 "hero_alt": "What the hero photograph shows.",
 "description": "One or two sentences. Used for the meta description and the tile.",
 "credit": "",
 "blocks": [ ... ]
}
```

- `slug` becomes the filename, `article-<slug>.html`. Keep it lowercase with hyphens.
- `eyebrow` is the small label above the headline: "Story" for a blog piece,
  "News" for an announcement.
- `pillar` is one of `parks`, `species`, `heal`, `news`. It sets the coloured chip
  on the tile, drives the filter buttons on articles.html, and decides which
  pillar page the article appears on.
- `place` is optional. It shows next to the date, for example "Field River, Hallett Cove, SA".
- `credit` is optional. It prints a small source line at the foot of the article.
- `related` is optional. Leave it out and `tools/merge_articles.py` fills it with
  the two articles either side by date. Write it yourself to pin specific cards.

## The blocks

One block is one section on the page, and every section has the same padding top
and bottom. That is the whole point of the system: do not add sections by hand.

| type    | what it is                                        |
|---------|---------------------------------------------------|
| `lead`  | the opening passage, reading width                 |
| `text`  | a reading-width passage, optional eyebrow          |
| `band`  | image beside text, `"flip": true` puts the image right, `"paper": true` changes the background |
| `story` | the same as a band but on the dark green ground    |
| `wide`  | a full-width image on its own                      |
| `list`  | a standalone list section                          |
| `quote` | a centred pull quote                               |

The body of a `lead`, `text`, `band` or `story` block is a `flow`: an ordered
list of small pieces, so one section can hold paragraphs, subheadings, lists and
an inline picture without splitting into extra sections.

```json
{"type": "band",
 "eyebrow": "The science",
 "heading": "Why native plants matter",
 "img": "https://fnpw.org.au/wp-content/uploads/2025/11/7.jpg",
 "alt": "Native bushland in summer",
 "caption": "A short line under the photograph.",
 "flip": true,
 "flow": [
   {"p": "A paragraph."},
   {"h": "A subheading"},
   {"ul": ["a bullet", "another bullet"]},
   {"ol": ["a numbered step", "the next step"]},
   {"q": "A line worth pulling out."},
   {"img": "https://...jpg", "alt": "...", "caption": "..."}
 ]}
```

The first `{"h": ...}` in a `text` block is the section heading. Any heading after
it drops a level, so a long section stays readable.

## Rhythm, so the page does not feel flat

- Alternate the bands: give every second one `"flip": true`.
- Make one band a `story` block, usually about two thirds of the way down, at the
  most reflective moment in the piece.
- One `"paper": true` block near the story gives a tonal change.
- An article with no photographs is all `text` and `list` blocks. Give one or two
  of them `"paper": true` so the page still has a rhythm.

## Images

Hero and body images currently point at the WordPress media library on
fnpw.org.au. That is fine for the prototype. Before launch they need to be
downloaded and moved into `assets/img/articles/`, which is tracked in the
playbook as a launch dependency.

Take the hero from the post's `og:image`, not from the first image in the body.
Those are often different, and `og:image` is the one that is actually the feature
image.

## Bulk import

`tools/merge_articles.py` merges authored entries from `~/harvest/entries/*.json`
into `data/articles.json`, sorts the file newest first and fills in any missing
"Keep reading" cards. An entry that already has a hand-written `related` list
keeps it. Run it with `--relink` to rebuild every related list from scratch.

## What is generated and what is not

Generated, do not edit by hand:

- every `article-*.html` page
- the featured card and tile grid on `articles.html`, between the
  `<!--ARTFEAT:...-->` and `<!--ARTGRID:...-->` markers
- the three related-article tiles on `growing-national-parks.html`,
  `saving-species.html` and `healing-the-land.html`, between the
  `<!--ARTREL:...-->` markers

Safe to edit by hand: everything outside those markers, including the article
hero on articles.html, the filter bar, the sort control and the newsletter strip.
