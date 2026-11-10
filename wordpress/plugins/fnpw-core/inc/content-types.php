<?php
/**
 * Block-editor support for the content types registered by Template Required Plugins.
 *
 * That plugin registers project, grant and donation (title, editor, thumbnail,
 * revisions) and their taxonomies without show_in_rest, so they open in the classic
 * editor and are missing from the REST API. These filters switch REST on and add the
 * supports the new templates need. Nothing is registered here: if the other plugin is
 * inactive the filters simply never match.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Post types to adjust, by their registered names.
 *
 * @return string[]
 */
function fnpw_core_post_types() {
	return (array) apply_filters( 'fnpw_core_post_types', array( 'project', 'grant', 'donation' ) );
}

/**
 * Taxonomies to adjust, by their registered names.
 *
 * @return string[]
 */
function fnpw_core_taxonomies() {
	return (array) apply_filters( 'fnpw_core_taxonomies', array( 'project_state', 'project_focus_area', 'project_year' ) );
}

/**
 * @param array  $args      Post type arguments.
 * @param string $post_type Post type name.
 * @return array
 */
function fnpw_core_post_type_args( $args, $post_type ) {
	if ( ! in_array( $post_type, fnpw_core_post_types(), true ) ) {
		return $args;
	}
	$args['show_in_rest'] = true;

	$supports = ( isset( $args['supports'] ) && is_array( $args['supports'] ) ) ? $args['supports'] : array( 'title', 'editor' );
	foreach ( array( 'editor', 'excerpt', 'custom-fields' ) as $feature ) {
		if ( ! in_array( $feature, $supports, true ) ) {
			$supports[] = $feature;
		}
	}
	$args['supports'] = $supports;

	return $args;
}
add_filter( 'register_post_type_args', 'fnpw_core_post_type_args', 10, 2 );

/**
 * @param array  $args     Taxonomy arguments.
 * @param string $taxonomy Taxonomy name.
 * @return array
 */
function fnpw_core_taxonomy_args( $args, $taxonomy ) {
	if ( in_array( $taxonomy, fnpw_core_taxonomies(), true ) ) {
		$args['show_in_rest'] = true;
	}
	return $args;
}
add_filter( 'register_taxonomy_args', 'fnpw_core_taxonomy_args', 10, 2 );
