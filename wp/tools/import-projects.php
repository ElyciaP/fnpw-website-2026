<?php
/**
 * Import the static build's project data into the Project content type.
 *
 * Run with WP-CLI from the WordPress root:
 *
 *   wp eval-file wp/tools/import-projects.php /absolute/path/to/repo --dry-run
 *   wp eval-file wp/tools/import-projects.php /absolute/path/to/repo
 *
 * Idempotent. Matching is by slug, so running it twice updates rather than
 * duplicates, and you can re-run it after a content pass without cleaning up.
 *
 * Reads data/projects.json (84 records: slug, title, img, pillar, state,
 * lat, lon, on_map, live_url) and data/projects-content.json (72 records with
 * the body blocks), and joins them on slug.
 *
 * @package fnpw-core
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
	fwrite( STDERR, "This script must be run through WP-CLI.\n" );
	exit( 1 );
}

$args    = $GLOBALS['argv'] ?? array();
$repo    = null;
$dry_run = false;

foreach ( array_slice( $args, 3 ) as $arg ) {
	if ( '--dry-run' === $arg ) {
		$dry_run = true;
	} elseif ( '' !== $arg && '-' !== $arg[0] ) {
		$repo = rtrim( $arg, '/' );
	}
}

if ( ! $repo || ! is_dir( $repo . '/data' ) ) {
	WP_CLI::error( 'Pass the absolute path to the repo root, the folder containing data/projects.json.' );
}

$pillar_map = array(
	'parks'   => 'growing-national-parks',
	'species' => 'saving-species',
	'healing' => 'healing-the-land',
);

$projects = json_decode( (string) file_get_contents( $repo . '/data/projects.json' ), true );
$content  = json_decode( (string) file_get_contents( $repo . '/data/projects-content.json' ), true );

if ( ! is_array( $projects ) ) {
	WP_CLI::error( 'Could not read data/projects.json.' );
}

$by_slug = array();
foreach ( (array) $content as $row ) {
	if ( ! empty( $row['slug'] ) ) {
		$by_slug[ $row['slug'] ] = $row;
	}
}

$created = 0;
$updated = 0;
$skipped = 0;

foreach ( $projects as $p ) {
	$slug = $p['slug'] ?? '';
	if ( '' === $slug ) {
		++$skipped;
		continue;
	}

	$body   = $by_slug[ $slug ] ?? array();
	$blocks = '';

	foreach ( (array) ( $body['blocks'] ?? array() ) as $b ) {
		$type = $b['t'] ?? 'p';
		$text = trim( (string) ( $b['v'] ?? '' ) );
		if ( '' === $text ) {
			continue;
		}

		if ( 'h2' === $type || 'h3' === $type ) {
			$level   = ( 'h2' === $type ) ? 2 : 3;
			$blocks .= sprintf(
				"<!-- wp:heading {\"level\":%d} -->\n<h%d class=\"wp-block-heading\">%s</h%d>\n<!-- /wp:heading -->\n\n",
				$level,
				$level,
				esc_html( $text ),
				$level
			);
		} else {
			$blocks .= sprintf(
				"<!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph -->\n\n",
				wp_kses_post( $text )
			);
		}
	}

	$existing = get_page_by_path( $slug, OBJECT, 'project' );

	$postarr = array(
		'post_type'    => 'project',
		'post_name'    => $slug,
		'post_title'   => $p['title'] ?? $slug,
		'post_excerpt' => $body['desc'] ?? '',
		'post_content' => $blocks,
		'post_status'  => 'draft',
	);

	if ( $dry_run ) {
		WP_CLI::log( sprintf( '%s %s', $existing ? 'would update' : 'would create', $slug ) );
		$existing ? $updated++ : $created++;
		continue;
	}

	if ( $existing ) {
		$postarr['ID'] = $existing->ID;
		$post_id       = wp_update_post( $postarr, true );
		++$updated;
	} else {
		$post_id = wp_insert_post( $postarr, true );
		++$created;
	}

	if ( is_wp_error( $post_id ) ) {
		WP_CLI::warning( sprintf( '%s: %s', $slug, $post_id->get_error_message() ) );
		continue;
	}

	if ( ! empty( $p['pillar'] ) && isset( $pillar_map[ $p['pillar'] ] ) ) {
		wp_set_object_terms( $post_id, $pillar_map[ $p['pillar'] ], 'pillar', false );
	}

	if ( ! empty( $p['state'] ) ) {
		wp_set_object_terms( $post_id, (string) $p['state'], 'project_location', false );
	}

	update_post_meta( $post_id, 'fnpw_lat', (float) ( $p['lat'] ?? 0 ) );
	update_post_meta( $post_id, 'fnpw_lon', (float) ( $p['lon'] ?? 0 ) );
	update_post_meta( $post_id, 'fnpw_on_map', ! empty( $p['on_map'] ) );
	update_post_meta( $post_id, 'fnpw_legacy_url', (string) ( $p['live_url'] ?? '' ) );

	WP_CLI::log( sprintf( 'ok  %s  (#%d)', $slug, $post_id ) );
}

WP_CLI::success(
	sprintf(
		'%s: %d created, %d updated, %d skipped. Imported as drafts. Featured images and the credit line are set by hand or by a second pass.',
		$dry_run ? 'Dry run' : 'Import complete',
		$created,
		$updated,
		$skipped
	)
);
