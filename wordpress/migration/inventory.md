<!-- @generated: written by build_inventory.py; edit the script, not this block -->
# Repo inventory

Generated 10 November 2026 from commit `23718e97` (2026-11-10). Per-page detail is in `inventory-pages.csv`. Re-run `python3 wordpress/migration/build_inventory.py` after changes to the static build; the admin audit section at the end is kept.

## Summary

- **297 HTML pages**: 167 article, 85 project, 21 content, 5 volunteering state, 4 hub, 3 legal, 3 pillar, 3 thank-you, 3 grant programme, 2 utility, 1 home.
- **Design layer**: `assets/css/global.css` (75 KB, 59 tokens) plus a page `<style>` block on most pages (1298 KB in total).
- **Partials**: `partials/header.html` and `partials/footer.html`, injected into every page by `tools/sync.py` between `@header` and `@footer` markers.
- **Scripts**: `assets/js/main.js` on every page, four feature scripts, and inline component scripts on 192 pages.
- **Fonts are local.** Sora and Figtree variable woff2 files sit in `assets/fonts/` with `@font-face` in global.css, and no page links Google Fonts. Caveat is gone: `--ff-h` now points at Figtree.
- **Images**: 1486 references to the live media library (fnpw.org.au/wp-content/uploads), 1197 to local files, 19 to other hosts.
- **Forms**: HubSpot embeds on 18 pages. Live pages embed the same HubSpot forms (admin audit, 10 November), so the embeds carry over as they are.

## Pages

### Site pages

