<?php
/**
 * Analytics and tracking tags.
 *
 * On the live site these are printed by the old theme from ACF "Settings: General", so
 * they would vanish at the theme switch. The IDs below are the live values read in the
 * admin audit of 10 November 2026 (wordpress/migration/inventory.md):
 *
 *   Google Tag Manager  GTM-K2P27RG       head, plus noscript after <body>
 *   Meta pixel          2023665144313964  head, with its noscript image
 *   Hotjar              1708422           head
 *
 * GA4 and Google Ads load inside the Tag Manager container; HubSpot tracking comes
 * from the HubSpot plugin. Neither is printed here.
 *
 * Output is for every visitor, as on live, but ONLY when the environment type is
 * "production" (wp_get_environment_type()), so staging and local traffic stay out of
 * the analytics. Override with the fnpw_core_tracking_enabled filter.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
 * IDs. Each can be changed with a constant in wp-config.php or with the matching
 * filter (fnpw_core_gtm_id, fnpw_core_meta_pixel_id, fnpw_core_hotjar_id). An empty
 * value switches that tag off.
 */
if ( ! defined( 'FNPW_CORE_GTM_ID' ) ) {
	define( 'FNPW_CORE_GTM_ID', 'GTM-K2P27RG' );
}
if ( ! defined( 'FNPW_CORE_META_PIXEL_ID' ) ) {
	define( 'FNPW_CORE_META_PIXEL_ID', '2023665144313964' );
}
if ( ! defined( 'FNPW_CORE_HOTJAR_ID' ) ) {
	define( 'FNPW_CORE_HOTJAR_ID', '1708422' );
}

/**
 * Whether tracking tags print on this request.
 *
 * @return bool
 */
function fnpw_core_tracking_enabled() {
	/**
	 * Filters whether the tracking tags are printed.
	 *
	 * @param bool $enabled True on production, false on every other environment type.
	 */
	return (bool) apply_filters( 'fnpw_core_tracking_enabled', 'production' === wp_get_environment_type() );
}

/**
 * A tracking ID, restricted to the characters these IDs use.
 *
 * @param string $which gtm, meta_pixel or hotjar.
 * @return string
 */
function fnpw_core_tracking_id( $which ) {
	$ids = array(
		'gtm'        => FNPW_CORE_GTM_ID,
		'meta_pixel' => FNPW_CORE_META_PIXEL_ID,
		'hotjar'     => FNPW_CORE_HOTJAR_ID,
	);
	$id  = isset( $ids[ $which ] ) ? $ids[ $which ] : '';
	$id  = (string) apply_filters( 'fnpw_core_' . $which . '_id', $id );
	return preg_replace( '/[^A-Za-z0-9_-]/', '', $id );
}

/**
 * Google Consent Mode v2 default state.
 *
 * Everything defaults to "granted" so behaviour matches the live site today, where the
 * tags run without a consent banner. To tighten later, return "denied" for the relevant
 * keys from this filter and have the consent tool call gtag('consent','update',...).
 *
 * @return array<string,string>
 */
function fnpw_core_consent_default() {
	$default = array(
		'ad_storage'              => 'granted',
		'ad_user_data'            => 'granted',
		'ad_personalization'      => 'granted',
		'analytics_storage'       => 'granted',
		'functionality_storage'   => 'granted',
		'personalization_storage' => 'granted',
		'security_storage'        => 'granted',
	);
	$consent = apply_filters( 'fnpw_core_consent_default', $default );
	return is_array( $consent ) ? $consent : $default;
}

/**
 * Head tags: consent default first, then Tag Manager, Meta pixel and Hotjar.
 */
function fnpw_core_tracking_head() {
	if ( ! fnpw_core_tracking_enabled() ) {
		return;
	}
	$gtm    = fnpw_core_tracking_id( 'gtm' );
	$pixel  = fnpw_core_tracking_id( 'meta_pixel' );
	$hotjar = fnpw_core_tracking_id( 'hotjar' );

	if ( $gtm ) {
		?>
<!-- Google Consent Mode v2 default (FNPW Core). Must run before Tag Manager. -->
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',<?php echo wp_json_encode( fnpw_core_consent_default() ); ?>);
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer',<?php echo wp_json_encode( $gtm ); ?>);</script>
<!-- End Google Tag Manager -->
		<?php
	}

	if ( $pixel ) {
		?>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', <?php echo wp_json_encode( $pixel ); ?>);
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none" alt=""
src="<?php echo esc_url( 'https://www.facebook.com/tr?id=' . $pixel . '&ev=PageView&noscript=1' ); ?>"/></noscript>
<!-- End Meta Pixel Code -->
		<?php
	}

	if ( $hotjar ) {
		?>
<!-- Hotjar Tracking Code -->
<script>
(function(h,o,t,j,a,r){
h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
h._hjSettings={hjid:<?php echo (int) $hotjar; ?>,hjsv:6};
a=o.getElementsByTagName('head')[0];
r=o.createElement('script');r.async=1;
r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
a.appendChild(r);
})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
</script>
<!-- End Hotjar Tracking Code -->
		<?php
	}
}
add_action( 'wp_head', 'fnpw_core_tracking_head', 1 );

/**
 * Tag Manager noscript frame, straight after the opening body tag.
 */
function fnpw_core_tracking_body_open() {
	if ( ! fnpw_core_tracking_enabled() ) {
		return;
	}
	$gtm = fnpw_core_tracking_id( 'gtm' );
	if ( ! $gtm ) {
		return;
	}
	?>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="<?php echo esc_url( 'https://www.googletagmanager.com/ns.html?id=' . $gtm ); ?>"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
	<?php
}
add_action( 'wp_body_open', 'fnpw_core_tracking_body_open', 1 );
