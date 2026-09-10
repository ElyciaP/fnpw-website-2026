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
- Phone: 1800 898 626. ABN: 51 248 905 949.

## Give a Tree

`gift-a-tree.html` keeps its filename but the campaign is branded **Give a Tree**
(tagline: Bring Back the Bush). The page is built by `tools/build_gat.py`, not by hand.

The donation form is an iframe pointing at `https://gift-a-tree.raiselysite.com/embed/donate`.
That is the only embeddable endpoint: `/` and `/donate` both send `X-Frame-Options: DENY`
and cannot be framed from our domain.

The home page tier tiles link in as `gift-a-tree.html?amount=100#give`; the page forwards
that amount to Raisely as a query parameter.
