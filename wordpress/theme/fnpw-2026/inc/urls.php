<?php
/**
 * Internal links. The static build links by file name (about.html); in WordPress each
 * of those files has the URL in the wp_url column of wordpress/migration/page-map.csv.
 * inc/url-map.php is generated from that file.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * The static-file => WordPress-path map.
 *
 * @return array<string,string>
 */
function fnpw_url_map() {
	static $map = null;
	if ( null === $map ) {
		$map = (array) apply_filters( 'fnpw_url_map', require get_template_directory() . '/inc/url-map.php' );
	}
	return $map;
}

/**
 * WordPress URL for a static page, by its file name without ".html".
 *
 * @param string $key Static file name without extension, e.g. "about".
 * @return string Absolute URL. Unknown keys fall back to /{key}/.
 */
function fnpw_url( $key ) {
	$map  = fnpw_url_map();
	$path = isset( $map[ $key ] ) ? $map[ $key ] : '/' . $key . '/';
	return home_url( $path );
}

/**
 * Which main-nav item is current, as a static file key. Mirrors tools/sync.py:
 * project pages and the three pillar pages light up "All Projects", the city
 * volunteering pages light up "Corporate Volunteering", and so on.
 *
 * @return string Empty when nothing is current.
 */
function fnpw_active_nav_key() {
	static $key = null;
	if ( null !== $key ) {
		return $key;
	}
	$key = '';

	if ( is_singular( 'project' ) || is_post_type_archive( 'project' ) || is_tax( array( 'project_state', 'project_focus_area', 'project_year' ) ) ) {
		$key = 'projects';
	} elseif ( is_home() ) {
		$key = 'articles';
	} elseif ( is_page() ) {
		$path  = trailingslashit( (string) wp_parse_url( get_permalink( get_queried_object_id() ), PHP_URL_PATH ) );
		$home  = trailingslashit( (string) wp_parse_url( home_url( '/' ), PHP_URL_PATH ) );
		$path  = '/' . ltrim( substr( $path, strlen( $home ) ), '/' );
		$file  = array_search( $path, fnpw_url_map(), true );
		$nav   = array( 'about', 'projects', 'contact', 'partner', 'partner-invest', 'government-partnerships', 'volunteer', 'bequests', 'donate-land', 'our-impact', 'reports', 'articles' );
		$alias = array(
			'growing-national-parks'         => 'projects',
			'saving-species'                 => 'projects',
			'healing-the-land'               => 'projects',
			'bequests-professional-advisers' => 'bequests',
		);
		if ( false !== $file ) {
			if ( isset( $alias[ $file ] ) ) {
				$key = $alias[ $file ];
			} elseif ( 0 === strpos( $file, 'corporate-volunteering-' ) ) {
				$key = 'volunteer';
			} elseif ( in_array( $file, $nav, true ) ) {
				$key = $file;
			}
		}
	}

	$key = (string) apply_filters( 'fnpw_active_nav_key', $key );
	return $key;
}

/**
 * Class attribute value for a main-nav link: " on" when current, else empty,
 * exactly as the static build writes it.
 *
 * @param string $key Static file key of the link.
 * @return string
 */
function fnpw_nav_class( $key ) {
	return ( did_action( 'wp' ) && fnpw_active_nav_key() === $key ) ? ' on' : '';
}
