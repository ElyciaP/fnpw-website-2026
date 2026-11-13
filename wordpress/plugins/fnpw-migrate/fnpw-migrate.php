<?php
/**
 * Plugin Name:       FNPW Import
 * Description:       One-off importer for the 2026 site rebuild. Reads an import package made by wordpress/migration/convert.py and creates or updates pages, posts and projects. Never deletes anything; keeps the previous content of every post it overwrites so it can be restored.
 * Version:           1.3.1
 * Requires at least: 6.6
 * Requires PHP:      8.1
 * Author:            Foundation for National Parks & Wildlife
 * License:           GPL-2.0-or-later
 * Text Domain:       fnpw-migrate
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_MIGRATE_VERSION', '1.3.1' );
define( 'FNPW_MIGRATE_DIR', plugin_dir_path( __FILE__ ) );
define( 'FNPW_MIGRATE_URL', plugin_dir_url( __FILE__ ) );

require FNPW_MIGRATE_DIR . 'inc/mail.php';
require FNPW_MIGRATE_DIR . 'inc/log.php';
require FNPW_MIGRATE_DIR . 'inc/package.php';
require FNPW_MIGRATE_DIR . 'inc/media.php';
require FNPW_MIGRATE_DIR . 'inc/importer.php';

if ( is_admin() ) {
	require FNPW_MIGRATE_DIR . 'inc/admin.php';
}

register_activation_hook( __FILE__, 'fnpw_migrate_log_install' );