| File | Type | Title | Sections in `<main>` | Interactive |
|---|---|---|---|---|
| 404.html | utility | Page not found | nf-hero, sec |  |
| about.html | content | About FNPW: 55 years of Australian conservation | ab-hero, sec, sec, ab-film, ht, sec.sand, sec.sand, sec.sand, sec.sand, abg, ab-cta, ac-sec | Read more toggles, Timeline rail (drag to scroll), Card arrows, Section snap, Video embed |
| articles.html | hub | Articles | nh, feat-art, filters-news, section, sec, nl-strip | Stories filter, sort and paging, HubSpot form embed |
| bequests-professional-advisers.html | content | Gifts in Wills for Professional Advisers | gw-hero, gw-proof, gw-why, gw-word, gw-how, gw-pil, gw-talk |  |
| bequests.html | content | Gifts in Wills | gw-hero.sky, gw-im, gw-feat, gw-leg, gw-pil, gw-ty, gw-pro-cta, gw-faq, gw-talk | Accordions (details), HubSpot form embed |
| contact.html | content | Contact | ct-hero, c-main, ct-news | HubSpot form embed, Google map embed |
| corporate-governance.html | legal | Corporate Governance | pj-hero, cg-sec, cg-sec.alt, cg-sec, cg-sec.alt, cg-sec |  |
| corporate-volunteering-nsw.html | volunteering state | NSW Volunteering Sites | vs-hero, vs-wrap, vs-gal, v-cta | Volunteer sites map, Photo gallery (pages of six), HubSpot form embed |
| corporate-volunteering-qld.html | volunteering state | QLD Volunteering Sites | vs-hero, vs-wrap, sec.vs-site, vs-gal, v-cta | Volunteer sites map, Photo gallery (pages of six), HubSpot form embed |
| corporate-volunteering-sa.html | volunteering state | SA Volunteering Sites | vs-hero, vs-wrap, vs-gal, v-cta | Volunteer sites map, Photo gallery (pages of six), HubSpot form embed |
| corporate-volunteering-vic.html | volunteering state | VIC Volunteering Sites | vs-hero, vs-wrap, vs-gal, v-cta | Volunteer sites map, Photo gallery (pages of six), HubSpot form embed |
| corporate-volunteering-wa.html | volunteering state | WA Volunteering Sites | vs-hero, vs-wrap, vs-gal, v-cta | Volunteer sites map, Photo gallery (pages of six), HubSpot form embed |
| donate-land.html | content | Donate Land | fb-hero, dl-how, dl-open, dl-proc, dl-cost, dl-contact, dl-faq | Accordions (details), HubSpot form embed |
| faqs.html | content | FAQs | pj-hero.pj-hero-soft, sec.fq-sec, fq-contact | Accordions (details) |
| fundraising-with-fnpw.html | content | Fundraising with FNPW | fb-hero, fw-intro, fw-ways, fw-paths, fw-thanks, fw-form, sec.dark | HubSpot form embed |
| government-partnerships.html | content | Government Partnerships | piw | Tabs (government partnerships), Read more toggles, Accordions (details), HubSpot form embed |
| grants.html | content | Conservation Grants in Australia | pj-hero, sec, sec.dark |  |
| growing-national-parks.html | pillar | Growing National Parks | ch.chi.pil-hero.chi-parks, pil-stats.ps-parks, sec, sec.dark, sec.sand.sec-head, fb.fb-paper.fb-parks, sec.sand.sec-cont, ra.ra-parks, sec, sec.dark | Project grid with pillar filter |
| healing-the-land.html | pillar | Healing the Land | ch.chi.pil-hero.chi-healing, pil-stats.ps-healing, sec, sts, sec.dark, sec.sand.sec-head, fb.fb-paper.fb-healing, sec.sand.sec-cont, ra.ra-healing, sec, sec.dark | Project grid with pillar filter |
| how-your-contributions-help.html | content | How Your Contributions Help | ch.chi, hc-open, hc-band, hc-band.alt, hc-band, hc-band.alt, sec.dark |  |
| in-the-news.html | hub | In the news | nw-hero, sec, pj-back |  |
| index.html | home | Foundation for National Parks & Wildlife | hx-hero, sec.door, hx-gat, sec.sand.hx-pils, sec.dark.hx-impact, sec.hx-rail-sec, hx-pt, sec.sand.hx-story, sec.strip.hx-news | Project slider (homepage), Animated counters |
| media-enquiry.html | content | Media Enquiries | pj-hero.pj-hero-split, me-sec | HubSpot form embed |
| newsletter-thank-you.html | thank-you | Thank you for signing up | sec |  |
| newsletters-sign-up.html | content | Newsletter Sign-up | pj-hero, sec | HubSpot form embed |
| our-impact.html | content | Our Impact | ip-hero, ip-jump, sec.ip-results, sec.ip-trees, sec, sec.sand, sec.ip-partners, sec.ip-close | Load more list |
| partner-invest.html | content | Partner With Us | piw | Tabs (partner and invest), HubSpot form embed |
| partner.html | content | Corporate Partnerships | piw | Load more list, HubSpot form embed |
| paws-magazine.html | content | PAWS Magazine | pj-hero.pj-hero-split, sec |  |
| privacy-policy.html | legal | Privacy Policy | ch.chi, sec |  |
| projects.html | hub | Projects | proj-hero, map-sec, style, fb, section, hx-camp.hx-camp-sm, ns, po, script | Project map, Project grid with pillar filter, Projects page tiles and filters, HubSpot form embed |
| reconciliation-action-plan.html | content | Innovate Reconciliation Action Plan | pj-hero.pj-hero-soft, sec, sec.sand |  |
| reports.html | hub | Reports & Publications | nh, feat-art, sec, nl-strip | Reports filter, HubSpot form embed |
| saving-species.html | pillar | Saving Species | ch.chi.pil-hero.chi-species, pil-stats.ps-species, sec, sec.dark, sec.sand.sec-head, fb.fb-paper.fb-species, sec.sand.sec-cont, ra.ra-species, sec, sec.dark | Project grid with pillar filter |
| search.html | utility | Search | pj-hero.srch-hero, sec | Site search (client-side index) |
| terms-and-conditions.html | legal | Terms & Conditions | ch.chi, sec |  |
| thank-you-volunteer-form.html | thank-you | Thank you for your volunteering enquiry | sec |  |
| thank-you.html | thank-you | Thank You | pj-hero.pj-hero-neutral, sec |  |
| volunteer.html | content | Corporate Volunteering | fb-hero, v-sticky, v-acts, v-where, v-prog, v-ben, v-cta, v-faq, script | Where-we-run state tabs, Photo carousel, Accordions (details), HubSpot form embed |
| ways-you-can-get-involved.html | content | Ways to Get Involved | pj-hero.pj-hero-soft.gi-hero, pa-intro, pa-band, pa-band.flip.alt, pa-band, pa-band.flip.alt, pa-rest, hx-camp.hx-camp-sm |  |
| why-your-support-is-needed.html | content | Why Your Support Is Needed | ch.chi, wy-open, wy-dark, wy-threats, wy-track |  |
| workplace-giving.html | content | Workplace Giving | pj-hero.pj-hero-neutral, wg-sec, wg-sec.alt, wg-sec.alt, wg-sec, wg-sec.alt, wg-sec, wg-cta |  |

