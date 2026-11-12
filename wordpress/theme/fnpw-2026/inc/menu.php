<?php
/**
 * Main menu: editable under Appearance > Menus, drawn with the static build's markup.
 *
 * global.css and main.js expect the header's own markup (a link, or a .ng group
 * holding a button and a .dd list), so the menu is not printed with wp_nav_menu().
 * The Search link and the Donate button are fixed in the header pattern.
 *
 * @package fnpw-2026
 */

defined( 'ABSPATH' ) || exit;

const FNPW_MENU_LOCATION = 'fnpw_primary';
const FNPW_MENU_NAME     = 'Main menu (FNPW 2026)';

add_action(
	'after_setup_theme',
	function () {
		register_nav_menus( array( FNPW_MENU_LOCATION => __( 'Main menu (header)', 'fnpw-2026' ) ) );
	}
);

/**
 * The menu as designed in the static build. Used until a menu is assigned, and
 * to create the starting menu when the theme is activated.
 * Each item: label, static file key, optional dropdown id and children.
 *
 * @return array
 */
function fnpw_default_menu() {
	return array(
		array( 'label' => 'About', 'key' => 'about' ),
		array(
			'label'    => 'Projects',
			'id'       => 'dd-projects',
			'children' => array(
				array( 'label' => 'All Projects', 'key' => 'projects' ),
				array( 'label' => 'Growing National Parks', 'key' => 'growing-national-parks' ),
				array( 'label' => 'Saving Species', 'key' => 'saving-species' ),
				array( 'label' => 'Healing the Land', 'key' => 'healing-the-land' ),
			),
		),
		array(
			'label'    => 'Partner With Us',
			'id'       => 'dd-partner',
			'children' => array(
				array( 'label' => 'Ways to Partner', 'key' => 'partner-invest' ),
				array( 'label' => 'Government Partnerships', 'key' => 'government-partnerships' ),
				array( 'label' => 'Corporate Partnerships', 'key' => 'partner' ),
			),
		),
		array(
			'label'    => 'Impact',
			'id'       => 'dd-impact',
			'children' => array(
				array( 'label' => 'Our Impact', 'key' => 'our-impact' ),
				array( 'label' => 'Impact Reports', 'key' => 'reports' ),
			),
		),
		array(
			'label'    => 'Get Involved',
			'id'       => 'dd-involved',
			'children' => array(
				array( 'label' => 'Ways to Get Involved', 'key' => 'ways-you-can-get-involved' ),
				array( 'label' => 'Corporate Volunteering', 'key' => 'volunteer' ),
				array( 'label' => 'Workplace Giving', 'key' => 'workplace-giving' ),
				array( 'label' => 'Fundraising', 'key' => 'fundraising-with-fnpw' ),
				array( 'label' => 'Gifts in Wills', 'key' => 'bequests' ),
				array( 'label' => 'Donate Land', 'key' => 'donate-land' ),
			),
		),
		array(
			'label'    => 'Stories',
			'id'       => 'dd-stories',
			'children' => array(
				array( 'label' => 'Articles', 'key' => 'articles' ),
			),
		),
		array( 'label' => 'Contact Us', 'key' => 'contact' ),
	);
}

/**
 * The assigned menu as a two-level list of label, url and children, or the
 * default menu when none is assigned or it is empty.
 *
 * @return array
 */
function fnpw_menu_tree() {
	$tree      = array();
	$locations = get_nav_menu_locations();
	$items     = empty( $locations[ FNPW_MENU_LOCATION ] ) ? array() : wp_get_nav_menu_items( $locations[ FNPW_MENU_LOCATION ] );

	if ( $items ) {
		$top = array();
		foreach ( $items as $item ) {
			$node = array(
				'label' => $item->title,
				'url'   => $item->url,
			);
			$parent = (int) $item->menu_item_parent;
			if ( 0 === $parent ) {
				$node['id']        = 'dd-' . (int) $item->ID;
				$node['children']  = array();
				$top[ $item->ID ]  = count( $tree );
				$tree[]            = $node;
			} elseif ( isset( $top[ $parent ] ) ) {
				$tree[ $top[ $parent ] ]['children'][] = $node;
			}
			// Deeper levels are not part of the header design and are left out.
		}
		return $tree;
	}

	foreach ( fnpw_default_menu() as $item ) {
		$node = array( 'label' => $item['label'] );
		if ( isset( $item['key'] ) ) {
			$node['url'] = fnpw_url( $item['key'] );
		}
		if ( isset( $item['children'] ) ) {
			$node['id']       = $item['id'];
			$node['children'] = array();
			foreach ( $item['children'] as $child ) {
				$node['children'][] = array(
					'label' => $child['label'],
					'url'   => fnpw_url( $child['key'] ),
				);
			}
		}
		$tree[] = $node;
	}
	return $tree;
}

