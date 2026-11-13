<?php
/**
 * Site pop-up: one small campaign card that slides into the bottom corner of every page.
 *
 * Edited under Settings > Site pop-up (switch it on or off, change the words, the button,
 * the link, the picture and an optional last day). A visitor who closes it does not see
 * it again for seven days, or until the heading or the link changes.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Saved settings merged over the defaults (the Give a Tree Christmas card, Nov 2026).
 *
 * @return array
 */
function fnpw_core_popup_settings() {
	$defaults = array(
		'enabled' => 1,
		'heading' => 'Give a Tree this Christmas.',
		'text'    => '$10 plants a native tree where habitat needs it most.',
		'button'  => 'Give a Tree',
		'url'     => 'https://giveatree.fnpw.org.au/',
		'image'   => '',
		'alt'     => 'A male gang-gang cockatoo with a bright red crest leaning out of a tree hollow',
		'until'   => '',
	);
	$saved    = get_option( 'fnpw_core_popup', array() );
	$settings = wp_parse_args( is_array( $saved ) ? $saved : array(), $defaults );
	if ( '' === trim( (string) $settings['image'] ) ) {
		$settings['image'] = FNPW_CORE_URL . 'assets/popup-give-a-tree.jpg';
	}
	return $settings;
}

/**
 * Whether the pop-up should print on this request.
 *
 * @return bool
 */
function fnpw_core_popup_active() {
	$s = fnpw_core_popup_settings();
	if ( empty( $s['enabled'] ) || '' === trim( (string) $s['heading'] ) || '' === trim( (string) $s['url'] ) ) {
		return false;
	}
	if ( '' !== $s['until'] && current_time( 'Y-m-d' ) > $s['until'] ) {
		return false;
	}
	return (bool) apply_filters( 'fnpw_core_popup_active', true );
}

