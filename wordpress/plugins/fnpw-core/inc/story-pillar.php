<?php
/**
 * "Story pillar" box on blog posts.
 *
 * The Stories index and the article hero read the fnpw_pillar field to show the
 * coloured pillar label and to drive the pillar filter. Imported articles carry
 * it already; this box lets editors choose it for new posts.
 *
 * @package fnpw-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Pillar keys and the labels editors see.
 *
 * @return array
 */
function fnpw_core_story_pillars() {
	return array(
		'news'    => 'News & Events',
		'parks'   => 'Growing National Parks',
		'species' => 'Saving Species',
		'heal'    => 'Healing the Land',
	);
}

add_action(
	'add_meta_boxes_post',
	function () {
		add_meta_box( 'fnpw-story-pillar', 'Story pillar', 'fnpw_core_story_pillar_box', 'post', 'side', 'high' );
	}
);

/**
 * Print the box.
 *
 * @param WP_Post $post Post being edited.
 */
function fnpw_core_story_pillar_box( $post ) {
	$current = (string) get_post_meta( $post->ID, 'fnpw_pillar', true );
	if ( 'healing' === $current ) {
		$current = 'heal';
	}
	if ( ! isset( fnpw_core_story_pillars()[ $current ] ) ) {
		$current = 'news';
	}
	wp_nonce_field( 'fnpw_story_pillar', 'fnpw_story_pillar_nonce' );
	echo '<label class="screen-reader-text" for="fnpw-story-pillar-select">Story pillar</label>';
	echo '<select id="fnpw-story-pillar-select" name="fnpw_story_pillar" style="width:100%">';
	foreach ( fnpw_core_story_pillars() as $key => $label ) {
		printf( '<option value="%s"%s>%s</option>', esc_attr( $key ), selected( $current, $key, false ), esc_html( $label ) );
	}
	echo '</select>';
	echo '<p class="description">Sets the coloured label on the story and where it appears in the Stories filter.</p>';
}

add_action(
	'save_post_post',
	function ( $post_id ) {
		if ( ! isset( $_POST['fnpw_story_pillar'], $_POST['fnpw_story_pillar_nonce'] ) ) {
			return;
		}
		if ( ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['fnpw_story_pillar_nonce'] ) ), 'fnpw_story_pillar' ) ) {
			return;
		}
		if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || ! current_user_can( 'edit_post', $post_id ) ) {
			return;
		}
		$key = sanitize_key( wp_unslash( $_POST['fnpw_story_pillar'] ) );
		if ( isset( fnpw_core_story_pillars()[ $key ] ) ) {
			update_post_meta( $post_id, 'fnpw_pillar', $key );
		}
	}
);
