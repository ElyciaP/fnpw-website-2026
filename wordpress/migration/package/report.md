# Conversion report

Written by `convert.py` on 13 November 2026. Regenerate rather than edit.

## Summary

| | Count |
|---|---|
| Pages converted | 295 (167 articles, 88 projects, 40 pages) |
| Top-level sections | 3544 |
| Sections converted to core blocks (Group with editable Heading, Paragraph or List inside) | 2949 (83%) |
| Sections carried whole in one Custom HTML block | 593 (17%) |
| Sections drawn by the theme or a dynamic block | 2 |
| Editable core blocks (Heading, Paragraph, List) | 4414 |
| Group blocks | 1761 |
| Custom HTML blocks in total (whole sections plus pieces inside converted sections) | 1504 |
| Images and documents to sideload from GitHub Pages | 232 |
| ...of which are not in the repo asset list | 16 |
| Images left on the live media library (URL unchanged) | 238 |
| Unresolved internal links | 0 |

For articles a "section" is one child of the article body (`.ed`): a paragraph, heading, figure or band. The hero, standfirst, related stories, back link and donate band of an article come from the theme template, not the post content.

| Kind | Sections | As core blocks |
|---|---|---|
| page | 197 | 144 (73%) |
| project | 591 | 385 (65%) |
| article | 2756 | 2420 (88%) |

## How the conversion decides

- A heading, paragraph or plain list becomes a core block when it has nothing but a class (and, for headings and paragraphs, a margin-only inline style, which maps to the block spacing setting). A `div`, `section`, `article`, `header`, `footer` or `aside` with only a class and id becomes a Group when something inside it is editable.
- Anything else is carried byte for byte in Custom HTML: images and figures (the Image block adds its own wrapper and drops `sizes`, `loading` and dimensions), links styled as buttons (the Button block wraps the link in a div), cards that are links, elements with inline styles beyond margins, `data-` attributes, `hidden`, forms, iframes, SVG, tabs, carousels, maps and accordions.
- Responsive variants (`<source>` and `srcset` pointing at `assets/img/r/`) are dropped from the HTML; the importer sideloads the fallback image and WordPress makes its own sizes. CSS backgrounds keep both files.

## Interactive components carried as HTML with their scripts

| Component | Pages | Script handling |
|---|---|---|
| Project map | projects | Dynamic block `fnpw/project-map` (FNPW Core); the static map script is dropped |
| Project grid, pillar filter, search and sort | projects | HTML + page script in `_fnpw_page_js` |
| Project grid with pillar filter | growing-national-parks, healing-the-land, saving-species | HTML + shared theme script |
| Stories filter, sort and paging | news | Theme block `fnpw/stories-index` from real posts + `articles.js` |
| Volunteer sites map, photo gallery | five city volunteering pages | HTML + shared theme scripts + `gallery.js` |
| State tabs, photo carousel, accordions | corporate-volunteering | HTML + page script + `carousel.js` |
| Tabs | government-partnerships, partner-with-us | HTML + page script |
| Read more toggles, timeline rail, card arrows, section snap | about-us | HTML + page scripts + `snap.js` (meta `fnpw_snap`) |
| Load more list | our-impact, corporate-partnerships | HTML + page script |
| Reports filter | annual-reports-financials | HTML + page script |
| Project slider, animated counters | home | HTML + page script; counters in `main.js` |
| Accordions (details) | bequest, donate-land, faqs, government-partnerships, corporate-volunteering | HTML (native details, no script) |
| HubSpot forms | 18 pages | HTML markup + embed script in `_fnpw_ext_js` + shared fallback script |
| Article reading bar | all articles | Theme script `article-progress.js` by template |
| Video, podcast and Google map embeds | about-us, koala-facts, contact-us | HTML (iframe) |

No custom blocks were built for these beyond the project map and the Stories index.

## Differences from the static pages, by design

- **Article dates.** The theme prints the post date as "Month YYYY" in the article hero and on cards. 149 static articles print the raw date (2022-07-06) instead; in WordPress they read the same way as the rest.
- **Article titles.** A post that already exists keeps its WordPress title, and the article hero prints that title. The static headline is in the package as `static_title` for checking, not imported. The three pages shown in the article layout keep their short page title and carry the headline in `fnpw_headline`.
- **Flat heroes.** 45 articles have a feature image too small for a full-width hero. They carry `fnpw_hero_flat` so the theme leaves the image off the hero even though the post has a featured image.
- **Stories index.** Drawn from published posts plus the pages that use the article template. Press-coverage posts in the `media` category that were not imported stay off it (they are on In the news). Card order follows the WordPress post dates.
- **Search.** The static page searched an index in the browser; WordPress search answers instead, so result counts differ.
- **Images inside content.** `<img>` tags keep one file (the fallback). WordPress does not add `srcset` to them because they are not Image blocks, so they are heavier on phones than the static `r/` variants were. Featured images and CSS backgrounds are unaffected.
- **Theme photos.** Three photos are used by theme files, not by content, and must be copied into the theme by hand because they are not in this copy of the repo: `assets/img/articles-hero-kookaburra.jpg`, `assets/img/r/articles-hero-kookaburra-1600.webp` (Stories hero) and `assets/img/search-hero-koala.jpg` (Search hero).

## Shared files written into the theme

- `assets/css/shared/corporate-volunteering-f91c1f87.css`
- `assets/css/shared/privacy-policy-6aaded07.css`
- `assets/css/shared/project-4206f1bf.css`
- `assets/css/shared/project-6df8bcef.css`
- `assets/js/shared/corporate-volunteering-c6b0b783.js`
- `assets/js/shared/growing-national-parks-70bf2c5f.js`
- `assets/js/shared/hs-fallback-884c1850.js`
- `assets/js/shared/volunteer-90c0411a.js`

## Unresolved links

None. Every internal `.html` link maps to a WordPress URL in page-map.csv.

## Images not in the repo asset list

- `assets/img/bequests-advisers-coastal-walk.jpg`
- `assets/img/bequests-hero-lookout-sunset.jpg`
- `assets/img/bequests-koala-branch.jpg`
- `assets/img/contact-hero-pigface.jpg`
- `assets/img/government-forest-canopy.jpg`
- `assets/img/government-grants-planting.jpg`
- `assets/img/home-partner-escarpment.jpg`
- `assets/img/partner-blue-mountains.jpg`
- `assets/img/partner-murray-mouth-aerial.jpg`
- `assets/img/projects/granite-little-penguin-burrow.jpg`
- `assets/img/projects/lion-island-burrows-beach.jpg`
- `assets/img/projects/lion-island-burrows-boat.jpg`
- `assets/img/projects/lion-island-penguins-burrow.jpg`
- `assets/img/projects/little-penguin-rock-crevice.jpg`
- `assets/img/projects/little-penguin-sand-night.jpg`
- `assets/img/projects/manly-little-penguin-nestbox.jpg`

## Per page

