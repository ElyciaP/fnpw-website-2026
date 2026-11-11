<?php
/**
 * Media: find an existing attachment for a package image, or sideload it.
 *
 * Images already on this site's media library (…/wp-content/uploads/…) are never
 * downloaded and their URLs are never changed. Everything else is looked up by the
 * source URL it was imported from, then by file name, and only then downloaded.
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * old URL => array( 'id' => attachment ID, 'url' => new URL ), kept between requests.
 */
function fnpw_migrate_media_map() {
	$map = get_option( 'fnpw_migrate_media_map' );
	return is_array( $map ) ? $map : array();
}

function fnpw_migrate_media_map_save( $map ) {
	update_option( 'fnpw_migrate_media_map', $map, false );
}

/**
 * True for a URL that points into a WordPress uploads folder (the live media library).
 */
function fnpw_migrate_is_library_url( $url ) {
	return false !== strpos( (string) $url, '/wp-content/uploads/' );
}

/**
 * Attachment ID for a media-library URL from the live site, or 0. Sized and edited
 * variants (-1024x683, -scaled, -e1658287534120) are tried against the original.
 */
function fnpw_migrate_library_attachment( $url ) {
	$pos = strpos( $url, '/wp-content/uploads/' );
	if ( false === $pos ) {
		return 0;
	}
	$rel     = substr( $url, $pos + strlen( '/wp-content/uploads/' ) );
	$rel     = strtok( $rel, '?#' );
	$uploads = wp_upload_dir();
	$tries   = array( $rel );
	$tries[] = preg_replace( '/-\d+x\d+(\.[a-z0-9]+)$/i', '$1', $rel );
	$tries[] = preg_replace( '/-scaled(\.[a-z0-9]+)$/i', '$1', end( $tries ) );
	$tries[] = preg_replace( '/-e\d{10,}(\.[a-z0-9]+)$/i', '$1', end( $tries ) );
	$tries[] = preg_replace( '/-scaled(\.[a-z0-9]+)$/i', '$1', end( $tries ) );
	foreach ( array_unique( $tries ) as $try ) {
		$id = attachment_url_to_postid( trailingslashit( $uploads['baseurl'] ) . $try );
		if ( $id ) {
			return (int) $id;
		}
		$found = get_posts(
			array(
				'post_type'      => 'attachment',
				'post_status'    => 'inherit',
				'posts_per_page' => 1,
				'fields'         => 'ids',
				'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery
					array(
						'key'   => '_wp_attached_file',
						'value' => $try,
					),
				),
			)
		);
		if ( $found ) {
			return (int) $found[0];
		}
	}
	return 0;
}

/**
 * An attachment already made from this source URL, or one with the same file name.
 *
 * @return array{0:int,1:string} Attachment ID (0 when none) and how it matched.
 */
function fnpw_migrate_existing_attachment( $url ) {
	$found = get_posts(
		array(
			'post_type'      => 'attachment',
			'post_status'    => 'inherit',
			'posts_per_page' => 1,
			'fields'         => 'ids',
			'meta_query'     => array( // phpcs:ignore WordPress.DB.SlowDBQuery
				array(
					'key'   => '_fnpw_migrate_source',
					'value' => $url,
				),
			),
		)
	);
	if ( $found ) {
		return array( (int) $found[0], 'source URL' );
	}
	global $wpdb;
	$base = wp_basename( (string) wp_parse_url( $url, PHP_URL_PATH ) );
	if ( '' === $base ) {
		return array( 0, '' );
	}
	$id = $wpdb->get_var( // phpcs:ignore WordPress.DB.DirectDatabaseQuery
		$wpdb->prepare(
			"SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = '_wp_attached_file' AND ( meta_value = %s OR meta_value LIKE %s ) ORDER BY post_id ASC LIMIT 1",
			$base,
			'%/' . $wpdb->esc_like( $base )
		)
	);
	return $id ? array( (int) $id, 'file name' ) : array( 0, '' );
}

/**
 * Work out (dry run) or do (apply) what one media entry needs.
 *
 * @param array  $entry Package media entry: url, alt, sideload.
 * @param bool   $apply False for a dry run.
 * @param string $base  Package media base URL.
 * @param string $fetch Base URL to download from instead of $base ('' for none).
 * @return array{action:string,id:int,url:string,message:string}
 */