function fnpw_core_popup_render() {
	if ( is_admin() || ! fnpw_core_popup_active() ) {
		return;
	}
	$s   = fnpw_core_popup_settings();
	$key = 'fnpwPop_' . substr( md5( $s['heading'] . '|' . $s['url'] ), 0, 10 );
	?>
<style>
.fnpw-pop{position:fixed;right:20px;bottom:20px;z-index:9990;width:320px;max-width:calc(100vw - 24px);background:#FAF6F2;color:#371F1D;box-shadow:0 16px 48px rgba(0,0,0,.3);transform:translateY(24px);opacity:0;transition:transform .45s ease,opacity .45s ease}
.fnpw-pop[hidden]{display:none}
.fnpw-pop.is-in{transform:none;opacity:1}
.fnpw-pop-im{display:block;line-height:0}
.fnpw-pop-im img{display:block;width:100%;height:auto;aspect-ratio:1/1;object-fit:cover}
.fnpw-pop-b{padding:16px 18px 18px;display:flex;flex-direction:column;gap:10px;align-items:flex-start}
.fnpw-pop-h{margin:0;font-family:var(--ff-d,Sora,sans-serif);font-weight:800;font-size:1.15rem;line-height:1.2;color:#0F3132}
.fnpw-pop-t{margin:0;font-size:.9rem;line-height:1.5}
.fnpw-pop-btn{display:inline-block;background:#C23747;color:#fff;font-family:var(--ff-d,Sora,sans-serif);font-weight:700;font-size:.92rem;line-height:1.2;padding:.75em 1.3em;text-decoration:none}
.fnpw-pop-btn:hover,.fnpw-pop-btn:focus{background:#8C1422;color:#fff}
.fnpw-pop-x{position:absolute;top:10px;right:10px;width:36px;height:36px;border-radius:50%;border:0;padding:0;background:rgba(15,49,50,.85);color:#FAF6F2;font:600 20px/36px sans-serif;cursor:pointer;z-index:2}
.fnpw-pop-x:focus-visible,.fnpw-pop-btn:focus-visible{outline:3px solid #C6EBCA;outline-offset:2px}
@media(max-width:600px){
.fnpw-pop{left:12px;right:12px;bottom:12px;width:auto;display:flex;align-items:stretch}
.fnpw-pop[hidden]{display:none}
.fnpw-pop-im{flex:0 0 112px}
.fnpw-pop-im img{height:100%;aspect-ratio:auto;object-position:78% 50%}
.fnpw-pop-b{padding:14px 44px 14px 14px;justify-content:center}
.fnpw-pop-h{font-size:1rem}
.fnpw-pop-t{display:none}
.fnpw-pop-btn{font-size:.85rem}
.fnpw-pop-x{top:6px;right:6px;width:30px;height:30px;font-size:17px;line-height:30px}
}
@media(prefers-reduced-motion:reduce){.fnpw-pop{transition:none}}
@media print{.fnpw-pop{display:none}}
</style>
<aside class="fnpw-pop" id="fnpw-pop" hidden aria-label="<?php echo esc_attr( $s['heading'] ); ?>">
	<button type="button" class="fnpw-pop-x" aria-label="Close">&times;</button>
	<a class="fnpw-pop-im" href="<?php echo esc_url( $s['url'] ); ?>" tabindex="-1" aria-hidden="true"><img src="<?php echo esc_url( $s['image'] ); ?>" alt="" width="720" height="720" loading="lazy" decoding="async"></a>
	<div class="fnpw-pop-b">
		<p class="fnpw-pop-h"><?php echo esc_html( $s['heading'] ); ?></p>
		<?php if ( '' !== trim( (string) $s['text'] ) ) : ?>
		<p class="fnpw-pop-t"><?php echo esc_html( $s['text'] ); ?></p>
		<?php endif; ?>
		<a class="fnpw-pop-btn" href="<?php echo esc_url( $s['url'] ); ?>"><?php echo esc_html( $s['button'] ? $s['button'] : 'Find out more' ); ?></a>
	</div>
</aside>
<script>
(function(){var el=document.getElementById('fnpw-pop');if(!el)return;var KEY=<?php echo wp_json_encode( $key ); ?>,WEEK=6048e5;
function closedRecently(){try{var t=parseInt(localStorage.getItem(KEY)||'0',10);return t&&(Date.now()-t)<WEEK;}catch(e){return false;}}
function remember(){try{localStorage.setItem(KEY,String(Date.now()));}catch(e){}}
if(closedRecently())return;
setTimeout(function(){el.hidden=false;requestAnimationFrame(function(){requestAnimationFrame(function(){el.classList.add('is-in');});});},5000);
el.querySelector('.fnpw-pop-x').addEventListener('click',function(){remember();el.classList.remove('is-in');setTimeout(function(){el.hidden=true;},460);});
el.querySelector('.fnpw-pop-btn').addEventListener('click',remember);
})();
</script>
	<?php
}
add_action( 'wp_footer', 'fnpw_core_popup_render', 30 );

// ---- Settings > Site pop-up ---------------------------------------------------------

function fnpw_core_popup_sanitize( $input ) {
	$input = is_array( $input ) ? $input : array();
	$until = isset( $input['until'] ) ? trim( (string) $input['until'] ) : '';
	return array(
		'enabled' => empty( $input['enabled'] ) ? 0 : 1,
		'heading' => isset( $input['heading'] ) ? sanitize_text_field( $input['heading'] ) : '',
		'text'    => isset( $input['text'] ) ? sanitize_text_field( $input['text'] ) : '',
		'button'  => isset( $input['button'] ) ? sanitize_text_field( $input['button'] ) : '',
		'url'     => isset( $input['url'] ) ? esc_url_raw( trim( (string) $input['url'] ) ) : '',
		'image'   => isset( $input['image'] ) ? esc_url_raw( trim( (string) $input['image'] ) ) : '',
		'alt'     => '',
		'until'   => preg_match( '/^\d{4}-\d{2}-\d{2}$/', $until ) ? $until : '',
	);
}

function fnpw_core_popup_admin_init() {
	register_setting( 'fnpw_core_popup', 'fnpw_core_popup', array( 'type' => 'array', 'sanitize_callback' => 'fnpw_core_popup_sanitize' ) );
}
add_action( 'admin_init', 'fnpw_core_popup_admin_init' );

function fnpw_core_popup_menu() {
	add_options_page( 'Site pop-up', 'Site pop-up', 'manage_options', 'fnpw-popup', 'fnpw_core_popup_screen' );
}
add_action( 'admin_menu', 'fnpw_core_popup_menu' );

function fnpw_core_popup_screen() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$s      = fnpw_core_popup_settings();
	$saved  = get_option( 'fnpw_core_popup', array() );
	$custom = is_array( $saved ) && ! empty( $saved['image'] ) ? $saved['image'] : '';
	?>
	<div class="wrap">
		<h1>Site pop-up</h1>
		<p>A small card that slides into the bottom corner of every page five seconds after it loads. A visitor who closes it does not see it again for seven days, or until you change the heading or the link.</p>
		<form method="post" action="options.php">
			<?php settings_fields( 'fnpw_core_popup' ); ?>
			<table class="form-table" role="presentation">
				<tr><th scope="row">Show the pop-up</th><td><label><input type="checkbox" name="fnpw_core_popup[enabled]" value="1" <?php checked( ! empty( $s['enabled'] ) ); ?>> Switched on</label></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-heading">Heading</label></th><td><input class="regular-text" id="fnpw-pop-heading" name="fnpw_core_popup[heading]" value="<?php echo esc_attr( $s['heading'] ); ?>"></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-text">Line of text</label></th><td><input class="large-text" id="fnpw-pop-text" name="fnpw_core_popup[text]" value="<?php echo esc_attr( $s['text'] ); ?>"><p class="description">Hidden on phones to keep the card small.</p></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-button">Button label</label></th><td><input class="regular-text" id="fnpw-pop-button" name="fnpw_core_popup[button]" value="<?php echo esc_attr( $s['button'] ); ?>"></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-url">Button link</label></th><td><input class="large-text" type="url" id="fnpw-pop-url" name="fnpw_core_popup[url]" value="<?php echo esc_attr( $s['url'] ); ?>"></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-image">Picture address</label></th><td><input class="large-text" type="url" id="fnpw-pop-image" name="fnpw_core_popup[image]" value="<?php echo esc_attr( $custom ); ?>" placeholder="Leave empty for the Give a Tree gang-gang picture"><p class="description">A square picture works best. Copy its address from the Media Library (File URL).</p></td></tr>
				<tr><th scope="row"><label for="fnpw-pop-until">Last day to show</label></th><td><input type="date" id="fnpw-pop-until" name="fnpw_core_popup[until]" value="<?php echo esc_attr( $s['until'] ); ?>"><p class="description">Optional. Leave empty to keep showing it until you switch it off.</p></td></tr>
			</table>
			<?php submit_button(); ?>
		</form>
	</div>
	<?php
}
