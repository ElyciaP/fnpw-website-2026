<?php
/**
 * Project fields.
 *
 * Registered through register_post_meta with show_in_rest, so every field is
 * available to the block editor, to the REST API and to anything that reads
 * the site as structured data later, including the Backyard Buddies work in
 * the phase after this one. No field plugin required.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function fnpw_register_project_meta() {

	$fields = array(
		'fnpw_credit' => array(
			'type'        => 'string',
			'description' => 'Partner, sponsor, grant round and funder credit line shown at the foot of the project page.',
			'default'     => '',
		),
		'fnpw_lat'    => array(
			'type'        => 'number',
			'description' => 'Latitude for the national project map.',
			'default'     => 0,
		),
		'fnpw_lon'    => array(
			'type'        => 'number',
			'description' => 'Longitude for the national project map.',
			'default'     => 0,
		),
		'fnpw_on_map' => array(
			'type'        => 'boolean',
			'description' => 'Whether this project appears on the national project map.',
			'default'     => true,
		),
		'fnpw_legacy_url' => array(
			'type'        => 'string',
			'description' => 'The original live URL, kept for redirect verification at launch.',
			'default'     => '',
		),
	);

	foreach ( $fields as $key => $args ) {
		register_post_meta(
			'project',
			$key,
			array(
				'type'              => $args['type'],
				'description'       => $args['description'],
				'default'           => $args['default'],
				'single'            => true,
				'show_in_rest'      => true,
				'sanitize_callback' => 'fnpw_sanitize_meta_' . $args['type'],
				'auth_callback'     => function () {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}
}
add_action( 'init', 'fnpw_register_project_meta' );

function fnpw_sanitize_meta_string( $value ) {
	return wp_kses_post( $value );
}

function fnpw_sanitize_meta_number( $value ) {
	return (float) $value;
}

function fnpw_sanitize_meta_boolean( $value ) {
	return (bool) $value;
}