### Projects (85)

Section sequences inside `<main>`, most common first:

| Pages | Sequence |
|---|---|
| 22 | pj-hero → sec → pj-band → pj-back → sec.dark |
| 16 | pj-hero → sec → sec → pj-back → sec.dark |
| 9 | pj-hero → sec → pj-band → sec.pj-credit → pj-back → sec.dark |
| 3 | pj-hero → sec → sec → sec.pj-credit → pj-back → sec.dark |
| 2 | pj-hero → sec → pj-band → sec.sand → sec.pj-credit → pj-back → sec.dark |
| 2 | pj-hero → sec → sec → sec.sand → pj-back → sec.dark |
| 2 | pj-hero → sec → pj-band → pj-story → sec.sand → pj-back → sec.dark |
| 2 | ch.chi → sec → sec → sec.sand → sec.dark → sec.pj-credit |
| 1 | pj-hero → pil-stats.ps-species → pj-band → pj-band.alt.flip → pj-story → pj-qband → sec → sec → sec.sand → sec → sec.sand → pj-back → sec.dark |
| 1 | pj-hero → sec → pj-band → sec.sand → pj-back → sec.dark |
| 25 | other sequences (see the csv) |

### Grant programme pages (3)

Built from live harvests by `tools/port_live.py`. On live these three sit in the project post type at /project/{slug}/.

Section sequences inside `<main>`, most common first:

| Pages | Sequence |
|---|---|
| 3 | pj-hero → sec → pj-back → sec.dark |

### Articles (167)

Section sequences inside `<main>`, most common first:

| Pages | Sequence |
|---|---|
| 167 | article.ed-art → sec.sand.ed-more → pj-back → sec.dark |

## Partials

- `partials/header.html`: skip link; Acknowledgement of Country strip (`.ack`); header (`.hdr`) with logo, mobile search icon, menu button and the main nav: About; Projects (All Projects and the three pillars); Partner With Us (Ways to Partner, Government Partnerships, Corporate Partnerships); Impact (Our Impact, Impact Reports); Get Involved (Ways to Get Involved, Corporate Volunteering, Workplace Giving, Fundraising, Gifts in Wills, Donate Land); Stories (Articles); Contact Us; a visible Search link; and the Donate button to https://bush.fnpw.org.au.
- `partials/footer.html`: logo and line, social links, Explore, Get Involved (Donate and Give a Tree go to Raisely), Visit Us (fnpw@fnpw.org.au, 1800 898 626, ABN 90 107 744 771), and legal links (Privacy, Terms, RAP).
- The Acknowledgement of Country sits in the strip above the header rather than in the footer, and the newsletter signup is a page band (`.nl-strip`) rather than part of the footer. The theme parts keep that arrangement.
- `tools/sync.py` sets the active-nav `on` class per page; the Navigation block does this itself in WordPress.

## Design layer

Tokens in the `:root` blocks of `global.css`, which become the theme.json palette, font families and spacing:

