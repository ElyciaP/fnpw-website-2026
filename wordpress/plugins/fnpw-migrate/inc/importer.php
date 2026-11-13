<?php
/**
 * The importer: one package item in, one create / update / skip out.
 *
 * Rules it never breaks:
 *  - it never deletes a post, a term or an attachment;
 *  - it never deletes or blanks post meta it was not given (old ACF fields stay, so the
 *    previous theme still finds its content if it is switched back on);
 *  - before it first overwrites the content of an existing post it saves that content
 *    in _fnpw_migrate_prev_content, and never overwrites that copy again;
 *  - a matched post keeps its ID, date, author, categories and URL.
 *
 * @package fnpw-migrate
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const FNPW_MIGRATE_PREV   = '_fnpw_migrate_prev_content';
const FNPW_MIGRATE_FIELDS = '_fnpw_migrate_prev_fields';
const FNPW_MIGRATE_HASH   = '_fnpw_migrate_hash';

/**
 * item key => post ID for everything the importer has matched or made.
 */
function fnpw_migrate_keymap() {
	$map = get_option( 'fnpw_migrate_keymap' );
	return is_array( $map ) ? $map : array();
}

/**
 * The post a package item refers to, or null.
 *
 * @param array $item Package item.
 * @return WP_Post|null
 */
function fnpw_migrate_find( $item ) {
	$type = isset( $item['post_type'] ) ? (string) $item['post_type'] : 'post';
	$slug = isset( $item['slug'] ) ? sanitize_title( (string) $item['slug'] ) : '';
	$role = isset( $item['role'] ) ? (string) $item['role'] : '';

	// The front page and the posts page are whatever Settings > Reading says they are.
	if ( 'page' === get_option( 'show_on_front' ) ) {
		$id = 0;
		if ( 'front_page' === $role ) {
			$id = (int) get_option( 'page_on_front' );
		} elseif ( 'posts_page' === $role ) {
			$id = (int) get_option( 'page_for_posts' );
		}
		$post = $id ? get_post( $id ) : null;
		if ( $post && 'page' === $post->post_type && 'trash' !== $post->post_status ) {
			return $post;
		}
	}
	if ( '' === $slug ) {
		return null;
	}
	if ( is_post_type_hierarchical( $type ) ) {
		$path = trim( ( isset( $item['parent_path'] ) ? trim( (string) $item['parent_path'], '/' ) . '/' : '' ) . $slug, '/' );
		$post = get_page_by_path( $path, OBJECT, $type );
		return ( $post && 'trash' !== $post->post_status ) ? $post : null;
	}
	$found = get_posts(
		array(
			'name'             => $slug,
			'post_type'        => $type,
			'post_status'      => array( 'publish', 'draft', 'pending', 'private', 'future' ),
			'posts_per_page'   => 1,
			'orderby'          => 'ID',
			'order'            => 'ASC',
			'suppress_filters' => true,
			'no_found_rows'    => true,
		)
	);
	return $found ? $found[0] : null;
}

/**
 * The item as it will be written, with sideloaded media URLs swapped in.
 */
function fnpw_migrate_prepare( $item, $media_map ) {
	foreach ( array( 'content', 'excerpt' ) as $field ) {
		if ( isset( $item[ $field ] ) ) {
			$item[ $field ] = fnpw_migrate_rewrite_media( (string) $item[ $field ], $media_map );
		}
	}
	if ( isset( $item['content'] ) ) {
		$item['content'] = fnpw_migrate_tag_images( $item['content'], $media_map );
	}
	if ( isset( $item['meta'] ) && is_array( $item['meta'] ) ) {
		foreach ( $item['meta'] as $key => $value ) {
			if ( is_string( $value ) ) {
				$item['meta'][ $key ] = fnpw_migrate_rewrite_media( $value, $media_map );
			}
		}
	} else {
		$item['meta'] = array();
	}
	$item['_thumb'] = 0;
	if ( ! empty( $item['featured_image'] ) ) {
		$url = (string) $item['featured_image'];
		if ( isset( $media_map[ $url ]['id'] ) && $media_map[ $url ]['id'] ) {
			$item['_thumb'] = (int) $media_map[ $url ]['id'];
		} elseif ( fnpw_migrate_is_library_url( $url ) ) {
			$item['_thumb'] = fnpw_migrate_library_attachment( $url );
		}
	}
	return $item;
}