/**
 * ' on' when the link is the current section, matching the static build.
 *
 * @param string $url Link address.
 * @return string
 */
function fnpw_menu_on( $url ) {
	if ( ! did_action( 'wp' ) ) {
		return '';
	}
	$key = fnpw_active_nav_key();
	if ( '' === (string) $key ) {
		return '';
	}
	return untrailingslashit( $url ) === untrailingslashit( fnpw_url( $key ) ) ? ' on' : '';
}

/**
 * The menu links, in the static header's markup.
 *
 * @return string
 */
function fnpw_primary_nav_items() {
	$out = '';
	foreach ( fnpw_menu_tree() as $item ) {
		if ( empty( $item['children'] ) ) {
			if ( empty( $item['url'] ) ) {
				continue;
			}
			$out .= sprintf( "    <a href=\"%s\" class=\"%s\">%s</a>\n", esc_url( $item['url'] ), esc_attr( fnpw_menu_on( $item['url'] ) ), esc_html( $item['label'] ) );
			continue;
		}
		$out .= "    <div class=\"ng\">\n";
		$out .= sprintf( "      <button aria-expanded=\"false\" aria-controls=\"%s\">%s <span class=\"ar\">▾</span></button>\n", esc_attr( $item['id'] ), esc_html( $item['label'] ) );
		$out .= sprintf( "      <div class=\"dd\" id=\"%s\">\n", esc_attr( $item['id'] ) );
		foreach ( $item['children'] as $child ) {
			$out .= sprintf( "        <a href=\"%s\" class=\"%s\">%s</a>\n", esc_url( $child['url'] ), esc_attr( fnpw_menu_on( $child['url'] ) ), esc_html( $child['label'] ) );
		}
		$out .= "      </div>\n    </div>\n";
	}
	return $out;
}

/**
 * Create the starting menu once, when the theme is first activated (or on the
 * next admin visit if it was already active). Pages are linked as pages where they exist, so
 * the link follows the page if its address changes.
 */
function fnpw_seed_menu() {
	// Runs once. WordPress carries the old theme's menu into this location when
	// themes are switched, so an assigned location is not a sign that the
	// designed menu exists. After this first run the assignment is left alone.
	if ( get_option( 'fnpw_2026_menu_seeded' ) ) {
		return;
	}
	$locations = get_nav_menu_locations();
	$menu = wp_get_nav_menu_object( FNPW_MENU_NAME );
	if ( ! $menu ) {
		$menu_id = wp_create_nav_menu( FNPW_MENU_NAME );
		if ( is_wp_error( $menu_id ) ) {
			return;
		}
		$add = function ( $label, $key, $parent ) use ( $menu_id ) {
			$args = array(
				'menu-item-title'     => $label,
				'menu-item-status'    => 'publish',
				'menu-item-parent-id' => $parent,
				'menu-item-type'      => 'custom',
				'menu-item-url'       => $key ? fnpw_url( $key ) : '#',
			);
			$page_id = $key ? url_to_postid( fnpw_url( $key ) ) : 0;
			if ( $page_id && 'page' === get_post_type( $page_id ) && (int) get_option( 'page_for_posts' ) !== $page_id ) {
				$args['menu-item-type']      = 'post_type';
				$args['menu-item-object']    = 'page';
				$args['menu-item-object-id'] = $page_id;
				unset( $args['menu-item-url'] );
			}
			return wp_update_nav_menu_item( $menu_id, 0, $args );
		};
		foreach ( fnpw_default_menu() as $item ) {
			$parent = $add( $item['label'], isset( $item['key'] ) ? $item['key'] : '', 0 );
			if ( is_wp_error( $parent ) || empty( $item['children'] ) ) {
				continue;
			}
			foreach ( $item['children'] as $child ) {
				$add( $child['label'], $child['key'], $parent );
			}
		}
	} else {
		$menu_id = $menu->term_id;
	}
	$locations[ FNPW_MENU_LOCATION ] = $menu_id;
	set_theme_mod( 'nav_menu_locations', $locations );
	update_option( 'fnpw_2026_menu_seeded', 1, false );
}
add_action( 'after_switch_theme', 'fnpw_seed_menu' );
add_action( 'admin_init', 'fnpw_seed_menu' );
