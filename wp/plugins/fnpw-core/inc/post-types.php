<?php
/**
 * Custom post types.
 *
 * The project rewrite slug is 'project' because that is what the live site
 * already uses: every live project sits at /project/<slug>/. Keeping it
 * identical means the 84 project URLs carry across with no redirect at all,
 * which closes the open item in Appendix A of the delivery plan and removes
 * the largest single block of entries from the redirect map.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function fnpw_register_post_types() {

	register_post_type(
		'project',
		array(
			'labels'        => array(
				'name'               => __( 'Projects', 'fnpw-core' ),
				'singular_name'      => __( 'Project', 'fnpw-core' ),
				'add_new_item'       => __( 'Add new project', 'fnpw-core' ),
				'edit_item'          => __( 'Edit project', 'fnpw-core' ),
				'search_items'       => __( 'Search projects', 'fnpw-core' ),
				'not_found'          => __( 'No projects found', 'fnpw-core' ),
			),
			'public'        => true,
			'show_in_rest'  => true,
			'menu_icon'     => 'dashicons-location-alt',
			'menu_position' => 20,
			'has_archive'   => 'projects',
			'rewrite'       => array(
				'slug'       => 'project',
				'with_front' => false,
			),
			'supports'      => array( 'title', 'editor', 'excerpt', 'thumbnail', 'revisions', 'custom-fields', 'page-attributes' ),
			'taxonomies'    => array( 'pillar', 'project_location' ),
		)
	);

	register_post_type(
		'report',
		array(
			'labels'        => array(
				'name'          => __( 'Reports', 'fnpw-core' ),
				'singular_name' => __( 'Report', 'fnpw-core' ),
				'add_new_item'  => __( 'Add new report', 'fnpw-core' ),
				'edit_item'     => __( 'Edit report', 'fnpw-core' ),
			),
			'public'        => true,
			'show_in_rest'  => true,
			'menu_icon'     => 'dashicons-media-document',
			'menu_position' => 21,
			'has_archive'   => 'reports',
			'rewrite'       => array(
				'slug'       => 'report',
				'with_front' => false,
			),
			'supports'      => array( 'title', 'editor', 'excerpt', 'thumbnail', 'revisions', 'custom-fields' ),
		)
	);
}
add_action( 'init', 'fnpw_register_post_types' );