/**
 * Fingerprint of everything the importer would write for an item.
 */
function fnpw_migrate_hash( $item ) {
	$parts = array();
	foreach ( array( 'post_type', 'slug', 'parent_path', 'title', 'content', 'excerpt', 'template', 'menu_order', 'status', 'date', 'meta', 'terms', '_thumb' ) as $field ) {
		if ( array_key_exists( $field, $item ) ) {
			$parts[ $field ] = $item[ $field ];
		}
	}
	return sha1( (string) wp_json_encode( $parts ) );
}

/**
 * Terms of an item as taxonomy => term IDs, plus notes about any that are missing.
 *
 * @return array{0:array<string,int[]>,1:string[]}
 */
function fnpw_migrate_terms( $item, $create, $apply ) {
	$out   = array();
	$notes = array();
	if ( empty( $item['terms'] ) || ! is_array( $item['terms'] ) ) {
		return array( $out, $notes );
	}
	foreach ( $item['terms'] as $taxonomy => $slugs ) {
		if ( ! taxonomy_exists( $taxonomy ) ) {
			$notes[] = 'taxonomy ' . $taxonomy . ' is not registered, terms not set';
			continue;
		}
		$ids = array();
		foreach ( (array) $slugs as $slug ) {
			$slug = sanitize_title( (string) $slug );
			$term = get_term_by( 'slug', $slug, $taxonomy );
			if ( $term ) {
				$ids[] = (int) $term->term_id;
			} elseif ( $create ) {
				if ( $apply ) {
					$made = wp_insert_term( ucwords( str_replace( '-', ' ', $slug ) ), $taxonomy, array( 'slug' => $slug ) );
					if ( is_wp_error( $made ) ) {
						$notes[] = 'could not create term ' . $slug . ': ' . $made->get_error_message();
					} else {
						$ids[]   = (int) $made['term_id'];
						$notes[] = 'created term ' . $taxonomy . '/' . $slug;
					}
				} else {
					$notes[] = 'would create term ' . $taxonomy . '/' . $slug;
				}
			} else {
				$notes[] = 'term ' . $taxonomy . '/' . $slug . ' does not exist and the package does not allow creating terms';
			}
		}
		$out[ $taxonomy ] = $ids;
	}
	return array( $out, $notes );
}

/**
 * Import one item.
 *
 * @param array $item    Package item.
 * @param bool  $apply   False for a dry run.
 * @param array $options media_map, create_terms.
 * @return array{action:string,post_id:int,message:string,key:string}
 */
