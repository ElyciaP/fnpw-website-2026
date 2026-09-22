# FNPW WordPress conversion

The static build at the repo root is the specification. This folder is the deliverable.

```
wp/
  themes/fnpw-2026/     the block theme
  plugins/fnpw-core/    Project and Report content types, taxonomies, fields
  tools/                import and setup scripts
```

Nothing at the repo root moved, so GitHub Pages and the Netlify prototype links the board has still work.

## Why the content model sits in a plugin

The audit's finding was that structure is locked inside a theme. If the Project
content type were registered in the theme, the next theme change would orphan
all 84 project pages and recreate the same problem. `fnpw-core` keeps the
content model independent of presentation. The theme can be replaced at any
time and the content stays addressable.

## URL structure, resolved

Every live project already sits at `/project/<slug>/`. The Project content type
uses exactly that rewrite slug, so all 84 project URLs carry across unchanged
and contribute nothing to the redirect map. This closes the open item in
Appendix A of the delivery plan.

## The working loop

WordPress cannot run on GitHub Pages, so the repo stays the source of truth and
the editing loop runs against a local WordPress.

1. Install [Local](https://localwp.com). Create a site, PHP 8.1 or above.
2. Symlink or copy `wp/themes/fnpw-2026` into `wp-content/themes/` and
   `wp/plugins/fnpw-core` into `wp-content/plugins/`. A symlink means you edit
   in the repo and see it immediately:

   ```bash
   ln -s "$PWD/wp/themes/fnpw-2026"  ~/Local\ Sites/fnpw/app/public/wp-content/themes/fnpw-2026
   ln -s "$PWD/wp/plugins/fnpw-core" ~/Local\ Sites/fnpw/app/public/wp-content/plugins/fnpw-core
   ```

3. Activate FNPW Core, then the FNPW 2026 theme.
4. Import the projects. Your static project pages are the source, so
   whatever is on the page is what comes across, rewrites included:

   ```bash
   bash wp/tools/sync.sh
   wp eval-file "$PWD/wp/tools/import-projects.php" "$PWD" --dry-run
   wp eval-file "$PWD/wp/tools/import-projects.php" "$PWD"
   ```

   Re-run both any time you edit a project page. Nothing duplicates.

5. Self-host the fonts once, which the theme then picks up automatically:

   ```bash
   bash wp/tools/fetch-fonts.sh
   ```

6. Commit. The repo is the record of the build.

## Getting a real copy of the live site

Build against real content, not an empty install. A blank WordPress will look
perfect and then break on contact with ten years of posts, media and plugins.

From the live WP admin, export the database and `wp-content` with a migration
plugin, leave the uploads folder out because the media library is large and the
theme work does not need it, then import into Local. Point at production image
URLs while building.

## Deploying to the live install

The theme is a folder in `wp-content/themes/`. Uploading it changes nothing
until it is activated, so deploying early is safe.

- **FTP:** upload `fnpw-2026` to `wp-content/themes/` with FileZilla.
- **Admin:** zip the theme folder and use Appearance, Themes, Add New, Upload.

Do not activate on production during the build. To see the new theme on the
real site with real content while visitors keep seeing the current one, install
[Theme Switcha](https://wordpress.org/plugins/theme-switcha/) and set it to
admins only. That gives a private preview on production without a staging
environment and without waiting on IT.

Proper staging is still needed for the cutover rehearsal, because it is the
only way to surface hosting constraints and plugin behaviour before launch.
That is a Site Tools task for Lucian, and the request should go in early rather
than in the launch week.

## Launch

Per section 4.4 of the delivery plan, the switch is a theme activation on the
live install. The database is never overwritten, so nothing published during
the build is lost, and the previous theme stays installed for single-action
rollback.

## Keeping it up to date

`bash wp/tools/sync.sh` copies global.css and main.js into the theme and
rebuilds the project bundle from the static pages. Run it after any design or
content change, then commit.

## Still to do in Phase 2

- The interactive project map. The R5 fallback, a filtered grid, is already in
  `archive-project.html` and works without JavaScript.
- HubSpot form embeds, confirmed against real form IDs.
- Page templates for the priority pages, converted from the static build.
- The Reports library, 21 publications, into the Report content type.
- Resized project imagery, replacing the multi-megabyte WordPress originals.
