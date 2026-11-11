<?php
/**
 * Action log: one row per thing the importer did or would do, in its own table.
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function fnpw_migrate_log_table() {
	global $wpdb;
	return $wpdb->prefix . 'fnpw_migrate_log';
}

function fnpw_migrate_log_install() {
	global $wpdb;
	require_once ABSPATH . 'wp-admin/includes/upgrade.php';
	$table   = fnpw_migrate_log_table();
	$charset = $wpdb->get_charset_collate();
	dbDelta(
		"CREATE TABLE {$table} (
			id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
			logged datetime NOT NULL,
			run varchar(40) NOT NULL DEFAULT '',
			mode varchar(12) NOT NULL DEFAULT '',
			item_key varchar(191) NOT NULL DEFAULT '',
			action varchar(24) NOT NULL DEFAULT '',
			post_id bigint(20) unsigned NOT NULL DEFAULT 0,
			message text NOT NULL,
			PRIMARY KEY  (id),
			KEY run (run)
		) {$charset};"
	);
	update_option( 'fnpw_migrate_db_version', '1', false );
}

function fnpw_migrate_log_ready() {
	if ( '1' !== get_option( 'fnpw_migrate_db_version' ) ) {
		fnpw_migrate_log_install();
	}
}

/**
 * @param string $run     Run id.
 * @param string $mode    dry | apply | restore.
 * @param string $key     Item key or media URL.
 * @param string $action  create | update | skip | error | media-reuse | media-sideload | ...
 * @param int    $post_id Post or attachment ID, 0 when none.
 * @param string $message Reason or detail.
 */
function fnpw_migrate_log( $run, $mode, $key, $action, $post_id, $message ) {
	global $wpdb;
	fnpw_migrate_log_ready();
	$wpdb->insert( // phpcs:ignore WordPress.DB.DirectDatabaseQuery
		fnpw_migrate_log_table(),
		array(
			'logged'   => current_time( 'mysql', true ),
			'run'      => substr( (string) $run, 0, 40 ),
			'mode'     => substr( (string) $mode, 0, 12 ),
			'item_key' => substr( (string) $key, 0, 191 ),
			'action'   => substr( (string) $action, 0, 24 ),
			'post_id'  => (int) $post_id,
			'message'  => (string) $message,
		),
		array( '%s', '%s', '%s', '%s', '%s', '%d', '%s' )
	);
}

/**
 * Send the whole log as a CSV download.
 */
function fnpw_migrate_log_csv() {
	global $wpdb;
	fnpw_migrate_log_ready();
	$table = fnpw_migrate_log_table();
	nocache_headers();
	header( 'Content-Type: text/csv; charset=utf-8' );
	header( 'Content-Disposition: attachment; filename="fnpw-import-log-' . gmdate( 'Ymd-His' ) . '.csv"' );
	$out = fopen( 'php://output', 'w' );
	fputcsv( $out, array( 'id', 'time_utc', 'run', 'mode', 'item', 'action', 'post_id', 'message' ), ',', '"', '\\' );
	$last = 0;
	do {
		$rows = $wpdb->get_results( $wpdb->prepare( "SELECT id, logged, run, mode, item_key, action, post_id, message FROM {$table} WHERE id > %d ORDER BY id ASC LIMIT 1000", $last ), ARRAY_N ); // phpcs:ignore WordPress.DB
		foreach ( $rows as $row ) {
			// Guard against spreadsheet formula injection.
			foreach ( $row as $i => $cell ) {
				if ( is_string( $cell ) && '' !== $cell && in_array( $cell[0], array( '=', '+', '-', '@' ), true ) ) {
					$row[ $i ] = "'" . $cell;
				}
			}
			fputcsv( $out, $row, ',', '"', '\\' );
			$last = (int) $row[0];
		}
	} while ( $rows );
	fclose( $out ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_system_operations_fclose
}
