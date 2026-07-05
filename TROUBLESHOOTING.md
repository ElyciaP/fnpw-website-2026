# FNPW Rebuild: What Can Go Wrong and How to Fix It

Companion to PLAYBOOK.md. Written for a non-developer. Read the Emergency Card now so
you know it exists; read the rest when something happens (or before each phase).

**The comforting truth first:** the way this project is set up, the live site is very hard
to break. All build work happens on a staging copy the public never sees. Donations run on
Raisely, outside WordPress entirely, so no theme work can touch payment processing. The old
theme stays installed, so the ultimate undo is Appearance > Themes > Activate old theme.
Almost everything below is "staging looks broken", which costs you a session, not a website.

---

## EMERGENCY CARD: the live site is down or broken right now

1. Don't panic-fix. Note what you did last (that is almost always the cause).
2. If wp-admin still loads: Appearance > Themes > activate the OLD fnpw theme. Site back.
3. If wp-admin won't load (white screen): log in to SiteGround > Site Tools > File Manager,
   go to `wp-content/themes/`, rename the new theme folder (e.g. `fnpw2026` →
   `fnpw2026-off`). WordPress instantly falls back. Same trick for a broken plugin:
   rename its folder in `wp-content/plugins/`.
4. Still broken: SiteGround Site Tools > Backups > restore the UpdraftPlus/SiteGround
   backup from before your change (you always made one, because Rule 3).
5. Then paste whatever error you saw into Claude with "the live site broke when I did X".

---

## 1. WordPress build phase (weeks 6-9)

### White screen after activating the theme or plugin (on staging)
- **Why:** a PHP syntax error, usually in functions.php. One missing semicolon does this.
- **Fix:** rename the theme folder via File Manager (see Emergency Card) to get admin back.
  Then in Site Tools > Statistics/Logs (or ask Claude how to enable WP_DEBUG_LOG), copy the
  exact error line and paste it to Claude with the file. It is always a one-line fix.
- **Prevent:** never edit code through wp-admin's Theme File Editor. Edit locally, upload
  the whole file. Test every upload on staging immediately.

### All the projects vanished from wp-admin
- **Why:** the post type isn't registered right now. Deactivating the old "Template Required
  Plugins" before the new fnpw-content plugin registers the same key does this. The content
  is NOT deleted; it is sitting safely in the database, invisible.
- **Fix:** reactivate the old plugin; everything reappears. Then have Claude compare the
  `register_post_type` key and args in both plugins until they match exactly.
- **Never** run anything that offers to "clean up orphaned posts" while they are invisible.

### Every project page is a 404 after activating the plugin/theme
- **Why:** WordPress hasn't refreshed its URL rules. Looks catastrophic, is nothing.
- **Fix:** Settings > Permalinks > click Save Changes (change nothing). Do it twice.

### ACF fields don't appear on the edit screen, or show but don't display on the page
- **Why (edit screen):** the field group's Location rule doesn't match the post type.
- **Why (front end):** the template asks for a different field name than the field's actual
  name, or `get_field()` is called before ACF loads.
- **Fix:** screenshot the field group settings + paste the template to Claude.

### The map shows no pins
- **Why:** projects have no lat/lng values yet, or the data isn't reaching the JS.
- **Fix:** add coordinates to 2 test projects first, view page source, search for the
  localized data array, paste what you find to Claude.

### Images broken after theme switch on staging
- **Fix:** usually wrong image size names; ask Claude. If thumbnails are missing sizes,
  install "Regenerate Thumbnails", run once, delete it.

## 2. The one real catastrophe to understand: the staging push

**SiteGround's "push staging to live" can copy the staging DATABASE over production.**
If people published news posts, edited pages, or received form entries on the live site
while you were building on staging, a full push erases those newer changes. This is the
single most expensive mistake available to you.

- **Safe path (use this):** do NOT full-push. Deploy manually: upload the theme zip and
  plugin zip to production, activate, import the acf-json, set menus, add redirects.
  Production database is never overwritten; nothing published is lost.
- **If you do push:** declare a content freeze (no publishing anywhere) from the moment
  you last refreshed staging until launch, and confirm SiteGround's push options: push
  files only if offered, or accept the freeze consciously.
