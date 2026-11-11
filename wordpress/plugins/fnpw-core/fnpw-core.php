<?php
/**
 * Plugin Name:       FNPW Core
 * Description:       Site functionality that must outlive any theme: block-editor support for the existing project, grant and donation content types, analytics and tracking tags, the project map block and the extra project fields.
 * Version:           0.2.0
 * Requires at least: 6.6
 * Requires PHP:      8.1
 * Author:            Foundation for National Parks & Wildlife
 * License:           GPL-2.0-or-later
 * Text Domain:       fnpw-core
 *
 * This plugin does NOT register post types or taxonomies. On the live site those come
 * from "Template Required Plugins" (project, grant, donation and their taxonomies),
 * which stays active. FNPW Core only adjusts their arguments, so it is harmless when
 * that plugin is switched off.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_CORE_VERSION', '0.2.0' );
define( 'FNPW_CORE_FILE', __FILE__ );
define( 'FNPW_CORE_DIR', plugin_dir_path( __FILE__ ) );
define( 'FNPW_CORE_URL', plugin_dir_url( __FILE__ ) );

require FNPW_CORE_DIR . 'inc/tracking.php';
require FNPW_CORE_DIR . 'inc/content-types.php';
require FNPW_CORE_DIR . 'inc/acf.php';
require FNPW_CORE_DIR . 'inc/project-map.php';
