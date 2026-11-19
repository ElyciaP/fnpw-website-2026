<?php
/**
 * Plugin Name: Site Credits
 * Description: Build attribution for fnpw.org.au.
 * Author: Elycia Paredes
 */

// HTML comment in the page source (View Source only)
add_action( 'wp_head', function () {
	echo "\n<!--\n";
	echo "  Foundation for National Parks & Wildlife | fnpw.org.au\n";
	echo "  Designed, developed and deployed by Elycia Paredes, Head of Content\n";
	echo "  Launched November 2026\n";
	echo "-->\n";
}, 1 );

// Message in the browser dev tools console (not visible on the page)
add_action( 'wp_footer', function () { ?>
<script>
console.log(
  '%cFoundation for National Parks & Wildlife%c\nDesigned, developed and deployed by Elycia Paredes, November 2026',
  'color:#0F7768;font-weight:700;font-size:14px',
  'color:inherit;font-size:12px'
);
</script>
<?php } );