| Token | Value |
|---|---|
| `--sp-1` | `8px` |
| `--sp-2` | `16px` |
| `--sp-3` | `24px` |
| `--sp-4` | `32px` |
| `--sp-5` | `48px` |
| `--sp-6` | `64px` |
| `--sec-sm` | `clamp(2rem,3vw,2.5rem)` |
| `--sec-md` | `clamp(3rem,5vw,4.5rem)` |
| `--hero-top` | `clamp(4.5rem,8vw,7rem)` |
| `--hero-bot` | `clamp(3rem,6vw,6rem)` |
| `--sec-y` | `var(--sec-md)` |
| `--euc` | `#0F7768` |
| `--euc-deep` | `#0F3132` |
| `--euc-mid` | `#51B593` |
| `--euc-soft` | `#C6EBCA` |
| `--euc-pale` | `#C6EBCA` |
| `--waratah` | `#C23747` |
| `--waratah-mid` | `#ED4E61` |
| `--waratah-dk` | `#8C1422` |
| `--waratah-soft` | `#FFADB7` |
| `--waratah-pale` | `#FFADB7` |
| `--reef` | `#2C4B89` |
| `--reef-deep` | `#202F54` |
| `--reef-mid` | `#5D7BC1` |
| `--reef-soft` | `#A8C4F3` |
| `--reef-pale` | `#A8C4F3` |
| `--hovea` | `#703985` |
| `--hovea-deep` | `#47243A` |
| `--hovea-mid` | `#B790DE` |
| `--hovea-soft` | `#DBD1EC` |
| `--hovea-pale` | `#DBD1EC` |
| `--bark` | `#AB7341` |
| `--bark-mid` | `#85735E` |
| `--bark-soft` | `#EEE8E1` |
| `--red-soil` | `#B64629` |
| `--red-soil-dk` | `#8E3821` |
| `--red-soil-bright` | `#E26539` |
| `--red-soil-soft` | `#FFAA8A` |
| `--wattle` | `#C4A927` |
| `--wattle-mid` | `#E1CD4A` |
| `--wattle-dk` | `#9F8506` |
| `--wattle-soft` | `#F8EEA9` |
| `--soil` | `#371F1D` |
| `--soil-deep` | `#241914` |
| `--soil-mid` | `#956F6F` |
| `--soil-soft` | `#CBABAB` |
| `--cream` | `#FAF6F2` |
| `--sand` | `#EEE8E1` |
| `--paper` | `#EEE8E1` |
| `--ink` | `#241914` |
| `--char` | `#241914` |
| `--stone` | `rgba(36,25,20,.74)` |
| `--rule` | `#E5DFD3` |
| `--bark-text` | `#80522A` |
| `--white` | `#fff` |
| `--ff-d` | `'Sora',sans-serif` |
| `--ff-b` | `'Figtree',sans-serif` |
| `--ff-h` | `'Figtree',sans-serif` |
| `--mw` | `1240px` |

These tokens carry the same value as another, so theme.json lists each colour once and keeps the alias as a CSS variable: `--euc-pale` = `--euc-soft`, `--waratah-pale` = `--waratah-soft`, `--reef-pale` = `--reef-soft`, `--hovea-pale` = `--hovea-soft`, `--paper` = `--sand`, `--char` = `--ink`.

## Section classes

Classes on the direct children of `<main>`, with the number of pages using each and where its CSS lives. "page" means it is styled only in that page's own `<style>` block, so those rules travel with the page or its pattern.