- Either way: full backup downloaded to your computer first.

## 3. Working with Claude (the AI-shaped risks)

### The code Claude gives you doesn't work
- Paste back: the exact error text or a screenshot, the full file (not a fragment), and
  what you expected. Ask for "the smallest possible fix, explained in one sentence".
  Do not accept a rewrite of the whole file when debugging; small diffs are checkable.

### A session confidently "fixes" things and now more is broken
- Stop. `git status` / `git diff` shows what changed. `git checkout -- <file>` reverts a
  file; `git reset --hard` reverts everything uncommitted. This is why Rule 4 says commit
  after every good session: you can always step back to the last known-good state.
- Start a fresh session with the PLAYBOOK bootstrap prompt rather than arguing with a
  session that has gone down a bad path.

### You hit your usage limit mid-session
- Max limits reset every few hours. Commit what works, note where you stopped in a
  NOTES.md line, resume later. Never leave staging half-broken overnight without a note.

### Claude invents a WordPress function or plugin setting that doesn't exist
- If something errors as "undefined function", say exactly that; it will correct itself.
  For anything involving money, deletion, or the live database, ask: "is there a safer,
  more standard way to do this?" before running it.

## 4. Updates, plugins and the live site (ongoing)

### A plugin update breaks the live site
- **Fix:** File Manager > rename that plugin's folder > site returns > restore backup if
  needed. This is why updates happen in small batches with a check between, backup first,
  and Elementor-sized updates go to staging first.

### Locked out of wp-admin
- Security Optimizer or repeated failed logins can lock you out. Fix: SiteGround Site
  Tools can reset your WordPress password; or rename the security plugin's folder via
  File Manager, log in, rename it back.

### Forms stop sending email
- Post SMTP handles delivery; check its log first (it shows every send attempt).
  Test the contact form after any plugin update. Check spam folders before panicking.

### Staging isn't available on our SiteGround plan
- Staging needs GrowBig or higher. If the plan is StartUp: upgrade (small monthly cost,
  put it in the project budget) rather than building without staging. Do not build live.

## 5. Launch and after

### Rankings wobble after launch
- A small dip for 1-2 weeks is normal. What matters: Search Console shows no coverage
  errors, and Redirection's 404 log stays quiet. Add redirects for any real 404s that
  appear. Only consider rolling back for major, persistent loss, which the URL-preserving
  design makes very unlikely.

### Donate button goes to the wrong place / short links die
- Theme work cannot break Raisely itself. If a donate link 404s, it is just an href typo:
  fix the link. The `bit.fnpw.org.au` short links are a separate service; if they die,
  point buttons at the full Raisely URLs (they are in PLAYBOOK.md section 2).

### GTM/analytics silent after launch
- The new theme must output the GTM container (GTM-K2P27RG) in header and body. Verify
  with Google Tag Assistant. If missing, ask Claude to add the standard GTM snippets to
  header.php.

### Something looks wrong only on phones
- Screenshot it with the phone, tell Claude the device and browser. Never launch without
  the real-phone spot check on the checklist.

## 6. Human-shaped risks (honestly the most likely ones)

- **The debugging spiral eats your 1.5 hours.** Rule: if you are stuck on one problem for
  30 minutes, stop, capture the error and what you tried, end the session. A fresh session
  with a clean description solves in 10 minutes what a tired spiral doesn't in 60.
- **Scope creep.** Every "while I'm in here, what if we also..." delays launch. Write the
  idea in the Phase 2 backlog (PLAYBOOK section 5) and move on. Launching is the feature.
- **Content season collision.** October is planner-heavy for you. The gate in the plan is
  the fix: if it slips past 1 November, the answer is February, not rushed testing.
- **You are the only one who knows anything.** Mitigate now: share the staging URL and this
  repo location with one other person, and put the SiteGround, WordPress and Raisely
  logins in whatever password manager FNPW uses, not just your head.
- **The old theme or drufloe plugin gets deleted too early.** Keep both installed
  (deactivated is fine) for a full month after launch. They are your rollback.

---

*If a problem isn't in this file, describe it to Claude with: what you did, what you
expected, what happened instead, and the exact error text. That sentence structure gets
good answers.*
