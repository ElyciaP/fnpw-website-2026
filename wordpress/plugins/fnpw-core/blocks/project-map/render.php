<?php
/**
 * Project map block: server render.
 *
 * Markup copied from <section class="map-sec" id="map"> on the static projects.html;
 * the pins, the count and the state buttons are built from the project data the way
 * tools/gen_map.py builds them.
 *
 * @package fnpw-core
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// The markup uses fixed ids (imPop, imStates...), so it can only appear once a page.
static $fnpw_core_map_rendered = false;
if ( $fnpw_core_map_rendered ) {
	return;
}
$fnpw_core_map_rendered = true;

$fnpw_projects = fnpw_core_map_projects();
$fnpw_pins     = array();
$fnpw_counts   = array();
foreach ( $fnpw_projects as $fnpw_p ) {
	if ( '' !== $fnpw_p['state'] ) {
		$fnpw_counts[ $fnpw_p['state'] ] = isset( $fnpw_counts[ $fnpw_p['state'] ] ) ? $fnpw_counts[ $fnpw_p['state'] ] + 1 : 1;
	}
	if ( $fnpw_p['on_map'] ) {
		$fnpw_pins[] = $fnpw_p;
	}
}

// Pin data for the popup script, in the static build's short keys plus the link.
$fnpw_imap = array();
foreach ( $fnpw_pins as $fnpw_p ) {
	$fnpw_imap[] = array(
		's'   => $fnpw_p['slug'],
		't'   => $fnpw_p['title'],
		'st'  => $fnpw_p['state'],
		'pl'  => $fnpw_p['pillar_label'],
		'pc'  => $fnpw_p['pillar_class'],
		'x'   => $fnpw_p['x'],
		'y'   => $fnpw_p['y'],
		'l'   => $fnpw_p['link'],
		'img' => $fnpw_p['img'],
	);
}
wp_add_inline_script(
	'fnpw-project-map-view',
	'var IMAP=' . wp_json_encode( $fnpw_imap, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG ) . ';',
	'before'
);

// State picker (phones), in the static build's display order, only states present.
$fnpw_order  = array( 'NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT', 'Christmas Island', 'Norfolk Island', 'Lord Howe Island', 'Australia' );
$fnpw_extra  = array_diff( array_keys( $fnpw_counts ), $fnpw_order );
sort( $fnpw_extra );
$fnpw_labels = array( 'Australia' => 'Australia-wide' );

$fnpw_art   = fnpw_core_map_artwork();
$fnpw_icons = FNPW_CORE_URL . 'blocks/project-map/icons/';
?>
<section class="map-sec" id="map">
  <div class="imap-band">
    <div class="cw">
    <div class="imap-grid">
    <div class="map-side rv">
      <span class="ey">Explore the work</span>
      <h2 class="map-h2"><span class="d-pins">Every pin is a project. Click to dive in.</span><span class="d-states">Every project, state by state.</span></h2>
      <p class="map-p"><span class="d-pins">Click a pin for a quick look at the project there, then jump to its full story.</span><span class="d-states">Choose a state or territory under the map to see the projects there.</span> Locations are approximate; the list below has every project.</p>
      <div class="im-legend">
  <span><i class="pb-parks"></i><img class="im-leg-ic" src="<?php echo esc_url( $fnpw_icons . 'fnpw-icon-landscape-dark-soil-rgb.svg' ); ?>" alt="" aria-hidden="true">Growing National Parks</span>
  <span><i class="pb-species"></i><img class="im-leg-ic" src="<?php echo esc_url( $fnpw_icons . 'fnpw-icon-koala-dark-soil-rgb.svg' ); ?>" alt="" aria-hidden="true">Saving Species</span>
  <span><i class="pb-healing"></i><img class="im-leg-ic" src="<?php echo esc_url( $fnpw_icons . 'fnpw-icon-plants-sprouting-dark-soil-rgb.svg' ); ?>" alt="" aria-hidden="true">Healing the Land</span>
  <span class="im-leg-n"><?php echo esc_html( count( $fnpw_pins ) ); ?> projects<span class="im-leg-click"> &#183; click a pin</span></span>
</div>
    </div>
    <div class="imap rv d1"<?php echo $fnpw_art['found'] ? '' : ' style="aspect-ratio:1500/1289"'; ?>>
<?php if ( $fnpw_art['found'] ) : ?>
  <picture>
<?php if ( $fnpw_art['webp'] ) : ?>
    <source srcset="<?php echo esc_url( $fnpw_art['webp'] ); ?>" type="image/webp">
<?php endif; ?>
    <img src="<?php echo esc_url( $fnpw_art['png'] ); ?>" width="1500" height="1289" alt="Map of Australia showing our twelve landscape priorities and project locations" draggable="false">
  </picture>
<?php else : ?>
  <!-- FNPW Core: map artwork missing. Copy projects-map-brand.png (and .webp) into blocks/project-map/. -->
<?php endif; ?>
  <div class="im-pop" id="imPop" role="dialog" aria-modal="false" aria-labelledby="imTitle" hidden>
    <button type="button" class="im-x" id="imX" aria-label="Close">&#215;</button>
    <span class="im-chip" id="imChip"></span>
    <h3 id="imTitle" tabindex="-1"></h3>
    <p id="imState"></p>
    <img class="im-thumb" id="imThumb" alt="" hidden>
    <a class="btn-p" id="imGo" href="#">View project</a>
  </div>
<?php foreach ( $fnpw_pins as $fnpw_i => $fnpw_p ) : ?>
<button class="im-pin <?php echo esc_attr( $fnpw_p['pillar_class'] ); ?>" style="left:<?php echo esc_attr( $fnpw_p['x'] ); ?>%;top:<?php echo esc_attr( $fnpw_p['y'] ); ?>%" data-i="<?php echo esc_attr( $fnpw_i ); ?>" aria-label="<?php echo esc_attr( $fnpw_p['title'] . ', ' . $fnpw_p['state'] ); ?>" title="<?php echo esc_attr( $fnpw_p['title'] ); ?>"></button>
<?php endforeach; ?>
</div>
    <div class="im-states" id="imStates">
      <p class="im-states-l" id="imStatesL">Choose a state or territory to filter the list below.</p>
      <div class="im-states-r" role="group" aria-labelledby="imStatesL">
<button type="button" class="im-st on" data-st="all" aria-pressed="true">All (<?php echo esc_html( count( $fnpw_projects ) ); ?>)</button>
<?php foreach ( array_merge( $fnpw_order, $fnpw_extra ) as $fnpw_state ) : ?>
<?php if ( isset( $fnpw_counts[ $fnpw_state ] ) ) : ?>
<button type="button" class="im-st" data-st="<?php echo esc_attr( $fnpw_state ); ?>" aria-pressed="false"><?php echo esc_html( isset( $fnpw_labels[ $fnpw_state ] ) ? $fnpw_labels[ $fnpw_state ] : $fnpw_state ); ?> (<?php echo esc_html( $fnpw_counts[ $fnpw_state ] ); ?>)</button>
<?php endif; ?>
<?php endforeach; ?>
      </div>
      <p class="im-states-m" id="imStMeta"></p>
    </div>
    </div>

    </div>
  </div>
</section>
