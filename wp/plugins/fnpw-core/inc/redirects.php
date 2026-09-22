<?php
/**
 * Permanent redirects for renamed or merged pages.
 *
 * The map lives in redirects.json at the plugin root, one "old path": "new path"
 * pair per line, so it can be reviewed (by Reef, per R8) without reading PHP.
 * Only paths that would otherwise 404 are redirected, so a real page is never
 * hidden by a stale entry.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function fnpw_redirect_map() {
	static $map = null;
	if ( null === $map ) {
		$file = dirname( __DIR__ ) . '/redirects.json';
		$map  = file_exists( $file ) ? (array) json_decode( (string) file_get_contents( $file ), true ) : array();
	}
	return $map;
}

function fnpw_apply_redirects() {
	if ( ! is_404() ) {
		return;
	}
	$path = trailingslashit( (string) wp_parse_url( $_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH ) );
	$map  = fnpw_redirect_map();
	if ( isset( $map[ $path ] ) ) {
		wp_safe_redirect( home_url( $map[ $path ] ), 301, 'FNPW Core' );
		exit;
	}
}
add_action( 'template_redirect', 'fnpw_apply_redirects', 1 );
