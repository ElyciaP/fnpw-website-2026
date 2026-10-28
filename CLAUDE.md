# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Static multi-page website for the **Foundation for National Parks & Wildlife (FNPW)**, an Australian conservation charity. No build system, bundler, or framework — each HTML file is fully self-contained.

To preview the site, open any `.html` file directly in a browser, or run a local server:
```bash
python3 -m http.server 8000
```

## Architecture

**13 HTML pages + shared assets (consolidated July 2026).** Shared code lives in one place:

- `assets/css/global.css` — design tokens (`:root`) and all global/reset CSS, linked by every page
- `assets/js/main.js` — base JS (hamburger, header scroll shadow, `.rv` reveal, `[data-count]` counters, dropdown a11y), loaded by every page except `donate.html` and `gift-a-tree.html` (their page JS still has the base JS merged inline — untangle during WordPress conversion)
- `partials/header.html` / `partials/footer.html` — canonical header and footer
- `assets/img/fnpw-logo.png`, `assets/img/fnpw-logo-footer.png` — logo assets (no more base64)

**Editing the header or footer:** edit the partial, then run `python3 tools/sync.py`. The script re-injects both partials into every page between `<!-- @header -->…<!-- /@header -->` and `<!-- @footer -->…<!-- /@footer -->` markers, and applies the active-nav `on` class per page (map lives in the script). Never hand-edit inside the marker regions.

Page-specific CSS remains in each page's own `<style>` block; page-specific JS in its own `<script>` block.

## Design system

All design tokens live in the `:root` block at the top of each file's first `<style>` tag.

**Colour families:**
- `--euc` / `--euc-deep` / `--euc-mid` / `--euc-soft` / `--euc-pale` — eucalyptus greens (primary brand)
- `--waratah` / `--waratah-dk` / `--waratah-soft` / `--waratah-pale` — red-pink accent
- `--reef` family — blue
- `--hovea` family — purple-pink
- `--bark`, `--red-soil`, `--wattle` — earthy warms
- `--cream` / `--sand` / `--paper` / `--ink` / `--char` / `--stone` / `--rule` — neutrals

**Typefaces** (Google Fonts):
- `--ff-d`: `Sora` — display headings
- `--ff-b`: `Figtree` — body text
- `--ff-h`: `Caveat` — handwritten accent

**Spacing tokens (Oct 2026):** one section rhythm sitewide, in the first `:root` of `global.css`.
- `--sec-md` is the padding for every standard section, top and bottom, whatever its background. `--sec-y` is an alias for it. `--sec-sm` is for thin strips only (newsletter band, proof bars). Heroes use `--hero-top` / `--hero-bot`.
- Gap scale: `--sp-1` 8, `--sp-2` 16, `--sp-3` 24, `--sp-4` 32, `--sp-5` 48, `--sp-6` 64 (px). Use these for grid gaps and stack spacing, not hard-coded values.
- Heading stack: eyebrow, then h2 8px below (`.ey + h2`), then intro 24px below. `.ey` is `vertical-align:top` so the gap is exact.
- Never put padding or margin in a section or heading `style=""` attribute. Inline spacing overrides the tokens; it was stripped from about.html.
- Helpers in `global.css` (spacing pass, Oct 2026): `.sec.strip` for thin bands (logo bars, evidence strips); `.sec-head` / `.sec-cont` for a list section split around a sticky filter bar (pillar pages); `.sec.pj-credit` for the funder credit line on project pages. Project pages have `<main class="pj-main">`, which collapses the top padding where two cream (or two sand) sections meet, so the gap is one `--sec-md`, not two.

**Section snap:** `assets/js/snap.js` gives a gentle one-direction settle onto `main > section` edges after scrolling stops (desktop, no reduced motion). Opt a page in by loading the script after main.js. Currently on: about.html.

**Key utility classes:**
- `.cw` — content wrapper (max-width 1240px, fluid horizontal padding)
- `.sec` — section padding; `.sec.dark`, `.sec.paper`, `.sec.sand` for background variants
- `.rv` / `.rv.d1–.d4` — scroll-reveal animation (opacity + translateY, triggered by IntersectionObserver)
- `.ey` — eyebrow label (small-caps with decorative rule)
- `.lede` — large intro paragraph
- `.two` — two-column grid, stacks on mobile
- `.framed` — image with offset coloured shadow block (`.framed.wt` wattle, `.framed.bk` bark)
- `.btn-p` / `.btn-o` / `.btn-s` / `.btn-g` — button variants (primary, outline, solid, ghost/underline)
- `.stat-n` / `.stat-l` — large animated statistic number + label

**`[data-count]` counter animation:** Add `data-count="123"` to an element; the JS animates it to that value on scroll. Optional: `data-dec` (decimal places), `data-suf` (suffix), `data-pre` (prefix).

## Navigation structure

```
Home (index.html)
About (about.html)
Projects (projects.html)
News (news.html)
Get Involved ▾
  ├ Become a Partner (partner.html)
  ├ Corporate Volunteering (volunteer.html)
  └ Bequests (bequests.html)
Contact (contact.html)
[Donate button] (donate.html)
```

`bring-back-the-bush.html` and `gift-a-tree.html` are reached via in-page links, not the main nav.

## Images

All images are sourced from Unsplash via URL (e.g. `https://images.unsplash.com/photo-…?w=1800&q=80`). The FNPW logos are real files in `assets/img/`.

## Contact details (do not change these)

- Email: **fnpw@fnpw.org.au**. Not `hello@fnpw.org.au`, which was wrong and has been
  corrected across every page and in `partials/footer.html`.
- Phone: 1800 898 626. ABN: 90 107 744 771.

## Donations (Sep 2026)

Donations stay on Raisely. Our own donate, Give a Tree and Bring Back the Bush pages were
removed. Every Donate button goes to https://bush.fnpw.org.au, Give a Tree goes to
https://gift-a-tree.fnpw.org.au and monthly giving (Habitat Heroes) to
https://habitat-heroes.fnpw.org.au. Never build an on-site payment form.

## Pages ported from the live site

`tools/port_live.py` builds the legal pages, grants hub and grant pages, PAWS archive,
eBook page, newsletter thank-you page, the FAQ tax group and three blog entries from the
word-for-word harvests in `data/live-port/*.md`. Re-run it after editing a harvest file.

## Alt text

Alt text was written by looking at every photograph (Sep 2026) and lives in
`data/alt-text/`. After running any page generator, run `python3 tools/apply_alt.py`
to fill alt text on anything the generator left empty. Add new images to
`alt-local.txt` (local files) or append to `remote-urls.json` + `alt-remote-by-index.txt`.
Decorative icons get `alt="" aria-hidden="true"`.
