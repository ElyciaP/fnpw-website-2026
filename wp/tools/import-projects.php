<?php
/**
 * Import projects into WordPress from wp/data/projects-bundle.json.
 *
 * The bundle is built from your live static project pages by
 * wp/tools/build_project_bundle.py (or wp/tools/sync.sh), so whatever is on
 * the page is what comes across. Run with WP-CLI from the Local site shell:
 *
 *   wp eval-file /path/to/repo/wp/tools/import-projects.php /path/to/repo --dry-run
 *   wp eval-file /path/to/repo/wp/tools/import-projects.php /path/to/repo
 *
 * Safe to re-run. Projects match on slug and are updated, not duplicated.
 * Images are uploaded to the media library once and reused after that.
 * New projects come in as drafts; existing ones keep their current status.
 *
 * @package fnpw-core
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
	fwrite( STDERR, "Run this through WP-CLI.\n" );
	exit( 1 );
}

require_once ABSPATH . 'wp-admin/includes/file.php';
require_once ABSPATH . 'wp-admin/includes/media.php';
require_once ABSPATH . 'wp-admin/includes/image.php';

$repo    = null;
$dry_run = false;
foreach ( array_slice( $GLOBALS['argv'] ?? array(), 3 ) as $arg ) {
	if ( '--dry-run' === $arg ) {
		$dry_run = true;
	} elseif ( '' !== $arg && '-' !== $arg[0] ) {
		$repo = rtrim( $arg, '/' );
	}
}

$bundle_path = $repo . '/wp/data/projects-bundle.json';
if ( ! $repo || ! file_exists( $bundle_path ) ) {
	WP_CLI::error( 'Pass the repo root path. Expected to find wp/data/projects-bundle.json there. Run wp/tools/sync.sh first.' );
}

$projects = json_decode( (string) file_get_contents( $bundle_path ), true );
if ( ! is_array( $projects ) ) {
	WP_CLI::error( 'Could not read the project bundle.' );
}

/**
 * Upload a repo image once and return its attachment ID. Reuses an existing
 * upload by matching the repo path stored on the attachment.
 */
function fnpw_import_image( $repo, $rel, $alt = '' ) {
	$existing = get_posts(
		array(
			'post_type'      => 'attachment',
			'post_status'    => 'inherit',
			'meta_key'       => '_fnpw_source',
			'meta_value'     => $rel,
			'fields'         => 'ids',
			'posts_per_page' => 1,
		)
	);
	if ( $existing ) {
		return (int) $existing[0];
	}

	$file = $repo . '/' . $rel;
	if ( ! file_exists( $file ) ) {
		WP_CLI::warning( "Image missing in repo: $rel" );
		return 0;
	}

	$tmp = wp_tempnam( basename( $file ) );
	copy( $file, $tmp );
	$id = media_handle_sideload( array( 'name' => basename( $file ), 'tmp_name' => $tmp ), 0 );
	if ( is_wp_error( $id ) ) {
		WP_CLI::warning( "$rel: " . $id->get_error_message() );
		return 0;
	}

	update_post_meta( $id, '_fnpw_source', $rel );
	if ( $alt ) {
		update_post_meta( $id, '_wp_attachment_image_alt', $alt );
	}
	return (int) $id;
}

/**
 * Point article links at the real post if it exists, otherwise at /slug/,
 * which WordPress redirects to the matching post by itself.
 */
function fnpw_resolve_article_links( $html ) {
	return preg_replace_callback(
		'/fnpw-article:([a-z0-9-]+)/',
		function ( $m ) {
			$post = get_page_by_path( $m[1], OBJECT, 'post' );
			return $post ? get_permalink( $post ) : home_url( '/' . $m[1] . '/' );
		},
		$html
	);
}

$created = 0;
$updated = 0;
$images  = 0;

