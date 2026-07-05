# FNPW Website Go-Live Playbook

**For:** Elycia. **Assumes:** 1.5 hrs per day, every day or second day (about 6 hrs/week).
**Written:** July 2026. This document is designed to be self-sufficient: everything Claude
worked out about this project is captured here, so any future Claude session (or a human
developer) can pick up from any point. When starting a new Claude session, paste the
relevant week's section and say "continue from here".

---

## 1. The rules (read first, they prevent disasters)

1. **Never build on the live site.** All theme and plugin work happens on the SiteGround
   staging copy. The live site only changes at launch, and via normal content publishing.
2. **Code flows up, content flows down.** Code: local repo → staging → production.
   Content: created on production (or staging just before launch), never re-keyed twice.
   WordPress databases cannot be merged; plan so you never need to.
3. **Backup before anything scary.** UpdraftPlus full backup before plugin updates, theme
   activation, or launch. Check the backup actually completed.
4. **Commit after every session.** `git add -A && git commit -m "what changed"` in the
   website-project folder. Git is the undo button.
5. **Launch freeze windows:** never switch themes in June (EOFY) or November-December
   (Gift a Tree, 12 Days of Wildlife). If you miss the October window, hold until February.
6. **Cultural content:** RAP, Kaurna and Firesticks material is ported verbatim, never
   rewritten, and any change needs sign-off through the existing approval process.
   Always "Kaurna Yarta". Always "&" in the organisation name. No em dashes.
7. **Donations stay on Raisely** for this launch. Donate buttons keep their existing hrefs.
   Payments migration (GiveWP) is phase 2, after the site is stable.

## 2. Inventory: what exists and where

**The repo** (`~/Downloads/website-project`, branch `consolidate`):
- 121 HTML pages: 13 originals + 83 project pages + 3 pillar pages + ~20 site pages
- `assets/css/global.css` - the whole design system (tokens + components), one file
- `assets/js/main.js` - shared JS; `partials/` - header + footer (canonical)
- `data/projects.json` - all 83 projects: slug, title, image, pillar (provisional), state
- `tools/sync.py` - edit a partial, run this, all pages update
- `tools/gen_projects.py`, `gen_pages.py`, `gen_exemplars.py` - page generators (re-runnable)
- `tools/make_design_pack.py` - rebuilds `design/` single-file templates
- `design/` - 8 template files + DESIGN-BRIEF.md + CLAUDE-DESIGN-PROMPT.md
- Exemplar pages with full real content: project-warddeken-mayh.html (long),
  project-remarkable-southern-flinders.html (medium), project-southern-highlands-koala-conservation.html (short)
- Preview: `python3 -m http.server 8000` in the folder, open http://localhost:8000

**The live stack (fnpw.org.au):**
- WordPress on **SiteGround** (staging available in Site Tools), custom `fnpw` theme
  (Sage/Blade, locked) + **Elementor 4.x** for page layouts
- **"Template Required Plugins" (by drufloe)** registers the `project` post type,
  taxonomies `project_state`, `project_focus_area`, `project_year`, plus `grant` and
  `donation` types. THIS IS CRITICAL: the new build must reuse these exact post type keys.
- **ACF Pro 6.8** installed and active. **Yoast SEO** (Premium subscription EXPIRED,
  free still works). **Redirection** plugin installed. **UpdraftPlus** backups.
  **Formidable Forms** + **HubSpot** (newsletter/EDM) + **Post SMTP** (email delivery).
- Analytics: Google Tag Manager container **GTM-K2P27RG**. Keep it through launch.
- Donations: **Raisely**, hosted off-site (foundation-for-national-parks-and-wildlife.raiselysite.com,
  habitat-heroes.raiselysite.com, bush.fnpw.org.au, gift-a-tree.fnpw.org.au subdomain).
- 85 live project URLs under `/project/<slug>/` (2 are junk/grants, see redirects).
- Org facts: ABN 90 107 744 771, 1800 898 626, GPO Box 2666 Sydney NSW 2001,
  ACNC registered, DGR endorsed.

**Known issues to fix along the way:** 29 plugins pending updates with auto-update off;
AccessPress Anonymous Post Pro must be DELETED (compromised vendor, powers the junk
upload-your-blog-post page); 7 inactive plugins to delete; Akismet unconfigured; decide
renew-or-drop Yoast Premium (Redirection covers redirects, so dropping is fine);
live og:locale says en_US, should be en_AU.

---

## 3. Week by week

Sessions are ~1.5 hrs. "Prompt" lines are what to paste into Claude (with relevant files).

### Week 1 (wc 6 Jul) - Foundations and cleanup, part 1
- **Session 1:** Email REEF/host contacts: confirm no contractual barrier to self-managed
  theme; confirm who owns the SiteGround account and get Site Tools access. Subscribe to
  Claude Max (5x) if not already.
- **Session 2:** UpdraftPlus full backup (verify it completed). Then in Plugins: DELETE
  AccessPress Anonymous Post Pro, and the inactive seven (Wordfence*, WP Rocket, Smush,
  reSmush, Image Optimizer, Autoptimize, Search & Replace). *Optional: activate Wordfence
  once first and run a malware scan, then delete.
