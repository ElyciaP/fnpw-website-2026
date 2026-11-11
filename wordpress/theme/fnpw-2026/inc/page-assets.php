<?php
/**
 * Per-page styles and scripts carried over from the static build.
 *
 * Most static pages have their own <style> block and some have their own inline
 * <script>. The converter (wordpress/migration/convert.py) sorts them into:
 *
 *   _fnpw_css_files  array of file names in assets/css/shared/ (a block shared by pages)
 *   _fnpw_page_css   string, CSS used by this one page, printed in the head
 *   _fnpw_js_files   array of file names in assets/js/shared/ (a script shared by pages)
 *   _fnpw_ext_js     array of external script URLs (HubSpot embeds), loaded deferred
 *   _fnpw_page_js    string, scripts used by this one page, printed in the footer.
 *                    Separate scripts are divided by FNPW_PAGE_JS_SPLIT and each is
 *                    printed in its own <script>, as on the static page.
 *
 * The rules themselves are never edited: they are the static build's, byte for byte,
 * apart from asset and link URLs.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_PAGE_JS_SPLIT', "\n/*__FNPW_SCRIPT__*/\n" );

/**
 * The post whose page assets apply to this request, or 0.
 *
 * @return int
 */
function fnpw_page_assets_post_id() {
	if ( is_singular() ) {
		return (int) get_queried_object_id();
	}
	return 0;
}

/**
 * A meta value that should be a list of plain file names or URLs.
 *
 * @param int    $post_id Post ID.
 * @param string $key     Meta key.
 * @return string[]
 */
function fnpw_page_assets_list( $post_id, $key ) {
	$value = get_post_meta( $post_id, $key, true );
	if ( is_string( $value ) && '' !== $value ) {
		$decoded = json_decode( $value, true );
		$value   = is_array( $decoded ) ? $decoded : array( $value );
	}
	return is_array( $value ) ? array_values( array_filter( array_map( 'strval', $value ) ) ) : array();
}

function fnpw_page_assets_enqueue() {
	$post_id = fnpw_page_assets_post_id();
	if ( ! $post_id ) {
		return;
	}
	foreach ( fnpw_page_assets_list( $post_id, '_fnpw_css_files' ) as $file ) {
		$file = sanitize_file_name( $file );
		fnpw_style( 'fnpw-shared-' . basename( $file, '.css' ), 'assets/css/shared/' . $file );
	}
	foreach ( fnpw_page_assets_list( $post_id, '_fnpw_ext_js' ) as $i => $url ) {
		if ( 0 === strpos( $url, 'https://' ) ) {
			wp_enqueue_script( 'fnpw-ext-' . md5( $url ), $url, array(), null, array( 'in_footer' => true, 'strategy' => 'defer' ) ); // phpcs:ignore WordPress.WP.EnqueuedResourceParameters.MissingVersion -- third-party embed, versioned by its host.
		}
	}
	foreach ( fnpw_page_assets_list( $post_id, '_fnpw_js_files' ) as $file ) {
		$file = sanitize_file_name( $file );
		fnpw_script( 'fnpw-shared-' . basename( $file, '.js' ), 'assets/js/shared/' . $file );
	}
}
add_action( 'wp_enqueue_scripts', 'fnpw_page_assets_enqueue', 30 );

/**
 * Page CSS, after the enqueued stylesheets (the static pages link global.css first and
 * then open their own <style> block).
 */
function fnpw_page_assets_css() {
	$post_id = fnpw_page_assets_post_id();
	$css     = $post_id ? (string) get_post_meta( $post_id, '_fnpw_page_css', true ) : '';
	if ( '' !== trim( $css ) ) {
		// Not escaped: it is CSS. A closing style tag is the only thing that could break out.
		echo '<style id="fnpw-page-css">' . "\n" . str_ireplace( '</style', '<\/style', $css ) . "\n" . '</style>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	}
}
add_action( 'wp_head', 'fnpw_page_assets_css', 50 );

/**
 * Page scripts, after main.js and the feature scripts.
 */
function fnpw_page_assets_js() {
	$post_id = fnpw_page_assets_post_id();
	$js      = $post_id ? (string) get_post_meta( $post_id, '_fnpw_page_js', true ) : '';
	if ( '' === trim( $js ) ) {
		return;
	}
	foreach ( explode( trim( FNPW_PAGE_JS_SPLIT ), $js ) as $script ) {
		if ( '' !== trim( $script ) ) {
			echo '<script>' . "\n" . str_ireplace( '</script', '<\/script', trim( $script ) ) . "\n" . '</script>' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
		}
	}
}
add_action( 'wp_footer', 'fnpw_page_assets_js', 50 );

/**
 * Only people who may post unfiltered HTML may set the CSS and script meta.
 */
function fnpw_page_assets_register_meta() {
	foreach ( array( '_fnpw_page_css', '_fnpw_page_js', '_fnpw_css_files', '_fnpw_js_files', '_fnpw_ext_js' ) as $key ) {
		register_meta(
			'post',
			$key,
			array(
				'show_in_rest'  => false,
				'auth_callback' => static function () {
					return current_user_can( 'unfiltered_html' );
				},
			)
		);
	}
}
add_action( 'init', 'fnpw_page_assets_register_meta' );

/**
 * The static copy is already typeset (curly quotes, dashes where wanted). WordPress
 * "texturize" would re-guess them and change line lengths, so it is off.
 */
add_filter( 'run_wptexturize', '__return_false' );

/**
 * Likewise the text-to-emoji swap: "8)" in a list of steps is not a smiley.
 */
remove_filter( 'the_content', 'convert_smilies', 20 );
remove_filter( 'the_excerpt', 'convert_smilies' );
