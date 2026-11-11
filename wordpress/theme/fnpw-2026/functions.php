<?php
/**
 * FNPW 2026 block theme.
 *
 * Deliberately thin. assets/css/global.css is the design layer, copied unchanged from
 * the static build; theme.json mirrors its tokens for the editor; converted content keeps
 * the static class names. Content types and tracking live in the FNPW Core plugin.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_THEME_VERSION', '0.3.0' );

require get_template_directory() . '/inc/urls.php';
require get_template_directory() . '/inc/menu.php';
require get_template_directory() . '/inc/head.php';
require get_template_directory() . '/inc/assets.php';
require get_template_directory() . '/inc/page-assets.php';
require get_template_directory() . '/inc/blocks.php';

/**
 * Theme supports.
 */
function fnpw_setup() {
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'title-tag' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'post-thumbnails' );
	remove_theme_support( 'core-block-patterns' );

	// The design layer in the editor, then the compatibility layer on top of it.
	add_editor_style(
		array(
			'assets/css/global.css',
			'assets/css/article.css',
			'assets/css/patterns.css',
			'assets/css/wp-compat.css',
		)
	);
}
add_action( 'after_setup_theme', 'fnpw_setup' );

/**
 * Pattern categories.
 */
function fnpw_pattern_categories() {
	register_block_pattern_category( 'fnpw-cta', array( 'label' => __( 'FNPW calls to action', 'fnpw-2026' ) ) );
	register_block_pattern_category( 'fnpw-site', array( 'label' => __( 'FNPW site furniture', 'fnpw-2026' ) ) );
}
add_action( 'init', 'fnpw_pattern_categories' );

/**
 * The static header carries its own skip link (.skip, first element in the body), so the
 * one WordPress adds to block themes would be a duplicate.
 */
remove_action( 'wp_footer', 'the_block_template_skip_link' );
remove_action( 'wp_enqueue_scripts', 'wp_enqueue_block_template_skip_link' );

/**
 * Converted content carries the static build's own sizes attributes. Leave them as
 * written: WordPress would otherwise prefix "auto" and add a contain-intrinsic-size
 * rule that changes how not-yet-loaded images are boxed.
 */
add_filter( 'wp_img_tag_add_auto_sizes', '__return_false' );