function fnpw_migrate_item( $item, $apply, $options ) {
	$key  = isset( $item['key'] ) ? (string) $item['key'] : ( ( isset( $item['post_type'] ) ? $item['post_type'] : '?' ) . ':' . ( isset( $item['slug'] ) ? $item['slug'] : '?' ) );
	$type = isset( $item['post_type'] ) ? (string) $item['post_type'] : '';
	$done = static function ( $action, $post_id, $message ) use ( $key ) {
		return array( 'action' => $action, 'post_id' => (int) $post_id, 'message' => $message, 'key' => $key );
	};

	if ( '' === $type || ! post_type_exists( $type ) ) {
		return $done( 'error', 0, 'Post type "' . $type . '" is not registered on this site (is its plugin active?).' );
	}
	if ( empty( $item['slug'] ) ) {
		return $done( 'error', 0, 'Item has no slug.' );
	}

	$item     = fnpw_migrate_prepare( $item, isset( $options['media_map'] ) ? $options['media_map'] : array() );
	$hash     = fnpw_migrate_hash( $item );
	$existing = fnpw_migrate_find( $item );
	$notes    = array();

	// Parent page.
	$parent_id = null;
	if ( is_post_type_hierarchical( $type ) && array_key_exists( 'parent_path', $item ) ) {
		$parent_path = trim( (string) $item['parent_path'], '/' );
		if ( '' === $parent_path ) {
			$parent_id = 0;
		} else {
			$parent = get_page_by_path( $parent_path, OBJECT, $type );
			if ( $parent ) {
				$parent_id = (int) $parent->ID;
			} elseif ( $apply ) {
				return $done( 'error', $existing ? $existing->ID : 0, 'Parent page /' . $parent_path . '/ does not exist.' );
			} else {
				$notes[] = 'parent /' . $parent_path . '/ does not exist yet (fine if this package creates it)';
			}
		}
	}

	list( $terms, $term_notes ) = fnpw_migrate_terms( $item, ! empty( $options['create_terms'] ), $apply );
	$notes                      = array_merge( $notes, $term_notes );

	if ( $existing && get_post_meta( $existing->ID, FNPW_MIGRATE_HASH, true ) === $hash ) {
		if ( $apply ) {
			fnpw_migrate_refresh_seo( $existing->ID );
		}
		return $done( 'skip', $existing->ID, 'Unchanged since the last import.' );
	}

	if ( $existing && 'publish' !== $existing->post_status ) {
		$notes[] = 'the existing ' . $type . ' is "' . $existing->post_status . '" and stays that way (publish it by hand if it should be live)';
	}

	// What will change, for the report.
	$changes = array();
	foreach ( array( 'title' => 'post_title', 'content' => 'post_content', 'excerpt' => 'post_excerpt' ) as $field => $column ) {
		if ( array_key_exists( $field, $item ) && ( ! $existing || (string) $existing->$column !== (string) $item[ $field ] ) ) {
			$changes[] = $field;
		}
	}
	if ( null !== $parent_id && $existing && (int) $existing->post_parent !== $parent_id ) {
		$changes[] = 'parent';
	}
	if ( array_key_exists( 'menu_order', $item ) && $existing && (int) $existing->menu_order !== (int) $item['menu_order'] ) {
		$changes[] = 'menu order';
	}
	$template = isset( $item['template'] ) ? (string) $item['template'] : '';
	if ( '' !== $template && ( ! $existing || get_post_meta( $existing->ID, '_wp_page_template', true ) !== $template ) ) {
		$changes[] = 'template ' . $template;
	}
	if ( $item['_thumb'] && ( ! $existing || (int) get_post_thumbnail_id( $existing->ID ) !== $item['_thumb'] ) ) {
		$changes[] = 'featured image';
	} elseif ( ! empty( $item['featured_image'] ) && ! $item['_thumb'] ) {
		$notes[] = 'featured image not in the media library, left as it is';
	}
	$meta_changed = 0;
	foreach ( $item['meta'] as $meta_key => $value ) {
		if ( ! $existing || get_post_meta( $existing->ID, $meta_key, true ) != $value ) { // phpcs:ignore Universal.Operators.StrictComparisons -- stored values come back as strings.
			++$meta_changed;
		}
	}
	if ( $meta_changed ) {
		$changes[] = $meta_changed . ' meta field' . ( 1 === $meta_changed ? '' : 's' );
	}
	if ( $terms ) {
		$changes[] = 'terms';
	}
	$summary = ( $changes ? implode( ', ', $changes ) : 'import fingerprint only' ) . ( $notes ? '. Notes: ' . implode( '; ', $notes ) : '' );

	if ( ! $apply ) {
		if ( $existing ) {
			$first = ! metadata_exists( 'post', $existing->ID, FNPW_MIGRATE_PREV ) && in_array( 'content', $changes, true );
			return $done( 'update', $existing->ID, 'Would update: ' . $summary . ( $first ? '. Current content will be saved for restore.' : '' ) );
		}
		return $done( 'create', 0, 'Would create ' . $type . ' "' . $item['slug'] . '": ' . $summary );
	}

	// ---- apply -------------------------------------------------------------------
	$postarr = array();
	foreach ( array( 'title' => 'post_title', 'content' => 'post_content', 'excerpt' => 'post_excerpt' ) as $field => $column ) {
		if ( array_key_exists( $field, $item ) ) {
			$postarr[ $column ] = (string) $item[ $field ];
		}
	}
	if ( null !== $parent_id ) {
		$postarr['post_parent'] = $parent_id;
	}
	if ( array_key_exists( 'menu_order', $item ) ) {
		$postarr['menu_order'] = (int) $item['menu_order'];
	}

	if ( $existing ) {
		$post_id = (int) $existing->ID;
		// Keep the previous content once, before the first overwrite, and never again.
		if ( array_key_exists( 'content', $item ) && ! metadata_exists( 'post', $post_id, FNPW_MIGRATE_PREV ) ) {
			add_post_meta( $post_id, FNPW_MIGRATE_PREV, wp_slash( $existing->post_content ), true );
			add_post_meta(
				$post_id,
				FNPW_MIGRATE_FIELDS,
				wp_slash(
					array(
						'title'     => $existing->post_title,
						'excerpt'   => $existing->post_excerpt,
						'parent'    => (int) $existing->post_parent,
						'template'  => metadata_exists( 'post', $post_id, '_wp_page_template' ) ? (string) get_post_meta( $post_id, '_wp_page_template', true ) : null,
						'thumbnail' => (int) get_post_thumbnail_id( $post_id ),
						'saved'     => gmdate( 'c' ),
					)
				),
				true
			);
		}
		if ( metadata_exists( 'post', $post_id, '_fnpw_migrate_unpublished' ) ) {
			// A rollback set this imported post to draft: publish it again.
			$postarr['post_status'] = isset( $item['status'] ) ? sanitize_key( (string) $item['status'] ) : 'publish';
			delete_post_meta( $post_id, '_fnpw_migrate_unpublished' );
		}
		if ( $postarr ) {
			$postarr['ID'] = $post_id;
			// wp_update_post() re-submits the page template it finds on the post. A template
			// of the previous theme is "invalid" under this one, which fails the update, or
			// worse resets the template to default. An empty value leaves the meta alone.
			$postarr['page_template'] = '';
			$result        = wp_update_post( wp_slash( $postarr ), true );
			if ( is_wp_error( $result ) ) {
				return $done( 'error', $post_id, 'Update failed: ' . $result->get_error_message() );
			}
		}
		$action = 'update';
	} else {
		$postarr['post_type']   = $type;
		$postarr['post_name']   = sanitize_title( (string) $item['slug'] );
		$postarr['post_status'] = isset( $item['status'] ) ? sanitize_key( (string) $item['status'] ) : 'draft';
		if ( ! isset( $postarr['post_title'] ) ) {
			$postarr['post_title'] = ucwords( str_replace( '-', ' ', (string) $item['slug'] ) );
		}
		if ( ! empty( $item['date'] ) ) {
			$postarr['post_date'] = gmdate( 'Y-m-d H:i:s', (int) strtotime( (string) $item['date'] ) );
		}
		$post_id = wp_insert_post( wp_slash( $postarr ), true );
		if ( is_wp_error( $post_id ) ) {
			return $done( 'error', 0, 'Create failed: ' . $post_id->get_error_message() );
		}
		$post_id = (int) $post_id;
		add_post_meta( $post_id, '_fnpw_migrate_created', gmdate( 'c' ), true );
		$action = 'create';
	}

	if ( '' !== $template ) {
		update_post_meta( $post_id, '_wp_page_template', wp_slash( $template ) );
	}
	if ( $item['_thumb'] ) {
		set_post_thumbnail( $post_id, $item['_thumb'] );
	}
	// Only the keys in the package are written. Nothing else on the post is touched.
	foreach ( $item['meta'] as $meta_key => $value ) {
		update_post_meta( $post_id, (string) $meta_key, wp_slash( $value ) );
	}
	foreach ( $terms as $taxonomy => $ids ) {
		if ( $ids ) {
			wp_set_object_terms( $post_id, $ids, $taxonomy, false );
		}
	}
	update_post_meta( $post_id, FNPW_MIGRATE_HASH, $hash );
	fnpw_migrate_refresh_seo( $post_id );

	$keymap         = fnpw_migrate_keymap();
	$keymap[ $key ] = $post_id;
	update_option( 'fnpw_migrate_keymap', $keymap, false );

	return $done( $action, $post_id, ( 'create' === $action ? 'Created: ' : 'Updated: ' ) . $summary );
}