| Class | Pages | Defined in |
|---|---|---|
| `sec` | 279 | global.css, page |
| `dark` | 262 | global.css |
| `pj-back` | 254 | global.css |
| `sand` | 204 | global.css |
| `ed-art` | 167 | no rule found (modifier or script hook) |
| `ed-more` | 167 | page |
| `pj-hero` | 92 | global.css, page |
| `pj-band` | 57 | global.css |
| `pj-credit` | 22 | global.css |
| `alt` | 20 | global.css, page |
| `flip` | 17 | global.css, page |
| `pil-stats` | 16 | global.css |
| `pj-story` | 15 | global.css |
| `ch` | 14 | global.css |
| `chi` | 14 | global.css, page |
| `pj-qband` | 8 | global.css |
| `ps-healing` | 6 | global.css |
| `ps-species` | 6 | global.css |
| `v-cta` | 6 | page |
| `vs-gal` | 5 | page |
| `vs-hero` | 5 | page |
| `vs-wrap` | 5 | page |
| `fb` | 4 | global.css, page |
| `ps-parks` | 4 | global.css |
| `fb-hero` | 3 | page |
| `fb-paper` | 3 | page |
| `pil-hero` | 3 | page |
| `piw` | 3 | page |
| `pj-hero-soft` | 3 | global.css |
| `ra` | 3 | global.css |
| `sec-cont` | 3 | global.css |
| `sec-head` | 3 | global.css |
| `feat-art` | 2 | page |
| `gw-hero` | 2 | page |
| `gw-pil` | 2 | page |
| `gw-talk` | 2 | page |
| `hx-camp` | 2 | global.css |
| `hx-camp-sm` | 2 | global.css |
| `nh` | 2 | global.css, page |
| `nl-strip` | 2 | page |
| `pj-hero-neutral` | 2 | global.css |
| `pj-hero-split` | 2 | global.css |
| `ab-cta` | 1 | page |
| `ab-film` | 1 | page |
| `ab-hero` | 1 | page |
| `abg` | 1 | page |
| `ac-sec` | 1 | page |
| `c-main` | 1 | page |
| `cg-sec` | 1 | page |
| `chi-healing` | 1 | global.css |
| `chi-parks` | 1 | global.css |
| `chi-species` | 1 | global.css |
| `ct-hero` | 1 | page |
| `ct-news` | 1 | page |
| `dl-contact` | 1 | page |
| `dl-cost` | 1 | page |
| `dl-faq` | 1 | page |
| `dl-how` | 1 | page |
| `dl-open` | 1 | page |
| `dl-proc` | 1 | page |
| `door` | 1 | no rule found (modifier or script hook) |
| `fb-healing` | 1 | global.css |
| `fb-parks` | 1 | global.css |
| `fb-species` | 1 | global.css |
| `filters-news` | 1 | page |
| `fq-contact` | 1 | page |
| `fq-sec` | 1 | page |
| `fw-form` | 1 | page |
| `fw-intro` | 1 | page |
| `fw-paths` | 1 | page |
| `fw-thanks` | 1 | page |
| `fw-ways` | 1 | page |
| `gi-hero` | 1 | page |
| `gw-faq` | 1 | page |
| `gw-feat` | 1 | page |
| `gw-how` | 1 | page |
| `gw-im` | 1 | page |
| `gw-leg` | 1 | page |
| `gw-pro-cta` | 1 | page |
| `gw-proof` | 1 | page |
| `gw-ty` | 1 | page |
| `gw-why` | 1 | page |
| `gw-word` | 1 | page |
| `hc-band` | 1 | page |
| `hc-open` | 1 | page |
| `ht` | 1 | page |
| `hx-gat` | 1 | page |
| `hx-hero` | 1 | page |
| `hx-impact` | 1 | page |
| `hx-news` | 1 | page |
| `hx-pils` | 1 | no rule found (modifier or script hook) |
| `hx-pt` | 1 | page |
| `hx-rail-sec` | 1 | no rule found (modifier or script hook) |
| `hx-story` | 1 | page |
| `ip-close` | 1 | page |
| `ip-hero` | 1 | page |
| `ip-jump` | 1 | page |
| `ip-partners` | 1 | page |
| `ip-results` | 1 | page |
| `ip-trees` | 1 | page |
| `map-sec` | 1 | page |
| `me-sec` | 1 | page |
| `nf-hero` | 1 | page |
| `ns` | 1 | page |
| `nw-hero` | 1 | page |
| `pa-band` | 1 | page |
| `pa-intro` | 1 | page |
| `pa-rest` | 1 | page |
| `po` | 1 | page |
| `proj-hero` | 1 | page |
| `ra-healing` | 1 | global.css |
| `ra-parks` | 1 | global.css |
| `ra-species` | 1 | global.css |
| `sky` | 1 | page |
| `srch-hero` | 1 | page |
| `strip` | 1 | global.css, page |
| `sts` | 1 | page |
| `v-acts` | 1 | page |
| `v-ben` | 1 | page |
| `v-faq` | 1 | page |
| `v-prog` | 1 | page |
| `v-sticky` | 1 | page |
| `v-where` | 1 | page |
| `vs-site` | 1 | no rule found (modifier or script hook) |
| `wg-cta` | 1 | page |
| `wg-sec` | 1 | page |
| `wy-dark` | 1 | page |
| `wy-open` | 1 | page |
| `wy-threats` | 1 | page |
| `wy-track` | 1 | page |

## Scripts

| File | Pages | Purpose |
|---|---|---|
| `assets/js/main.js` | 297 | Base: mobile drawer, header shadow, scroll reveal (.rv), [data-count] counters, dropdown and accordion nav |
| `https://js-ap1.hsforms.net/forms/embed/441704788.js` | 12 | HubSpot form embed (external) |
| `https://js-ap1.hsforms.net/forms/embed/v2.js` | 6 | HubSpot form embed (external) |
| `assets/js/gallery.js` | 5 | Photo gallery in pages of six |
| `assets/js/snap.js` | 1 | Section snap (About page) |
| `assets/js/articles.js` | 1 | Stories page filter, sort and paging |
| `assets/js/carousel.js` | 1 | Photo carousel (scroll-snap, auto-advance) |

