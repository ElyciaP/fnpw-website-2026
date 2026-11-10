<?php
/**
 * Extra project fields (ACF).
 *
 * The live site already has the ACF Pro group "Single - Project" (project_details:
 * start_year, project_latitude, project_longitude, project_state, project_focusarea,
 * first_nations_), saved as JSON by Template Required Plugins. That group is left
 * alone. acf-json/ here holds one small group with only the fields the new project
 * template needs and live lacks: pillar and partner credit line.
 *
 * Without ACF the filter below never runs, so the plugin works (minus those two
 * field boxes) when ACF is not installed.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Add this plugin's acf-json folder to the places ACF loads field groups from.
 *
 * @param string[] $paths Load paths.
 * @return string[]
 */
function fnpw_core_acf_json_load_path( $paths ) {
	$paths   = is_array( $paths ) ? $paths : array();
	$paths[] = FNPW_CORE_DIR . 'acf-json';
	return $paths;
}
add_filter( 'acf/settings/load_json', 'fnpw_core_acf_json_load_path' );

/**
 * The two fields are plain post meta, so expose them to the REST API and the block
 * editor whether or not ACF is running.
 */
function fnpw_core_register_project_meta() {
	if ( ! post_type_exists( 'project' ) ) {
		return;
	}
	foreach ( array( 'pillar', 'partner_credit' ) as $key ) {
		register_post_meta(
			'project',
			$key,
			array(
				'type'              => 'string',
				'single'            => true,
				'show_in_rest'      => true,
				'sanitize_callback' => 'sanitize_text_field',
				'auth_callback'     => static function () {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}
}
add_action( 'init', 'fnpw_core_register_project_meta', 20 );