- **Session 3:** Update all plugins EXCEPT Elementor (backup first, update in batches of
  five, check the site loads after each batch). Configure Akismet (free key).
- **Done when:** backup verified, cruft gone, updates applied, access confirmed.

### Week 2 (wc 13 Jul) - Staging + pillar data
- **Session 1:** SiteGround Site Tools > WordPress > Staging > Create. Update Elementor on
  staging, check key pages, then repeat on live. In staging wp-admin, open the "Template
  Required Plugins" code (Plugins > Plugin File Editor) and copy the register_post_type /
  register_taxonomy code into a file for Claude. This tells us the exact CPT keys.
- **Session 2:** Review `data/projects.json`: correct the pillar guess for every project
  you know (43 species / 28 healing / 12 parks currently, all marked unconfirmed). Ask
  Claude to regenerate pages after edits: `python3 tools/gen_projects.py && python3 tools/gen_exemplars.py && python3 tools/sync.py`.
- **Session 3:** Sweep the yellow "To port from live site" boxes: copy-paste real copy from
  the live pages into a single notes file (or give Claude the live URLs and ask it to port
  them into the static pages the way the exemplars were done).
- **Done when:** staging exists, CPT registration code captured, pillars corrected.

### Weeks 3-5 (wc 20 Jul - 9 Aug) - Design
- One Claude design session per sitting, in this order: index, projects hub, project detail
  (warddeken), pillar page, campaign, donate, about, simple content page.
- Use `design/CLAUDE-DESIGN-PROMPT.md` + attach the brand guidelines PDF + ONE file from
  `design/`. From session 2 onward also attach the approved homepage as reference.
- After each session, bring the returned file to Claude (Cowork) with:
  **Prompt:** "Here is the redesigned template from Claude design. Diff it against the
  original in design/, merge the changed CSS into assets/css/global.css (and partials if
  the header/footer changed), run tools/sync.py, and show me what changed."
- **Done when:** all 8 templates approved and merged; whole 121-page site restyled; commit.

### Weeks 6-9 (wc 10 Aug - 6 Sep) - WordPress theme build (on staging only)
This is the part you haven't done before. It is a mechanical translation, not a redesign.

- **Session 1 (scaffold):**
  **Prompt:** "Build a classic WordPress theme called fnpw2026 from this static site. Here
  are partials/header.html, partials/footer.html, assets/, and index.html. Produce:
  style.css (theme header comment), functions.php (enqueue global.css, main.js and Google
  fonts; register a primary menu; add theme supports), header.php and footer.php (from the
  partials, with wp_head()/wp_footer() and home_url() links), front-page.php (from
  index.html), page.php (generic content template). Zip layout ready for upload."
  Upload via staging wp-admin > Appearance > Themes > Add New > Upload. Activate ON STAGING.
  Expect it to look right but with dead links; that is fine.
- **Session 2 (content plugin):**
  **Prompt:** "Here is the register_post_type code from the current site's Template Required
  Plugins. Write a small standalone plugin, fnpw-content, that registers the SAME post type
  keys and slugs for project (and keeps grant/donation types readable), plus a new public
  'pillar' taxonomy (growing-national-parks, saving-species, healing-the-land) attached to
  project. It must not conflict if the old plugin is active; guard with post_type_exists()."
  Install on staging, then deactivate the old drufloe plugin and confirm all projects are
  still visible in wp-admin and at /project/... If anything vanishes, reactivate the old one
  and debug with Claude.
- **Session 3 (ACF):** In staging: ACF > add field groups for Projects (year, state, status,
  latitude, longitude, stats repeater, gallery, lead partner) and an Options page (contact
  details, ABN, donate URLs). Ask Claude for the import JSON instead of clicking it all:
  **Prompt:** "Generate an ACF Pro import JSON for these field groups... and tell me how to
  enable Local JSON (acf-json folder in the theme)."
