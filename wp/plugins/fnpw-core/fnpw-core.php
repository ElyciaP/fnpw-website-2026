<?php
/**
 * Plugin Name:       FNPW Core
 * Description:       Content model for the Foundation for National Parks & Wildlife: the Project and Report content types, their taxonomies and fields. Lives in a plugin, not the theme, so the content survives any future theme change. This is the direct answer to the lock-in finding in the technical audit.
 * Version:           0.1.0
 * Requires at least: 6.6
 * Requires PHP:      8.1
 * Author:            Foundation for National Parks & Wildlife
 * License:           GPL-2.0-or-later
 * Text Domain:       fnpw-core
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_CORE_VERSION', '0.1.0' );

require_once __DIR__ . '/inc/post-types.php';
require_once __DIR__ . '/inc/taxonomies.php';
require_once __DIR__ . '/inc/fields.php';
require_once __DIR__ . '/inc/redirects.php';

/**
 * Flush rewrite rules on activation and deactivation only.
 *
 * Never on init. Flushing on every load is a common and expensive mistake.
 */
function fnpw_core_activate() {
	fnpw_register_post_types();
	fnpw_register_taxonomies();
	flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'fnpw_core_activate' );

function fnpw_core_deactivate() {
	flush_rewrite_rules();
}
register_deactivation_hook( __FILE__, 'fnpw_core_deactivate' );
