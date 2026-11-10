<?php
/**
 * Server-rendered template blocks.
 *
 * The templates need a handful of dynamic pieces (article hero, project hero, card
 * grids, search results) whose markup has to match the static build class for class,
 * which core's Query Loop and Post Title blocks cannot produce. Each is a small
 * PHP-rendered block with no build step. They are template furniture, not inserter
 * blocks; "autoRegister" lets WordPress 7.0 preview them in the Site Editor.
 *
 * Markup in every callback is taken from the static pages named in its comment.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Register the blocks.
 */
function fnpw_register_template_blocks() {
	$blocks = array(
		'article-hero'     => array( 'Article hero', 'fnpw_render_article_hero' ),
		'keep-reading'     => array( 'Keep reading', 'fnpw_render_keep_reading' ),
		'project-hero'     => array( 'Project hero', 'fnpw_render_project_hero' ),
		'related-projects' => array( 'Related projects', 'fnpw_render_related_projects' ),
		'archive-hero'     => array( 'Archive hero', 'fnpw_render_archive_hero' ),
		'post-grid'        => array( 'Story grid', 'fnpw_render_post_grid' ),
		'project-grid'     => array( 'Project grid', 'fnpw_render_project_grid' ),
		'search-results'   => array( 'Search form and results', 'fnpw_render_search_results' ),
	);
	foreach ( $blocks as $name => $def ) {
		register_block_type(
			'fnpw/' . $name,
			array(
				'api_version'     => 3,
				'title'           => $def[0],
				'category'        => 'theme',
				'render_callback' => $def[1],
				'attributes'      => array(
					'eyebrow' => array( 'type' => 'string', 'default' => '' ),
				),
				'supports'        => array(
					'html'         => false,
					'inserter'     => false,
					'autoRegister' => true,
				),
			)
		);
	}
}
add_action( 'init', 'fnpw_register_template_blocks' );

/**
 * Two small adjustments to core/post-content so the DOM matches the static build:
 *
 * - tagName "main": add id="main" (skip-link target), and still print the <main> when
 *   the page has no content yet.
 * - className "fnpw-unwrap": drop the wrapper element, so the imported sections sit
 *   directly inside <main> next to the template's own sections. global.css relies on
 *   that (".pj-main .sec + .sec", snap.js "main > section").
 *
 * @param string $html  Rendered block.
 * @param array  $block Parsed block.
 * @return string
 */
function fnpw_post_content_markup( $html, $block ) {
	$attrs = isset( $block['attrs'] ) ? $block['attrs'] : array();

	if ( isset( $attrs['tagName'] ) && 'main' === $attrs['tagName'] ) {
		if ( '' === trim( $html ) ) {
			return '<main id="main"></main>';
		}
		$tags = new WP_HTML_Tag_Processor( $html );
		if ( $tags->next_tag( 'main' ) && null === $tags->get_attribute( 'id' ) ) {
			$tags->set_attribute( 'id', 'main' );
			$html = $tags->get_updated_html();
		}
		return $html;
	}

	if ( isset( $attrs['className'] ) && false !== strpos( $attrs['className'], 'fnpw-unwrap' ) ) {
		$html  = trim( $html );
		$open  = strpos( $html, '>' );
		$close = strrpos( $html, '</' );
		if ( false !== $open && false !== $close && $close > $open ) {
			$html = substr( $html, $open + 1, $close - $open - 1 );
		}
	}
	return $html;
}
add_filter( 'render_block_core/post-content', 'fnpw_post_content_markup', 10, 2 );

/* ---------------------------------------------------------------------------
 * Helpers
 * ------------------------------------------------------------------------- */

/**
 * Breadcrumb trail. Items are array( label, url ); a null url is the current page.
 *
 * @param array  $items Trail after Home.
 * @param string $class Class on the nav ("breadcrumb" or "ed-crumb").
 * @param string $style Optional inline style carried over from the static markup.
 * @return string
 */
function fnpw_breadcrumb( $items, $class = 'breadcrumb', $style = '' ) {
	$out = sprintf(
		'<nav aria-label="Breadcrumb" class="%s"%s><a href="%s">Home</a>',
		esc_attr( $class ),
		$style ? ' style="' . esc_attr( $style ) . '"' : '',
		esc_url( home_url( '/' ) )
	);
	foreach ( $items as $item ) {
		$out .= '<span>/</span>';
		$out .= empty( $item[1] )
			? esc_html( $item[0] )
			: sprintf( '<a href="%s">%s</a>', esc_url( $item[1] ), esc_html( $item[0] ) );
	}
	return $out . '</nav>';
}

