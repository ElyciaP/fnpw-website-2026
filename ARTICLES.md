# Adding a blog post to the prototype

Every article page is generated. Nothing is hand-written HTML, which is why the
spacing, the hero, the "keep reading" cards and the donate block are identical on
all of them. To add a post you edit one data file and run four commands.

## The short version

1. Add one entry to `data/articles.json`.
2. Run:

```
python3 tools/merge_articles.py       # sorts, and tops the related cards up to three
python3 tools/gen_articles.py         # builds article-<slug>.html
python3 tools/gen_articles_index.py   # its tile on articles.html and the pillar pages
python3 tools/sync.py                 # header and footer
```

3. Commit and push.

`python3 tools/gen_articles.py <slug>` rebuilds a single article if you are
iterating on one.

## How a page is laid out

An article is treated as one document, not as a stack of sections. The body is a
single CSS grid with a fixed text column of about 66 characters, and images break
out of that column rather than sitting beside it, so the left edge of the body
copy is identical from the first word to the last. There are two image widths in
the body, the text column and a wider breakout, plus the full-bleed hero.

The hero is the site's standard one: the photograph sits behind the words at
normal page width, so it lines up with the heroes on the project and pillar
pages.

Spacing is deliberate and worth not breaking:

- Every gap between one section and the next is exactly `--sec-y`, top and
  bottom, the same token the rest of the site uses. Three `:has()` rules zero the
  bottom margin of whatever sits immediately before a section boundary, so a
  paragraph's own margin never adds to the next heading's.
- Paragraph spacing is deliberately tight, `1em` against a `1.65` line height.
  A third of the paragraphs in these articles run under 25 words, because the old
  WordPress template was padding them out. Loosen this and the pages read as
  mostly white space.

The previous template, which put the text in a half-width column beside each
image and moved that left edge several times per article, is kept for reference
at `tools/gen_articles_bands.py`. It is not wired into anything.

## The entry

```json
{
 "slug": "planning-for-fire-season-starts-in-the-garden",
 "title": "Planning for Fire Season Starts in the Garden",
 "eyebrow": "Story",
 "date": "November 2025",
 "place": "",
 "pillar": "heal",
 "standfirst": "One sentence, sits under the headline in the hero.",
 "hero": "https://fnpw.org.au/wp-content/uploads/2025/11/7-1024x537.jpg",
 "hero_alt": "What the hero photograph actually shows.",
 "description": "One or two sentences. Used for the meta description and the tile.",
 "credit": "",
 "blocks": [ ... ]
}
```

- `slug` becomes the filename, `article-<slug>.html`. Lowercase with hyphens.
- `eyebrow` is the small label above the headline: "Story" for a blog piece,
  "News" for an announcement.
- `pillar` is one of `parks`, `species`, `heal`, `news`. It sets the coloured
  chip on the tile, drives the filter buttons on articles.html, and decides which
  pillar page the article appears on.
- `place` is optional and shows next to the date, for example
  "Field River, Hallett Cove, SA".
- `credit` is optional and prints a small source line at the foot of the article.
- `related` is optional. Leave it out and `merge_articles.py` fills it with the
  three nearest articles by date. Write one or two entries yourself to pin
  specific cards and it will top the list up to three around them.
- Take `hero` from the post's `og:image`, not from the first image in the body.
  Those are often different, and `og:image` is the real feature image.

## The blocks

| type    | what it is                                                    |
|---------|---------------------------------------------------------------|
| `lead`  | the opening passage                                            |
| `text`  | a passage, optional `eyebrow` and heading                      |
| `band`  | a section that opens with its photograph                       |
| `story` | the same, but the whole section runs on the dark green ground  |
| `wide`  | a photograph on its own inside a passage                       |
| `quote` | a pull quote, `text` plus `attrib`                             |

The body of a `lead`, `text`, `band` or `story` block is a `flow`: an ordered
list of small pieces, so one section can hold paragraphs, subheadings, lists and
a picture without splitting into extra sections.

```json
{"type": "band",
 "eyebrow": "The science",
 "heading": "Why native plants matter",
 "img": "https://fnpw.org.au/wp-content/uploads/2025/11/7-1024x537.jpg",
 "alt": "Native bushland in summer",
 "caption": "Only if it says something the paragraph does not.",
 "flow": [
   {"p": "A paragraph."},
   {"h": "A subheading"},
   {"ul": ["a bullet", "another bullet"]},
   {"ol": ["a numbered step", "the next step"]},
   {"q": "A line worth pulling out.", "attrib": "Who said it"}
 ]}
```

Blocks are grouped into sections at render time. A section starts at a heading
and runs until the next one, so a section that begins in the dark chapter break
also ends there. An image with no text before it opens its section and breaks
wide; every other image stays at column width.

Make one section a `story` block, usually about two thirds of the way down, at
the most reflective moment. That is the single dark band, and one per article is
the right number.

## Captions

Most of the captions in this file were generated by lifting the opening sentence
of the paragraph beside the image, which means they repeat text the reader is
about to read. The generator suppresses any caption that duplicates the start of
the paragraph under it. Write a caption only when it says something the body does
not, such as a place, a date or a credit.

## Images

Hero and body images point at the WordPress media library on fnpw.org.au. That is
fine for the prototype. Before launch they need to be downloaded into
`assets/img/articles/`, which the playbook tracks as a launch dependency. They
also need recompressing: the current files run about 600KB at 1024px, roughly six
times what they should be.

The `srcset` in the generator assumes the 768 / 1024 / 1536 renditions that
WordPress made for the current uploads. A general version needs an image
manifest, which comes free once the images are local.

## Bulk import

`tools/merge_articles.py` adds any article from `~/harvest/entries/*.json` that is
not already in `data/articles.json`, sorts the file newest first, and tops up the
related cards.

**`data/articles.json` is the source of truth.** An article already in it is not
re-imported, because the file carries later editing (image cuts, corrected alt
text, pillars) that the raw harvest entries do not have. `--reimport` overrides
that deliberately. `--relink` throws away every related list and rebuilds it from
the dates.

## What is generated and what is not

Generated, do not edit by hand:

- every `article-*.html` page
- the featured card and tile grid on `articles.html`, between the
  `<!--ARTFEAT:...-->` and `<!--ARTGRID:...-->` markers
- the three related tiles on `growing-national-parks.html`,
  `saving-species.html` and `healing-the-land.html`, between the
  `<!--ARTREL:...-->` markers

Safe to edit by hand: everything outside those markers, including the articles
page hero, the filter bar, the sort control and the newsletter strip.

## House rules

- Never use an em dash.
- Write the organisation's name as "Foundation for National Parks & Wildlife"
  with an ampersand, never "and".
- Spell it "Kaurna Yarta", never "Kaurna Yerta".
- The paragraphs in `data/articles.json` are published copy, reproduced verbatim.
  Do not rewrite them.