/**
 * Put back the content a post had before its first import. The saved copy stays, and
 * the import fingerprint is removed so the next import updates the post again.
 *
 * @param int $post_id Post ID.
 * @return true|WP_Error
 */
function fnpw_migrate_restore( $post_id ) {
	$post_id = (int) $post_id;
	$post    = get_post( $post_id );
	if ( ! $post || ! metadata_exists( 'post', $post_id, FNPW_MIGRATE_PREV ) ) {
		return new WP_Error( 'fnpw_migrate_no_prev', 'Post ' . $post_id . ' has no saved previous content.' );
	}
	$fields  = get_post_meta( $post_id, FNPW_MIGRATE_FIELDS, true );
	$postarr = array(
		'ID'            => $post_id,
		'post_content'  => (string) get_post_meta( $post_id, FNPW_MIGRATE_PREV, true ),
		'page_template' => '', // Leave the template meta alone; see fnpw_migrate_item().
	);
	if ( is_array( $fields ) ) {
		if ( isset( $fields['title'] ) ) {
			$postarr['post_title'] = (string) $fields['title'];
		}
		if ( isset( $fields['excerpt'] ) ) {
			$postarr['post_excerpt'] = (string) $fields['excerpt'];
		}
		if ( isset( $fields['parent'] ) ) {
			$postarr['post_parent'] = (int) $fields['parent'];
		}
	}
	$filtered = fnpw_migrate_kses_off();
	$result   = wp_update_post( wp_slash( $postarr ), true );
	fnpw_migrate_kses_on( $filtered );
	if ( is_wp_error( $result ) ) {
		return $result;
	}
	if ( is_array( $fields ) ) {
		if ( array_key_exists( 'template', $fields ) && null !== $fields['template'] ) {
			update_post_meta( $post_id, '_wp_page_template', wp_slash( (string) $fields['template'] ) );
		}
		if ( ! empty( $fields['thumbnail'] ) && get_post( (int) $fields['thumbnail'] ) ) {
			set_post_thumbnail( $post_id, (int) $fields['thumbnail'] );
		}
	}
	delete_post_meta( $post_id, FNPW_MIGRATE_HASH );
	return true;
}