/**
 * Attachment ID of a post's hero image: the featured image, else the banner_image
 * field of the live site's ACF group "Single - Header" (posts, projects, grants,
 * donations), so existing content keeps its hero without re-entering it.
 *
 * @param int $post_id Post ID.
 * @return int 0 when there is none.
 */
function fnpw_hero_image_id( $post_id ) {
	$id = (int) get_post_thumbnail_id( $post_id );
	if ( ! $id ) {
		$banner = get_post_meta( $post_id, 'banner_image', true );
		$id     = is_numeric( $banner ) ? (int) $banner : 0;
	}
	return $id;
}

/**
 * Whole-minute reading time for a post. Same sum as the static generator
 * (tools/gen_articles.py): 220 words a minute, never less than two minutes.
 *
 * @param int $post_id Post ID.
 * @return int
 */
function fnpw_reading_minutes( $post_id ) {
	$words = str_word_count( wp_strip_all_tags( strip_shortcodes( (string) get_post_field( 'post_content', $post_id ) ) ) );
	return max( 2, (int) round( $words / 220 ) );
}

/**
 * Numbered pagination for the main query. The static build has no server-side paging,
 * so this is the one component with its own small rules in wp-compat.css.
 *
 * @return string
 */
function fnpw_pagination() {
	$links = paginate_links(
		array(
			'type'      => 'array',
			'mid_size'  => 1,
			'prev_text' => '&#8592; ' . __( 'Newer', 'fnpw-2026' ),
			'next_text' => __( 'Older', 'fnpw-2026' ) . ' &#8594;',
		)
	);
	if ( empty( $links ) ) {
		return '';
	}
	return '<nav class="fnpw-pager" aria-label="' . esc_attr__( 'Pages', 'fnpw-2026' ) . '">' . implode( '', $links ) . '</nav>';
}

/**
 * Pillar of a project as array( label, slug ) where slug is parks, species or healing.
 * Reads the "pillar" field added by FNPW Core, then falls back to the focus-area terms
 * the live site already has.
 *
 * @param int $post_id Project ID.
 * @return array{0:string,1:string}|null
 */
function fnpw_project_pillar( $post_id ) {
	$pillars = array(
		'parks'   => 'Growing National Parks',
		'species' => 'Saving Species',
		'healing' => 'Healing the Land',
	);
	$value   = (string) get_post_meta( $post_id, 'pillar', true );
	if ( isset( $pillars[ $value ] ) ) {
		return array( $pillars[ $value ], $value );
	}
	$found = array_search( $value, $pillars, true );
	if ( false !== $found ) {
		return array( $value, $found );
	}
	if ( taxonomy_exists( 'project_focus_area' ) ) {
		$terms = get_the_terms( $post_id, 'project_focus_area' );
		if ( is_array( $terms ) ) {
			foreach ( $terms as $term ) {
				if ( false !== strpos( $term->slug, 'park' ) ) {
					return array( $pillars['parks'], 'parks' );
				}
				if ( false !== strpos( $term->slug, 'species' ) ) {
					return array( $pillars['species'], 'species' );
				}
				if ( false !== strpos( $term->slug, 'heal' ) ) {
					return array( $pillars['healing'], 'healing' );
				}
			}
		}
	}
	return null;
}

/**
 * Comma-separated names of a post's terms in a taxonomy, or '' if there are none.
 *
 * @param int    $post_id  Post ID.
 * @param string $taxonomy Taxonomy.
 * @return string
 */
function fnpw_term_names( $post_id, $taxonomy ) {
	if ( ! taxonomy_exists( $taxonomy ) ) {
		return '';
	}
	$terms = get_the_terms( $post_id, $taxonomy );
	return is_array( $terms ) ? implode( ', ', wp_list_pluck( $terms, 'name' ) ) : '';
}

/**
 * One project card. Markup: the .pc tiles on the static project pages.
 *
 * @param int $post_id Project ID.
 * @return string
 */