## Interactive components

The treatment column is the build-spec proposal, confirmed as each one is built.

| Component | Pages | How it works now | Proposed WordPress treatment |
|---|---|---|---|
| Project map | 1: projects | Inline IMAP data (from data/projects.json via tools/gen_map.py) plus inline map script; pins open project cards | Custom block fnpw/project-map (block.json + render.php), reads a JSON file generated at import, live project data after launch |
| Project grid with pillar filter | 4: growing-national-parks, healing-the-land, projects, saving-species | Inline script filters #pgrid tiles by state and type | Custom block fnpw/project-grid, server-rendered tiles, filter script enqueued only where used |
| Projects page tiles and filters | 1: projects | Inline script on projects.html (popup data retired Nov 2026, cards link to project pages) | Part of fnpw/project-grid |
| Stories filter, sort and paging | 1: articles | assets/js/articles.js over .art-grid tiles | Core Query Loop for posts plus a small filter script, or a custom block if the sort must stay client-side |
| Article reading bar | 167: article-10000-native-give-away-trees-and-shrubs-hit-the-ground, article-2022-impact-report, article-2023-foundation-for-national-parks-wildlife-impact-report, article-30765, article-80000-additional-trees-to-be-planted-at-friends-of-the-koala-nursery-to-support-koala-population and 162 more | Inline script adds a progress bar to the .ed article body | One script in the single post template, not per post |
| Volunteer sites map | 5: corporate-volunteering-nsw, corporate-volunteering-qld, corporate-volunteering-sa, corporate-volunteering-vic, corporate-volunteering-wa | Inline script toggles state map pins and the site list | Custom block fnpw/volunteer-map with data/volunteer-sites.json |
| Where-we-run state tabs | 1: volunteer | Inline tab switcher on volunteer.html | Custom block fnpw/tabs (shared with the other tab sets) |
| Photo carousel | 1: volunteer | assets/js/carousel.js, scroll-snap track #volTrack, auto-advance | Pattern with carousel.js enqueued where the pattern is used |
| Photo gallery (pages of six) | 5: corporate-volunteering-nsw, corporate-volunteering-qld, corporate-volunteering-sa, corporate-volunteering-vic, corporate-volunteering-wa | assets/js/gallery.js, scroll-snap track | Pattern with gallery.js enqueued on use |
| Project slider (homepage) | 1: index | Inline script on [data-fls] with previous and next buttons | Custom block fnpw/project-slider, or a pattern plus script |
| Tabs (government partnerships) | 1: government-partnerships | Inline tab switcher .jt | fnpw/tabs |
| Tabs (partner and invest) | 1: partner-invest | Inline ARIA tablist | fnpw/tabs |
| Read more toggles | 2: about, government-partnerships | Inline expanders (.jd-more, .tc-more on bios) | Core Details block where the markup allows, else a small shared script |
| Load more list | 2: our-impact, partner | Inline load-more on #lmq | Shared theme script, enqueued on use |
| Timeline rail (drag to scroll) | 1: about | Inline drag-scroll on #htRail | Pattern plus small script |
| Card arrows | 1: about | Inline scroll buttons on .abs-arr | Pattern plus small script |
| Reports filter | 1: reports | Inline filter buttons #rpf | Custom block, or Query Loop with a taxonomy filter |
| Site search (client-side index) | 1: search | Inline 28 KB index of every page, searched in the browser | Retired: the WordPress search template replaces it |
| Section snap | 1: about | assets/js/snap.js settles onto section edges | Enqueue snap.js on the About page only |
| Accordions (details) | 5: bequests, donate-land, faqs, government-partnerships, volunteer | Native details and summary | Core Details block |
| Animated counters | 1: index | main.js animates [data-count] | Keep in main.js; data-count carried on the converted markup |
| HubSpot form embed | 18: articles, bequests, contact, corporate-volunteering-nsw, corporate-volunteering-qld and 13 more | HubSpot embed script (portal 441704788, region ap1) | Keep the HubSpot embed in a Custom HTML block or small fnpw/hubspot-form block (live pages use the same HubSpot forms) |
| Video embed | 1: about | YouTube no-cookie iframe | Core Embed block |
| Podcast embed | 1: article-koala-facts | Omny iframe | Core Embed or Custom HTML |
| Google map embed | 1: contact | Google Maps iframe | Custom HTML block |

