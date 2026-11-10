<?php
/**
 * Title: Page not found
 * Slug: fnpw-2026/not-found
 * Categories: fnpw-site
 * Inserter: no
 * Description: 404 page. Markup and copy from 404.html.
 *
 * @package fnpw-2026
 */

?>
<!-- wp:html -->
<section class="nf-hero">
  <div class="cw rv">
    <nav aria-label="Breadcrumb" class="breadcrumb"><a href="<?php echo esc_url( fnpw_url( 'index' ) ); ?>">Home</a><span>/</span>Page not found</nav>
    <span class="ey">Error 404</span>
    <h1>That page has wandered off.</h1>
    <p class="lede">We could not find the page you were after. It may have moved when we rebuilt the site, or the link may be out of date.</p>
  </div>
</section>
<section class="sec">
  <div class="cw rv">
    <div class="nf-links">
      <a class="btn-p" href="<?php echo esc_url( fnpw_url( 'index' ) ); ?>">Back to the home page</a>
      <a class="btn-o" href="<?php echo esc_url( fnpw_url( 'search' ) ); ?>">Search the site</a>
      <a class="btn-o" href="<?php echo esc_url( fnpw_url( 'projects' ) ); ?>">Browse our projects</a>
      <a class="btn-o" href="<?php echo esc_url( fnpw_url( 'articles' ) ); ?>">Read our stories</a>
    </div>
  </div>
</section>
<!-- /wp:html -->