function fnpw_project_card( $post_id ) {
	$pillar = fnpw_project_pillar( $post_id );
	$state  = fnpw_term_names( $post_id, 'project_state' );
	$title  = get_the_title( $post_id );
	$hero   = fnpw_hero_image_id( $post_id );
	$image  = $hero ? wp_get_attachment_image_url( $hero, 'large' ) : '';

	$out  = '<article class="pc">' . "\n";
	$out .= '  <a href="' . esc_url( get_permalink( $post_id ) ) . '" class="pc-link">' . "\n";
	$out .= '    <div class="pc-im">';
	if ( $image ) {
		$out .= '<img src="' . esc_url( $image ) . '" alt="' . esc_attr( $title ) . '" loading="lazy" decoding="async">';
	}
	if ( $pillar ) {
		$out .= "\n" . '      <span class="pc-pb pb-' . esc_attr( $pillar[1] ) . '">' . esc_html( $pillar[0] ) . '</span>';
	}
	if ( $state ) {
		$out .= "\n" . '      <span class="pc-lo">' . esc_html( $state ) . '</span>';
	}
	$out .= "\n" . '    </div>' . "\n";
	$out .= '    <div class="pc-bd"><h3>' . esc_html( $title ) . '</h3></div>' . "\n";
	$out .= '  </a>' . "\n" . '</article>';
	return $out;
}

/* ---------------------------------------------------------------------------
 * Articles (static source: article-*.html)
 * ------------------------------------------------------------------------- */

function fnpw_render_article_hero() {
	$post_id = get_queried_object_id();
	if ( ! $post_id ) {
		return '';
	}
	$hero   = fnpw_hero_image_id( $post_id );
	$image  = $hero
		? wp_get_attachment_image(
			$hero,
			'full',
			false,
			array(
				'sizes'         => '100vw',
				'fetchpriority' => 'high',
				'decoding'      => 'async',
				'loading'       => false,
			)
		)
		: '';
	$kicker = (string) get_post_meta( $post_id, 'fnpw_kicker', true );
	if ( '' === $kicker && 'post' === get_post_type( $post_id ) ) {
		$cats = get_the_category( $post_id );
		if ( $cats && 'uncategorized' !== $cats[0]->slug ) {
			$kicker = $cats[0]->name;
		}
	}

	$out = '<header class="ed-hero' . ( $image ? '' : ' ed-hero-flat' ) . '">' . "\n";
	if ( $image ) {
		$out .= '    <figure class="ed-hero-im">' . $image . '</figure>' . "\n";
	}
	$out .= '    <div class="cw">' . "\n";
	$out .= '      ' . fnpw_breadcrumb( array( array( 'Articles', fnpw_url( 'articles' ) ) ), 'ed-crumb' ) . "\n";
	if ( '' !== $kicker ) {
		$out .= '      <span class="ed-kicker ed-kicker-top">' . esc_html( $kicker ) . '</span>' . "\n";
	}
	$out .= '      <h1>' . wp_kses_post( get_the_title( $post_id ) ) . '</h1>' . "\n";
	if ( has_excerpt( $post_id ) ) {
		$out .= '      <p class="ed-stand">' . esc_html( get_the_excerpt( $post_id ) ) . '</p>' . "\n";
	}
	$out .= sprintf(
		'      <p class="ed-meta">%s &nbsp;&middot;&nbsp; %d min read</p>' . "\n",
		esc_html( get_the_date( 'F Y', $post_id ) ),
		fnpw_reading_minutes( $post_id )
	);
	$out .= '    </div>' . "\n" . '  </header>';
	return $out;
}

function fnpw_render_keep_reading() {
	$current = get_queried_object_id();
	$args    = array(
		'post_type'           => 'post',
		'posts_per_page'      => 3,
		'post__not_in'        => array( $current ),
		'ignore_sticky_posts' => true,
		'no_found_rows'       => true,
	);
	$cats    = wp_get_post_categories( $current );
	if ( $cats ) {
		$args['category__in'] = $cats;
	}
	$posts = get_posts( $args );
	if ( ! $posts ) {
		return '';
	}

	$out  = '<section class="sec sand ed-more">' . "\n" . '  <div class="cw rv">' . "\n";
	$out .= '    <span class="ey">Keep reading</span>' . "\n" . '    <h2>More from the field.</h2>' . "\n";
	$out .= '    <div class="pj-readgrid">' . "\n";
	foreach ( $posts as $post ) {
		$out .= '      <a class="pj-rcard" href="' . esc_url( get_permalink( $post ) ) . '">' . "\n";
		if ( has_post_thumbnail( $post ) ) {
			$out .= '        ' . get_the_post_thumbnail(
				$post,
				'large',
				array(
					'class'    => 'pj-rcard-im',
					'loading'  => 'lazy',
					'decoding' => 'async',
				)
			) . "\n";
		}
		$out .= '        <div class="pj-rcard-bd">' . "\n";
		$out .= '          <span class="pj-rd">' . esc_html( get_the_date( 'F Y', $post ) ) . '</span>' . "\n";
		$out .= '          <h3>' . esc_html( get_the_title( $post ) ) . '</h3>' . "\n";
		$out .= '          <p>' . esc_html( get_the_excerpt( $post ) ) . '</p>' . "\n";
		$out .= '          <span class="pj-rgo">Read the story &#8594;</span>' . "\n";
		$out .= '        </div>' . "\n" . '      </a>' . "\n";
	}
	$out .= '    </div>' . "\n" . '  </div>' . "\n" . '</section>';
	return $out;
}

