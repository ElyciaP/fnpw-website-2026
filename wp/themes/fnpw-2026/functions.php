<?php
/**
 * FNPW 2026 block theme.
 *
 * Deliberately thin. The design system lives in theme.json, components live in
 * patterns, and the Project and Report content types live in the fnpw-core
 * plugin so they survive any future theme change.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FNPW_THEME_VERSION', '0.1.0' );

/**
 * Theme supports.
 */
function fnpw_setup() {
	add_theme_support( 'wp-block-styles' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'title-tag' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'post-thumbnails' );
	add_editor_style( 'assets/css/global.css' );
	load_theme_textdomain( 'fnpw-2026', get_template_directory() . '/languages' );
}
add_action( 'after_setup_theme', 'fnpw_setup' );

/**
 * Front-end assets.
 *
 * global.css is the component layer ported from the static build. It is
 * versioned by file modification time so a deploy busts the cache without a
 * manual version bump.
 */
function fnpw_assets() {
	$dir = get_template_directory();
	$uri = get_template_directory_uri();

	wp_enqueue_style(
		'fnpw-global',
		$uri . '/assets/css/global.css',
		array(),
		(string) filemtime( $dir . '/assets/css/global.css' )
	);

	wp_enqueue_style(
		'fnpw-components',
		$uri . '/assets/css/components.css',
		array( 'fnpw-global' ),
		(string) filemtime( $dir . '/assets/css/components.css' )
	);

	wp_enqueue_script(
		'fnpw-main',
		$uri . '/assets/js/main.js',
		array(),
		(string) filemtime( $dir . '/assets/js/main.js' ),
		true
	);
}
add_action( 'wp_enqueue_scripts', 'fnpw_assets' );

/**
 * Pattern categories, so the component library is browsable in the inserter.
 */
function fnpw_pattern_categories() {
	$categories = array(
		'fnpw-page'    => __( 'FNPW page sections', 'fnpw-2026' ),
		'fnpw-cta'     => __( 'FNPW calls to action', 'fnpw-2026' ),
		'fnpw-content' => __( 'FNPW content blocks', 'fnpw-2026' ),
	);

	foreach ( $categories as $slug => $label ) {
		register_block_pattern_category( $slug, array( 'label' => $label ) );
	}
}
add_action( 'init', 'fnpw_pattern_categories' );

/**
 * Remove the core pattern directory so the inserter shows FNPW patterns only.
 */
remove_theme_support( 'core-block-patterns' );

/**
 * Preload the two variable fonts actually used above the fold.
 */
function fnpw_preload_fonts() {
	if ( ! fnpw_fonts_are_self_hosted() ) {
		return;
	}

	$uri   = get_template_directory_uri() . '/assets/fonts/';
	$fonts = array( 'sora-variable.woff2', 'figtree-variable.woff2' );

	foreach ( $fonts as $font ) {
		if ( file_exists( get_template_directory() . '/assets/fonts/' . $font ) ) {
			printf(
				'<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n",
				esc_url( $uri . $font )
			);
		}
	}
}
add_action( 'wp_head', 'fnpw_preload_fonts', 1 );

/**
 * Font loading.
 *
 * Self-hosted variable fonts are preferred, because a third-party font request
 * is a measurable cost against Core Web Vitals. Until the woff2 files are in
 * assets/fonts/, fall back to Google Fonts so the theme never renders in a
 * system font. Run wp/tools/fetch-fonts.sh to self-host, then this falls away
 * on its own.
 */
function fnpw_fonts_are_self_hosted() {
	return file_exists( get_template_directory() . '/assets/fonts/sora-variable.woff2' )
		&& file_exists( get_template_directory() . '/assets/fonts/figtree-variable.woff2' );
}

function fnpw_google_fonts_fallback() {
	if ( fnpw_fonts_are_self_hosted() ) {
		return;
	}

	wp_enqueue_style(
		'fnpw-google-fonts',
		'https://fonts.googleapis.com/css2?family=Sora:wght@300..800&family=Figtree:wght@300..900&display=swap',
		array(),
		null
	);
}
add_action( 'wp_enqueue_scripts', 'fnpw_google_fonts_fallback' );

