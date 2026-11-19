<?php
/**
 * Recompress the resized copies of imported images.
 *
 * The images were downloaded while the old theme was active, and their resized copies
 * (the 300, 768, 1024 and 1536 pixel versions the pages ask for on phones) were written
 * at maximum JPEG quality, so many are larger than the full-size original. This rewrites
 * each resized copy in place at a normal quality. File names, dimensions and URLs do not
 * change, the full-size original is never touched, and a copy is only replaced when the
 * new file is smaller.
 *
 * @package FNPW_Migrate
 */

defined( 'ABSPATH' ) || exit;

const FNPW_MIGRATE_IMG_QUALITY = 82;
const FNPW_MIGRATE_IMG_DONE    = '_fnpw_migrate_recompressed';

/**
 * Attachments the importer downloaded that have resized copies worth rewriting.
 *
 * @return int[]
 */
function fnpw_migrate_image_ids() {
	global $wpdb;
	$ids = $wpdb->get_col( // phpcs:ignore WordPress.DB.DirectDatabaseQuery
		$wpdb->prepare(
			"SELECT DISTINCT p.ID FROM {$wpdb->posts} p
			INNER JOIN {$wpdb->postmeta} m ON m.post_id = p.ID AND m.meta_key = %s
			WHERE p.post_type = 'attachment' AND p.post_mime_type IN ( 'image/jpeg', 'image/webp' )
			ORDER BY p.ID ASC",
			'_fnpw_migrate_source'
		)
	);
	return array_map( 'intval', $ids );
}

/**
 * Quality used while this tool runs, whatever a theme or plugin asks for.
 */
function fnpw_migrate_image_quality() {
	return FNPW_MIGRATE_IMG_QUALITY;
}

/**
 * Rewrite the resized copies of one attachment.
 *
 * @param int $id Attachment ID.
 * @return array{files:int,before:int,after:int,skipped:bool}
 */