foreach ( $projects as $p ) {
	$slug     = $p['slug'];
	$existing = get_page_by_path( $slug, OBJECT, 'project' );

	if ( $dry_run ) {
		WP_CLI::log( sprintf( '%-8s %-55s %2d sections, %2d images', $existing ? 'update' : 'create', $slug, count( $p['sections'] ), count( $p['images'] ) ) );
		$existing ? $updated++ : $created++;
		continue;
	}

	// Upload local images and swap their paths for media library URLs.
	$content = implode( "\n", $p['sections'] );
	foreach ( $p['images'] as $rel ) {
		$id = fnpw_import_image( $repo, $rel );
		if ( $id ) {
			$content = str_replace( $rel, wp_get_attachment_url( $id ), $content );
			++$images;
		}
	}
	$content = fnpw_resolve_article_links( $content );

	// Each section becomes its own block, so sections can be reordered or
	// removed in the editor while keeping the design exactly as built.
	$blocks = '';
	foreach ( preg_split( '/(?=<section\b)/', $content, -1, PREG_SPLIT_NO_EMPTY ) as $section ) {
		$section = trim( $section );
		if ( '' !== $section ) {
			$blocks .= "<!-- wp:html -->\n" . $section . "\n<!-- /wp:html -->\n\n";
		}
	}

	$postarr = array(
		'post_type'    => 'project',
		'post_name'    => $slug,
		'post_title'   => $p['title'],
		'post_excerpt' => $p['excerpt'],
		'post_content' => $blocks,
	);

	if ( $existing ) {
		$postarr['ID'] = $existing->ID;
		$post_id       = wp_update_post( wp_slash( $postarr ), true );
		++$updated;
	} else {
		$postarr['post_status'] = 'draft';
		$post_id                = wp_insert_post( wp_slash( $postarr ), true );
		++$created;
	}

	if ( is_wp_error( $post_id ) ) {
		WP_CLI::warning( "$slug: " . $post_id->get_error_message() );
		continue;
	}

	// Featured image: a repo image is uploaded, a live-site URL is sideloaded once.
	$hero = $p['hero_image'];
	if ( $hero ) {
		if ( 0 === strpos( $hero, 'assets/img/' ) ) {
			$thumb = fnpw_import_image( $repo, $hero, $p['hero_alt'] );
		} else {
			$found = get_posts( array( 'post_type' => 'attachment', 'post_status' => 'inherit', 'meta_key' => '_fnpw_source', 'meta_value' => $hero, 'fields' => 'ids', 'posts_per_page' => 1 ) );
			$thumb = $found ? (int) $found[0] : media_sideload_image( $hero, $post_id, $p['hero_alt'], 'id' );
			if ( ! is_wp_error( $thumb ) && ! $found ) {
				update_post_meta( $thumb, '_fnpw_source', $hero );
			}
		}
		if ( $thumb && ! is_wp_error( $thumb ) ) {
			set_post_thumbnail( $post_id, $thumb );
		}
	}

	if ( $p['pillar'] ) {
		wp_set_object_terms( $post_id, $p['pillar'], 'pillar', false );
	}
	if ( $p['state'] ) {
		wp_set_object_terms( $post_id, $p['state'], 'project_location', false );
	}

	update_post_meta( $post_id, 'fnpw_lat', (float) $p['lat'] );
	update_post_meta( $post_id, 'fnpw_lon', (float) $p['lon'] );
	update_post_meta( $post_id, 'fnpw_on_map', (bool) $p['on_map'] );
	update_post_meta( $post_id, 'fnpw_legacy_url', $p['legacy_url'] );
	update_post_meta( $post_id, 'fnpw_credit', $p['credit'] );

	WP_CLI::log( sprintf( 'ok  %-55s #%d', $slug, $post_id ) );
}

WP_CLI::success( sprintf( '%s: %d created, %d updated, %d images placed.', $dry_run ? 'Dry run' : 'Done', $created, $updated, $images ) );
