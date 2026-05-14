# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Static multi-page website for the **Foundation for National Parks & Wildlife (FNPW)**, an Australian conservation charity. No build system, bundler, or framework — each HTML file is fully self-contained.

To preview the site, open any `.html` file directly in a browser, or run a local server:
```bash
python3 -m http.server 8000
```

## Architecture

**11 self-contained HTML pages.** Each file contains all its CSS in inline `<style>` blocks and all its JavaScript in inline `<script>` tags at the bottom. There are no external `.css` or `.js` files.

### What is duplicated across every page

The following blocks are copied verbatim into every HTML file — changes must be applied to all 11 files:

- **CSS custom properties** (`:root` block): the full design token set
- **Global/reset CSS**: typography, links, buttons, `.sec`, `.cw`, utilities
- **Header HTML**: `.ack` acknowledgement bar, `.hdr` sticky nav with `.ng` dropdown groups and base64 logo
- **Footer HTML**: `.ftr` four-column grid with links, ABN, copyright
- **Base JS**: hamburger toggle, scroll shadow on header, `.rv` scroll-reveal `IntersectionObserver`, `[data-count]` counter animation, `.ng` dropdown keyboard accessibility

### Page-specific logic

| Page | Unique feature |
|---|---|
| `index.html` | Campaign launch countdown banner (calculates days until `2026-05-18 AEST`) |
| `donate.html` | Full donation wizard: frequency (once/monthly), preset amounts, fee-coverage checkbox, tribute, impact copy by tier, payment method selector |
| `bring-back-the-bush.html` | Dedicated campaign landing page for the Bring Back The Bush initiative |

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

All images are sourced from Unsplash via URL (e.g. `https://images.unsplash.com/photo-…?w=1800&q=80`). The FNPW logo is embedded as a base64 PNG directly in the `<img>` tag inside the header.