| File | WordPress URL | Sections: blocks / HTML / theme | Editable blocks | HTML blocks | CSS | JS | Unresolved links | Media (missing) |
|---|---|---|---|---|---|---|---|---|
| article-international-womens-day-2020.html | /news/latest-news/international-womens-day-2020/ | 9 / 1 / 0 | 9 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-wildlife-heroes-caring-for-carers-podcast.html | /news/latest-news/the-wildlife-heroes-caring-for-carers-podcast/ | 23 / 0 / 0 | 23 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-bushfire-recovery-grants-to-support-wildlife-volunteers.html | /news/latest-news/bushfire-recovery-grants-to-support-wildlife-volunteers/ | 23 / 4 / 0 | 23 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-community-conservation-grants-2019-grantees.html | /news/latest-news/fnpw-community-conservation-grants-2019-grantees/ | 12 / 1 / 0 | 12 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-community-conservation-grants-2020-grantees.html | /news/latest-news/fnpw-community-conservation-grants-2020-grantees/ | 1 / 0 / 0 | 1 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-to-plant-1-million-trees-across-australia-in-response-to-devastating-bushfires.html | /news/latest-news/fnpw-to-plant-1-million-trees-across-australia-in-response-to-devastating-bushfires/ | 17 / 3 / 0 | 17 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-take-time-for-nature-this-world-environment-day.html | /news/latest-news/take-time-for-nature-this-world-environment-day/ | 28 / 0 / 0 | 28 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-acts-greening-australia-nursery-one-of-nations-first-bushfire-recovery-nurseries.html | /news/latest-news/acts-greening-australia-nursery-one-of-nations-first-bushfire-recovery-nurseries/ | 5 / 2 / 0 | 5 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-sas-yankalilla-community-nursery-one-of-australias-first-bushfire-recovery-nurseries.html | /news/latest-news/sas-yankalilla-community-nursery-one-of-australias-first-bushfire-recovery-nurseries/ | 9 / 0 / 0 | 9 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-grants-announced-to-assist-wildlife-rehabilitators.html | /news/latest-news/grants-announced-to-assist-wildlife-rehabilitators/ | 13 / 0 / 0 | 13 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-nsw-wildlife-heroes-vaccination-fund-grant-recipients-announced.html | /news/latest-news/nsw-wildlife-heroes-vaccination-fund-grant-recipients-announced/ | 17 / 1 / 0 | 17 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-australian-government-support-for-wildlife-heroes.html | /news/latest-news/australian-government-support-for-wildlife-heroes/ | 13 / 0 / 0 | 13 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-large-durable-asset-grants-recipients-announced.html | /news/latest-news/wildlife-heroes-large-durable-asset-grants-recipients-announced/ | 31 / 1 / 0 | 31 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-giving-australian-wildlife-volunteers-the-help-they-need.html | /news/latest-news/giving-australian-wildlife-volunteers-the-help-they-need/ | 13 / 0 / 0 | 13 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-emergency-grants-provide-relief-for-nsw-wildlife-volunteers.html | /news/latest-news/emergency-grants-provide-relief-for-nsw-wildlife-volunteers/ | 10 / 0 / 0 | 10 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-announces-bushfire-emergency-appeal.html | /news/latest-news/fnpw-announces-bushfire-emergency-appeal/ | 12 / 1 / 0 | 12 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-aboriginal-site-recording-yengo-np-and-surrounding-country.html | /news/latest-news/aboriginal-site-recording-yengo-np-and-surrounding-country/ | 6 / 2 / 0 | 6 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-announces-healing-our-land.html | /news/latest-news/fnpw-announces-healing-our-land/ | 9 / 1 / 0 | 9 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-wildlife-rescue-handbook-to-keep-animals-and-rescuers-safe-this-summer.html | /news/latest-news/wildlife-heroes-wildlife-rescue-handbook-to-keep-animals-and-rescuers-safe-this-summer/ | 11 / 0 / 0 | 11 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-loccitane-australia-helps-fnpw-plant-one-million-trees.html | /news/latest-news/loccitane-australia-helps-fnpw-plant-one-million-trees/ | 13 / 2 / 0 | 13 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-fnpw-announces-next-bushfire-recovery-nursery.html | /news/latest-news/the-fnpw-announces-next-bushfire-recovery-nursery/ | 4 / 0 / 0 | 4 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-50th-anniversary-tour-of-nilpena-and-the-flinders-ranges.html | /news/latest-news/fnpw-50th-anniversary-tour-of-nilpena-and-the-flinders-ranges/ | 8 / 2 / 0 | 8 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-banking-on-the-future.html | /news/latest-news/banking-on-the-future/ | 9 / 3 / 0 | 9 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-our-impact.html | /news/latest-news/our-impact/ | 5 / 0 / 0 | 5 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-matthew-mcconaugheys-wild-turkey-and-homecamp-pair-up-to-create-tent-and-give-a-proportion-of-proceeds-to-fnpw.html | /news/media/matthew-mcconaugheys-wild-turkey-and-homecamp-pair-up-to-create-tent-and-give-a-proportion-of-proceeds-to-fnpw/ | 2 / 1 / 0 | 2 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-are-you-ready-for-bushfire-season.html | /news/latest-blogs/are-you-ready-for-bushfire-season/ | 15 / 4 / 0 | 15 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-a-visit-to-the-southern-flinders-ranges.html | /news/latest-news/a-visit-to-the-southern-flinders-ranges/ | 10 / 3 / 0 | 10 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-supports-the-australian-wildlife-rehabilitation-conference.html | /news/latest-news/wildlife-heroes-supports-the-australian-wildlife-rehabilitation-conference/ | 8 / 1 / 0 | 8 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-byron-bay-wildlife-hospital-goes-on-tour-with-fnpws-wildlife-friendly-vets.html | /news/latest-news/byron-bay-wildlife-hospital-goes-on-tour-with-fnpws-wildlife-friendly-vets/ | 3 / 2 / 0 | 3 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wollombi-and-laguna-primary-school-earth-day-planting.html | /news/latest-blogs/wollombi-and-laguna-primary-school-earth-day-planting/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-turtle-talk.html | /news/latest-news/turtle-talk/ | 19 / 0 / 0 | 19 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-restoration-funding-closing-date-extended.html | /news/latest-news/fnpw-restoration-funding-closing-date-extended/ | 11 / 0 / 0 | 11 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-thank-you-for-completing-the-2021-supporter-survey.html | /news/latest-news/thank-you-for-completing-the-2021-supporter-survey/ | 12 / 0 / 0 | 12 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-warddeken-mayh-species-recovery-project.html | /news/latest-blogs/warddeken-mayh-species-recovery-project/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-abc-radio-interview-with-kylie-piper.html | /news/media/abc-radio-interview-with-kylie-piper/ | 14 / 1 / 0 | 14 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-kosciuszko-national-park.html | /news/latest-news/kosciuszko-national-park/ | 18 / 2 / 0 | 18 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-regeneration-of-kosciuszko-national-park.html | /news/latest-news/regeneration-of-kosciuszko-national-park/ | 17 / 4 / 0 | 17 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-polish-fundraise-for-the-recovery-of-kosciuszko-national-park.html | /news/latest-news/polish-fundraise-for-the-recovery-of-kosciuszko-national-park/ | 20 / 0 / 0 | 20 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-launch-flood-emergency-appeal.html | /news/latest-news/fnpw-launch-flood-emergency-appeal/ | 15 / 0 / 0 | 15 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-protecting-bilbies-through-right-way-fire-management-in-the-kimberley.html | /news/latest-news/protecting-bilbies-through-right-way-fire-management-in-the-kimberley/ | 8 / 0 / 0 | 8 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-nsws-hawkesbury-community-nursery-as-one-of-australias-first-bushfire-recovery-nurseries.html | /news/latest-news/nsws-hawkesbury-community-nursery-as-one-of-australias-first-bushfire-recovery-nurseries/ | 9 / 0 / 0 | 9 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-launches-new-bushfire-recovery-nurseries.html | /news/latest-news/fnpw-launches-new-bushfire-recovery-nurseries/ | 18 / 2 / 0 | 18 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-foundation-for-national-parks-wildlife-wins-charity-of-the-year-2021.html | /news/latest-news/foundation-for-national-parks-wildlife-wins-charity-of-the-year-2021/ | 4 / 4 / 0 | 4 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-flood-emergency-grant-applications-open-in-nsw.html | /news/latest-news/fnpw-flood-emergency-grant-applications-open-in-nsw/ | 4 / 0 / 0 | 4 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-updates-from-the-field.html | /news/latest-blogs/wildlife-heroes-updates-from-the-field/ | 10 / 0 / 0 | 10 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-giving-day-2022.html | /news/latest-news/fnpw-giving-day-2022/ | 7 / 0 / 0 | 7 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-discovering-a-hidden-gem.html | /news/latest-blogs/discovering-a-hidden-gem/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-update-from-namabunda-bundjalung-country.html | /news/latest-blogs/update-from-namabunda-bundjalung-country/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-crookshanks-wildlife-corridor-will-extend-from-the-murrumbidgee-river-to-crookshanks-peak.html | /news/latest-blogs/crookshanks-wildlife-corridor-will-extend-from-the-murrumbidgee-river-to-crookshanks-peak/ | 8 / 1 / 0 | 8 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-currumbin-wildlife-sanctuary-bushland-regeneration-project.html | /news/latest-blogs/currumbin-wildlife-sanctuary-bushland-regeneration-project/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-desert-yarning-with-don-rowlands.html | /news/latest-blogs/desert-yarning-with-don-rowlands/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-drawing-australian-gliders.html | /news/latest-news/drawing-australian-gliders/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-un-schools-program.html | /news/latest-news/un-schools-program/ | 10 / 0 / 0 | 10 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-10000-native-give-away-trees-and-shrubs-hit-the-ground.html | /news/latest-blogs/10000-native-give-away-trees-and-shrubs-hit-the-ground/ | 9 / 1 / 0 | 9 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-browsers-not-just-grazers.html | /news/latest-blogs/browsers-not-just-grazers/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-nsw-flood-emergency-grants-awarded.html | /news/latest-news/wildlife-heroes-nsw-flood-emergency-grants-awarded/ | 23 / 0 / 0 | 23 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-state-of-the-environment-report-statement.html | /news/latest-news/fnpw-state-of-the-environment-report-statement/ | 5 / 0 / 0 | 5 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-planting-parties-key-to-success-on-small-properties.html | /news/latest-blogs/planting-parties-key-to-success-on-small-properties/ | 12 / 4 / 0 | 12 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-impactreport2021.html | /news/latest-news/impactreport2021/ | 2 / 0 / 0 | 2 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-riverina-highlands-landcare-nursery-upgrade.html | /news/latest-news/riverina-highlands-landcare-nursery-upgrade/ | 6 / 2 / 0 | 6 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-upcoming-activities.html | /news/latest-news/wildlife-heroes-upcoming-activities/ | 11 / 1 / 0 | 11 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-growing-trees.html | /news/latest-news/growing-trees/ | 8 / 1 / 0 | 8 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes.html | /news/latest-news/wildlife-heroes/ | 7 / 1 / 0 | 7 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-currumbin-wildlife-sanctuary-bushland-regeneration-project-2.html | /news/latest-blogs/currumbin-wildlife-sanctuary-bushland-regeneration-project-2/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-drowning-in-butterfly-vines.html | /news/latest-blogs/drowning-in-butterfly-vines/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-challenges-facing-the-australian-climate.html | /news/latest-news/the-challenges-facing-the-australian-climate/ | 4 / 0 / 0 | 4 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-trees-planted-in-mccullys-gap.html | /news/latest-blogs/trees-planted-in-mccullys-gap/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-exciting-progress-at-the-bunyah-restoration-project.html | /news/latest-blogs/exciting-progress-at-the-bunyah-restoration-project/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-royalla-landcare-conservation-area-restoration-project.html | /news/latest-blogs/royalla-landcare-conservation-area-restoration-project/ | 8 / 1 / 0 | 8 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-bombay-bossiaea-post-fire-survey-success.html | /news/latest-blogs/bombay-bossiaea-post-fire-survey-success/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-rewilding.html | /news/latest-blogs/rewilding/ | 2 / 2 / 0 | 2 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-trees-for-fire-affected-landcarers.html | /news/latest-blogs/trees-for-fire-affected-landcarers/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wombatrescues.html | /news/latest-blogs/wombatrescues/ | 6 / 2 / 0 | 6 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-nationalparkshiddengems.html | /news/latest-news/nationalparkshiddengems/ | 39 / 12 / 0 | 39 | 12 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-crookshanks-wildlife-corridor-fnpw-extension-flourishing.html | /news/latest-blogs/crookshanks-wildlife-corridor-fnpw-extension-flourishing/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-upper-yango-creek-residents-get-planting.html | /news/latest-blogs/upper-yango-creek-residents-get-planting/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-thriving-seedlings.html | /news/latest-blogs/thriving-seedlings/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-bushfire-recovery-grant-0014brrg_r2-summary-report-rifflerun.html | /news/latest-blogs/fnpw-bushfire-recovery-grant-0014brrg_r2-summary-report-rifflerun/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-cop15-australia.html | /news/latest-blogs/cop15-australia/ | 43 / 2 / 0 | 43 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-30765.html | /news/media/30765/ | 14 / 1 / 0 | 14 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-grants.html | /news/latest-news/wildlife-heroes-grants/ | 8 / 0 / 0 | 8 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-application-highlight.html | /news/latest-news/wildlife-heroes-application-highlight/ | 7 / 0 / 0 | 7 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-baby-banksias-thrive-in-volunteer-run-nursery.html | /news/latest-blogs/baby-banksias-thrive-in-volunteer-run-nursery/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-bushfire-recovery-partnership.html | /news/latest-news/bushfire-recovery-partnership/ | 7 / 2 / 0 | 7 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-namabundaplanting.html | /news/latest-blogs/namabundaplanting/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-supporting-recovery-of-flood-impacted-landscapes-in-the-northern-rivers-nsw.html | /news/latest-blogs/supporting-recovery-of-flood-impacted-landscapes-in-the-northern-rivers-nsw/ | 7 / 1 / 0 | 7 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-2022-impact-report.html | /news/latest-news/2022-impact-report/ | 3 / 0 / 0 | 3 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-frog-disease.html | /news/latest-blogs/frog-disease/ | 3 / 1 / 0 | 3 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-wildlife-heroes-project-supporting-volunteers-through-training.html | /news/latest-news/wildlife-heroes-project-supporting-volunteers-through-training/ | 9 / 0 / 0 | 9 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-we-must-act-now-ipcc-report.html | /news/latest-news/we-must-act-now-ipcc-report/ | 17 / 0 / 0 | 17 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-quoll-headquarters-koala-recovery-project.html | /news/latest-blogs/quoll-headquarters-koala-recovery-project/ | 11 / 4 / 0 | 11 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-80000-additional-trees-to-be-planted-at-friends-of-the-koala-nursery-to-support-koala-population.html | /news/latest-news/80000-additional-trees-to-be-planted-at-friends-of-the-koala-nursery-to-support-koala-population/ | 9 / 2 / 0 | 9 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-takeaways-for-mitigating-effects.html | /news/latest-blogs/takeaways-for-mitigating-effects/ | 18 / 0 / 0 | 18 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-new-chair-and-new-directors.html | /news/media/fnpw-new-chair-and-new-directors/ | 24 / 1 / 0 | 24 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-upper-snowy-landcare-network.html | /news/latest-blogs/upper-snowy-landcare-network/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-farmers-creek-revegetation-project.html | /news/latest-blogs/farmers-creek-revegetation-project/ | 2 / 1 / 0 | 2 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-plantings-provide-green-corridors-for-wildlife.html | /news/latest-blogs/plantings-provide-green-corridors-for-wildlife/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-sherwood-creek.html | /news/latest-blogs/sherwood-creek/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-nymboida-river-riparian.html | /news/latest-blogs/nymboida-river-riparian/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-latest-blog-ian-darbyshire-30-by-30-target.html | /news/latest-blogs/latest-blog-ian-darbyshire-30-by-30-target/ | 29 / 0 / 0 | 29 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-re-wilding.html | /news/latest-blogs/re-wilding/ | 3 / 1 / 0 | 3 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-rifflerun-a-work-in-progress.html | /news/latest-blogs/rifflerun-a-work-in-progress/ | 7 / 1 / 0 | 7 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-monitoring-surveying-greater-gliders-for-future.html | /news/latest-blogs/monitoring-surveying-greater-gliders-for-future/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-upper-yango-revegation-project.html | /news/latest-blogs/upper-yango-revegation-project/ | 8 / 1 / 0 | 8 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-harwood-island-northern-nsw-bush-regeneration-project.html | /news/latest-blogs/harwood-island-northern-nsw-bush-regeneration-project/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-nymboida-river-riparian-2.html | /news/latest-blogs/nymboida-river-riparian-2/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-invasive-no-more-a-landscape-transformed.html | /news/latest-blogs/invasive-no-more-a-landscape-transformed/ | 3 / 1 / 0 | 3 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-upper-narho-creek-planting-success.html | /news/latest-blogs/upper-narho-creek-planting-success/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fire-wise-project-lanscape-resilience.html | /news/latest-news/fire-wise-project-lanscape-resilience/ | 21 / 0 / 0 | 21 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-secret-lives-of-australian-freshwater-turtles.html | /news/latest-news/the-secret-lives-of-australian-freshwater-turtles/ | 31 / 4 / 0 | 31 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-koala-bears.html | /news/latest-news/koala-bears/ | 31 / 4 / 0 | 31 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-conserving-australias-wildlife.html | /news/latest-news/conserving-australias-wildlife/ | 19 / 0 / 0 | 19 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-gardens-of-stone-tree-planting.html | /news/latest-blogs/gardens-of-stone-tree-planting/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-saving-the-northern-quoll.html | /news/latest-news/saving-the-northern-quoll/ | 12 / 2 / 0 | 12 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-healing-our-land-emergency-bushfire-recovery-grants-awarded.html | /news/latest-news/healing-our-land-emergency-bushfire-recovery-grants-awarded/ | 17 / 0 / 0 | 17 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-supporting-australias-world-heritage-sites.html | /news/latest-news/supporting-australias-world-heritage-sites/ | 9 / 3 / 0 | 9 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fire-wise-project.html | /news/media/fire-wise-project/ | 7 / 1 / 0 | 7 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-first-nations-women-in-ranger-programs.html | /news/latest-news/first-nations-women-in-ranger-programs/ | 13 / 2 / 0 | 13 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-students-release-turtle-hatchlings-in-conservation-first.html | /news/latest-blogs/students-release-turtle-hatchlings-in-conservation-first/ | 25 / 3 / 0 | 25 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-latest-news-kangaroo-island-project.html | /news/media/latest-news-kangaroo-island-project/ | 14 / 0 / 0 | 14 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-personal-protective-equipment-wildlife-heroes.html | /news/latest-news/personal-protective-equipment-wildlife-heroes/ | 7 / 0 / 0 | 7 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-gold-coast-hinterland-expansion.html | /news/media/gold-coast-hinterland-expansion/ | 28 / 0 / 0 | 28 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-hard-to-kill-heres-why-eucalypts-are-survival-experts.html | /news/latest-news/hard-to-kill-heres-why-eucalypts-are-survival-experts/ | 35 / 5 / 0 | 35 | 5 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-2023-foundation-for-national-parks-wildlife-impact-report.html | /news/latest-news/2023-foundation-for-national-parks-wildlife-impact-report/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-usl-trees.html | /news/latest-blogs/usl-trees/ | 4 / 1 / 0 | 4 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-bringing-back-subtropical-rainforest-on-private-lands-around-nightcap-national-park.html | /news/latest-blogs/bringing-back-subtropical-rainforest-on-private-lands-around-nightcap-national-park/ | 1 / 1 / 0 | 1 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-passing-elders-fight-to-protect-nature-in-fingal-to-the-next-generation.html | /news/media/passing-elders-fight-to-protect-nature-in-fingal-to-the-next-generation/ | 11 / 2 / 0 | 11 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-green-gully.html | /news/latest-blogs/green-gully/ | 3 / 1 / 0 | 3 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-polish-firefighters-raise-money-for-australian-bushfire-relief.html | /news/latest-news/polish-firefighters-raise-money-for-australian-bushfire-relief/ | 6 / 1 / 0 | 6 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-growing-koala-food-trees.html | /news/latest-news/growing-koala-food-trees/ | 10 / 2 / 0 | 10 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-battle-in-the-treetops-australian-birds-fight-for-survival.html | /news/latest-news/battle-in-the-treetops-australian-birds-fight-for-survival/ | 52 / 7 / 0 | 52 | 7 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-protecting-southern-flinders-ranges.html | /news/latest-news/protecting-southern-flinders-ranges/ | 25 / 3 / 0 | 25 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fire-wise-project-impact.html | /news/latest-news/fire-wise-project-impact/ | 42 / 4 / 0 | 42 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-restoring-grossmans-block.html | /news/latest-news/restoring-grossmans-block/ | 27 / 3 / 0 | 27 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-land-restoration-australia-forktree-project.html | /news/latest-news/land-restoration-australia-forktree-project/ | 31 / 4 / 0 | 31 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-bandicoot-a-little-gardener-beneath-our-feet.html | /news/latest-news/the-bandicoot-a-little-gardener-beneath-our-feet/ | 19 / 6 / 0 | 24 | 8 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-charleston-conservation-park-from-ashes-to-banksias.html | /news/latest-news/charleston-conservation-park-from-ashes-to-banksias/ | 34 / 4 / 0 | 34 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-protecting-threatened-species-australia.html | /news/latest-blogs/protecting-threatened-species-australia/ | 56 / 7 / 0 | 61 | 9 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-hindmarsh-island-ecological-restoration.html | /news/latest-news/hindmarsh-island-ecological-restoration/ | 18 / 4 / 0 | 18 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-australian-threatened-species.html | /news/latest-news/australian-threatened-species/ | 31 / 2 / 0 | 31 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-world-rainforest-day-2023.html | /news/latest-blogs/world-rainforest-day-2023/ | 14 / 0 / 0 | 14 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-truth-behind-your-pledge-to-plant-a-tree.html | /news/media/the-truth-behind-your-pledge-to-plant-a-tree/ | 16 / 0 / 0 | 16 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-fnpw-expands-bushfire-recovery-project-towards-1-million-trees-goal.html | /news/latest-news/the-fnpw-expands-bushfire-recovery-project-towards-1-million-trees-goal/ | 5 / 1 / 0 | 5 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-honour-national-tree-day-this-sunday-1-august.html | /news/latest-news/honour-national-tree-day-this-sunday-1-august/ | 11 / 0 / 0 | 11 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-taking-sustainable-action-to-protect-parks-and-save-species.html | /news/latest-news/taking-sustainable-action-to-protect-parks-and-save-species/ | 9 / 0 / 0 | 9 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-planning-for-fire-season-starts-in-the-garden.html | /news/latest-blogs/planning-for-fire-season-starts-in-the-garden/ | 32 / 5 / 0 | 32 | 5 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-importance-of-wildlife-corridors-australia-summer.html | /news/latest-news/importance-of-wildlife-corridors-australia-summer/ | 52 / 8 / 0 | 55 | 10 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-growing-resilience-from-the-ground-up.html | /news/latest-news/growing-resilience-from-the-ground-up/ | 39 / 8 / 0 | 45 | 10 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-why-expanding-national-parks-matters-for-australias-future.html | /news/latest-news/why-expanding-national-parks-matters-for-australias-future/ | 47 / 10 / 0 | 51 | 12 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-a-new-future-for-mundoo-island.html | /news/uncategorized/a-new-future-for-mundoo-island/ | 19 / 6 / 0 | 24 | 8 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-lesser-known-endangered-animals.html | /news/latest-news/lesser-known-endangered-animals/ | 42 / 15 / 0 | 45 | 17 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-caring-for-country-with-firesticks.html | /news/latest-news/caring-for-country-with-firesticks/ | 44 / 4 / 0 | 44 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-bringing-back-the-growling-grass-frog.html | /news/latest-news/bringing-back-the-growling-grass-frog/ | 18 / 10 / 0 | 22 | 12 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-the-land-behind-australias-world-heritage-bid.html | /news/latest-news/the-land-behind-australias-world-heritage-bid/ | 16 / 6 / 0 | 19 | 8 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-from-advocate-to-chair.html | /news/latest-blogs/from-advocate-to-chair/ | 38 / 6 / 0 | 38 | 6 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-a-million-reasons-to-say-thank-you.html | /news/latest-blogs/a-million-reasons-to-say-thank-you/ | 23 / 6 / 0 | 26 | 8 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-years-of-restoration-written-in-layers.html | /news/latest-blogs/years-of-restoration-written-in-layers/ | 27 / 5 / 0 | 27 | 5 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 1 (0) |
| article-caring-for-country-starts-with-listening.html | /news/latest-blogs/caring-for-country-starts-with-listening/ | 78 / 0 / 0 | 78 | 0 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-a-wildlife-corridor-is-only-as-wide-as-its-narrowest-point.html | /news/latest-blogs/a-wildlife-corridor-is-only-as-wide-as-its-narrowest-point/ | 34 / 9 / 0 | 38 | 12 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-fnpw-launches-manyana-conservation-fund.html | /news/latest-news/fnpw-launches-manyana-conservation-fund/ | 13 / 2 / 0 | 13 | 2 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-your-backyard-is-habitat-too-help-native-wildlife.html | /news/latest-news/your-backyard-is-habitat-too-help-native-wildlife/ | 18 / 9 / 0 | 21 | 11 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-what-does-healthy-bushland-look-like.html | /news/latest-blogs/what-does-healthy-bushland-look-like/ | 30 / 9 / 0 | 35 | 11 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| article-why-species-matters-plant-selection.html | /news/latest-blogs/why-species-matters-plant-selection/ | 35 / 5 / 0 | 35 | 5 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 1 (0) |
| article-the-number-almost-no-one-publishes.html | /news/latest-blogs/the-number-almost-no-one-publishes/ | 28 / 3 / 0 | 31 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| index.html | / | 9 / 0 / 0 | 24 | 29 | page CSS in _fnpw_page_css (18523 bytes) | 1 page script(s) in _fnpw_page_js (1232 bytes) | none | 9 (1) |
| newsletter-thank-you.html | /newsletter-thank-you/ | 0 / 1 / 0 | 0 | 1 | none | none | none | 0 (0) |
| thank-you.html | /thank-you/ | 1 / 1 / 0 | 2 | 3 | none | none | none | 1 (0) |
| paws-magazine.html | /paws-magazine/ | 2 / 0 / 0 | 5 | 3 | page CSS in _fnpw_page_css (1939 bytes) | none | none | 1 (0) |
| articles.html | /news/ | 0 / 0 / 1 | 0 | 0 | NOTE: stories.css in the theme differs from the static block only by asset paths (checked by length 9246 vs 9426); stories.css (theme, by template) | articles.js (theme, by template); newsletter band pattern carries the HubSpot embed | none | 1 (0) |
| grants.html | /grants/ | 2 / 1 / 0 | 5 | 4 | page CSS in _fnpw_page_css (1928 bytes) | none | none | 0 (0) |
| article-mitigating-effects-environmental-change.html | /mitigating-effects-environmental-change/ | 7 / 1 / 0 | 7 | 1 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 1 (0) |
| thank-you-volunteer-form.html | /thank-you-volunteer-form/ | 0 / 1 / 0 | 0 | 1 | none | none | none | 0 (0) |
| how-your-contributions-help.html | /how-your-contributions-help/ | 5 / 2 / 0 | 17 | 11 | page CSS in _fnpw_page_css (1307 bytes) | none | none | 0 (0) |
| reconciliation-action-plan.html | /reconciliation-action-plan/ | 2 / 1 / 0 | 8 | 5 | none | none | none | 0 (0) |
| privacy-policy.html | /privacy-policy/ | 1 / 1 / 0 | 30 | 1 | shared file privacy-policy-6aaded07.css | none | none | 0 (0) |
| corporate-governance.html | /corporate-governance/ | 6 / 0 / 0 | 12 | 3 | page CSS in _fnpw_page_css (1129 bytes) | none | none | 1 (0) |
| terms-and-conditions.html | /terms-and-conditions/ | 1 / 1 / 0 | 39 | 1 | shared file privacy-policy-6aaded07.css | none | none | 0 (0) |
| workplace-giving.html | /workplace-giving/ | 8 / 0 / 0 | 27 | 8 | page CSS in _fnpw_page_css (2634 bytes) | none | none | 1 (0) |
| article-biodiversity-month.html | /biodiversity-month/ | 21 / 4 / 0 | 21 | 4 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| why-your-support-is-needed.html | /why-your-support-is-needed/ | 4 / 1 / 0 | 15 | 9 | page CSS in _fnpw_page_css (2933 bytes) | none | none | 0 (0) |
| article-koala-facts.html | /koala-facts/ | 24 / 3 / 0 | 24 | 3 | article.css (theme, by template) | article-progress.js (theme, by template) | none | 0 (0) |
| contact.html | /contact-us/ | 3 / 0 / 0 | 10 | 9 | page CSS in _fnpw_page_css (7049 bytes) | external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 1 (1) |
| fundraising-with-fnpw.html | /fundraising-with-fnpw/ | 6 / 1 / 0 | 33 | 12 | page CSS in _fnpw_page_css (4748 bytes) | external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 1 (0) |
| donate-land.html | /donate-land/ | 6 / 1 / 0 | 35 | 16 | page CSS in _fnpw_page_css (9532 bytes) | external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 2 (0) |
| faqs.html | /faqs/ | 3 / 0 / 0 | 11 | 10 | page CSS in _fnpw_page_css (2019 bytes) | none | none | 1 (0) |
| volunteer.html | /corporate-volunteering/ | 7 / 1 / 0 | 45 | 37 | page CSS in _fnpw_page_css (31275 bytes) | 1 page script(s) in _fnpw_page_js (1642 bytes); assets/js/carousel.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file volunteer-90c0411a.js | none | 19 (0) |
| corporate-volunteering-nsw.html | /corporate-volunteering/sydney/ | 4 / 0 / 0 | 10 | 10 | shared file corporate-volunteering-f91c1f87.css | 1 page script(s) in _fnpw_page_js (73 bytes); assets/js/gallery.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file corporate-volunteering-c6b0b783.js; shared file volunteer-90c0411a.js | none | 16 (0) |
| corporate-volunteering-vic.html | /corporate-volunteering/melbourne/ | 4 / 0 / 0 | 10 | 10 | shared file corporate-volunteering-f91c1f87.css | 1 page script(s) in _fnpw_page_js (66 bytes); assets/js/gallery.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file corporate-volunteering-c6b0b783.js; shared file volunteer-90c0411a.js | none | 16 (0) |
| corporate-volunteering-qld.html | /corporate-volunteering/brisbane/ | 5 / 0 / 0 | 23 | 11 | shared file corporate-volunteering-f91c1f87.css | 1 page script(s) in _fnpw_page_js (68 bytes); assets/js/gallery.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file corporate-volunteering-c6b0b783.js; shared file volunteer-90c0411a.js | none | 16 (0) |
| corporate-volunteering-sa.html | /corporate-volunteering/adelaide/ | 4 / 0 / 0 | 10 | 10 | shared file corporate-volunteering-f91c1f87.css | 1 page script(s) in _fnpw_page_js (72 bytes); assets/js/gallery.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file corporate-volunteering-c6b0b783.js; shared file volunteer-90c0411a.js | none | 16 (0) |
| corporate-volunteering-wa.html | /corporate-volunteering/perth/ | 4 / 0 / 0 | 10 | 10 | shared file corporate-volunteering-f91c1f87.css | 1 page script(s) in _fnpw_page_js (74 bytes); assets/js/gallery.js (theme, enqueued where its markup is used); external: https://js-ap1.hsforms.net/forms/embed/v2.js; shared file corporate-volunteering-c6b0b783.js; shared file volunteer-90c0411a.js | none | 16 (0) |
| media-enquiry.html | /media-enquiry/ | 2 / 0 / 0 | 6 | 5 | page CSS in _fnpw_page_css (1316 bytes) | external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 1 (0) |
| reports.html | /annual-reports-financials/ | 3 / 1 / 0 | 6 | 7 | page CSS in _fnpw_page_css (11123 bytes) | 1 page script(s) in _fnpw_page_js (351 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 4 (0) |
| newsletters-sign-up.html | /foundation-for-national-parks-and-wildlife-newsletter/ | 1 / 1 / 0 | 3 | 3 | none | external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 1 (0) |
| bequests.html | /bequest/ | 8 / 1 / 0 | 42 | 34 | page CSS in _fnpw_page_css (14405 bytes) | 1 page script(s) in _fnpw_page_js (385 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js | none | 10 (2) |
| ways-you-can-get-involved.html | /ways-you-can-get-involved/ | 7 / 1 / 0 | 21 | 19 | page CSS in _fnpw_page_css (3843 bytes) | none | none | 6 (0) |
| projects.html | /projects/ | 3 / 3 / 1 | 7 | 10 | page CSS in _fnpw_page_css (18148 bytes) | 1 page script(s) in _fnpw_page_js (5538 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js; map script dropped: the fnpw/project-map block has its own; shared file hs-fallback-884c1850.js | none | 9 (0) |
| about.html | /about-us/ | 3 / 9 / 0 | 5 | 15 | page CSS in _fnpw_page_css (13558 bytes) | 3 page script(s) in _fnpw_page_js (1460 bytes); assets/js/snap.js (theme, enqueued where its markup is used) | none | 5 (0) |
| partner.html | /corporate-partnerships/ | 1 / 0 / 0 | 4 | 6 | page CSS in _fnpw_page_css (19071 bytes) | 1 page script(s) in _fnpw_page_js (1081 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 25 (2) |
| project-garners-beach-cassowary-rehabilitation-centre-project.html | /project/garners-beach-cassowary-rehabilitation-centre-project/ | 3 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-tangaroa-blue.html | /project/tangaroa-blue/ | 2 / 4 / 0 | 8 | 7 | none | none | none | 0 (0) |
| project-bushfire-recovery-small-grants.html | /project/bushfire-recovery-small-grants/ | 2 / 2 / 0 | 33 | 4 | shared file project-4206f1bf.css | none | none | 0 (0) |
| project-private-land-conservation-grants.html | /project/private-land-conservation-grants/ | 2 / 2 / 0 | 44 | 5 | shared file project-4206f1bf.css | none | none | 0 (0) |
| project-genetic-code-of-koalas.html | /project/genetic-code-of-koalas/ | 10 / 3 / 0 | 31 | 20 | none | none | none | 6 (0) |
| project-community-conservation-grants.html | /project/community-conservation-grants/ | 2 / 2 / 0 | 26 | 9 | shared file project-4206f1bf.css | none | none | 0 (0) |
| project-bushfire-recovery-habitat-restoration.html | /project/bushfire-recovery-habitat-restoration/ | 4 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-bilby-fire-project.html | /project/bilby-fire-project/ | 5 / 2 / 0 | 18 | 7 | none | none | none | 0 (0) |
| project-brush-tailed-rock-wallaby-school-education.html | /project/brush-tailed-rock-wallaby-school-education/ | 3 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-caught-on-camera.html | /project/caught-on-camera/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-christmas-island-reptiles.html | /project/christmas-island-reptiles/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-eastern-bristlebird.html | /project/eastern-bristlebird/ | 4 / 2 / 0 | 16 | 5 | none | none | none | 0 (0) |
| project-endangered-pomaderris-plants.html | /project/endangered-pomaderris-plants/ | 3 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-feather-leaved-banksia-of-wa.html | /project/feather-leaved-banksia-of-wa/ | 3 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-gogerlys-point-heritage-precinct.html | /project/gogerlys-point-heritage-precinct/ | 3 / 2 / 0 | 14 | 6 | none | none | none | 0 (0) |
| project-granite-island-little-penguins.html | /project/granite-island-little-penguins/ | 3 / 3 / 0 | 10 | 7 | none | none | none | 3 (3) |
| project-green-parrot-breeding-project.html | /project/green-parrot-breeding-project/ | 3 / 2 / 0 | 6 | 7 | none | none | none | 0 (0) |
| project-habitats-for-koalas-in-the-otways.html | /project/habitats-for-koalas-in-the-otways/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-jungurra.html | /project/jungurra/ | 3 / 2 / 0 | 12 | 5 | none | none | none | 0 (0) |
| project-kangaroo-islands-bandicoots.html | /project/kangaroo-islands-bandicoots/ | 3 / 2 / 0 | 13 | 6 | none | none | none | 0 (0) |
| project-kangaroo-islands-enigma-moth.html | /project/kangaroo-islands-enigma-moth/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-koala-tree-planting.html | /project/koala-tree-planting/ | 3 / 2 / 0 | 12 | 6 | none | none | none | 0 (0) |
| project-kosciuszko-national-park-2020-fire-recovery.html | /project/kosciuszko-national-park-2020-fire-recovery/ | 4 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-kukundi-nature-playspace.html | /project/kukundi-nature-playspace/ | 4 / 2 / 0 | 18 | 7 | none | none | none | 0 (0) |
| project-lane-cove-bushcare-program-2018.html | /project/lane-cove-bushcare-program-2018/ | 3 / 2 / 0 | 13 | 6 | none | none | none | 0 (0) |
| project-malleefowl-conservation.html | /project/malleefowl-conservation/ | 3 / 2 / 0 | 12 | 6 | none | none | none | 0 (0) |
| project-manly-little-penguins.html | /project/manly-little-penguins/ | 3 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-movement-of-koalas-back-into-severely-burnt-forest.html | /project/movement-of-koalas-back-into-severely-burnt-forest/ | 3 / 2 / 0 | 7 | 5 | none | none | none | 0 (0) |
| project-mt-schank-walking-trail.html | /project/mt-schank-walking-trail/ | 3 / 2 / 0 | 10 | 5 | none | none | none | 0 (0) |
| project-petaurus-connections.html | /project/petaurus-connections/ | 3 / 2 / 0 | 8 | 6 | none | none | none | 0 (0) |
| project-quolls.html | /project/quolls/ | 3 / 2 / 0 | 14 | 6 | none | none | none | 0 (0) |
| project-red-tailed-phascogale.html | /project/red-tailed-phascogale/ | 4 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-redlands-koala-planting.html | /project/redlands-koala-planting/ | 3 / 2 / 0 | 15 | 6 | none | none | none | 0 (0) |
| project-remarkable-southern-flinders.html | /project/remarkable-southern-flinders/ | 8 / 4 / 0 | 18 | 20 | shared file project-6df8bcef.css | none | none | 6 (0) |
| project-restoring-the-glideways-of-k2w.html | /project/restoring-the-glideways-of-k2w/ | 3 / 2 / 0 | 7 | 5 | none | none | none | 0 (0) |
| project-seagrass-collaboration.html | /project/seagrass-collaboration/ | 6 / 2 / 0 | 24 | 8 | none | none | none | 0 (0) |
| project-southern-highlands-koala-conservation.html | /project/southern-highlands-koala-conservation/ | 4 / 2 / 0 | 11 | 9 | shared file project-6df8bcef.css | none | none | 0 (0) |
| project-tassie-devil-roadkill.html | /project/tassie-devil-roadkill/ | 2 / 2 / 0 | 5 | 5 | none | none | none | 0 (0) |
| project-the-great-koala-count.html | /project/the-great-koala-count/ | 3 / 2 / 0 | 11 | 5 | none | none | none | 0 (0) |
| project-trails-for-tails.html | /project/trails-for-tails/ | 3 / 2 / 0 | 12 | 6 | none | none | none | 0 (0) |
| project-wa-bird-watering-stations.html | /project/wa-bird-watering-stations/ | 4 / 2 / 0 | 11 | 5 | none | none | none | 0 (0) |
| project-warddeken-mayh.html | /project/warddeken-mayh/ | 4 / 2 / 0 | 18 | 11 | shared file project-6df8bcef.css | none | none | 0 (0) |
| project-was-woylie-survival.html | /project/was-woylie-survival/ | 3 / 2 / 0 | 13 | 6 | none | none | none | 0 (0) |
| project-western-swamp-tortoise.html | /project/western-swamp-tortoise/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-woomargama-national-park.html | /project/woomargama-national-park/ | 3 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-yarning-online-oncountry-kurrupurra-pila-weaving.html | /project/yarning-online-oncountry-kurrupurra-pila-weaving/ | 4 / 3 / 0 | 14 | 7 | none | none | none | 0 (0) |
| project-yarrahapinni-wetlands-restoration-stage-1.html | /project/yarrahapinni-wetlands-restoration-stage-1/ | 5 / 2 / 0 | 13 | 7 | none | none | none | 0 (0) |
| project-youth-wildlife-ambassadors.html | /project/youth-wildlife-ambassadors/ | 4 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-enhancing-biodiversity-protecting-cultural-heritage-at-torrens-island-conservation.html | /project/enhancing-biodiversity-protecting-cultural-heritage-at-torrens-island-conservation/ | 4 / 2 / 0 | 12 | 6 | none | none | none | 0 (0) |
| project-fnpw-koala-projects.html | /project/fnpw-koala-projects/ | 3 / 2 / 0 | 18 | 6 | none | none | none | 0 (0) |
| project-nilpena-nationalpark.html | /project/nilpena-nationalpark/ | 3 / 4 / 0 | 6 | 9 | none | none | none | 0 (0) |
| project-aussie-ark-quolls.html | /project/aussie-ark-quolls/ | 3 / 2 / 0 | 18 | 6 | none | none | none | 0 (0) |
| project-lion-island-little-penguin.html | /project/lion-island-little-penguin/ | 3 / 2 / 0 | 13 | 6 | none | none | none | 4 (4) |
| project-impact-of-bushfires-on-koalas.html | /project/impact-of-bushfires-on-koalas/ | 3 / 2 / 0 | 7 | 6 | none | none | none | 0 (0) |
| project-alpine-frogs-a-calling.html | /project/alpine-frogs-a-calling/ | 4 / 3 / 0 | 11 | 7 | none | none | none | 0 (0) |
| project-ngurrawaana-ranger-habitat-conservation.html | /project/ngurrawaana-ranger-habitat-conservation/ | 4 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-heritage-estates.html | /project/heritage-estates/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-1-million-turtles.html | /project/1-million-turtles/ | 8 / 5 / 0 | 19 | 23 | none | none | none | 12 (0) |
| project-native-plant-nurseries.html | /project/native-plant-nurseries/ | 4 / 4 / 0 | 12 | 10 | none | none | none | 0 (0) |
| project-cultivating-koala-habitat.html | /project/cultivating-koala-habitat/ | 12 / 3 / 0 | 35 | 25 | none | none | none | 9 (0) |
| project-mountain-pygmy-possum.html | /project/mountain-pygmy-possum/ | 8 / 3 / 0 | 60 | 12 | none | none | none | 0 (0) |
| project-wild-heart.html | /project/wild-heart/ | 10 / 2 / 0 | 21 | 11 | none | none | none | 1 (0) |
| project-bushfire-recovery-program.html | /project/bushfire-recovery-program/ | 3 / 3 / 0 | 28 | 7 | none | none | none | 0 (0) |
| project-fire-wise.html | /project/fire-wise/ | 7 / 4 / 0 | 13 | 17 | none | none | none | 0 (0) |
| project-sturt-national-park.html | /project/sturt-national-park/ | 3 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-wildlife-heroes.html | /project/wildlife-heroes/ | 5 / 3 / 0 | 14 | 10 | none | none | none | 0 (0) |
| project-black-cockatoo-corridor.html | /project/black-cockatoo-corridor/ | 3 / 2 / 0 | 10 | 5 | none | none | none | 0 (0) |
| project-memorial-trees.html | /project/memorial-trees/ | 5 / 2 / 0 | 14 | 7 | none | none | none | 1 (0) |
| project-bandicoot-superhighway-project.html | /project/bandicoot-superhighway-project/ | 12 / 3 / 0 | 28 | 25 | none | none | none | 14 (0) |
| project-students-dig-in-for-conservation.html | /project/students-dig-in-for-conservation/ | 4 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-devil-ark.html | /project/devil-ark/ | 3 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-bushfire-recovery-seedbanks.html | /project/bushfire-recovery-seedbanks/ | 5 / 3 / 0 | 20 | 8 | none | none | none | 0 (0) |
| project-mary-valley-rail-trail-habitat-link.html | /project/mary-valley-rail-trail-habitat-link/ | 5 / 2 / 0 | 23 | 7 | none | none | none | 0 (0) |
| project-save-the-orange-bellied-parrot.html | /project/save-the-orange-bellied-parrot/ | 5 / 3 / 0 | 23 | 9 | none | none | none | 0 (0) |
| project-recovering-blue-butterflies-in-victoria.html | /project/recovering-blue-butterflies-in-victoria/ | 4 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-restoring-campbells-wetland-walkway.html | /project/restoring-campbells-wetland-walkway/ | 4 / 2 / 0 | 9 | 6 | none | none | none | 0 (0) |
| project-nest-boxes-in-plenty-gorge-park.html | /project/nest-boxes-in-plenty-gorge-park/ | 3 / 2 / 0 | 10 | 6 | none | none | none | 0 (0) |
| project-backyard-buddies.html | /project/backyard-buddies/ | 3 / 3 / 0 | 16 | 7 | none | none | none | 0 (0) |
| project-white-throated-grasswren.html | /project/white-throated-grasswren/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-mount-field-national-park.html | /project/mount-field-national-park/ | 3 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-booningyah-junior-rangers-program.html | /project/booningyah-junior-rangers-program/ | 6 / 3 / 0 | 40 | 9 | none | none | none | 0 (0) |
| project-dalki-garringa-botanic-park.html | /project/dalki-garringa-botanic-park/ | 4 / 2 / 0 | 11 | 6 | none | none | none | 0 (0) |
| project-gift-a-tree-for-nature-conservation.html | /project/gift-a-tree-for-nature-conservation/ | 5 / 2 / 0 | 16 | 6 | none | none | none | 0 (0) |
| project-curb-wombat-mange-program.html | /project/curb-wombat-mange-program/ | 10 / 3 / 0 | 21 | 21 | none | none | none | 13 (0) |
| project-supporting-community-led-treatment-to-protect-bare-nosed-wombats.html | /project/supporting-community-led-treatment-to-protect-bare-nosed-wombats/ | 9 / 2 / 0 | 40 | 9 | none | none | none | 1 (0) |
| bequests-professional-advisers.html | /bequest/professional-advisers/ | 5 / 2 / 0 | 26 | 18 | page CSS in _fnpw_page_css (17258 bytes) | none | none | 3 (1) |
| government-partnerships.html | /government-partnerships/ | 1 / 0 / 0 | 7 | 6 | page CSS in _fnpw_page_css (21532 bytes) | 2 page script(s) in _fnpw_page_js (1041 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 16 (2) |
| growing-national-parks.html | /growing-national-parks/ | 5 / 5 / 0 | 10 | 16 | page CSS in _fnpw_page_css (1318 bytes) | shared file growing-national-parks-70bf2c5f.js | none | 5 (0) |
| healing-the-land.html | /healing-the-land/ | 6 / 5 / 0 | 12 | 18 | page CSS in _fnpw_page_css (2620 bytes) | shared file growing-national-parks-70bf2c5f.js | none | 6 (0) |
| in-the-news.html | /in-the-news/ | 1 / 2 / 0 | 2 | 3 | page CSS in _fnpw_page_css (1215 bytes) | none | none | 0 (0) |
| our-impact.html | /our-impact/ | 6 / 2 / 0 | 14 | 20 | page CSS in _fnpw_page_css (14498 bytes) | 1 page script(s) in _fnpw_page_js (283 bytes) | none | 65 (0) |
| partner-invest.html | /partner-with-us/ | 0 / 1 / 0 | 0 | 1 | page CSS in _fnpw_page_css (19081 bytes) | 1 page script(s) in _fnpw_page_js (881 bytes); external: https://js-ap1.hsforms.net/forms/embed/441704788.js; shared file hs-fallback-884c1850.js | none | 67 (0) |
| project-kaurna-cultural-fire-field-river.html | /project/kaurna-cultural-fire-field-river/ | 10 / 2 / 0 | 26 | 19 | none | none | none | 3 (0) |
| project-mundoo-island-acquisition.html | /project/mundoo-island-acquisition/ | 11 / 3 / 0 | 28 | 23 | none | none | none | 10 (0) |
| project-nectar-sippers.html | /project/nectar-sippers/ | 10 / 4 / 0 | 28 | 23 | none | none | none | 8 (0) |
| saving-species.html | /saving-species/ | 5 / 5 / 0 | 10 | 16 | page CSS in _fnpw_page_css (1321 bytes) | shared file growing-national-parks-70bf2c5f.js | none | 6 (0) |

## Sections carried as HTML, with the reason

Site pages and projects only (article bodies are listed in the table above by count). Identical runs across project pages are grouped.

- `section.sec.dark` (94): <div class="cw rv"> has attributes a Group block cannot hold (style). Pages: grants.html, how-your-contributions-help.html, fundraising-with-fnpw.html, project-garners-beach-cassowary-rehabilitation-centre-project.html and 90 more
- `section.pj-back` (87): <a> has no core block with the same markup. Pages: project-garners-beach-cassowary-rehabilitation-centre-project.html, project-tangaroa-blue.html, project-bushfire-recovery-small-grants.html, project-private-land-conservation-grants.html and 83 more
- `section.ch.chi` (11): <section class="ch chi"> has attributes a Group block cannot hold (style). Pages: how-your-contributions-help.html, privacy-policy.html, terms-and-conditions.html, why-your-support-is-needed.html and 7 more
- `section.sec.sand` (9): <span> has no core block with the same markup. Pages: project-yarning-online-oncountry-kurrupurra-pila-weaving.html, project-alpine-frogs-a-calling.html, project-mountain-pygmy-possum.html, project-bushfire-recovery-program.html and 5 more
- `section.pj-qband` (8): <figure> has no core block with the same markup. Pages: project-genetic-code-of-koalas.html, project-1-million-turtles.html, project-native-plant-nurseries.html, project-cultivating-koala-habitat.html and 4 more
- `section.sec` (4): <section class="sec"> has attributes a Group block cannot hold (style). Pages: newsletter-thank-you.html, thank-you-volunteer-form.html, about.html, about.html
- `section.sec` (3): <figure> has no core block with the same markup. Pages: project-granite-island-little-penguins.html, project-1-million-turtles.html, project-nectar-sippers.html
- `section.sec.dark` (3): <div class="two"> has attributes a Group block cannot hold (style). Pages: growing-national-parks.html, healing-the-land.html, saving-species.html
- `section.sec.sand.sec-cont` (3): <article class="pc"> has attributes a Group block cannot hold (data-state). Pages: growing-national-parks.html, healing-the-land.html, saving-species.html
- `section.pil-stats.ps-parks` (2): <span> has no core block with the same markup. Pages: project-remarkable-southern-flinders.html, project-nilpena-nationalpark.html
- `section.sec` (2): <a> has no core block with the same markup. Pages: reports.html, in-the-news.html
- `section.sec.sand` (2): <div> holds loose text beside its elements. Pages: about.html, about.html
- `div.fb` (1): <button> has no core block with the same markup. Pages: projects.html
- `div.fb.fb-paper.fb-healing` (1): <button> has no core block with the same markup. Pages: healing-the-land.html
- `div.fb.fb-paper.fb-parks` (1): <button> has no core block with the same markup. Pages: growing-national-parks.html
- `div.fb.fb-paper.fb-species` (1): <button> has no core block with the same markup. Pages: saving-species.html
- `div.piw` (1): markup is not well formed (implicitly closed <div> by </section> at 14774), carried untouched. Pages: partner-invest.html
- `div.po` (1): <button> has no core block with the same markup. Pages: projects.html
- `div.v-sticky` (1): <div class="v-sticky"> has attributes a Group block cannot hold (role, aria-label). Pages: volunteer.html
- `nav.ip-jump` (1): <nav> has no core block with the same markup. Pages: our-impact.html
- `section` (1): <section class=""> has attributes a Group block cannot hold (style). Pages: projects.html
- `section.ab-cta` (1): <span> has no core block with the same markup. Pages: about.html
- `section.ab-film` (1): <iframe> has no core block with the same markup. Pages: about.html
- `section.ac-sec` (1): <div class="rv"> has attributes a Group block cannot hold (style). Pages: about.html
- `section.ch.chi.pil-hero.chi-healing` (1): <section class="ch chi pil-hero chi-healing"> has attributes a Group block cannot hold (style). Pages: healing-the-land.html
- `section.ch.chi.pil-hero.chi-parks` (1): <section class="ch chi pil-hero chi-parks"> has attributes a Group block cannot hold (style). Pages: growing-national-parks.html
- `section.ch.chi.pil-hero.chi-species` (1): <section class="ch chi pil-hero chi-species"> has attributes a Group block cannot hold (style). Pages: saving-species.html
- `section.dl-faq` (1): <details> has no core block with the same markup. Pages: donate-land.html
- `section.gw-faq` (1): <details> has no core block with the same markup. Pages: bequests.html
- `section.gw-proof` (1): <div> holds loose text beside its elements. Pages: bequests-professional-advisers.html
- `section.gw-word` (1): <section class="gw-word"> has attributes a Group block cannot hold (style). Pages: bequests-professional-advisers.html
- `section.ht` (1): <div class=""> has attributes a Group block cannot hold (style). Pages: about.html
- `section.pa-intro` (1): <span> has no core block with the same markup. Pages: ways-you-can-get-involved.html
- `section.pil-stats.ps-healing` (1): <span> has no core block with the same markup. Pages: project-tangaroa-blue.html
- `section.pil-stats.ps-species` (1): <span> has no core block with the same markup. Pages: project-1-million-turtles.html
- `section.sec` (1): <article class="ip-cs rv"> has attributes a Group block cannot hold (style). Pages: our-impact.html
- `section.sec` (1): <div class=""> has attributes a Group block cannot hold (style). Pages: newsletters-sign-up.html
- `section.sec` (1): <p> inline style beyond margins (text-align:center). Pages: thank-you.html
- `section.sec.sand` (1): <div class=""> has attributes a Group block cannot hold (style). Pages: reconciliation-action-plan.html
- `section.sec.sand` (1): <div class="pj-body"> has attributes a Group block cannot hold (style). Pages: project-curb-wombat-mange-program.html
- `section.sec.sand` (1): <div class="two"> has attributes a Group block cannot hold (style). Pages: about.html