/* ---------------------------------------------------------------------------
 * Projects (static source: project-*.html)
 * ------------------------------------------------------------------------- */

function fnpw_render_project_hero() {
	$post_id = get_queried_object_id();
	if ( ! $post_id ) {
		return '';
	}
	$title  = get_the_title( $post_id );
	$pillar = fnpw_project_pillar( $post_id );
	$hero   = fnpw_hero_image_id( $post_id );
	$image  = $hero ? wp_get_attachment_image_url( $hero, 'full' ) : '';

	// "NSW · Funded 2018", from the project_state and project_year taxonomies (the live
	// ACF start_year field is a taxonomy field that saves to project_year).
	$meta  = array();
	$state = fnpw_term_names( $post_id, 'project_state' );
	if ( $state ) {
		$meta[] = esc_html( $state );
	}
	$year = fnpw_term_names( $post_id, 'project_year' );
	if ( '' !== $year ) {
		$meta[] = 'Funded ' . esc_html( $year );
	}

	$out = '<section class="ch chi"' . ( $image ? ' style="--chi:url(\'' . esc_url( $image ) . '\')"' : '' ) . '>' . "\n";
	$out .= '  <div class="cw rv">' . "\n";
	$out .= '    ' . fnpw_breadcrumb(
		array(
			array( 'Projects', fnpw_url( 'projects' ) ),
			array( $title, null ),
		),
		'breadcrumb',
		'display:flex;gap:.5em;font-size:.82rem;margin-bottom:1.5rem'
	) . "\n";
	if ( $pillar ) {
		$out .= '    <span class="ey">' . esc_html( $pillar[0] ) . '</span>' . "\n";
	}
	$out .= '    <h1 style="margin:1rem 0 1.2rem;max-width:22ch">' . wp_kses_post( $title ) . '</h1>' . "\n";
	if ( $meta ) {
		$out .= '    <p class="pj-hero-meta">' . implode( ' &nbsp;&nbsp;&middot;&nbsp;&nbsp; ', $meta ) . '</p>' . "\n";
	}
	if ( has_excerpt( $post_id ) ) {
		$out .= '    <p class="lede">' . esc_html( get_the_excerpt( $post_id ) ) . '</p>' . "\n";
	}
	$out .= '  </div>' . "\n" . '</section>';
	return $out;
}

function fnpw_render_related_projects() {
	$current = get_queried_object_id();
	if ( ! $current || ! post_type_exists( 'project' ) ) {
		return '';
	}
	$args = array(
		'post_type'      => 'project',
		'posts_per_page' => 3,
		'post__not_in'   => array( $current ),
		'no_found_rows'  => true,
	);
	// Same pillar first, as on the static pages ("More from this pillar").
	$pillar = fnpw_project_pillar( $current );
	if ( $pillar ) {
		$labels             = array(
			'parks'   => 'Growing National Parks',
			'species' => 'Saving Species',
			'healing' => 'Healing the Land',
		);
		$args['meta_query'] = array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query -- three rows, single template.
			array(
				'key'     => 'pillar',
				'value'   => array( $pillar[1], $labels[ $pillar[1] ] ),
				'compare' => 'IN',
			),
		);
	}
	$posts = get_posts( $args );
	if ( ! $posts && $pillar ) {
		unset( $args['meta_query'] );
		$posts = get_posts( $args );
	}
	if ( ! $posts ) {
		return '';
	}

	$out  = '<section class="sec sand">' . "\n" . '  <div class="cw rv">' . "\n";
	$out .= '<span class="ey">More from this pillar</span><h2 style="margin:.8rem 0 1.6rem">Related projects</h2><div class="pg">';
	foreach ( $posts as $post ) {
		$out .= fnpw_project_card( $post->ID ) . "\n";
	}
	$out .= '</div>' . "\n" . '  </div>' . "\n" . '</section>';
	return $out;
}

