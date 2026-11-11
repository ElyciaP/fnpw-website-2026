<?php
/**
 * Title: Site header
 * Slug: fnpw-2026/site-header
 * Categories: fnpw-site
 * Inserter: no
 * Description: Skip link, Acknowledgement of Country strip and the main header, from partials/header.html.
 *
 * GENERATED from the static partial by the build script, except the menu links,
 * which come from Appearance > Menus (inc/menu.php) and fall back to the designed menu. The markup, classes and
 * link set match the static build exactly because global.css and main.js depend on them
 * (mobile drawer, dropdowns, focus handling). Links are built with home_url().
 *
 * @package fnpw-2026
 */

?>
<!-- wp:html -->
<a class="skip" href="#main">Skip to content</a>
<div class="ack" role="region" aria-label="Acknowledgement of Country">We acknowledge the Traditional Custodians of Country throughout Australia. <span class="ack-more">We pay our respects to Elders past and present.</span></div>
<header class="hdr" id="hdr">
<div class="cw"><div class="hdr-in">
  <a href="<?php echo esc_url( fnpw_url( 'index' ) ); ?>" class="logo"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/img/fnpw-logo.png' ) ); ?>" alt="Foundation for National Parks &amp; Wildlife" style="height:42px;width:auto;display:block"></a>
  <a href="<?php echo esc_url( fnpw_url( 'search' ) ); ?>" class="m-srch" aria-label="Search the site"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4.2-4.2"/></svg></a>
  <button class="mt" id="mt" aria-label="Menu" aria-controls="mn" aria-expanded="false"><span></span><span></span><span></span></button>
  <nav class="nav" id="mn" aria-label="Main">
<?php echo fnpw_primary_nav_items(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped in inc/menu.php. Edit under Appearance > Menus. ?>
    <a href="<?php echo esc_url( fnpw_url( 'search' ) ); ?>" class="nav-srch" aria-label="Search the site"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4.2-4.2"/></svg><span>Search</span></a>
    <a href="https://bush.fnpw.org.au" class="btn btn-don">Donate</a>
  </nav>
  <div class="nav-bd" id="nav-bd" hidden></div>
</div></div>
</header>
<!-- /wp:html -->
