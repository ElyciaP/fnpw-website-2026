<?php
/**
 * Project map block (fnpw/project-map): registration and data.
 *
 * Server-rendered, no build step. The markup, CSS classes and script logic come from
 * the map on the static projects.html (.map-sec) so it looks and behaves the same.
 * The stylesheet and script are only enqueued on pages where the block renders.
 *
 * DATA SOURCE. The pins come from the published project posts, filled in from
 * blocks/project-map/data/projects.json (a copy of the static build's
 * data/projects.json with the pin positions tools/gen_map.py worked out) wherever a
 * post has no coordinates. Everything downstream only sees the array returned by
 * fnpw_core_map_projects(), so the source can be swapped without touching the block:
 *
 *   add_filter( 'fnpw_core_map_source', fn() => 'json' );    // the shipped file only
 *   add_filter( 'fnpw_core_map_source', fn() => 'query' );   // project posts only
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
	 * Filters where the map reads its projects from:
	 *
	 *   "auto"  (default) published project posts, each filled in from the shipped JSON
	 *           where the post has no coordinates; the JSON alone when there are no
	 *           project posts.
	 *   "query" project posts only.
	 *   "json"  the shipped JSON only.
	 */
	$source = apply_filters( 'fnpw_core_map_source', 'auto' );
	if ( 'json' === $source ) {
		$projects = fnpw_core_map_projects_from_json();
	} elseif ( 'query' === $source ) {
		$projects = fnpw_core_map_projects_from_query();
	} else {
		$projects = fnpw_core_map_projects_merged();
	}

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
			'lat'          => isset( $row['lat'] ) && is_numeric( $row['lat'] ) ? (float) $row['lat'] : null,
			'lon'          => isset( $row['lon'] ) && is_numeric( $row['lon'] ) ? (float) $row['lon'] : null,
		);
	}
	return $out;
}

/**
 * A project's coordinates from the live ACF group "Single - Project". The group field
 * project_details stores its sub-fields as project_details_project_latitude and
 * project_details_project_longitude; plain project_latitude / project_longitude and
 * an array under project_details are accepted too.
 *
 * @param int $post_id Project ID.
 * @return array{0:float,1:float}|null Latitude, longitude.
 */
function fnpw_core_project_latlon( $post_id ) {
	$pairs = array(
		array( 'project_details_project_latitude', 'project_details_project_longitude' ),
		array( 'project_latitude', 'project_longitude' ),
	);
	foreach ( $pairs as $pair ) {
		$lat = get_post_meta( $post_id, $pair[0], true );
		$lon = get_post_meta( $post_id, $pair[1], true );
		if ( is_numeric( $lat ) && is_numeric( $lon ) && ( 0.0 !== (float) $lat || 0.0 !== (float) $lon ) ) {
			return array( (float) $lat, (float) $lon );
		}
	}
	$group = get_post_meta( $post_id, 'project_details', true );
	if ( is_array( $group ) && isset( $group['project_latitude'], $group['project_longitude'] )
		&& is_numeric( $group['project_latitude'] ) && is_numeric( $group['project_longitude'] ) ) {
		return array( (float) $group['project_latitude'], (float) $group['project_longitude'] );
	}
	return null;
}

/**
 * Popup thumbnail for a project post: its featured image, else the banner_image of the
 * live "Single - Header" group.
 *
 * @param int $post_id Project ID.
 * @return string URL or ''.
 */
function fnpw_core_project_thumb( $post_id ) {
	$url = get_the_post_thumbnail_url( $post_id, 'medium_large' );
	if ( ! $url ) {
		$banner = get_post_meta( $post_id, 'banner_image', true );
		$url    = is_numeric( $banner ) ? wp_get_attachment_image_url( (int) $banner, 'medium_large' ) : '';
	}
	return $url ? (string) $url : '';
}

