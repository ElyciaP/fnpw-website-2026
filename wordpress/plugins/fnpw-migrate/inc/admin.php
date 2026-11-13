<?php
/**
 * Tools > FNPW import: upload, dry run, apply, restore and the log download.
 *
 * Every action checks the manage_options capability and a nonce. The run itself is
 * batched over admin-ajax: the package is uploaded once, stored in
 * uploads/fnpw-migrate/, and each request handles a few entries by index, so neither a
 * timeout nor max_input_vars is in play.
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const FNPW_MIGRATE_MEDIA_BATCH = 4;
const FNPW_MIGRATE_ITEM_BATCH  = 12;

function fnpw_migrate_menu() {
	add_management_page( 'FNPW import', 'FNPW import', 'manage_options', 'fnpw-migrate', 'fnpw_migrate_screen' );
}
add_action( 'admin_menu', 'fnpw_migrate_menu' );

function fnpw_migrate_can() {
	return current_user_can( 'manage_options' );
}

/**
 * Form posts: upload, restore, log download.
 */
function fnpw_migrate_handle_post() {
	if ( ! fnpw_migrate_can() ) {
		wp_die( esc_html__( 'You are not allowed to do that.', 'fnpw-migrate' ), 403 );
	}
	$do = isset( $_POST['fnpw_do'] ) ? sanitize_key( wp_unslash( $_POST['fnpw_do'] ) ) : '';
	check_admin_referer( 'fnpw_migrate_' . $do );
	$notice = '';
	$type   = 'success';

	if ( 'upload' === $do ) {
		$result = fnpw_migrate_store_upload( isset( $_FILES['package'] ) ? $_FILES['package'] : array() ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput -- checked in the function.
		if ( is_wp_error( $result ) ) {
			$notice = $result->get_error_message();
			$type   = 'error';
		} else {
			$notice = sprintf( 'Package stored: %d items, %d media entries.', $result['items'], $result['media'] );
			fnpw_migrate_log( 'upload-' . $result['hash'], 'upload', $result['name'], 'upload', 0, $notice );
		}
	} elseif ( 'mailtest' === $do ) {
		fnpw_migrate_block_mail();
		$user = wp_get_current_user();
		wp_mail( $user->user_email, 'FNPW import: email block test', 'If this email arrives, the importer is not blocking email. Do not run an import.' );
		$blocked = fnpw_migrate_mail_blocked_now();
		$notice  = $blocked ? 'Email block is working: the test email to ' . $user->user_email . ' was stopped. Check your inbox and the email log to confirm nothing arrived.' : 'The email block did NOT catch the test email. Do not run an import.';
		$type    = $blocked ? 'success' : 'error';
		fnpw_migrate_log( 'mailtest-' . gmdate( 'Ymd-His' ), 'mailtest', $user->user_email, $blocked ? 'mail-blocked' : 'error', 0, $notice );
	} elseif ( 'log' === $do ) {
		fnpw_migrate_log_csv();
		exit;
	} elseif ( 'restore' === $do ) {
		$post_id = isset( $_POST['post_id'] ) ? absint( $_POST['post_id'] ) : 0;
		$result  = fnpw_migrate_restore( $post_id );
		$run     = 'restore-' . gmdate( 'Ymd-His' );
		if ( is_wp_error( $result ) ) {
			$notice = $result->get_error_message();
			$type   = 'error';
			fnpw_migrate_log( $run, 'restore', 'post ' . $post_id, 'error', $post_id, $notice );
		} else {
			$notice = 'Previous content restored on "' . get_the_title( $post_id ) . '" (post ' . $post_id . ').';
			fnpw_migrate_log( $run, 'restore', 'post ' . $post_id, 'restore', $post_id, 'Previous content restored.' );
		}
	}
	set_transient( 'fnpw_migrate_notice_' . get_current_user_id(), array( $type, $notice ), 60 );
	wp_safe_redirect( admin_url( 'tools.php?page=fnpw-migrate' ) );
	exit;
}
add_action( 'admin_post_fnpw_migrate', 'fnpw_migrate_handle_post' );

/**
 * One batch of a run.
 *
 * POST: mode (dry|apply), phase (media|items|finish|restore), offset, run, fetch_base,
 * set_reading (1 only when the tick box was ticked).
 */
function fnpw_migrate_ajax() {
	if ( ! fnpw_migrate_can() ) {
		wp_send_json_error( array( 'message' => 'Not allowed.' ), 403 );
	}
	check_ajax_referer( 'fnpw_migrate_run', 'nonce' );

	$mode   = ( isset( $_POST['mode'] ) && 'apply' === $_POST['mode'] ) ? 'apply' : 'dry';
	$phase  = isset( $_POST['phase'] ) ? sanitize_key( wp_unslash( $_POST['phase'] ) ) : 'media';
	$offset = isset( $_POST['offset'] ) ? absint( $_POST['offset'] ) : 0;
	$run    = isset( $_POST['run'] ) ? preg_replace( '/[^a-z0-9-]/', '', strtolower( sanitize_text_field( wp_unslash( $_POST['run'] ) ) ) ) : '';
	$fetch  = isset( $_POST['fetch_base'] ) ? esc_url_raw( trim( wp_unslash( $_POST['fetch_base'] ) ) ) : ''; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	$apply  = 'apply' === $mode;
	if ( '' === $run ) {
		$run = ( 'restore' === $phase ? 'restore' : $mode ) . '-' . gmdate( 'Ymd-His' );
	}
	if ( $apply && ! current_user_can( 'unfiltered_html' ) ) {
		wp_send_json_error( array( 'message' => 'Your account may not save unfiltered HTML (scripts, iframes), which the imported pages need. Run the import as an administrator; on a multisite network, as a super admin.' ) );
	}

	@set_time_limit( 120 ); // phpcs:ignore WordPress.PHP.NoSilencedErrors, Squiz.PHP.DiscouragedFunctions
	wp_raise_memory_limit( 'admin' );

	// Restore-all runs through the same batching, without a package.
	if ( 'restore' === $phase ) {
		$created = fnpw_migrate_created();
		$ids     = array_merge( fnpw_migrate_restorable(), $created );
		$slice   = array_slice( $ids, $offset, FNPW_MIGRATE_ITEM_BATCH );
		$rows    = array();
		foreach ( $slice as $post_id ) {
			if ( in_array( $post_id, $created, true ) ) {
				// The import created this post, so there is nothing to put back: take it offline.
				$result = fnpw_migrate_unpublish( $post_id );
				$row    = array(
					'key'     => get_post_type( $post_id ) . ': ' . get_the_title( $post_id ),
					'action'  => is_wp_error( $result ) ? 'error' : 'restore',
					'post_id' => $post_id,
					'message' => is_wp_error( $result ) ? $result->get_error_message() : 'Created by the import: set to draft.',
				);
				fnpw_migrate_log( $run, 'restore', $row['key'], $row['action'], $post_id, $row['message'] );
				$rows[] = $row;
				continue;
			}
			$result = fnpw_migrate_restore( $post_id );
			$row    = array(
				'key'     => get_post_type( $post_id ) . ': ' . get_the_title( $post_id ),
				'action'  => is_wp_error( $result ) ? 'error' : 'restore',
				'post_id' => $post_id,
				'message' => is_wp_error( $result ) ? $result->get_error_message() : 'Previous content restored.',
			);
			fnpw_migrate_log( $run, 'restore', $row['key'], $row['action'], $post_id, $row['message'] );
			$rows[] = $row;
		}
		$next = $offset + count( $slice );
		wp_send_json_success( array( 'run' => $run, 'phase' => 'restore', 'rows' => $rows, 'offset' => $next, 'total' => count( $ids ), 'done' => $next >= count( $ids ) ) );
	}

	$package = fnpw_migrate_package();
	if ( is_wp_error( $package ) ) {
		wp_send_json_error( array( 'message' => $package->get_error_message() ) );
	}
	$base = isset( $package['media_base'] ) ? (string) $package['media_base'] : '';
	$rows = array();

	if ( 'media' === $phase ) {
		$total = count( $package['media'] );
		$map   = fnpw_migrate_media_map();
		$slice = array_slice( $package['media'], $offset, FNPW_MIGRATE_MEDIA_BATCH );
		foreach ( $slice as $entry ) {
			$url = isset( $entry['url'] ) ? (string) $entry['url'] : '';
			try {
				$result = fnpw_migrate_media_entry( $entry, $apply, $base, $fetch );
			} catch ( Throwable $e ) {
				$result = array( 'action' => 'media-error', 'id' => 0, 'url' => $url, 'message' => 'Error: ' . $e->getMessage() );
			}
			if ( $apply && in_array( $result['action'], array( 'media-reuse', 'media-sideload', 'media-leave' ), true ) && '' !== $url ) {
				$map[ $url ] = array( 'id' => (int) $result['id'], 'url' => (string) $result['url'] );
			}
			fnpw_migrate_log( $run, $mode, $url, $result['action'], $result['id'], $result['message'] );
			$rows[] = array( 'key' => $url, 'action' => $result['action'], 'post_id' => (int) $result['id'], 'message' => $result['message'] );
		}
		if ( $apply ) {
			fnpw_migrate_media_map_save( $map );
		}
		$next = $offset + count( $slice );
		$done = $next >= $total;
		wp_send_json_success( array( 'run' => $run, 'phase' => $done ? 'items' : 'media', 'rows' => $rows, 'offset' => $done ? 0 : $next, 'at' => $next, 'total' => $total, 'label' => 'media', 'done' => false ) );
	}

	if ( 'items' === $phase ) {
		$total    = count( $package['items'] );
		$slice    = array_slice( $package['items'], $offset, FNPW_MIGRATE_ITEM_BATCH );
		$options  = array(
			'media_map'    => fnpw_migrate_media_map(),
			'create_terms' => ! empty( $package['create_terms'] ),
		);
		$filtered = $apply ? fnpw_migrate_kses_off() : false;
		foreach ( $slice as $item ) {
			try {
				$result = fnpw_migrate_item( $item, $apply, $options );
			} catch ( Throwable $e ) {
				$result = array( 'action' => 'error', 'post_id' => 0, 'key' => isset( $item['key'] ) ? (string) $item['key'] : '?', 'message' => 'Error: ' . $e->getMessage() );
			}
			fnpw_migrate_log( $run, $mode, $result['key'], $result['action'], $result['post_id'], $result['message'] );
			$rows[] = $result;
		}
		fnpw_migrate_kses_on( $filtered );
		$next = $offset + count( $slice );
		$done = $next >= $total;
		wp_send_json_success( array( 'run' => $run, 'phase' => $done ? 'finish' : 'items', 'rows' => $rows, 'offset' => $done ? 0 : $next, 'at' => $next, 'total' => $total, 'label' => 'items', 'done' => false ) );
	}

	// finish
	$want_reading = isset( $_POST['set_reading'] ) && '1' === $_POST['set_reading'];
	if ( ! empty( $package['settings'] ) ) {
		if ( $want_reading ) {
			foreach ( fnpw_migrate_apply_reading( $package, $apply ) as $line ) {
				fnpw_migrate_log( $run, $mode, 'Settings > Reading', 'settings', 0, $line );
				$rows[] = array( 'key' => 'Settings > Reading', 'action' => 'settings', 'post_id' => 0, 'message' => $line );
			}
		} else {
			$line = 'Front page and posts page left as they are (the box was not ticked).';
			fnpw_migrate_log( $run, $mode, 'Settings > Reading', 'skip', 0, $line );
			$rows[] = array( 'key' => 'Settings > Reading', 'action' => 'skip', 'post_id' => 0, 'message' => $line );
		}
	}
	if ( $apply ) {
		flush_rewrite_rules( false );
	}
	wp_send_json_success( array( 'run' => $run, 'phase' => 'finish', 'rows' => $rows, 'offset' => 0, 'done' => true ) );
}
add_action( 'wp_ajax_fnpw_migrate_batch', 'fnpw_migrate_ajax' );

function fnpw_migrate_assets( $hook ) {
	if ( 'tools_page_fnpw-migrate' !== $hook ) {
		return;
	}
	wp_enqueue_script( 'fnpw-migrate-admin', FNPW_MIGRATE_URL . 'assets/admin.js', array(), (string) filemtime( FNPW_MIGRATE_DIR . 'assets/admin.js' ), true );
	wp_localize_script(
		'fnpw-migrate-admin',
		'FNPW_MIGRATE',
		array(
			'ajax'  => admin_url( 'admin-ajax.php' ),
			'nonce' => wp_create_nonce( 'fnpw_migrate_run' ),
			'edit'  => admin_url( 'post.php?action=edit&post=' ),
		)
	);
}
add_action( 'admin_enqueue_scripts', 'fnpw_migrate_assets' );

function fnpw_migrate_screen() {
	if ( ! fnpw_migrate_can() ) {
		return;
	}
	$info   = get_option( 'fnpw_migrate_package' );
	$notice = get_transient( 'fnpw_migrate_notice_' . get_current_user_id() );
	delete_transient( 'fnpw_migrate_notice_' . get_current_user_id() );
	$action = admin_url( 'admin-post.php' );
	$ids    = fnpw_migrate_restorable();
	?>
	<div class="wrap" id="fnpw-migrate">
		<h1>FNPW import</h1>
		<?php if ( is_array( $notice ) && '' !== $notice[1] ) : ?>
			<div class="notice notice-<?php echo esc_attr( $notice[0] ); ?>"><p><?php echo esc_html( $notice[1] ); ?></p></div>
		<?php endif; ?>
		<p>Creates or updates pages, posts and projects from an import package. It never deletes anything, never clears fields it was not given, and keeps the previous content of every post it overwrites.</p>

		<h2>1. Package</h2>
		<?php if ( is_array( $info ) ) : ?>
			<p id="fnpw-package"><strong><?php echo esc_html( $info['name'] ); ?></strong>: <?php echo (int) $info['items']; ?> items, <?php echo (int) $info['media']; ?> media entries. Generated <?php echo esc_html( $info['generated'] ); ?>, uploaded <?php echo esc_html( wp_date( 'j F Y H:i', (int) $info['uploaded'] ) ); ?>.</p>
		<?php else : ?>
			<p id="fnpw-package">No package uploaded yet.</p>
		<?php endif; ?>
		<form method="post" action="<?php echo esc_url( $action ); ?>" enctype="multipart/form-data">
			<input type="hidden" name="action" value="fnpw_migrate">
			<input type="hidden" name="fnpw_do" value="upload">
			<?php wp_nonce_field( 'fnpw_migrate_upload' ); ?>
			<label for="fnpw-file" class="screen-reader-text">Import package</label>
			<input type="file" id="fnpw-file" name="package" accept=".json,.zip" required>
			<?php submit_button( is_array( $info ) ? 'Upload a different package' : 'Upload package', 'secondary', 'submit', false ); ?>
			<p class="description">package.json, or a zip that holds it. Upload limit on this server: <?php echo esc_html( size_format( wp_max_upload_size() ) ); ?>.</p>
		</form>

		<?php if ( is_array( $info ) ) : ?>
		<h2>2. Run</h2>
		<table class="form-table" role="presentation">
			<tr>
				<th scope="row"><label for="fnpw-fetch">Download media from</label></th>
				<td><input type="url" id="fnpw-fetch" class="regular-text code" placeholder="<?php echo esc_attr( $info['base'] ); ?>">
				<p class="description">Leave empty to use the address in the package (<?php echo esc_html( $info['base'] ); ?>). Images already in this site's media library are never downloaded.</p></td>
			</tr>
			<?php if ( ! empty( $info['settings'] ) ) : ?>
			<tr>
				<th scope="row">Settings &gt; Reading</th>
				<td><label><input type="checkbox" id="fnpw-reading"> Also set the front page and the posts page from the package</label>
				<p class="description">Off unless ticked. Only applies on Apply; a dry run reports what it would set.</p></td>
			</tr>
			<?php endif; ?>
		</table>
		<p>
			<button type="button" class="button button-secondary" id="fnpw-dry">Dry run</button>
			<button type="button" class="button button-primary" id="fnpw-apply">Apply import</button>
		</p>
		<div id="fnpw-progress" hidden>
			<progress id="fnpw-bar" max="100" value="0" style="width:100%;max-width:640px;height:1.4em"></progress>
			<p id="fnpw-status" aria-live="polite"></p>
		</div>
		<div id="fnpw-summary" aria-live="polite"></div>
		<p id="fnpw-filter" hidden><label><input type="checkbox" id="fnpw-hide-skip"> Hide unchanged (skip) rows</label></p>
		<table class="widefat striped" id="fnpw-results" hidden>
			<thead><tr><th scope="col">Item</th><th scope="col">Action</th><th scope="col">Post</th><th scope="col">Detail</th></tr></thead>
			<tbody></tbody>
		</table>
		<?php endif; ?>

		<h2>3. Restore</h2>
		<p><span id="fnpw-restorable"><?php echo count( $ids ); ?></span> posts have their pre-import content saved. Restoring puts that content (and title, excerpt, template and featured image) back; the saved copy is kept, and the next import will update the post again.</p>
		<?php if ( $ids ) : ?>
			<p><button type="button" class="button" id="fnpw-restore-all">Restore all previous content</button></p>
			<details>
				<summary>Restore one post</summary>
				<table class="widefat striped" id="fnpw-restore-list">
					<thead><tr><th scope="col">Post</th><th scope="col">Type</th><th scope="col">State</th><th scope="col"></th></tr></thead>
					<tbody>
					<?php foreach ( array_slice( $ids, 0, 600 ) as $post_id ) : ?>
						<tr>
							<td><a href="<?php echo esc_url( (string) get_edit_post_link( $post_id ) ); ?>"><?php echo esc_html( get_the_title( $post_id ) ); ?></a> <code><?php echo esc_html( (string) get_post_field( 'post_name', $post_id ) ); ?></code></td>
							<td><?php echo esc_html( (string) get_post_type( $post_id ) ); ?></td>
							<td><?php echo metadata_exists( 'post', $post_id, FNPW_MIGRATE_HASH ) ? 'imported' : 'restored'; ?></td>
							<td>
								<form method="post" action="<?php echo esc_url( $action ); ?>">
									<input type="hidden" name="action" value="fnpw_migrate">
									<input type="hidden" name="fnpw_do" value="restore">
									<input type="hidden" name="post_id" value="<?php echo (int) $post_id; ?>">
									<?php wp_nonce_field( 'fnpw_migrate_restore', '_wpnonce', false ); ?>
									<button type="submit" class="button button-small" data-restore="<?php echo (int) $post_id; ?>">Restore</button>
								</form>
							</td>
						</tr>
					<?php endforeach; ?>
					</tbody>
				</table>
			</details>
		<?php endif; ?>

		<h2>Email safety</h2>
		<p>No email leaves the site while an import, dry run or restore is running. Emails blocked so far: <strong><?php echo (int) get_option( 'fnpw_migrate_mail_blocked_total', 0 ); ?></strong>.</p>
		<form method="post" action="<?php echo esc_url( $action ); ?>">
			<input type="hidden" name="action" value="fnpw_migrate">
			<input type="hidden" name="fnpw_do" value="mailtest">
			<?php wp_nonce_field( 'fnpw_migrate_mailtest' ); ?>
			<p><button type="submit" class="button" id="fnpw-mailtest">Test the email block</button> Sends one test email to your own address, which should be stopped.</p>
		</form>

		<h2>4. Log</h2>
		<form method="post" action="<?php echo esc_url( $action ); ?>">
			<input type="hidden" name="action" value="fnpw_migrate">
			<input type="hidden" name="fnpw_do" value="log">
			<?php wp_nonce_field( 'fnpw_migrate_log' ); ?>
			<p>Every dry run, import and restore is logged. <button type="submit" class="button" id="fnpw-log">Download the log (CSV)</button></p>
		</form>
	</div>
	<?php
}