## Forms

HubSpot form IDs in the static build and the pages they sit on. The admin audit at the end compares them with live.

| HubSpot form ID | Pages |
|---|---|
| `5275a663-85fc-43d4-8400-b17d34ece7fa` | corporate-volunteering-nsw, corporate-volunteering-qld, corporate-volunteering-sa, corporate-volunteering-vic, corporate-volunteering-wa, volunteer |
| `be19c736-6c95-4159-8245-e7b32af6dba3` | articles, newsletters-sign-up, projects, reports |
| `368738b1-f478-4c8b-93ac-484ef27a6540` | government-partnerships, partner, partner-invest |
| `51106005-f5bb-4960-a900-2250a60244a0` | bequests |
| `e33c8c8b-1d45-4477-be3e-8e5ca7b3e82b` | contact |
| `39b8240c-ac28-4012-b9b7-30e589d105f4` | donate-land |
| `eca5e898-c9f5-429d-aa0f-1f4986c079c1` | fundraising-with-fnpw |
| `e9e550ed-025f-474c-b214-a5cb3c0511eb` | media-enquiry |

## Assets

- `assets/img`: 862 files, 137.0 MB (all images)
- `assets/img/r`: 631 files, 83.1 MB (responsive webp sizes from tools/build_images.py)
- `assets/img/projects`: 83 files, 27.3 MB (project heroes)
- `assets/img/partners`: 55 files, 1.1 MB (partner logos)
- `assets/img/volunteering`: 16 files, 5.7 MB (volunteering photos)
- `assets/img/reports`: 1 files, 0.1 MB (report covers)
- `assets/icons`: 120 files, 0.7 MB (icons)
- `assets/fonts`: 2 files, 0.1 MB (Sora and Figtree woff2)
- `assets/docs`: 1 files, 1.8 MB (PDFs)
- Repo root: favicon.svg, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png and site.webmanifest go into the theme. robots.txt, sitemap.xml, feed.xml, llms.txt and llms-full.txt come from `tools/meta.py --site`; WordPress and Yoast produce their own at launch.
- Image hosts: fnpw.org.au (1486), (local assets/) (1197), images.theconversation.com (16), counter.theconversation.com (2), cdnc.heyzine.com (1).

## Data and generators

- `data/projects.json` (85 projects with slug, pillar, state, coordinates and live URL) feeds the map and project pages; `data/projects-content.json` holds harvested live project copy (72 projects).
- `data/articles.json` (166 articles) feeds the article pages and the Stories index. `data/live-port/` holds word-for-word harvests used by `tools/port_live.py`.
- `data/meta.json` holds the hand-written titles and descriptions that `tools/meta.py` writes into every head. Yoast owns these in WordPress, so this file is the source for setting them there.
- `data/alt-text/` holds alt text written from the photographs and applied by `tools/apply_alt.py`; `data/wp-media.json` has featured-image alt and sizes from the live REST API.

## Flags for Ely

- **Page count.** The handover says 121 pages. The repo has 297: 167 articles and 130 site, project and grant pages. How the articles import is a page-map decision.
- **Forms.** Live pages use the same HubSpot forms as the static build, so nothing is swapped. Three Formidable forms are still on live pages; see the admin audit.
- **Old WordPress scaffold.** `wp/` (September) holds an earlier block theme and plugin. Its fnpw-core registers its own `project` post type and taxonomies, which would clash with Template Required Plugins. Decision pending on whether to build fresh in `wordpress/` and borrow from it.
- **CLAUDE.md is out of date in two places.** It says images come from Unsplash (none do now) and lists Caveat as a typeface (removed).
<!-- /@generated -->

## Admin audit (task 8)

Read on 10 November from wp-admin (Ely logged in, nothing changed) and from the theme and plugin files downloaded to Documents/fnpw-live-reference.

### Tracking

