<?php
/**
 * Title: Site header
 * Slug: fnpw-2026/site-header
 * Categories: fnpw-site
 * Inserter: no
 * Description: Skip link, Acknowledgement of Country strip and the main header, from partials/header.html.
 *
 * GENERATED from the static partial by the build script. The markup, classes and
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
    <a href="<?php echo esc_url( fnpw_url( 'about' ) ); ?>" class="<?php echo fnpw_nav_class( 'about' ); ?>">About</a>
    <div class="ng">
      <button aria-expanded="false" aria-controls="dd-projects">Projects <span class="ar">▾</span></button>
      <div class="dd" id="dd-projects">
        <a href="<?php echo esc_url( fnpw_url( 'projects' ) ); ?>" class="<?php echo fnpw_nav_class( 'projects' ); ?>">All Projects</a>
        <a href="<?php echo esc_url( fnpw_url( 'growing-national-parks' ) ); ?>" class="<?php echo fnpw_nav_class( 'growing-national-parks' ); ?>">Growing National Parks</a>
        <a href="<?php echo esc_url( fnpw_url( 'saving-species' ) ); ?>" class="<?php echo fnpw_nav_class( 'saving-species' ); ?>">Saving Species</a>
        <a href="<?php echo esc_url( fnpw_url( 'healing-the-land' ) ); ?>" class="<?php echo fnpw_nav_class( 'healing-the-land' ); ?>">Healing the Land</a>
      </div>
    </div>
    <div class="ng">
      <button aria-expanded="false" aria-controls="dd-partner">Partner With Us <span class="ar">▾</span></button>
      <div class="dd" id="dd-partner">
        <a href="<?php echo esc_url( fnpw_url( 'partner-invest' ) ); ?>" class="<?php echo fnpw_nav_class( 'partner-invest' ); ?>">Ways to Partner</a>
        <a href="<?php echo esc_url( fnpw_url( 'government-partnerships' ) ); ?>" class="<?php echo fnpw_nav_class( 'government-partnerships' ); ?>">Government Partnerships</a>
        <a href="<?php echo esc_url( fnpw_url( 'partner' ) ); ?>" class="<?php echo fnpw_nav_class( 'partner' ); ?>">Corporate Partnerships</a>
      </div>
    </div>
    <div class="ng">
      <button aria-expanded="false" aria-controls="dd-impact">Impact <span class="ar">▾</span></button>
      <div class="dd" id="dd-impact">
        <a href="<?php echo esc_url( fnpw_url( 'our-impact' ) ); ?>" class="<?php echo fnpw_nav_class( 'our-impact' ); ?>">Our Impact</a>
        <a href="<?php echo esc_url( fnpw_url( 'reports' ) ); ?>" class="<?php echo fnpw_nav_class( 'reports' ); ?>">Impact Reports</a>
      </div>
    </div>
    <div class="ng">
      <button aria-expanded="false" aria-controls="dd-involved">Get Involved <span class="ar">▾</span></button>
      <div class="dd" id="dd-involved">
        <a href="<?php echo esc_url( fnpw_url( 'ways-you-can-get-involved' ) ); ?>" class="<?php echo fnpw_nav_class( 'ways-you-can-get-involved' ); ?>">Ways to Get Involved</a>
        <a href="<?php echo esc_url( fnpw_url( 'volunteer' ) ); ?>" class="<?php echo fnpw_nav_class( 'volunteer' ); ?>">Corporate Volunteering</a>
        <a href="<?php echo esc_url( fnpw_url( 'workplace-giving' ) ); ?>" class="<?php echo fnpw_nav_class( 'workplace-giving' ); ?>">Workplace Giving</a>
        <a href="<?php echo esc_url( fnpw_url( 'fundraising-with-fnpw' ) ); ?>" class="<?php echo fnpw_nav_class( 'fundraising-with-fnpw' ); ?>">Fundraising</a>
        <a href="<?php echo esc_url( fnpw_url( 'bequests' ) ); ?>" class="<?php echo fnpw_nav_class( 'bequests' ); ?>">Gifts in Wills</a>
        <a href="<?php echo esc_url( fnpw_url( 'donate-land' ) ); ?>" class="<?php echo fnpw_nav_class( 'donate-land' ); ?>">Donate Land</a>
      </div>
    </div>
    <div class="ng">
      <button aria-expanded="false" aria-controls="dd-stories">Stories <span class="ar">▾</span></button>
      <div class="dd" id="dd-stories">
        <a href="<?php echo esc_url( fnpw_url( 'articles' ) ); ?>" class="<?php echo fnpw_nav_class( 'articles' ); ?>">Articles</a>
      </div>
    </div>
    <a href="<?php echo esc_url( fnpw_url( 'contact' ) ); ?>" class="<?php echo fnpw_nav_class( 'contact' ); ?>">Contact Us</a>
    <a href="<?php echo esc_url( fnpw_url( 'search' ) ); ?>" class="nav-srch" aria-label="Search the site"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4.2-4.2"/></svg><span>Search</span></a>
    <a href="https://bush.fnpw.org.au" class="btn btn-don">Donate</a>
  </nav>
  <div class="nav-bd" id="nav-bd" hidden></div>
</div></div>
</header>
<!-- /wp:html -->