/**
 * Yoast SEO reads titles and descriptions from its own index table, not straight from
 * post meta, and that index is built when a post is saved. The import writes the SEO
 * fields after the save, so the index entry is rebuilt here. If Yoast's builder is not
 * available the stale entry is removed, and Yoast builds a fresh one on the next view.
 *
 * @param int $post_id Post ID.
 */
function fnpw_migrate_refresh_seo( $post_id ) {
	$post_id = (int) $post_id;
	if ( ! $post_id || ! function_exists( 'YoastSEO' ) ) {
		return;
	}
	$stale = false;
	try {
		$classes   = YoastSEO()->classes;
		$repo      = $classes->get( 'Yoast\\WP\\SEO\\Repositories\\Indexable_Repository' );
		$builder   = $classes->get( 'Yoast\\WP\\SEO\\Builders\\Indexable_Builder' );
		$indexable = $repo->find_by_id_and_type( $post_id, 'post', false );
		$builder->build_for_id_and_type( $post_id, 'post', $indexable ? $indexable : false );
		// Yoast does not save its index outside production (a staging site, say), so check
		// the stored entry really carries the new title.
		$stored = $repo->find_by_id_and_type( $post_id, 'post', false );
		$want   = (string) get_post_meta( $post_id, '_yoast_wpseo_title', true );
		$stale  = $stored && '' !== $want && (string) $stored->title !== $want;
	} catch ( \Throwable $e ) {
		$stale = true;
	}
	if ( $stale ) {
		global $wpdb;
		$wpdb->delete( $wpdb->prefix . 'yoast_indexable', array( 'object_id' => $post_id, 'object_type' => 'post' ) ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery
	}
}

/**
 * Posts the import created (they have no previous content to restore).
 *
 * @return int[]
 */
function fnpw_migrate_created() {
	global $wpdb;
	return array_map( 'intval', $wpdb->get_col( $wpdb->prepare( "SELECT pm.post_id FROM {$wpdb->postmeta} pm JOIN {$wpdb->posts} p ON p.ID = pm.post_id WHERE pm.meta_key = %s AND p.post_status <> 'trash' ORDER BY pm.post_id ASC", '_fnpw_migrate_created' ) ) ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery
}

/**
 * Rollback for a post the import created: set it to draft and mark it, so the next
 * import publishes it again.
 *
 * @param int $post_id Post ID.
 * @return true|WP_Error
 */
function fnpw_migrate_unpublish( $post_id ) {
	$post_id = (int) $post_id;
	if ( 'publish' !== get_post_status( $post_id ) ) {
		return true; // Already offline: leave it as the editor left it.
	}
	$result  = wp_update_post( array( 'ID' => $post_id, 'post_status' => 'draft', 'page_template' => '' ), true );
	if ( is_wp_error( $result ) ) {
		return $result;
	}
	update_post_meta( $post_id, '_fnpw_migrate_unpublished', gmdate( 'c' ) );
	delete_post_meta( $post_id, FNPW_MIGRATE_HASH );
	return true;
}

/**
 * IDs of every post that has saved previous content.
 *
 * @return int[]
 */
function fnpw_migrate_restorable() {
	global $wpdb;
	return array_map( 'intval', $wpdb->get_col( $wpdb->prepare( "SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id ASC", FNPW_MIGRATE_PREV ) ) ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery
}

/**
 * The imported markup holds scripts, iframes and style attributes, which the content
 * filters would strip. The import screen is limited to people who may post unfiltered
 * HTML, so the filters are lifted for the write and put straight back.
 *
 * @return bool Whether the filters were on.
 */
function fnpw_migrate_kses_off() {
	$on = false !== has_filter( 'content_save_pre', 'wp_filter_post_kses' );
	if ( $on ) {
		kses_remove_filters();
	}
	return $on;
}

function fnpw_migrate_kses_on( $was_on ) {
	if ( $was_on ) {
		kses_init_filters();
	}
}

/**
 * Set Settings > Reading from the package. Only called on an explicit tick at apply time.
 *
 * @return string[] What was done.
 */
function fnpw_migrate_apply_reading( $package, $apply ) {
	$out      = array();
	$settings = isset( $package['settings'] ) && is_array( $package['settings'] ) ? $package['settings'] : array();
	$find     = static function ( $key ) use ( $package ) {
		foreach ( $package['items'] as $item ) {
			if ( isset( $item['key'] ) && $item['key'] === $key ) {
				$post = fnpw_migrate_find( $item );
				return $post ? (int) $post->ID : 0;
			}
		}
		return 0;
	};
	$front    = ! empty( $settings['front_page'] ) ? $find( $settings['front_page'] ) : 0;
	$posts    = ! empty( $settings['posts_page'] ) ? $find( $settings['posts_page'] ) : 0;
	if ( ! $front && ! $posts ) {
		$out[] = 'The package names no front page or posts page that exists on this site yet.';
		return $out;
	}
	if ( $front ) {
		$out[] = ( $apply ? 'Front page set to' : 'Would set the front page to' ) . ' page ' . $front . ' (' . get_the_title( $front ) . '), was ' . (int) get_option( 'page_on_front' ) . '.';
	}
	if ( $posts ) {
		$out[] = ( $apply ? 'Posts page set to' : 'Would set the posts page to' ) . ' page ' . $posts . ' (' . get_the_title( $posts ) . '), was ' . (int) get_option( 'page_for_posts' ) . '.';
	}
	if ( $apply ) {
		update_option( 'show_on_front', 'page' );
		if ( $front ) {
			update_option( 'page_on_front', $front );
		}
		if ( $posts ) {
			update_option( 'page_for_posts', $posts );
		}
	}
	return $out;
}