The snippets are theme templates (`fnpw/resources/views/partials/`) that print values held in ACF Settings: General. They disappear when the theme switches, so FNPW Core has to output them.

| Snippet | Value on live | Where it prints |
|---|---|---|
| Google Tag Manager | GTM-K2P27RG | head, plus noscript after the body tag |
| Meta pixel | 2023665144313964 | head |
| Hotjar | 1708422 | head |
| Universal Analytics | empty | not printed |
| Head scripts, footer scripts | empty | not printed |
| HubSpot tracking | from the HubSpot plugin | survives the switch |

The two GA4 properties and two Google Ads IDs are not in the page source. They load through the Tag Manager container, so they carry over with GTM and their clean-up is a Tag Manager job for Reef. A Google Maps API key is also stored in Settings: General for the old map; the new build only needs it if the project map uses Google Maps.

### Forms

Live pages already use HubSpot forms, embedded through Elementor, with the same form IDs as the static build. The 14 Formidable forms are mostly history.

| Live page | Form on live | Static build |
|---|---|---|
| Home, newsletter page, Ways to Get Involved | HubSpot be19c736 | Same form |
| Contact | HubSpot e33c8c8b | Same |
| Bequest | HubSpot 51106005 | Same |
| Corporate partnerships | HubSpot 368738b1 | Same |
| Corporate volunteering and the five city pages | HubSpot 5275a663 | Same |
| Fundraising | HubSpot eca5e898 | Same |
| Media enquiry | HubSpot e9e550ed | Same |
| Donate land | HubSpot 39b8240c | **Different:** the build uses the Contact form e33c8c8b |
| Workplace giving, /tech4forests/ | Formidable 4 (Corporate Contact Us) | No form on workplace-giving.html |
| eBook page | Formidable 17 (Ebook submission) | No form on the page |
| /test-form/, /project/form-test/ | Formidable 12 (contractor expression of interest) | Not in the build |

Formidable forms and entries: 2 Donation (3), 3 Contact Us (1,567), 4 Corporate Contact Us (366), 5 Newsletter (985), 6 Bequest Contact Us (20), 7 Fundraising Contact Us (14), 8 Giving Circle Contact Us (5), 9 Media Enquiry (10), 10 Newsletter (5,230), 12 Contractor expression of interest (1), 16 Ebook (1), 17 Ebook submission (25), 18 Corporate Volunteering Contact Us (354), 19 Newsletter Sidebar (16).

Not yet read: the confirmation settings for Formidable forms 4, 12 and 17, and the thank-you redirects for the HubSpot forms, which are set inside HubSpot.

### ACF field groups (29)

Saved as JSON by Template Required Plugins in `acf-json/field-groups/`.

- **Project fields:** `Single - Project` holds `project_details` (start_year, project_latitude, project_longitude, project_state, project_focusarea, first_nations_). `Single - Project/Grant` holds `flexible_sections` with the layouts project_copy, project_overview, project_news, related_projects, project_gallery, project_video and decor_spacer. `Single - Header` (posts, projects, grants, donations) holds banner_image, title_override, subtitle_optional and excerpt.
- **Per-page groups:** Home, About Us, Contact Us, Contributions Help, Corporate Partners, Donations, Donations Listing, FAQs, Get Involved, Grants, News, Projects, Support Needed and Template - Flexible, each tied to a Sage page template.
- **Sections:** Hero, Heritage Map.
- **Settings (options pages):** General, Header, Footer.
- **Others:** Single - Donation, Single - Grant/Donation, Menu - Custom Fields, Widget - Announcement, Widget - Latest News, Attachments - Link, group with link.

### Template Required Plugins

- Registers `project`, `grant` and `donation` with the slugs /project/, /grant/ and /donation/, supporting title, editor, thumbnail and revisions, plus the taxonomies at projects/state, projects/focus_area, projects/year, grants/category and donations/category.
- Two shortcodes, `[mydate]` and `[assetpath]`, and two widgets (announcement, latest news).
- It also sets the ACF JSON save and load path, so the field groups stay available after the theme switch.

### Menus

Two menus exist: Primary Navigation Desktop (assigned to both the desktop and mobile locations) and Primary Navigation Mobile (unassigned). The footer links come from ACF Settings: Footer, not a menu. The new theme builds its menus from the static header and footer.
