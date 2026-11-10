<?php
/**
 * Project map block (fnpw/project-map): registration and data.
 *
 * Server-rendered, no build step. The markup, CSS classes and script logic come from
 * the map on the static projects.html (.map-sec) so it looks and behaves the same.
 * The stylesheet and script are only enqueued on pages where the block renders.
 *
 * DATA SOURCE. At launch the pins come from blocks/project-map/data/projects.json, a
 * copy of the static build's data/projects.json with each link pointing at
 * /project/{slug}/ and the pin positions the static generator (tools/gen_map.py)
 * worked out. Everything downstream only sees the array returned by
 * fnpw_core_map_projects(), so the source can be swapped without touching the block:
 *
 *   add_filter( 'fnpw_core_map_source', fn() => 'query' );   // live project posts
 *   add_filter( 'fnpw_core_map_projects', $callback );        // or any array you build
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Pillar slug => array( label, pin class ).
 *
 * @return array<string,array{0:string,1:string}>
 */
function fnpw_core_pillars() {
	return array(
		'parks'   => array( 'Growing National Parks', 'pb-parks' ),
		'species' => array( 'Saving Species', 'pb-species' ),
		'healing' => array( 'Healing the Land', 'pb-healing' ),
	);
}

/**
 * Register the block and its assets.
 */
function fnpw_core_register_project_map() {
	$dir = FNPW_CORE_DIR . 'blocks/project-map/';
	$url = FNPW_CORE_URL . 'blocks/project-map/';

	wp_register_style( 'fnpw-project-map', $url . 'style.css', array(), (string) filemtime( $dir . 'style.css' ) );
	wp_register_script( 'fnpw-project-map-view', $url . 'view.js', array(), (string) filemtime( $dir . 'view.js' ), true );

	register_block_type( $dir );
}
add_action( 'init', 'fnpw_core_register_project_map' );

/**
 * Every project the map knows about, in one normalised shape:
 *
 *   slug, title, state, pillar (parks|species|healing), pillar_label, pillar_class,
 *   on_map (bool), x, y (pin position, % of the artwork), link (URL), img (URL or '')
 *
 * @return array<int,array<string,mixed>>
 */
function fnpw_core_map_projects() {
	/**
	 * Filters where the map reads its projects from: "json" (launch default) or "query".
	 */
	$source   = apply_filters( 'fnpw_core_map_source', 'json' );
	$projects = ( 'query' === $source ) ? fnpw_core_map_projects_from_query() : fnpw_core_map_projects_from_json();

	/**
	 * Filters the final list of map projects.
	 *
	 * @param array  $projects Normalised projects.
	 * @param string $source   Source that produced them.
	 */
	$projects = apply_filters( 'fnpw_core_map_projects', $projects, $source );
	return is_array( $projects ) ? array_values( $projects ) : array();
}

/**
 * Source 1 (launch): the JSON file shipped with the plugin.
 *
 * @return array<int,array<string,mixed>>
 */