/* ---------------------------------------------------------------------------
 * Archives
 * ------------------------------------------------------------------------- */

/**
 * Sand hero (.ch) for category, tag, project and project-taxonomy archives: breadcrumb,
 * eyebrow, the archive's own title and its description when one is set.
 *
 * @param array $attributes Block attributes; "eyebrow" overrides the default eyebrow.
 * @return string
 */
function fnpw_render_archive_hero( $attributes ) {
	$trail   = array();
	$eyebrow = '';
	$title   = '';
	$lede    = '';

	if ( is_post_type_archive( 'project' ) ) {
		$title   = post_type_archive_title( '', false );
		$trail[] = array( 'Projects', null );
	} elseif ( is_tax() ) {
		$term     = get_queried_object();
		$taxonomy = get_taxonomy( $term->taxonomy );
		$title    = $term->name;
		$eyebrow  = $taxonomy ? $taxonomy->labels->singular_name : '';
		$lede     = term_description();
		$trail[]  = array( 'Projects', fnpw_url( 'projects' ) );
		$trail[]  = array( $title, null );
	} elseif ( is_category() || is_tag() ) {
		$title   = single_term_title( '', false );
		$lede    = term_description();
		$trail[] = array( 'Articles', fnpw_url( 'articles' ) );
		$trail[] = array( $title, null );
	} else {
		$title   = wp_strip_all_tags( get_the_archive_title() );
		$trail[] = array( $title, null );
	}
	if ( ! empty( $attributes['eyebrow'] ) ) {
		$eyebrow = $attributes['eyebrow'];
	}

	$out  = '<section class="ch">' . "\n" . '  <div class="cw rv">' . "\n";
	$out .= '    ' . fnpw_breadcrumb( $trail, 'breadcrumb', 'display:flex;gap:.5em;font-size:.82rem;margin-bottom:1.5rem' ) . "\n";
	if ( '' !== $eyebrow ) {
		$out .= '    <span class="ey">' . esc_html( $eyebrow ) . '</span>' . "\n";
	}
	$out .= '    <h1 style="margin:1rem 0 1.2rem">' . esc_html( $title ) . '</h1>' . "\n";
	if ( '' !== trim( wp_strip_all_tags( (string) $lede ) ) ) {
		$out .= '    <p class="lede">' . esc_html( wp_strip_all_tags( $lede ) ) . '</p>' . "\n";
	}
	$out .= '  </div>' . "\n" . '</section>';
	return $out;
}

/**
 * The main query as story tiles. Markup: the .art tiles on articles.html.
 */
function fnpw_render_post_grid() {
	global $wp_query;

	$out = '<section>' . "\n" . '  <div class="cw">';
	if ( ! $wp_query->have_posts() ) {
		return $out . '<div class="art-grid"><p>' . esc_html__( 'There are no stories here yet.', 'fnpw-2026' ) . '</p></div></div>' . "\n" . '</section>';
	}
	$out .= '<div class="art-grid">' . "\n";
	foreach ( $wp_query->posts as $post ) {
		$kicker = (string) get_post_meta( $post->ID, 'fnpw_kicker', true );
		$cats   = get_the_category( $post->ID );
		$cat    = ( $cats && 'uncategorized' !== $cats[0]->slug ) ? $cats[0]->name : '';
		$date   = get_the_date( 'F Y', $post );

		$out .= '    <a href="' . esc_url( get_permalink( $post ) ) . '" class="art rv">' . "\n";
		$out .= '      <div class="art-im">';
		if ( has_post_thumbnail( $post ) ) {
			$out .= get_the_post_thumbnail(
				$post,
				'large',
				array(
					'loading'  => 'lazy',
					'decoding' => 'async',
				)
			);
		}
		if ( '' !== $cat ) {
			$out .= '<span class="cat">' . esc_html( $cat ) . '</span>';
		}
		$out .= '</div>' . "\n";
		$out .= '      <div class="art-bd">' . "\n";
		$out .= '        <div class="art-date">' . esc_html( $date ) . ( '' !== $kicker ? ' &middot; ' . esc_html( $kicker ) : '' ) . '</div>' . "\n";
		$out .= '        <h3>' . esc_html( get_the_title( $post ) ) . '</h3>' . "\n";
		$out .= '        <p>' . esc_html( get_the_excerpt( $post ) ) . '</p>' . "\n";
		$out .= '        <span class="art-link">Read more</span>' . "\n";
		$out .= '      </div>' . "\n" . '    </a>' . "\n";
	}
	$out .= '  </div>' . fnpw_pagination() . '</div>' . "\n" . '</section>';
	return $out;
}