function fnpw_migrate_recompress( $id ) {
	$out  = array( 'files' => 0, 'before' => 0, 'after' => 0, 'skipped' => false );
	$file = get_attached_file( $id );
	$meta = wp_get_attachment_metadata( $id );
	if ( ! $file || ! is_array( $meta ) || empty( $meta['sizes'] ) || ! is_array( $meta['sizes'] ) ) {
		$out['skipped'] = true;
		return $out;
	}
	if ( (int) get_post_meta( $id, FNPW_MIGRATE_IMG_DONE, true ) === FNPW_MIGRATE_IMG_QUALITY ) {
		$out['skipped'] = true;
		return $out;
	}

	$dir     = dirname( $file );
	$seen    = array();
	$changed = false;
	foreach ( $meta['sizes'] as $key => $size ) {
		if ( empty( $size['file'] ) ) {
			continue;
		}
		$name = wp_basename( (string) $size['file'] );
		$path = $dir . '/' . $name;
		if ( $path === $file || ! is_file( $path ) ) {
			continue;
		}
		if ( isset( $seen[ $name ] ) ) {
			// Two size names that share one file: reuse the result.
			if ( $seen[ $name ] ) {
				$meta['sizes'][ $key ]['filesize'] = $seen[ $name ];
				$changed                           = true;
			}
			continue;
		}
		$seen[ $name ] = 0;
		$old           = (int) filesize( $path );
		$dims          = @getimagesize( $path ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
		$editor        = wp_get_image_editor( $path );
		if ( is_wp_error( $editor ) || ! $dims ) {
			continue;
		}
		$editor->set_quality( FNPW_MIGRATE_IMG_QUALITY );
		$tmp   = $dir . '/fnpwtmp-' . (int) $id . '-' . $name;
		$mime  = isset( $size['mime-type'] ) ? (string) $size['mime-type'] : null;
		$saved = $editor->save( $tmp, $mime );
		unset( $editor );
		if ( is_wp_error( $saved ) || empty( $saved['path'] ) || ! is_file( $saved['path'] ) ) {
			continue;
		}
		$new      = (int) filesize( $saved['path'] );
		$new_dims = @getimagesize( $saved['path'] ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
		$same     = $new_dims && $new_dims[0] === $dims[0] && $new_dims[1] === $dims[1] && $new_dims[2] === $dims[2];
		if ( $same && $new > 0 && $new < $old && @rename( $saved['path'], $path ) ) { // phpcs:ignore WordPress.PHP.NoSilencedErrors, WordPress.WP.AlternativeFunctions
			++$out['files'];
			$out['before']                    += $old;
			$out['after']                     += $new;
			$seen[ $name ]                     = $new;
			$meta['sizes'][ $key ]['filesize'] = $new;
			$changed                           = true;
		} else {
			wp_delete_file( $saved['path'] );
		}
	}
	if ( $changed ) {
		wp_update_attachment_metadata( $id, $meta );
	}
	update_post_meta( $id, FNPW_MIGRATE_IMG_DONE, FNPW_MIGRATE_IMG_QUALITY );
	return $out;
}

/**
 * One batch. POST: offset.
 */
function fnpw_migrate_images_ajax() {
	if ( ! fnpw_migrate_can() ) {
		wp_send_json_error( array( 'message' => 'Not allowed.' ), 403 );
	}
	check_ajax_referer( 'fnpw_migrate_run', 'nonce' );

	$offset = isset( $_POST['offset'] ) ? absint( $_POST['offset'] ) : 0;
	$ids    = fnpw_migrate_image_ids();
	$total  = count( $ids );
	$batch  = array_slice( $ids, $offset, 4 );
	$sum    = array( 'files' => 0, 'before' => 0, 'after' => 0, 'images' => 0 );

	add_filter( 'wp_editor_set_quality', 'fnpw_migrate_image_quality', PHP_INT_MAX );
	add_filter( 'jpeg_quality', 'fnpw_migrate_image_quality', PHP_INT_MAX );
	foreach ( $batch as $id ) {
		$one = fnpw_migrate_recompress( $id );
		if ( $one['files'] ) {
			++$sum['images'];
		}
		$sum['files']  += $one['files'];
		$sum['before'] += $one['before'];
		$sum['after']  += $one['after'];
	}
	remove_filter( 'wp_editor_set_quality', 'fnpw_migrate_image_quality', PHP_INT_MAX );
	remove_filter( 'jpeg_quality', 'fnpw_migrate_image_quality', PHP_INT_MAX );

	$next = $offset + count( $batch );
	if ( $sum['files'] ) {
		fnpw_migrate_log( 'images-' . gmdate( 'Ymd' ), 'apply', 'Image sizes ' . $offset . ' to ' . $next, 'recompress', 0, $sum['files'] . ' resized copies rewritten, ' . size_format( $sum['before'] ) . ' down to ' . size_format( $sum['after'] ) . '.' );
	}
	wp_send_json_success(
		array(
			'offset' => $next,
			'total'  => $total,
			'done'   => $next >= $total,
			'files'  => $sum['files'],
			'images' => $sum['images'],
			'before' => $sum['before'],
			'after'  => $sum['after'],
		)
	);
}
add_action( 'wp_ajax_fnpw_migrate_images', 'fnpw_migrate_images_ajax' );

/**
 * The section on Tools > FNPW import.
 */
function fnpw_migrate_images_section() {
	$total = count( fnpw_migrate_image_ids() );
	?>
	<h2>Image sizes</h2>
	<p><?php echo (int) $total; ?> imported photos have resized copies. This rewrites those copies at normal quality so phones download smaller files. Addresses and full-size originals stay the same, and it is safe to run more than once.</p>
	<p><button type="button" class="button" id="fnpw-images">Shrink resized copies</button> <span id="fnpw-images-status" aria-live="polite"></span></p>
	<script>
	( function () {
		var btn = document.getElementById( 'fnpw-images' ), out = document.getElementById( 'fnpw-images-status' );
		if ( ! btn ) { return; }
		var files = 0, before = 0, after = 0;
		function mb( n ) { return ( n / 1048576 ).toFixed( 1 ) + ' MB'; }
		function step( offset ) {
			var body = new URLSearchParams( { action: 'fnpw_migrate_images', nonce: FNPW_MIGRATE.nonce, offset: offset } );
			fetch( FNPW_MIGRATE.ajax, { method: 'POST', credentials: 'same-origin', body: body } )
				.then( function ( r ) { return r.json(); } )
				.then( function ( j ) {
					if ( ! j || ! j.success ) { throw new Error( ( j && j.data && j.data.message ) || 'failed' ); }
					files += j.data.files; before += j.data.before; after += j.data.after;
					if ( j.data.done ) {
						out.textContent = 'Finished. ' + files + ' resized copies rewritten, ' + mb( before ) + ' down to ' + mb( after ) + '.';
						btn.disabled = false;
					} else {
						out.textContent = 'Working: ' + j.data.offset + ' of ' + j.data.total + ' photos';
						step( j.data.offset );
					}
				} )
				.catch( function ( e ) { out.textContent = 'Stopped at ' + offset + ': ' + e.message + '. Press the button to carry on.'; btn.disabled = false; } );
		}
		btn.addEventListener( 'click', function () { if ( ! window.FNPW_MIGRATE ) { out.textContent = 'The page has not finished loading. Try again.'; return; } btn.disabled = true; files = 0; before = 0; after = 0; out.textContent = 'Starting'; step( 0 ); } );
	}() );
	</script>
	<?php
}