function fnpw_core_map_projects_from_json() {
	$file = apply_filters( 'fnpw_core_map_json_file', FNPW_CORE_DIR . 'blocks/project-map/data/projects.json' );
	if ( ! is_string( $file ) || ! is_readable( $file ) ) {
		return array();
	}
	$rows = json_decode( (string) file_get_contents( $file ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents -- local file.
	if ( ! is_array( $rows ) ) {
		return array();
	}
	$out = array();
	foreach ( $rows as $row ) {
		if ( empty( $row['slug'] ) || empty( $row['title'] ) ) {
			continue;
		}
		$link  = isset( $row['link'] ) ? (string) $row['link'] : '/project/' . $row['slug'] . '/';
		$out[] = array(
			'slug'         => (string) $row['slug'],
			'title'        => (string) $row['title'],
			'state'        => isset( $row['state'] ) ? (string) $row['state'] : '',
			'pillar'       => isset( $row['pillar'] ) ? (string) $row['pillar'] : '',
			'pillar_label' => isset( $row['pillar_label'] ) ? (string) $row['pillar_label'] : '',
			'pillar_class' => isset( $row['pillar_class'] ) ? (string) $row['pillar_class'] : '',
			'on_map'       => ! empty( $row['on_map'] ) && isset( $row['x'], $row['y'] ),
			'x'            => isset( $row['x'] ) ? (float) $row['x'] : null,
			'y'            => isset( $row['y'] ) ? (float) $row['y'] : null,
			// Site-relative links in the file become full URLs for this install.
			'link'         => ( 0 === strpos( $link, '/' ) ) ? home_url( $link ) : $link,
			'img'          => isset( $row['img'] ) ? (string) $row['img'] : '',
		);
	}
	return $out;
}

/**
 * Source 2 (after launch): published project posts.
 *
 * Reads the pillar from the "pillar" field this plugin adds, the state from the
 * project_state taxonomy and the coordinates from the live ACF group
 * project_details (project_latitude, project_longitude). Projects without
 * coordinates are listed but get no pin.
 *
 * Not the launch source: unlike tools/gen_map.py it does not nudge pins that share a
 * spot or sit on a region label, and it has not been run against live data.
 *
 * @return array<int,array<string,mixed>>
 */
function fnpw_core_map_projects_from_query() {
	if ( ! post_type_exists( 'project' ) ) {
		return array();
	}
	$pillars = fnpw_core_pillars();
	$query   = new WP_Query(
		array(
			'post_type'      => 'project',
			'post_status'    => 'publish',
			'posts_per_page' => 500,
			'no_found_rows'  => true,
			'orderby'        => 'date',
			'order'          => 'DESC',
		)
	);
	$out     = array();
	foreach ( $query->posts as $post ) {
		$pillar = (string) get_post_meta( $post->ID, 'pillar', true );
		if ( ! isset( $pillars[ $pillar ] ) ) {
			foreach ( $pillars as $slug => $def ) {
				if ( $def[0] === $pillar ) {
					$pillar = $slug;
				}
			}
		}
		$state = '';
		if ( taxonomy_exists( 'project_state' ) ) {
			$terms = get_the_terms( $post->ID, 'project_state' );
			$state = is_array( $terms ) ? $terms[0]->name : '';
		}
		$lat   = get_post_meta( $post->ID, 'project_details_project_latitude', true );
		$lon   = get_post_meta( $post->ID, 'project_details_project_longitude', true );
		$xy    = ( is_numeric( $lat ) && is_numeric( $lon ) ) ? fnpw_core_map_xy( (float) $lat, (float) $lon ) : null;
		$image = get_the_post_thumbnail_url( $post->ID, 'medium_large' );

		$out[] = array(
			'slug'         => $post->post_name,
			'title'        => get_the_title( $post ),
			'state'        => $state,
			'pillar'       => isset( $pillars[ $pillar ] ) ? $pillar : '',
			'pillar_label' => isset( $pillars[ $pillar ] ) ? $pillars[ $pillar ][0] : '',
			'pillar_class' => isset( $pillars[ $pillar ] ) ? $pillars[ $pillar ][1] : '',
			'on_map'       => null !== $xy && isset( $pillars[ $pillar ] ),
			'x'            => $xy ? $xy[0] : null,
			'y'            => $xy ? $xy[1] : null,
			'link'         => get_permalink( $post ),
			'img'          => $image ? $image : '',
		);
	}
	return $out;
}

/**
 * Latitude and longitude to a pin position, as percentages of the map artwork.
 * Same calibration as tools/gen_map.py in the static build (2461 x 2115 frame;
 * Tasmania has its own frame on the artwork).
 *
 * @param float $lat Latitude (negative in Australia).
 * @param float $lon Longitude.
 * @return array{0:float,1:float}|null Null when the point falls outside the artwork.
 */
function fnpw_core_map_xy( $lat, $lon ) {
	if ( $lat < -40 ) {
		$x = -6571.1 + $lon * 57.03;
		$y = -1340.9 + ( -$lat ) * 76.92;
	} else {
		$x = -5535.9 + $lon * 49.83;
		$y = -522.2 + ( -$lat ) * 56.05;
	}
	$x = round( $x / 2461 * 100, 2 );
	$y = round( $y / 2115 * 100, 2 );
	if ( $x < 0 || $x > 100 || $y < 0 || $y > 100 ) {
		return null;
	}
	return array( $x, $y );
}

/**
 * URLs of the map artwork (webp and png). The artwork is the static build's
 * assets/img/projects-map-brand.{webp,png}; copy both into blocks/project-map/.
 *
 * @return array{webp:string,png:string,found:bool}
 */
function fnpw_core_map_artwork() {
	$dir  = FNPW_CORE_DIR . 'blocks/project-map/';
	$url  = FNPW_CORE_URL . 'blocks/project-map/';
	$art  = array(
		'webp'  => file_exists( $dir . 'projects-map-brand.webp' ) ? $url . 'projects-map-brand.webp' : '',
		'png'   => $url . 'projects-map-brand.png',
		'found' => file_exists( $dir . 'projects-map-brand.png' ),
	);
	$art  = apply_filters( 'fnpw_core_map_artwork', $art );
	return $art;
}
