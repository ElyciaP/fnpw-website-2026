<?php
/**
 * Taxonomies.
 *
 * Pillar is the organisation's own strategic structure, so it is a taxonomy
 * rather than a field: it drives archives, filtering and the REST API.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function fnpw_register_taxonomies() {

	register_taxonomy(
		'pillar',
		array( 'project', 'report', 'post' ),
		array(
			'labels'            => array(
				'name'          => __( 'Pillars', 'fnpw-core' ),
				'singular_name' => __( 'Pillar', 'fnpw-core' ),
			),
			'public'            => true,
			'hierarchical'      => true,
			'show_in_rest'      => true,
			'show_admin_column' => true,
			'rewrite'           => array( 'slug' => 'pillar', 'with_front' => false ),
		)
	);

	register_taxonomy(
		'project_location',
		array( 'project' ),
		array(
			'labels'            => array(
				'name'          => __( 'Locations', 'fnpw-core' ),
				'singular_name' => __( 'Location', 'fnpw-core' ),
			),
			'public'            => true,
			'hierarchical'      => false,
			'show_in_rest'      => true,
			'show_admin_column' => true,
			'rewrite'           => array( 'slug' => 'where', 'with_front' => false ),
		)
	);
}
add_action( 'init', 'fnpw_register_taxonomies' );

/**
 * Seed the three pillars on activation so the terms exist with the right names
 * and slugs, rather than being typed differently by different people later.
 */
function fnpw_seed_pillars() {
	$pillars = array(
		'growing-national-parks' => 'Growing National Parks',
		'saving-species'         => 'Saving Species',
		'healing-the-land'       => 'Healing the Land',
	);

	foreach ( $pillars as $slug => $name ) {
		if ( ! term_exists( $slug, 'pillar' ) ) {
			wp_insert_term( $name, 'pillar', array( 'slug' => $slug ) );
		}
	}
}
add_action( 'admin_init', 'fnpw_seed_pillars' );
