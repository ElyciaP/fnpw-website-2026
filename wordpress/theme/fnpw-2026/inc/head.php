<?php
/**
 * Head output: font preloads, icons and (only without Yoast SEO) canonical, Open Graph,
 * Twitter and JSON-LD metadata.
 *
 * @package fnpw-2026
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Fonts (WP6, Nov 2026): Sora and Figtree are self-hosted.
 *
 * The variable woff2 files live in assets/fonts/ and the @font-face rules sit at the top
 * of assets/css/global.css, so the theme never needs a third-party font request. Both
 * files are preloaded from wp_head so the first paint already has them.
 *
 * Google Fonts is an explicit opt-in only, for a site where the files cannot be served:
 *
 *     add_filter( 'fnpw_google_fonts_fallback', '__return_true' );
 *
 * It defaults to off; with it off nothing is requested from fonts.googleapis.com.
 */
function fnpw_fonts_are_self_hosted() {
	return file_exists( get_template_directory() . '/assets/fonts/sora-variable.woff2' )
		&& file_exists( get_template_directory() . '/assets/fonts/figtree-variable.woff2' );
}

function fnpw_use_google_fonts() {
	/**
	 * Load Sora and Figtree from Google Fonts instead of the self-hosted files.
	 *
	 * @param bool $use Default false: fonts are self-hosted.
	 */
	return (bool) apply_filters( 'fnpw_google_fonts_fallback', false );
}

function fnpw_preload_fonts() {
	if ( fnpw_use_google_fonts() ) {
		return;
	}

	$uri   = get_template_directory_uri() . '/assets/fonts/';
	$fonts = array( 'sora-variable.woff2', 'figtree-variable.woff2' );

	foreach ( $fonts as $font ) {
		if ( file_exists( get_template_directory() . '/assets/fonts/' . $font ) ) {
			printf(
				'<link rel="preload" as="font" type="font/woff2" crossorigin href="%s">' . "\n",
				esc_url( $uri . $font )
			);
		}
	}
}
add_action( 'wp_head', 'fnpw_preload_fonts', 1 );

function fnpw_google_fonts_fallback() {
	if ( ! fnpw_use_google_fonts() ) {
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
	if ( 'preconnect' === $relation_type && fnpw_use_google_fonts() ) {
		$urls[] = array( 'href' => 'https://fonts.gstatic.com', 'crossorigin' => 'anonymous' );
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'fnpw_google_fonts_preconnect', 10, 2 );

/**
 * ---------------------------------------------------------------------------
 * Head metadata (WP7), printed ONLY when Yoast SEO is not active (see
 * fnpw_seo_plugin_active()). Mirrors tools/meta.py on the static build: canonical,
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
		// The import stores each page's hand-written description in the Yoast field. With
		// Yoast switched off it is still the best description there is.
		$text = (string) get_post_meta( get_queried_object_id(), '_yoast_wpseo_metadesc', true );
		if ( '' === trim( $text ) || false !== strpos( $text, '%%' ) ) {
			$text = get_the_excerpt( get_queried_object_id() );
		}
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

/**
 * True when an SEO plugin owns the head metadata. The live site runs Yoast SEO, which
 * prints its own description, canonical, Open Graph, Twitter and schema output, so the
 * theme stays silent to avoid duplicates.
 */
function fnpw_seo_plugin_active() {
	return (bool) apply_filters( 'fnpw_seo_plugin_active', defined( 'WPSEO_VERSION' ) );
}

/**
 * Without Yoast, use the title the import stored in the Yoast field (it is the static
 * build's <title>, written by hand in data/meta.json).
 *
 * @param string $title Short-circuit title; empty to let WordPress build one.
 * @return string
 */
function fnpw_document_title( $title ) {
	if ( fnpw_seo_plugin_active() || ! is_singular() ) {
		return $title;
	}
	$stored = (string) get_post_meta( get_queried_object_id(), '_yoast_wpseo_title', true );
	return ( '' !== trim( $stored ) && false === strpos( $stored, '%%' ) ) ? $stored : $title;
}
add_filter( 'pre_get_document_title', 'fnpw_document_title' );

function fnpw_head_meta() {
	if ( is_admin() || is_404() || fnpw_seo_plugin_active() ) {
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

	fnpw_print_ld( fnpw_organization_ld() );
	if ( is_front_page() ) {
		fnpw_print_ld( fnpw_website_ld() );
	}
}
add_action( 'wp_head', 'fnpw_head_meta', 2 );

/**
 * Core prints its own canonical on singular pages; ours covers every view, so drop the
 * duplicate. Only when the theme is printing metadata: with Yoast active, Yoast handles it.
 */
function fnpw_drop_core_canonical() {
	if ( ! fnpw_seo_plugin_active() ) {
		remove_action( 'wp_head', 'rel_canonical' );
	}
}
add_action( 'template_redirect', 'fnpw_drop_core_canonical' );

/**
 * Icon links and web manifest from the theme, unless a Site Icon is set in the Customiser
 * (WordPress prints that itself). Not SEO metadata, so it prints with or without Yoast.
 */
function fnpw_head_icons() {
	if ( has_site_icon() ) {
		return;
	}
	printf( '<link rel="icon" href="%s" type="image/svg+xml">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/favicon.svg' ) ) );
	printf( '<link rel="icon" href="%s" sizes="32x32" type="image/png">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/favicon-32.png' ) ) );
	printf( '<link rel="apple-touch-icon" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/apple-touch-icon.png' ) ) );
	printf( '<link rel="manifest" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/icons/site.webmanifest' ) ) );
}
add_action( 'wp_head', 'fnpw_head_icons', 3 );

/**
 * Robots: keep search results and the thin archives out of the index.
 */
function fnpw_robots( $robots ) {
	if ( fnpw_seo_plugin_active() ) {
		return $robots;
	}
	if ( is_search() || is_attachment() || is_author() || is_date() ) {
		$robots['noindex'] = true;
		$robots['follow']  = true;
		unset( $robots['index'] );
	}
	return $robots;
}
add_filter( 'wp_robots', 'fnpw_robots' );
