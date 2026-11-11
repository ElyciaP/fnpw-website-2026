<?php
/**
 * Front-end styles and scripts.
 *
 * global.css is the design layer and is never edited here. Anything WordPress needs
 * that the static build did not goes in wp-compat.css. The other stylesheets are the
 * page-level <style> blocks of the static templates, lifted unchanged.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Enqueue one theme stylesheet, versioned by file time so a deploy busts the cache.
 *
 * @param string   $handle Handle.
 * @param string   $file   Path relative to the theme root.
 * @param string[] $deps   Dependencies.
 */
function fnpw_style( $handle, $file, $deps = array( 'fnpw-global' ) ) {
	$path = get_theme_file_path( $file );
	if ( file_exists( $path ) ) {
		wp_enqueue_style( $handle, get_theme_file_uri( $file ), $deps, (string) filemtime( $path ) );
	}
}

/**
 * Enqueue one theme script in the footer, after main.js.
 *
 * @param string $handle Handle.
 * @param string $file   Path relative to the theme root.
 */
function fnpw_script( $handle, $file ) {
	$path = get_theme_file_path( $file );
	if ( file_exists( $path ) ) {
		wp_enqueue_script( $handle, get_theme_file_uri( $file ), array( 'fnpw-main' ), (string) filemtime( $path ), true );
	}
}

/**
 * Raw content of the page being shown, for cheap "does this page use component X" checks.
 *
 * @return string
 */
function fnpw_current_content() {
	if ( ! is_singular() ) {
		return '';
	}
	$post = get_queried_object();
	return ( $post instanceof WP_Post ) ? (string) $post->post_content : '';
}

function fnpw_assets() {
	// After WordPress's own global styles, so the design layer has the last word.
	$deps = wp_style_is( 'global-styles', 'registered' ) ? array( 'global-styles' ) : array();
	fnpw_style( 'fnpw-global', 'assets/css/global.css', $deps );
	fnpw_style( 'fnpw-patterns', 'assets/css/patterns.css' );
	fnpw_style( 'fnpw-wp-compat', 'assets/css/wp-compat.css' );

	$is_article = is_singular( 'post' ) || is_page_template( 'page-article' );
	if ( $is_article ) {
		fnpw_style( 'fnpw-article', 'assets/css/article.css' );
	}
	if ( is_home() || is_category() || is_tag() || is_date() || is_author() ) {
		fnpw_style( 'fnpw-stories', 'assets/css/stories.css' );
	}
	if ( is_search() ) {
		fnpw_style( 'fnpw-search', 'assets/css/search.css' );
	}
	if ( is_404() ) {
		fnpw_style( 'fnpw-404', 'assets/css/404.css' );
	}

	// main.js loads everywhere: mobile drawer, header shadow, reveal, counters, dropdowns.
	$main = get_theme_file_path( 'assets/js/main.js' );
	wp_enqueue_script( 'fnpw-main', get_theme_file_uri( 'assets/js/main.js' ), array(), (string) filemtime( $main ), true );

	// Feature scripts load only where their markup is on the page.
	if ( $is_article ) {
		fnpw_script( 'fnpw-article-progress', 'assets/js/article-progress.js' );
	}
	$content = fnpw_current_content();
	if ( false !== strpos( $content, 'id="galTrack"' ) ) {
		fnpw_script( 'fnpw-gallery', 'assets/js/gallery.js' );
	}
	if ( false !== strpos( $content, 'id="volTrack"' ) ) {
		fnpw_script( 'fnpw-carousel', 'assets/js/carousel.js' );
	}
	// articles.js drives the client-side filter, sort and "more" button of the Stories
	// index (home template, block fnpw/stories-index) and of any page that carries the
	// static controls (id="asort").
	if ( is_home() || false !== strpos( $content, 'id="asort"' ) ) {
		fnpw_script( 'fnpw-articles', 'assets/js/articles.js' );
	}
	/*
	 * snap.js has no markup hook: the static build opts a page in by loading the script
	 * (about.html only). The converter sets the fnpw_snap post meta on that page.
	 */
	$snap_pages = (array) apply_filters( 'fnpw_snap_pages', array() );
	$snap       = ( $snap_pages && is_page( $snap_pages ) )
		|| ( is_singular() && get_post_meta( get_queried_object_id(), 'fnpw_snap', true ) );
	if ( $snap ) {
		fnpw_script( 'fnpw-snap', 'assets/js/snap.js' );
	}
}
add_action( 'wp_enqueue_scripts', 'fnpw_assets', 20 );