function fnpw_google_fonts_preconnect( $urls, $relation_type ) {
	if ( 'preconnect' === $relation_type && ! fnpw_fonts_are_self_hosted() ) {
		$urls[] = array( 'href' => 'https://fonts.gstatic.com', 'crossorigin' => 'anonymous' );
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'fnpw_google_fonts_preconnect', 10, 2 );

/**
 * ---------------------------------------------------------------------------
 * Head metadata (WP7). Mirrors tools/meta.py on the static build: canonical,
 * Open Graph and Twitter tags, icon links and the Organization JSON-LD, built
 * from WordPress data so the WP plugin and the theme need no SEO plugin for
 * the basics. The static build's SITE_URL becomes home_url() here.
 * ---------------------------------------------------------------------------
 */
define( 'FNPW_ORG_NAME', 'Foundation for National Parks & Wildlife' );
define( 'FNPW_ORG_ABN', '90 107 744 771' );
define( 'FNPW_ORG_PHONE', '+61 1800 898 626' );
define( 'FNPW_ORG_EMAIL', 'fnpw@fnpw.org.au' );

function fnpw_org_same_as() {
	return array(
		'https://www.facebook.com/fnpwaustralia/',
		'https://www.instagram.com/fnpwaustralia/',
		'https://au.linkedin.com/company/foundation-for-national-parks-%26-wildlife',
	);
}

/** Absolute URL of the organisation logo: the Customizer logo, else the theme copy. */
function fnpw_logo_url() {
	$id = (int) get_theme_mod( 'custom_logo' );
	if ( $id ) {
		$url = wp_get_attachment_image_url( $id, 'full' );
		if ( $url ) {
			return $url;
		}
	}
	return get_theme_file_uri( 'assets/img/fnpw-logo.png' );
}

/** The page's share image: featured image, else the site-wide 1200x630 fallback. */
function fnpw_meta_image() {
	if ( is_singular() && has_post_thumbnail() ) {
		$url = get_the_post_thumbnail_url( get_queried_object_id(), 'full' );
		if ( $url ) {
			return array( $url, false );
		}
	}
	return array( get_theme_file_uri( 'assets/img/og-default.jpg' ), true );
}

/** Meta description: the excerpt (hand-written or generated) trimmed to 155 characters. */
function fnpw_meta_description() {
	$text = '';
	if ( is_singular() ) {
		$text = get_the_excerpt( get_queried_object_id() );
	} elseif ( is_front_page() || is_home() ) {
		$text = get_bloginfo( 'description', 'display' );
	} elseif ( is_post_type_archive() ) {
		$obj  = get_queried_object();
		$text = $obj && ! empty( $obj->description ) ? $obj->description : '';
	} elseif ( is_category() || is_tag() || is_tax() ) {
		$text = term_description();
	}
	$text = trim( wp_strip_all_tags( html_entity_decode( (string) $text, ENT_QUOTES, 'UTF-8' ) ) );
	$text = preg_replace( '/\s+/', ' ', $text );
	if ( mb_strlen( $text ) > 155 ) {
		$cut  = mb_substr( $text, 0, 152 );
		$text = mb_substr( $cut, 0, (int) mb_strrpos( $cut, ' ' ) ) . '...';
	}
	return $text;
}

/** Canonical URL of the current request. */
function fnpw_canonical_url() {
	if ( is_front_page() ) {
		return home_url( '/' );
	}
	if ( is_singular() ) {
		return get_permalink( get_queried_object_id() );
	}
	if ( is_post_type_archive() ) {
		return get_post_type_archive_link( get_post_type() );
	}
	if ( is_category() || is_tag() || is_tax() ) {
		$link = get_term_link( get_queried_object() );
		return is_wp_error( $link ) ? '' : $link;
	}
	if ( is_home() ) {
		return get_permalink( (int) get_option( 'page_for_posts' ) ) ?: home_url( '/' );
	}
	return '';
}

function fnpw_organization_ld() {
	return array(
		'@context'        => 'https://schema.org',
		'@type'           => 'Organization',
		'@id'             => home_url( '/#organization' ),
		'name'            => FNPW_ORG_NAME,
		'legalName'       => FNPW_ORG_NAME,
		'alternateName'   => 'FNPW',
		'url'             => home_url( '/' ),
		'logo'            => array( '@type' => 'ImageObject', 'url' => fnpw_logo_url() ),
		'taxID'           => FNPW_ORG_ABN,
		'nonprofitStatus' => 'NonprofitType',
		'foundingDate'    => '1970',
		'sameAs'          => fnpw_org_same_as(),
		'contactPoint'    => array(
			'@type'             => 'ContactPoint',
			'contactType'       => 'customer service',
			'telephone'         => FNPW_ORG_PHONE,
			'email'             => FNPW_ORG_EMAIL,
			'areaServed'        => 'AU',
			'availableLanguage' => 'en',
		),
		'address'         => array(
			'@type'           => 'PostalAddress',
			'addressLocality' => 'Sydney',
			'addressRegion'   => 'NSW',
			'addressCountry'  => 'AU',
		),
	);
}

function fnpw_website_ld() {
	return array(
		'@context'        => 'https://schema.org',
		'@type'           => 'WebSite',
		'@id'             => home_url( '/#website' ),
		'url'             => home_url( '/' ),
		'name'            => FNPW_ORG_NAME,
		'publisher'       => array( '@id' => home_url( '/#organization' ) ),
		'inLanguage'      => 'en-AU',
		'potentialAction' => array(
			'@type'       => 'SearchAction',
			'target'      => array( '@type' => 'EntryPoint', 'urlTemplate' => home_url( '/?s={search_term_string}' ) ),
			'query-input' => 'required name=search_term_string',
		),
	);
}

function fnpw_print_ld( $data ) {
	printf(
		'<script type="application/ld+json">%s</script>' . "\n",
		wp_json_encode( $data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG )
	);
}

function fnpw_head_meta() {
	if ( is_admin() || is_404() ) {
		return;
	}
	$title       = wp_get_document_title();
	$description = fnpw_meta_description();
	$canonical   = fnpw_canonical_url();
	list( $image, $is_fallback ) = fnpw_meta_image();
	$type        = is_singular( 'post' ) ? 'article' : 'website';

	if ( $description ) {
		printf( '<meta name="description" content="%s">' . "\n", esc_attr( $description ) );
	}
	if ( $canonical ) {
		printf( '<link rel="canonical" href="%s">' . "\n", esc_url( $canonical ) );
	}
	$og = array(
		'og:type'        => $type,
		'og:site_name'   => FNPW_ORG_NAME,
		'og:locale'      => 'en_AU',
		'og:title'       => $title,
		'og:description' => $description,
		'og:url'         => $canonical,
		'og:image'       => $image,
	);
	if ( $is_fallback ) {
		$og['og:image:width']  = '1200';
		$og['og:image:height'] = '630';
	}
	if ( is_singular( 'post' ) ) {
		$og['article:published_time'] = get_the_date( 'c', get_queried_object_id() );
		$og['article:modified_time']  = get_the_modified_date( 'c', get_queried_object_id() );
	}
	foreach ( $og as $property => $content ) {
		if ( '' === $content ) {
			continue;
		}
		$value = ( 'og:url' === $property || 'og:image' === $property ) ? esc_url( $content ) : esc_attr( $content );
		printf( '<meta property="%s" content="%s">' . "\n", esc_attr( $property ), $value );
	}
	$twitter = array(
		'twitter:card'        => 'summary_large_image',
		'twitter:title'       => $title,
		'twitter:description' => $description,
		'twitter:image'       => $image,
	);
	foreach ( $twitter as $name => $content ) {
		if ( '' === $content ) {
			continue;
		}
		$value = ( 'twitter:image' === $name ) ? esc_url( $content ) : esc_attr( $content );
		printf( '<meta name="%s" content="%s">' . "\n", esc_attr( $name ), $value );
	}

	// Icon links from the theme, unless a Site Icon is set in the Customizer (WordPress prints that itself).
	if ( ! has_site_icon() ) {
		printf( '<link rel="icon" href="%s" type="image/svg+xml">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/favicon.svg' ) ) );
		printf( '<link rel="icon" href="%s" sizes="32x32" type="image/png">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/favicon-32.png' ) ) );
		printf( '<link rel="apple-touch-icon" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/apple-touch-icon.png' ) ) );
	}

	fnpw_print_ld( fnpw_organization_ld() );
	if ( is_front_page() ) {
		fnpw_print_ld( fnpw_website_ld() );
	}
}
add_action( 'wp_head', 'fnpw_head_meta', 2 );

/** Core prints its own canonical on singular pages; ours covers every view, so drop the duplicate. */
remove_action( 'wp_head', 'rel_canonical' );

/**
 * Robots: keep search results and the thin archives out of the index.
 */
function fnpw_robots( $robots ) {
	if ( is_search() || is_attachment() || is_author() || is_date() ) {
		$robots['noindex'] = true;
		$robots['follow']  = true;
		unset( $robots['index'] );
	}
	return $robots;
}
add_filter( 'wp_robots', 'fnpw_robots' );