/**
 * The main query as project cards, for the project archive and its three taxonomies.
 */
function fnpw_render_project_grid() {
	global $wp_query;

	$out = '<section class="sec">' . "\n" . '  <div class="cw rv">' . "\n";
	if ( ! $wp_query->have_posts() ) {
		return $out . '<p>' . esc_html__( 'There are no projects here yet.', 'fnpw-2026' ) . '</p>' . "\n" . '  </div>' . "\n" . '</section>';
	}
	$out .= '<div class="pg">';
	foreach ( $wp_query->posts as $post ) {
		$out .= fnpw_project_card( $post->ID ) . "\n";
	}
	$out .= '</div>' . fnpw_pagination() . "\n" . '  </div>' . "\n" . '</section>';
	return $out;
}

/* ---------------------------------------------------------------------------
 * Search (static source: search.html). The static page searched an inline index in
 * the browser; here the same form posts to WordPress search and the results list is
 * printed by the server.
 * ------------------------------------------------------------------------- */

function fnpw_render_search_results() {
	global $wp_query;

	$query = get_search_query( false );
	$hero  = 'assets/img/search-hero-koala.jpg';

	$out = '<section class="pj-hero srch-hero">' . "\n";
	if ( file_exists( get_theme_file_path( $hero ) ) ) {
		$out .= '  <figure class="pj-hero-im"><img src="' . esc_url( get_theme_file_uri( $hero ) ) . '" alt="A koala climbing along a branch through eucalypt woodland" style="object-position:62% 40%" width="1600" height="1066" fetchpriority="high" decoding="async"></figure>' . "\n";
	}
	$out .= '  <div class="cw rv">' . "\n";
	$out .= '    ' . fnpw_breadcrumb( array( array( 'Search', null ) ), 'breadcrumb', 'display:flex;gap:.5em;font-size:.82rem;flex-wrap:wrap' ) . "\n";
	$out .= '    <span class="ey">Search</span>' . "\n";
	$out .= '    <h1>Branch out and explore.</h1>' . "\n";
	$out .= '    <p class="lede">Search our projects, stories, reports and ways to get involved.</p>' . "\n";
	$out .= '  </div>' . "\n" . '</section>';

	$out .= '<section class="sec ">' . "\n" . '  <div class="cw rv">' . "\n";
	$out .= '<form class="srch-f" id="sf" role="search" method="get" action="' . esc_url( home_url( '/' ) ) . '">' . "\n";
	$out .= '  <label for="q" class="srch-l">What are you looking for?</label>' . "\n";
	$out .= '  <div class="srch-row"><input id="q" name="s" class="srch" type="search" value="' . esc_attr( $query ) . '" placeholder="Try: koala, volunteering, gifts in wills" autocomplete="off"><button type="submit" class="srch-b">Search</button></div>' . "\n";
	$out .= '</form>' . "\n";

	if ( '' !== trim( $query ) ) {
		$found = (int) $wp_query->found_posts;
		$out  .= '<p class="srch-n" id="rn" aria-live="polite">' . esc_html(
			sprintf(
				/* translators: 1: number of results, 2: search term. */
				_n( '%1$s result for "%2$s"', '%1$s results for "%2$s"', $found, 'fnpw-2026' ),
				number_format_i18n( $found ),
				$query
			)
		) . '</p>' . "\n";
		$out .= '<ul id="res" class="srch-res">';
		foreach ( $wp_query->posts as $post ) {
			$out .= '<li><a href="' . esc_url( get_permalink( $post ) ) . '">' . esc_html( get_the_title( $post ) ) . '</a></li>';
		}
		$out .= '</ul>' . "\n" . fnpw_pagination();
	} else {
		$out .= '<p class="srch-n" id="rn" aria-live="polite"></p>' . "\n" . '<ul id="res" class="srch-res"></ul>' . "\n";
	}
	$out .= '  </div>' . "\n" . '</section>';
	return $out;
}
