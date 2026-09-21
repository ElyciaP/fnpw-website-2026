<?php
/**
 * FNPW 2026 block theme.
 *
 * Deliberately thin. The design system lives in theme.json, components live in
 * patterns, and the Project and Report content types live in the fnpw-core
 * plugin so they survive any future theme change.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_THEME_VERSION', '0.1.0' );

/**
 * Theme supports.
 */
function fnpw_setup() {
	add_theme_support( 'wp-block-styles' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_editor_style( 'assets/css/global.css' );
	load_theme_textdomain( 'fnpw-2026', get_template_directory() . '/languages' );
}
add_action( 'after_setup_theme', 'fnpw_setup' );

/**
 * Front-end assets.
 *
 * global.css is the component layer ported from the static build. It is
 * versioned by file modification time so a deploy busts the cache without a
 * manual version bump.
 */
function fnpw_assets() {
	$dir = get_template_directory();
	$uri = get_template_directory_uri();

	wp_enqueue_style(
		'fnpw-global',
		$uri . '/assets/css/global.css',
		array(),
		(string) filemtime( $dir . '/assets/css/global.css' )
	);

	wp_enqueue_script(
		'fnpw-main',
		$uri . '/assets/js/main.js',
		array(),
		(string) filemtime( $dir . '/assets/js/main.js' ),
		true
	);
}
add_action( 'wp_enqueue_scripts', 'fnpw_assets' );

/**
 * Pattern categories, so the component library is browsable in the inserter.
 */
function fnpw_pattern_categories() {
	$categories = array(
		'fnpw-page'    => __( 'FNPW page sections', 'fnpw-2026' ),
		'fnpw-cta'     => __( 'FNPW calls to action', 'fnpw-2026' ),
		'fnpw-content' => __( 'FNPW content blocks', 'fnpw-2026' ),
	);

	foreach ( $categories as $slug => $label ) {
		register_block_pattern_category( $slug, array( 'label' => $label ) );
	}
}
add_action( 'init', 'fnpw_pattern_categories' );

/**
 * Remove the core pattern directory so the inserter shows FNPW patterns only.
 */
remove_theme_support( 'core-block-patterns' );

/**
 * Preload the two variable fonts actually used above the fold.
 */
function fnpw_preload_fonts() {
	if ( ! fnpw_fonts_are_self_hosted() ) {
		return;
	}

	$uri   = get_template_directory_uri() . '/assets/fonts/';
	$fonts = array( 'sora-variable.woff2', 'figtree-variable.woff2' );

	foreach ( $fonts as $font ) {
		if ( file_exists( get_template_directory() . '/assets/fonts/' . $font ) ) {
			printf(
				'<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n",
				esc_url( $uri . $font )
			);
		}
	}
}
add_action( 'wp_head', 'fnpw_preload_fonts', 1 );

/**
 * Font loading.
 *
 * Self-hosted variable fonts are preferred, because a third-party font request
 * is a measurable cost against Core Web Vitals. Until the woff2 files are in
 * assets/fonts/, fall back to Google Fonts so the theme never renders in a
 * system font. Run wp/tools/fetch-fonts.sh to self-host, then this falls away
 * on its own.
 */
function fnpw_fonts_are_self_hosted() {
	return file_exists( get_template_directory() . '/assets/fonts/sora-variable.woff2' )
		&& file_exists( get_template_directory() . '/assets/fonts/figtree-variable.woff2' );
}

function fnpw_google_fonts_fallback() {
	if ( fnpw_fonts_are_self_hosted() ) {
		return;
	}

	wp_enqueue_style(
		'fnpw-google-fonts',
		'https://fonts.googleapis.com/css2?family=Sora:wght@300..800&family=Figtree:wght@300..900&family=Caveat:wght@400..700&display=swap',
		array(),
		null
	);
}
add_action( 'wp_enqueue_scripts', 'fnpw_google_fonts_fallback' );

function fnpw_google_fonts_preconnect( $urls, $relation_type ) {
	if ( 'preconnect' === $relation_type && ! fnpw_fonts_are_self_hosted() ) {
		$urls[] = array( 'href' => 'https://fonts.gstatic.com', 'crossorigin' => 'anonymous' );
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'fnpw_google_fonts_preconnect', 10, 2 );
