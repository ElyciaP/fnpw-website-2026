<?php
/**
 * No email leaves the site while the importer is working.
 *
 * Updating or restoring a post can make other plugins send notifications (for
 * example a "your story has been published" email to the person who submitted
 * it). Every importer request blocks outgoing email in three ways, so it holds
 * whichever mail plugin is active:
 *   1. pre_wp_mail, which WordPress's own wp_mail() obeys;
 *   2. post_smtp_do_send_email, for Post SMTP's replacement wp_mail();
 *   3. the wp_mail filter, which removes every recipient as a last resort.
 *
 * @package fnpw-migrate
 */

defined( 'ABSPATH' ) || exit;

/**
 * Switch the block on for the rest of this request.
 */
function fnpw_migrate_block_mail() {
	static $on = false;
	if ( $on ) {
		return;
	}
	$on = true;
	add_filter( 'pre_wp_mail', 'fnpw_migrate_mail_stop', 1, 2 );
	add_filter( 'post_smtp_do_send_email', '__return_false', 1 );
	add_filter( 'wp_mail', 'fnpw_migrate_mail_strip', PHP_INT_MAX );
	add_action( 'shutdown', 'fnpw_migrate_mail_tally' );
}

/**
 * Note one blocked email.
 *
 * @param array $atts wp_mail arguments.
 */
function fnpw_migrate_mail_note( $atts ) {
	$GLOBALS['fnpw_migrate_mail_blocked'][] = isset( $atts['subject'] ) ? (string) $atts['subject'] : '';
}

function fnpw_migrate_mail_stop( $return, $atts ) {
	// The wp_mail filter below runs first and has already counted this email
	// when it emptied the recipient, so only count it here if that did not happen.
	if ( ! empty( $atts['to'] ) ) {
		fnpw_migrate_mail_note( (array) $atts );
	}
	return true;
}

function fnpw_migrate_mail_strip( $atts ) {
	if ( is_array( $atts ) ) {
		if ( ! empty( $atts['to'] ) ) {
			fnpw_migrate_mail_note( $atts );
		}
		$atts['to']      = '';
		$atts['headers'] = '';
	}
	return $atts;
}

/**
 * How many emails this request blocked.
 *
 * @return int
 */
function fnpw_migrate_mail_blocked_now() {
	return empty( $GLOBALS['fnpw_migrate_mail_blocked'] ) ? 0 : count( $GLOBALS['fnpw_migrate_mail_blocked'] );
}

function fnpw_migrate_mail_tally() {
	$n = fnpw_migrate_mail_blocked_now();
	if ( $n ) {
		update_option( 'fnpw_migrate_mail_blocked_total', (int) get_option( 'fnpw_migrate_mail_blocked_total', 0 ) + $n, false );
	}
}

/**
 * Block email on every importer request: the batch calls and the form posts.
 */
add_action(
	'plugins_loaded',
	function () {
		$action = isset( $_REQUEST['action'] ) ? sanitize_key( wp_unslash( $_REQUEST['action'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification -- only switches email off.
		if ( 'fnpw_migrate_batch' === $action || 'fnpw_migrate' === $action ) {
			fnpw_migrate_block_mail();
		}
	},
	0
);