function fnpw_migrate_media_entry( $entry, $apply, $base, $fetch ) {
	$url = isset( $entry['url'] ) ? (string) $entry['url'] : '';
	$alt = isset( $entry['alt'] ) ? (string) $entry['alt'] : '';
	if ( '' === $url ) {
		return array( 'action' => 'error', 'id' => 0, 'url' => '', 'message' => 'Media entry has no URL.' );
	}
	if ( fnpw_migrate_is_library_url( $url ) || empty( $entry['sideload'] ) ) {
		$id = fnpw_migrate_is_library_url( $url ) ? fnpw_migrate_library_attachment( $url ) : 0;
		return array(
			'action'  => 'media-leave',
			'id'      => $id,
			'url'     => $url,
			'message' => $id ? 'Already in the media library (attachment ' . $id . '); URL left as it is.' : 'Media library URL left as it is (no matching attachment found on this site).',
		);
	}
	list( $id, $how ) = fnpw_migrate_existing_attachment( $url );
	if ( $id ) {
		$new = wp_get_attachment_url( $id );
		return array( 'action' => 'media-reuse', 'id' => $id, 'url' => $new ? $new : $url, 'message' => 'Reused attachment ' . $id . ' (matched by ' . $how . ').' );
	}
	$from = $url;
	if ( '' !== $fetch && '' !== $base && 0 === strpos( $url, $base ) ) {
		$from = trailingslashit( $fetch ) . substr( $url, strlen( $base ) );
	}
	if ( ! $apply ) {
		return array( 'action' => 'media-sideload', 'id' => 0, 'url' => $url, 'message' => 'Would download from ' . $from );
	}
	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';
	require_once ABSPATH . 'wp-admin/includes/image.php';
	$tmp = download_url( $from, 60 );
	if ( is_wp_error( $tmp ) ) {
		return array( 'action' => 'media-error', 'id' => 0, 'url' => $url, 'message' => 'Download failed from ' . $from . ': ' . $tmp->get_error_message() . '. The content keeps the source URL.' );
	}
	$file = array(
		'name'     => wp_basename( (string) wp_parse_url( $url, PHP_URL_PATH ) ),
		'tmp_name' => $tmp,
	);
	$id   = media_handle_sideload( $file, 0, null, array( 'post_title' => '' !== $alt ? wp_strip_all_tags( $alt ) : preg_replace( '/\.[^.]+$/', '', $file['name'] ) ) );
	if ( is_wp_error( $id ) ) {
		if ( file_exists( $tmp ) ) {
			wp_delete_file( $tmp );
		}
		return array( 'action' => 'media-error', 'id' => 0, 'url' => $url, 'message' => 'Could not add ' . $file['name'] . ' to the media library: ' . $id->get_error_message() . '. The content keeps the source URL.' );
	}
	update_post_meta( $id, '_fnpw_migrate_source', wp_slash( $url ) );
	if ( '' !== $alt ) {
		update_post_meta( $id, '_wp_attachment_image_alt', wp_slash( $alt ) );
	}
	return array( 'action' => 'media-sideload', 'id' => (int) $id, 'url' => (string) wp_get_attachment_url( $id ), 'message' => 'Downloaded from ' . $from . ' as attachment ' . $id . '.' );
}

/**
 * Swap sideloaded source URLs for their media-library URLs in a string.
 *
 * @param string $text Content, CSS or script.
 * @param array  $map  fnpw_migrate_media_map().
 * @return string
 */
function fnpw_migrate_rewrite_media( $text, $map ) {
	if ( ! is_string( $text ) || '' === $text || ! $map ) {
		return $text;
	}
	static $pairs = null, $for = null;
	if ( $for !== $map ) {
		$pairs = array();
		foreach ( $map as $old => $row ) {
			if ( ! empty( $row['url'] ) && $row['url'] !== $old && ! fnpw_migrate_is_library_url( $old ) ) {
				$pairs[ $old ] = $row['url'];
			}
		}
		// Longest first, so a URL that is the start of another is not cut short.
		uksort(
			$pairs,
			static function ( $a, $b ) {
				return strlen( $b ) - strlen( $a );
			}
		);
		$for = $map;
	}
	return $pairs ? strtr( $text, $pairs ) : $text;
}