/**
 * Source 2: published project posts.
 *
 * Reads the pillar from the "pillar" field this plugin adds (else the focus-area
 * terms), the state from the project_state taxonomy and the coordinates from the live
 * ACF group project_details. Projects without coordinates are listed but get no pin.
 *
 * Unlike tools/gen_map.py it does not nudge pins that share a spot or sit on a region
 * label; the merged source keeps the hand-placed positions from the JSON for that.
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
		if ( ! isset( $pillars[ $pillar ] ) && taxonomy_exists( 'project_focus_area' ) ) {
			$areas = get_the_terms( $post->ID, 'project_focus_area' );
			foreach ( is_array( $areas ) ? $areas : array() as $area ) {
				if ( false !== strpos( $area->slug, 'park' ) ) {
					$pillar = 'parks';
				} elseif ( false !== strpos( $area->slug, 'species' ) ) {
					$pillar = 'species';
				} elseif ( false !== strpos( $area->slug, 'heal' ) ) {
					$pillar = 'healing';
				}
			}
		}
		$state = '';
		if ( taxonomy_exists( 'project_state' ) ) {
			$terms = get_the_terms( $post->ID, 'project_state' );
			if ( is_array( $terms ) ) {
				// The map's state buttons use short names; the live terms are spelled out.
				$short = array(
					'new-south-wales'              => 'NSW',
					'victoria'                     => 'VIC',
					'queensland'                   => 'QLD',
					'qld'                          => 'QLD',
					'south-australia'              => 'SA',
					'western-australia'            => 'WA',
					'tasmania'                     => 'TAS',
					'northern-territory'           => 'NT',
					'australian-capital-territory' => 'ACT',
					'national'                     => 'Australia',
				);
				$state = isset( $short[ $terms[0]->slug ] ) ? $short[ $terms[0]->slug ] : $terms[0]->name;
			}
		}
		$latlon = fnpw_core_project_latlon( $post->ID );
		$xy     = $latlon ? fnpw_core_map_xy( $latlon[0], $latlon[1] ) : null;

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
			'lat'          => $latlon ? $latlon[0] : null,
			'lon'          => $latlon ? $latlon[1] : null,
			'link'         => get_permalink( $post ),
			'img'          => fnpw_core_project_thumb( $post->ID ),
		);
	}
	return $out;
}

/**
 * Source 3 (default): project posts, filled in from the shipped JSON.
 *
 * For each published project the post is the authority for title, link and thumbnail.
 * Position: when the post has coordinates and they differ from the ones the JSON was
 * built from, the pin is computed from the post; otherwise the JSON position is used
 * (it carries the hand nudges that keep pins from stacking). Pillar and state fall back
 * to the JSON when the post has none, and the JSON thumbnail when the post has no image.
 * With no project posts at all, the JSON is used as it is.
 *
 * @return array<int,array<string,mixed>>
 */
function fnpw_core_map_projects_merged() {
	$json  = fnpw_core_map_projects_from_json();
	$posts = fnpw_core_map_projects_from_query();
	if ( ! $posts ) {
		return $json;
	}
	$by_slug = array();
	foreach ( $json as $row ) {
		$by_slug[ $row['slug'] ] = $row;
	}
	$pillars = fnpw_core_pillars();
	$out     = array();
	foreach ( $posts as $row ) {
		$j = isset( $by_slug[ $row['slug'] ] ) ? $by_slug[ $row['slug'] ] : null;
		if ( $j ) {
			$same = null === $row['lat']
				|| ( isset( $j['lat'], $j['lon'] ) && abs( $row['lat'] - $j['lat'] ) < 0.011 && abs( $row['lon'] - $j['lon'] ) < 0.011 );
			if ( $same && null !== $j['x'] && null !== $j['y'] ) {
				$row['x'] = $j['x'];
				$row['y'] = $j['y'];
			}
			if ( '' === $row['pillar'] && isset( $pillars[ $j['pillar'] ] ) ) {
				$row['pillar']       = $j['pillar'];
				$row['pillar_label'] = $pillars[ $j['pillar'] ][0];
				$row['pillar_class'] = $pillars[ $j['pillar'] ][1];
			}
			// The map's state buttons use the build's short state names.
			if ( '' !== $j['state'] ) {
				$row['state'] = $j['state'];
			}
			if ( '' === $row['img'] ) {
				$row['img'] = $j['img'];
			}
			$row['on_map'] = null !== $row['x'] && null !== $row['y'] && '' !== $row['pillar'] && ( $j['on_map'] || null !== $row['lat'] );
		}
		// A project with no pillar, no state and no pin (a retired or placeholder post) is
		// not map material, and would only inflate the "All" count.
		if ( '' === $row['pillar'] && '' === $row['state'] && ! $row['on_map'] ) {
			continue;
		}
		$out[] = $row;
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