- **Sessions 4-6 (templates):**
  **Prompt:** "Convert these static pages into theme templates wired to WordPress:
  single-project.php from project-warddeken-mayh.html (title, ACF fields, the_content,
  related projects by shared pillar term); taxonomy-pillar.php from saving-species.html
  (term title/description + WP_Query loop of that term's projects using the card markup);
  page templates for campaign and simple content pages; archive and search.php and 404.php.
  Replace hardcoded card grids with loops. Map pins: wp_localize_script an array of
  {title, lat, lng, url} from a WP_Query of projects."
  Iterate: upload, look, screenshot problems back to Claude.
- **Session 7:** Menus (Appearance > Menus, match the static nav), widgets/footer links,
  Yoast on the new templates, permalinks check (project URLs must not change).
- **Done when:** staging site renders the new design from the CMS: front page, a pillar
  page listing its projects from the taxonomy, warddeken renders from post content + ACF,
  menus work, old URLs resolve.

### Weeks 10-11 (wc 7 - 20 Sep) - Content
- Tag all 83 projects with their pillar term (data/projects.json is the source of truth;
  Claude can generate a WP-CLI or CSV import to do it in bulk, or do it manually, ~2 sessions).
- Set featured images (they are already in the media library from the old site).
- Port remaining yellow-box copy into WP pages. Recreate corporate volunteering city pages
  as CHILD pages of corporate-volunteering so URLs stay /corporate-volunteering/sydney/
  (the static prototype flattened these; WordPress should not).
- Newsletter: paste the HubSpot form embed into the newsletter page and test a signup.
  Forms: rebuild/embed the Formidable contact + media forms, test submissions arrive.
- **Done when:** no yellow boxes remain on staging, forms tested, projects all tagged.

### Weeks 12-13 (wc 21 Sep - 4 Oct) - Quality
- **Redirects** (Redirection plugin), minimum set:
  /grants/ and /grant/wildlife-heroes-grants/ → /ways-you-can-get-involved/ (we no longer do grants);
  /project/form-test/, /test-form/, /upload-your-blog-post/ → 410 gone or → home;
  /project/bushfire-recovery-small-grants/, /private-land-conservation-grants/,
  /community-conservation-grants/ → /projects/ ;
  /paws-magazine/ → /news/ ; /tax-deductible-charity-donation/ → /donations/ ;
  /foundation-for-national-parks-and-wildlife-newsletter/ → /newsletters-sign-up/.
  Everything else keeps its URL by design, so no other redirects should be needed.
  Verify with Yoast that titles/metas carried over on key pages.
- **Accessibility pass:** keyboard-tab the nav, map and FAQ accordions; alt text sweep;
  contrast check anywhere wattle or light text was used. Fix og:locale to en_AU.
- **Performance:** run PageSpeed on staging URL; lazy-load confirmed; ask Claude to fix
  anything under ~85 mobile.
- **Cross-browser/device:** Safari, Chrome, an iPhone and an Android. Screenshot issues
  to Claude.
- **Done when:** the launch checklist below is all green ON STAGING.

### Week 14 (wc 5 Oct) - Launch (window A)
Decision gate: if this slips past 1 November, STOP. Keep staging warm, launch early
February 2027 instead. Never switch during Gift a Tree season.
- **Pre-flight (session 1):** full UpdraftPlus backup of production (files + DB), download
  it. Confirm rollback plan: Appearance > Themes > activate old theme = instant undo.
- **Launch (session 2, pick a quiet morning, Tue-Thu):** SiteGround "push staging to live"
  (Site Tools does this) OR: upload fnpw2026 theme + fnpw-content plugin to production,
  activate plugin, activate theme, import acf-json, set menus, add redirects.
  Then immediately: click every nav item, make a $2 test donation via the donate page
  (refund it), submit the contact form, sign up to the newsletter, check GTM fires
  (Tag Assistant), check /project/warddeken-mayh/ and two other old URLs.
- **Post-launch week:** watch Redirection's 404 log daily and add redirects for anything
  real; check Search Console for coverage errors; monitor site speed and forms.

### Launch checklist (copy into an issue and tick)
- [ ] Backup taken and downloaded
- [ ] Old theme still installed (rollback path)
- [ ] All nav + footer links resolve
- [ ] Donate → Raisely works end to end (test gift)
- [ ] Newsletter signup reaches HubSpot
- [ ] Contact + media forms deliver email
- [ ] 5 sampled old project URLs return 200
- [ ] Redirect list live and tested
- [ ] GTM firing, GA receiving
- [ ] Yoast sitemap regenerated and submitted in Search Console
- [ ] 404 page, search page work
- [ ] Mobile spot-check on a real phone
- [ ] og:locale en_AU, favicons, social share cards look right

---

## 4. Canned prompts for future Claude sessions

- **Context bootstrap:** "You are helping me finish the FNPW website rebuild. Read
  PLAYBOOK.md and CLAUDE.md in this folder, then tell me where we are up to based on
  git log, and what this session should do. I have 1.5 hours."
- **Debugging WP:** "Here is the template file, the error/screenshot, and what I expected.
  Fix it and explain the change in one sentence." (Always paste the actual file.)
- **Design merge:** see Weeks 3-5.
- **Bulk content:** "Generate a WP-CLI script / CSV import to [task] using data/projects.json.
  I will run it on staging via SiteGround's WP-CLI in Site Tools."
- **Security review (before launch):** "Review fnpw2026 theme and fnpw-content plugin for
  escaping (esc_html/esc_url/wp_kses), nonces, and unsanitised input. List and fix issues."

## 5. Phase 2 backlog (after launch, not before)
- Donations on-site: GiveWP + Fee Recovery, one appeal first, recurring donors last;
  check whether Raisely runs on FNPW's own Stripe account before planning migration.
- Threatened Species Spotlight hub; blog category templates; Reports archive as CPT.
- Google Ad Grants application (US$10k/month free search ads for eligible charities).
- Retire Elementor once no live pages depend on it; drop Yoast Premium if not renewed.
- Delete the old fnpw theme after a stable month. Keep the drufloe plugin deactivated
  for a month before deleting.
- Handover: walk your colleague through this file + one publish + one deploy.
