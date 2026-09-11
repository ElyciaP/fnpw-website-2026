"""Build the corporate volunteering state pages and the state section on volunteer.html.

Source of truth: data/volunteer-sites.json, built from Helen's site list by
tools/build_vol_sites.py and geocoded once. State outlines come from
data/state-outlines.json (OpenStreetMap, simplified).

Each state page draws its own SVG map, in the flat silhouette style of the
national Landscape Priorities artwork, with a numbered pin per site beside a
numbered list. Hovering or focusing either one highlights the other.

    python3 tools/gen_vol_states.py
    python3 tools/sync.py
"""
import json, math, os, re, sys, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page

NL = chr(10)
SITES = 'data/volunteer-sites.json'
OUTLINES = 'data/state-outlines.json'

# States that get their own page. QLD has a single site, so it is listed on the
# hub page but has nowhere further to go.
PAGES = ['NSW', 'VIC', 'SA', 'WA']

W, Hh, PAD = 760, 620, 26

# The sites are not spread evenly across a state. Twelve of the fourteen in NSW
# sit in greater Sydney, so a whole-state frame collapses them into one blob.
# The main map is therefore framed on the sites themselves, with a locator inset
# showing where that frame sits in the state.
INSET_W, MIN_SPAN = 168, 1.1     # degrees of latitude, about 120km


def esc(t):
    return H.escape(t or '', quote=True)


def slug_state(code):
    return 'corporate-volunteering-%s.html' % code.lower()


def fit(bbox, w, h, pad):
    """Equirectangular, corrected for longitude convergence, fitted to a box."""
    s, n, west, east = bbox
    kx = math.cos(math.radians((s + n) / 2))
    dw, dh = max((east - west) * kx, 1e-6), max(n - s, 1e-6)
    k = min((w - 2 * pad) / dw, (h - 2 * pad) / dh)
    ox, oy = (w - dw * k) / 2, (h - dh * k) / 2

    def to_xy(lat, lon):
        return (round(ox + (lon - west) * kx * k, 1), round(oy + (n - lat) * k, 1))
    return to_xy


def site_frame(sites, state_bbox):
    """A box around the sites, never smaller than MIN_SPAN and never larger
    than the state, with room to breathe around the outermost pins."""
    lats = [s['lat'] for s in sites]
    lons = [s['lon'] for s in sites]
    clat, clon = (min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2
    kx = max(math.cos(math.radians(clat)), 0.2)
    dh = max(max(lats) - min(lats), MIN_SPAN) * 1.35
    dw = max((max(lons) - min(lons)) * kx, MIN_SPAN * (W / Hh)) * 1.35 / kx
    # match the frame to the panel so the outline is not distorted
    if dw * kx / dh < W / Hh:
        dw = dh * (W / Hh) / kx
    else:
        dh = dw * kx * (Hh / W)
    ss, sn, sw, se = state_bbox
    return [max(clat - dh / 2, ss - .4), min(clat + dh / 2, sn + .4),
            max(clon - dw / 2, sw - .4), min(clon + dw / 2, se + .4)]


def declutter(pts, sep=27.0, passes=60):
    """Ease overlapping pins apart.

    Two sites can share a car park, and Lane Cove National Park appears twice
    with two different meeting points, so at this zoom their dots land on top of
    one another. This nudges them just far enough apart to be readable and
    clickable. The caption on the page says the positions are approximate.
    """
    pts = [list(p) for p in pts]
    for _ in range(passes):
        moved = False
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
                d = math.hypot(dx, dy)
                if d >= sep:
                    continue
                if d < 1e-6:                      # exactly coincident
                    ang = (i * 2.39996) % (2 * math.pi)
                    dx, dy, d = math.cos(ang), math.sin(ang), 1.0
                push = (sep - d) / 2 / d
                pts[i][0] -= dx * push; pts[i][1] -= dy * push
                pts[j][0] += dx * push; pts[j][1] += dy * push
                moved = True
        if not moved:
            break
    return [(round(x, 1), round(y, 1)) for x, y in pts]


def rings_path(rings, to_xy):
    return ' '.join('M' + 'L'.join('%s,%s' % to_xy(p[1], p[0]) for p in r) + 'Z' for r in rings)


def svg_map(code, outline, sites):
    """Detail map framed on the sites, plus a locator inset of the whole state."""
    frame = site_frame(sites, outline['bbox'])
    to_xy = fit(frame, W, Hh, PAD)
    land = rings_path(outline['rings'], to_xy)

    xy = declutter([to_xy(s['lat'], s['lon']) for s in sites])
    pins = []
    for i, s in enumerate(sites, 1):
        x, y = xy[i - 1]
        pins.append(
            '      <g class="vm-pin" data-i="%d" tabindex="0" role="button" '
            'aria-label="%s, %s">%s'
            '        <circle class="vm-hit" cx="%s" cy="%s" r="18"></circle>%s'
            '        <circle class="vm-dot" cx="%s" cy="%s" r="11.5"></circle>%s'
            '        <text class="vm-num" x="%s" y="%s">%d</text>%s'
            '      </g>'
            % (i, esc(s['name']), esc(s['city']), NL, x, y, NL, x, y, NL, x, y + 3.8, i, NL))

    # locator inset: the whole state, with the detail frame drawn on it
    ss, sn, sw, se = outline['bbox']
    ih = int(INSET_W * ((sn - ss) / max((se - sw) * math.cos(math.radians((ss + sn) / 2)), 1e-6)))
    ih = max(70, min(ih, 190))
    ito = fit(outline['bbox'], INSET_W, ih, 8)
    iland = rings_path(outline['rings'], ito)
    fx1, fy1 = ito(frame[1], frame[2])
    fx2, fy2 = ito(frame[0], frame[3])
    inset = (
        '      <g class="vm-inset" transform="translate(%d,%d)" aria-hidden="true">%s'
        '        <rect class="vm-inset-bg" x="-8" y="-8" width="%d" height="%d"></rect>%s'
        '        <path class="vm-inset-land" d="%s"></path>%s'
        '        <rect class="vm-inset-box" x="%s" y="%s" width="%s" height="%s"></rect>%s'
        '      </g>'
        % (W - INSET_W - 16, Hh - ih - 16, NL, INSET_W + 16, ih + 16, NL, iland, NL,
           round(fx1, 1), round(fy1, 1), round(max(fx2 - fx1, 5), 1), round(max(fy2 - fy1, 5), 1), NL))

    return (
        '    <svg class="vm-svg" viewBox="0 0 %d %d" role="img" '
        'aria-label="Map of the %s region showing %d corporate volunteering sites, '
        'with a locator map of %s">%s'
        '      <path class="vm-land" d="%s"></path>%s%s%s%s%s    </svg>'
        % (W, Hh, esc(outline['name']), len(sites), esc(outline['name']), NL, land, NL,
           inset, NL, NL.join(pins), NL))


def card(i, s):
    bits = ['<span class="vs-type">%s</span>' % esc(s['type']),
            '<span class="vs-city">%s</span>' % esc(s['city'])]
    return (
        '        <li class="vs-card" data-i="%d" data-type="%s" data-km="%d" data-name="%s" tabindex="0">%s'
        '          <span class="vs-num">%d</span>%s'
        '          <div class="vs-bd">%s'
        '            <h3>%s</h3>%s'
        '            <p class="vs-meta">%s</p>%s'
        '            <p class="vs-addr">%s</p>%s'
        '            <p class="vs-dist">%d km from the %s CBD</p>%s'
        '            <p class="vs-mgr"><span>Managed with</span> %s</p>%s'
        '          </div>%s        </li>'
        % (i, esc(s['type']), s['km'], esc(s['name'].lower()), NL, i, NL, NL,
           esc(s['name']), NL, '<span class="vs-dot"></span>'.join(bits), NL,
           esc(', '.join(x for x in (s['address'], s['postcode']) if x)), NL,
           s['km'], esc(s['cbd']), NL, esc(s['manager']), NL, NL))


def summarise(rows):
    """A plain sentence describing a state's sites, built from the data."""
    from collections import Counter
    c = Counter(r['type'] for r in rows)
    def plural(t, n):
        return t.lower() + ('' if t.lower().endswith('s') or n == 1 else 's')
    parts = ['%d %s' % (n, plural(t, n)) for t, n in c.most_common()]
    if len(parts) > 1:
        types = ', '.join(parts[:-1]) + ' and ' + parts[-1]
    else:
        types = parts[0]
    kms = sorted(r['km'] for r in rows)
    if len(rows) == 1:
        reach = '%d km from the %s CBD' % (kms[0], rows[0]['cbd'])
    else:
        reach = 'between %d and %d km from the %s CBD' % (kms[0], kms[-1], rows[0]['cbd'])
    return '%s, %s.' % (types[0].upper() + types[1:], reach)


PAGE_CSS = '''
.vs-hero{background:var(--euc-deep);color:var(--cream);padding:var(--sec-y) 0}
.vs-hero .ey{color:var(--euc-soft)}.vs-hero .ey::before{background:var(--euc-soft)}
.vs-hero h1{color:var(--cream);font-size:clamp(2rem,4.2vw,3.1rem);font-weight:600;
  letter-spacing:-.028em;line-height:1.05;margin:1rem 0 0;max-width:18ch}
.vs-hero .lede{color:rgba(250,246,242,.88);margin-top:1.1rem;max-width:56ch}
.vs-crumb{display:flex;gap:.5em;font-size:.82rem;color:rgba(250,246,242,.72);
  margin-bottom:1.3rem;flex-wrap:wrap}
.vs-crumb a{color:var(--euc-soft)}
.vs-tally{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.5rem;padding:0;list-style:none}
.vs-tally li{font-size:.8rem;font-weight:600;color:var(--euc-deep);background:var(--euc-soft);
  padding:.45em .85em}

.vs-wrap{padding:var(--sec-y) 0;background:var(--paper)}
.vs-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:3rem;align-items:start}
@media(max-width:1000px){.vs-split{grid-template-columns:1fr;gap:2rem}}

.vs-mapcol{position:sticky;top:92px}
@media(max-width:1000px){.vs-mapcol{position:static}}
.vm{background:var(--cream);border:1px solid var(--rule);padding:.6rem}
.vm-svg{display:block;width:100%;height:auto}
.vm-land{fill:var(--euc-soft);stroke:var(--euc);stroke-width:1.5;stroke-linejoin:round}
.vm-hit{fill:transparent}
.vm-dot{fill:var(--euc-deep);stroke:var(--cream);stroke-width:2;transition:fill .18s ease,r .18s ease}
.vm-num{fill:var(--cream);font-family:var(--ff-d);font-weight:700;font-size:11px;
  text-anchor:middle;pointer-events:none}
.vm-pin{cursor:pointer}
.vm-pin:hover .vm-dot,.vm-pin:focus .vm-dot,.vm-pin.on .vm-dot{fill:var(--waratah);r:14}
.vm-pin:focus{outline:none}
.vm-pin:focus .vm-dot{stroke:var(--euc-deep);stroke-width:3}
.vm-inset-bg{fill:var(--cream);stroke:var(--rule);stroke-width:1}
.vm-inset-land{fill:none;stroke:var(--euc);stroke-width:1.2;stroke-linejoin:round}
.vm-inset-box{fill:rgba(194,55,71,.16);stroke:var(--waratah);stroke-width:1.4}
.vm-cap{margin:.7rem .2rem 0;font-size:.78rem;color:var(--stone);line-height:1.5}

.vs-filter{display:flex;flex-wrap:wrap;gap:.45rem;margin-bottom:1.3rem}
.vs-filter button{font-size:.78rem;font-weight:600;padding:.5em .9em;border:1.5px solid var(--bark-mid);
  background:transparent;color:var(--euc-deep);cursor:pointer;transition:.2s}
.vs-filter button:hover{border-color:var(--euc-deep)}
.vs-filter button.on{background:var(--euc-deep);border-color:var(--euc-deep);color:var(--cream)}

.vs-listwrap{position:relative}
.vs-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.8rem}

/* Desktop: the list scrolls inside a panel the height of the map beside it, so the
   two columns stay level instead of the list running on down the page. */
@media(min-width:1001px){
  .vs-list{max-height:625px;overflow-y:auto;padding-right:.7rem;
    scrollbar-width:thin;scrollbar-color:var(--bark-mid) transparent;overscroll-behavior:contain}
  .vs-list::-webkit-scrollbar{width:8px}
  .vs-list::-webkit-scrollbar-thumb{background:var(--bark-mid)}
  .vs-list::-webkit-scrollbar-track{background:transparent}
  .vs-listwrap::after{content:"";position:absolute;left:0;right:.7rem;bottom:0;height:64px;
    pointer-events:none;opacity:1;transition:opacity .25s ease;
    background:linear-gradient(to bottom,rgba(244,238,230,0),var(--paper))}
  .vs-listwrap.at-end::after{opacity:0}
}
.vs-more{display:none;width:100%;margin-top:.9rem;padding:.85em 1.2em;background:transparent;
  border:1.5px solid var(--euc-deep);color:var(--euc-deep);font-weight:700;font-size:.82rem;
  letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:.2s}
.vs-more:hover{background:var(--euc-deep);color:var(--cream)}
@media(max-width:1000px){.vs-more.on{display:block}}
.vs-card{display:flex;gap:1rem;background:var(--white);border:1px solid var(--rule);
  border-left:3px solid var(--euc-soft);padding:1.1rem 1.2rem;transition:.2s;cursor:default}
.vs-card:hover,.vs-card:focus,.vs-card.on{border-left-color:var(--waratah);
  box-shadow:0 10px 26px -18px rgba(15,49,50,.4);outline:none}
.vs-num{flex:0 0 auto;width:26px;height:26px;border-radius:50%;background:var(--euc-deep);
  color:var(--cream);display:flex;align-items:center;justify-content:center;
  font-family:var(--ff-d);font-weight:700;font-size:.8rem;margin-top:.15rem;transition:.2s}
.vs-card:hover .vs-num,.vs-card:focus .vs-num,.vs-card.on .vs-num{background:var(--waratah)}
.vs-bd{min-width:0}
.vs-bd h3{font-size:1.02rem;margin:0 0 .35rem;color:var(--euc-deep);line-height:1.25}
.vs-meta{margin:0 0 .35rem;font-size:.82rem;color:var(--euc);font-weight:600;
  display:flex;align-items:center;gap:.5em;flex-wrap:wrap}
.vs-dot{width:3px;height:3px;border-radius:50%;background:var(--bark-mid);display:inline-block}
.vs-addr{margin:0 0 .35rem;font-size:.86rem;color:var(--char);line-height:1.5}
.vs-mgr{margin:0;font-size:.8rem;color:var(--stone);line-height:1.5}
.vs-mgr span{font-weight:700;color:var(--euc-deep)}
.vs-dist{margin:0 0 .35rem;font-size:.82rem;color:var(--char)}
.vs-count{font-size:.82rem;color:var(--stone);margin:0}

.vs-tools{display:flex;align-items:center;justify-content:space-between;gap:1rem;
  flex-wrap:wrap;margin-bottom:1.1rem}
.vs-sort{display:flex;align-items:center;gap:.5em;font-size:.82rem;color:var(--stone)}
.vs-sort select{padding:.45em 1.9em .45em .7em;border:1.5px solid var(--bark-mid);background:var(--white);
  font-family:var(--ff-b);font-size:.82rem;color:var(--euc-deep);font-weight:600}
.vs-empty{padding:1.6rem;background:var(--white);border:1px dashed var(--bark-mid);
  font-size:.9rem;color:var(--stone);text-align:center}

.vs-gal{padding:var(--sec-y) 0;background:var(--white)}
.vs-gal-g{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem}
@media(max-width:820px){.vs-gal-g{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.vs-gal-g{grid-template-columns:1fr}}
.vs-gal-g figure{margin:0}
.vs-gal-g img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;background:var(--sand)}
.vs-gal-note{margin:1.2rem 0 0;font-size:.8rem;color:var(--stone)}
'''

PAGE_JS = '''<script>
(function () {
  var pins = [].slice.call(document.querySelectorAll('.vm-pin'));
  var list = document.querySelector('.vs-list');
  var cards = [].slice.call(document.querySelectorAll('.vs-card'));
  if (!pins.length || !list) return;

  function mark(i, on) {
    pins.forEach(function (p) { if (+p.dataset.i === i) p.classList.toggle('on', on); });
    cards.forEach(function (c) { if (+c.dataset.i === i) c.classList.toggle('on', on); });
  }
  function wire(el) {
    var i = +el.dataset.i;
    el.addEventListener('mouseenter', function () { mark(i, true); });
    el.addEventListener('mouseleave', function () { mark(i, false); });
    el.addEventListener('focus', function () { mark(i, true); });
    el.addEventListener('blur', function () { mark(i, false); });
  }
  pins.forEach(wire);
  cards.forEach(wire);

  // Tapping a pin brings its entry into view. That is the point of the map on a
  // phone, where the two are stacked rather than side by side.
  pins.forEach(function (p) {
    p.addEventListener('click', function () {
      var c = cards.filter(function (x) { return x.dataset.i === p.dataset.i; })[0];
      if (c) { c.scrollIntoView({ behavior: 'smooth', block: 'center' }); c.focus({ preventScroll: true }); }
    });
    p.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); p.click(); }
    });
  });

  // On a phone the map sits above the list, and a scrolling box inside a
  // scrolling page is horrible to use, so there the list shows four and expands.
  // On desktop it is a scroll panel matched to the map, and the fade at the
  // bottom edge switches off once you reach the end.
  var wrap = document.querySelector('.vs-listwrap');
  var more = document.getElementById('vsMore');
  var STEP = 4, expanded = false;
  var touchLayout = window.matchMedia('(max-width: 1000px)');

  function fade() {
    if (!wrap) return;
    var atEnd = list.scrollTop + list.clientHeight >= list.scrollHeight - 4;
    wrap.classList.toggle('at-end', atEnd || list.scrollHeight <= list.clientHeight + 4);
  }
  list.addEventListener('scroll', fade, { passive: true });
  window.addEventListener('resize', function () { render(); });

  var btns = [].slice.call(document.querySelectorAll('.vs-filter button'));
  var count = document.getElementById('vsCount');
  var sort = document.getElementById('vsSort');
  var empty = document.getElementById('vsEmpty');
  var filter = 'all';

  function render() {
    var shown = 0;
    cards.forEach(function (c) {
      var hit = (filter === 'all' || c.dataset.type === filter);
      c.hidden = !hit;
      if (hit) shown++;
      pins.forEach(function (p) {
        if (p.dataset.i === c.dataset.i) p.style.opacity = hit ? '' : '.15';
      });
    });
    var mode = sort ? sort.value : 'distance';
    cards.slice().sort(function (a, b) {
      if (mode === 'name') return a.dataset.name.localeCompare(b.dataset.name);
      if (mode === 'type') return a.dataset.type.localeCompare(b.dataset.type)
        || (+a.dataset.km) - (+b.dataset.km);
      return (+a.dataset.km) - (+b.dataset.km);
    }).forEach(function (c) { list.appendChild(c); });
    if (count) count.textContent = shown + (shown === 1 ? ' site' : ' sites');
    if (empty) empty.hidden = shown > 0;

    var capped = touchLayout.matches && !expanded && shown > STEP;
    var n = 0;
    cards.forEach(function (c) {
      if (c.hidden) return;
      n++;
      if (capped && n > STEP) c.hidden = true;
    });
    if (more) {
      more.classList.toggle('on', touchLayout.matches && shown > STEP);
      more.hidden = !(touchLayout.matches && shown > STEP);
      more.textContent = expanded ? 'Show fewer sites'
        : 'Show all ' + shown + (shown === 1 ? ' site' : ' sites');
    }
    fade();
  }

  if (more) more.addEventListener('click', function () { expanded = !expanded; render(); });

  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      btns.forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      filter = b.dataset.f;
      render();
    });
  });
  if (sort) sort.addEventListener('change', render);
  render();
})();
</script>'''


GALLERY_N = 6


def extract_form(state_name=None):
    """Lift the enquiry form, and the styles it needs, out of volunteer.html.

    There is one form on the site and it lives on volunteer.html. Rather than
    keep a copy, the state pages borrow that markup, so a change there reaches
    every page on the next build.
    """
    v = open('volunteer.html', encoding='utf-8').read()
    a = v.index('<section class="v-cta" id="enquire">')
    b = v.index('</section>', v.index('</div>\n</section>', a)) + len('</section>')
    markup = v[a:b]

    style = v[v.index('<style>'):v.index('</style>')]
    want = ('.v-cta', '.vform', '.v-steps')
    rules = []
    for chunk in re.findall(r'(?m)^(?:@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}|[^@\n][^{]*\{[^{}]*\})', style):
        if any(w in chunk.split('{')[0] for w in want) or (
                chunk.startswith('@media') and any(w in chunk for w in want)):
            rules.append(chunk.strip())
    css = NL.join(rules)

    if state_name:
        markup = markup.replace('Pick from the sites listed above',
                                'Pick from the %s sites above' % state_name)
    return css, markup


def gallery(code, idx):
    """A rotating slice of the corporate volunteering photographs.

    These are real photographs from FNPW volunteering days, but they are not
    photographs of these particular sites. The caption says so. Per-site
    photographs are the single most useful thing that could be added here.
    """
    shots = ['assets/img/volunteering/vol-%02d.jpg' % n for n in range(1, 17)]
    pick = [shots[(idx * 3 + n) % len(shots)] for n in range(GALLERY_N)]
    figs = NL.join(
        '        <figure><img src="%s" alt="" loading="lazy" decoding="async"></figure>' % f
        for f in pick)
    return NL.join([
        '<section class="vs-gal">',
        '  <div class="cw rv">',
        '    <span class="ey">On the ground</span>',
        '    <h2 style="margin:.9rem 0 0">What a day looks like.</h2>',
        '    <div class="vs-gal-g">',
        figs,
        '    </div>',
        '    <p class="vs-gal-note">Photographs from corporate volunteering days around the '
        'country. PLACEHOLDER: swap for photographs of the %s sites when we have them.</p>' % code,
        '  </div>',
        '</section>',
    ])


def state_page(code, outline, sites, idx):
    from collections import Counter
    counts = Counter(s['type'] for s in sites)
    types = sorted(counts)
    tally = ''.join('        <li>%d %s</li>%s'
                    % (counts[t], esc(t + ('' if t.endswith('s') or counts[t] == 1 else 's')), NL)
                    for t in types)
    filters = ''.join(
        '        <button type="button" data-f="%s">%s <span>%d</span></button>%s'
        % (esc(t), esc(t), counts[t], NL) for t in types)
    form_css, form_html = extract_form(outline['name'])

    body = NL.join([
        '<section class="vs-hero">',
        '  <div class="cw rv">',
        '    <nav class="vs-crumb"><a href="index.html">Home</a><span style="opacity:.45">/</span>'
        '<a href="volunteer.html">Corporate Volunteering</a><span style="opacity:.45">/</span>%s</nav>' % esc(outline['name']),
        '    <span class="ey">Corporate volunteering</span>',
        '    <h1>%s sites</h1>' % esc(outline['name']),
        '    <p class="lede">%d sites across %s where your team can spend a day on the ground. '
        '%s Pick one from the map or the list, then send us your dates from the form below.</p>'
        % (len(sites), esc(outline['name']), esc(summarise(sites))),
        '      <ul class="vs-tally">',
        tally.rstrip(NL),
        '      </ul>',
        '  </div>',
        '</section>',
        '',
        '<section class="vs-wrap">',
        '  <div class="cw">',
        '    <div class="vs-split">',
        '      <div class="vs-mapcol rv">',
        '        <div class="vm">',
        svg_map(code, outline, sites),
        '        </div>',
        '        <p class="vm-cap">The map is zoomed to where the sites actually are; the small '
        'inset shows that area within %s. Pin positions are approximate. Hover a pin to find it '
        'in the list, or tap one to jump straight to it.</p>' % esc(outline['name']),
        '      </div>',
        '      <div class="rv d1">',
        '        <div class="vs-filter">',
        '        <button type="button" data-f="all" class="on">All <span>%d</span></button>' % len(sites),
        filters.rstrip(NL),
        '        </div>',
        '        <div class="vs-tools">',
        '          <p class="vs-count" id="vsCount">%d sites</p>' % len(sites),
        '          <label class="vs-sort" for="vsSort">Sort by',
        '            <select id="vsSort">',
        '              <option value="distance">Distance from %s</option>' % esc(sites[0]['cbd']),
        '              <option value="name">Name</option>',
        '              <option value="type">Site type</option>',
        '            </select>',
        '          </label>',
        '        </div>',
        '        <div class="vs-listwrap">',
        '        <ul class="vs-list">',
        NL.join(card(i, s) for i, s in enumerate(sites, 1)),
        '        </ul>',
        '        </div>',
        '        <button class="vs-more" id="vsMore" type="button" hidden>Show all %d sites</button>' % len(sites),
        '        <p class="vs-empty" id="vsEmpty" hidden>No sites of that type in %s. '
        'Choose another type, or pick All.</p>' % esc(outline['name']),
        '      </div>',
        '    </div>',
        '  </div>',
        '</section>',
        '',
        gallery(code, idx),
        '',
        form_html,
    ])
    desc = ('%d corporate volunteering sites across %s, from national parks and community '
            'nurseries to wetlands and conservation centres.' % (len(sites), outline['name']))
    write_page(slug_state(code), '%s Volunteering Sites' % code, esc(desc), body,
               page_css=PAGE_CSS + NL + form_css, extra_js=PAGE_JS)
    return len(sites)


def main():
    sites = json.load(open(SITES, encoding='utf-8'))
    outlines = json.load(open(OUTLINES, encoding='utf-8'))
    by = {}
    for s in sites:
        if s.get('lat') is None:
            print('  no coordinates, skipped: %s' % s['id'])
            continue
        by.setdefault(s['state'], []).append(s)
    for st in by:
        by[st].sort(key=lambda s: s['name'].lower())

    for idx, code in enumerate(PAGES):
        n = state_page(code, outlines[code], by[code], idx)
        print('%s  %-22s %2d sites' % (code, slug_state(code), n))
    extra = sorted(set(by) - set(PAGES))
    for code in extra:
        print('%s  listed on volunteer.html only, no page (%d site%s)'
              % (code, len(by[code]), '' if len(by[code]) == 1 else 's'))
    patch_hub(by)
    print('now run: python3 tools/sync.py')




# ---------------------------------------------------------------------------
# The hub page section: every state, every site, and a way through to the
# state page. Replaces the old four-city tab switcher.
# ---------------------------------------------------------------------------

HUB_CSS = '''
.vw-tabs{display:flex;flex-wrap:wrap;gap:.5rem;margin:2rem 0 1.6rem}
.vw-tabs button{display:inline-flex;align-items:center;gap:.55em;font-size:.88rem;font-weight:600;
  padding:.7em 1.1em;border:1.5px solid var(--bark-mid);background:transparent;color:var(--euc-deep);
  cursor:pointer;transition:.2s}
.vw-tabs button:hover{border-color:var(--euc-deep)}
.vw-tabs button span{font-size:.72rem;font-weight:700;background:var(--euc-soft);color:var(--euc-deep);
  padding:.2em .5em;transition:.2s}
.vw-tabs button[aria-selected="true"]{background:var(--euc-deep);border-color:var(--euc-deep);color:var(--cream)}
.vw-tabs button[aria-selected="true"] span{background:rgba(250,246,242,.22);color:var(--cream)}

.vw-panel{background:var(--white);border:1px solid var(--rule);padding:1.8rem}
@media(max-width:600px){.vw-panel{padding:1.3rem 1.2rem}}
.vw-p[hidden]{display:none}
.vw-p-head{display:flex;align-items:flex-start;gap:1.5rem;flex-wrap:wrap;
  padding-bottom:1.2rem;margin-bottom:1.3rem;border-bottom:1px solid var(--rule)}
.vw-p-head h3{font-size:1.3rem;margin:0 0 .4rem;color:var(--euc-deep)}
.vw-p-head p{margin:0;font-size:.92rem;color:var(--stone);line-height:1.55;max-width:62ch}
.vw-go{margin-left:auto;font-size:.8rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--euc-deep);border:1.5px solid var(--euc-deep);padding:.7em 1.15em;transition:.2s;
  white-space:nowrap}
.vw-go:hover{background:var(--euc-deep);color:var(--cream);opacity:1}
.vw-only{margin-left:auto;font-size:.8rem;color:var(--stone);white-space:nowrap}
.vw-sites{list-style:none;margin:0;padding:0;columns:3;column-gap:2rem}
@media(max-width:1000px){.vw-sites{columns:2}}
@media(max-width:620px){.vw-sites{columns:1}}
.vw-sites li{break-inside:avoid;margin:0 0 .9rem;padding-left:.9rem;position:relative;line-height:1.45}
.vw-sites li::before{content:"";position:absolute;left:0;top:.5em;width:5px;height:5px;
  border-radius:50%;background:var(--euc)}
.vw-sites b{display:block;font-weight:600;color:var(--euc-deep);font-size:.94rem}
.vw-sites span{font-size:.82rem;color:var(--stone)}
.vw-sites .vw-ty{color:var(--euc);font-weight:600}
.vw-sites .vw-km{color:var(--bark-mid)}
'''

HUB_JS = '''
  // Where we run: one panel at a time, switched by the state tabs.
  var wt = document.getElementById('vwTabs');
  if (wt) {
    var panels = [].slice.call(document.querySelectorAll('.vw-p'));
    wt.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      Array.prototype.forEach.call(wt.children, function (x) {
        x.setAttribute('aria-selected', x === b ? 'true' : 'false');
      });
      panels.forEach(function (p) { p.hidden = p.dataset.s !== b.dataset.s; });
      var sel = document.getElementById('vf-state');
      if (sel) sel.value = b.dataset.s;
    });
    wt.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      var tabs = [].slice.call(wt.children);
      var i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      e.preventDefault();
      var n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      n.focus(); n.click();
    });
  }
'''


def hub_section(by):
    order = sorted(by, key=lambda k: (-len(by[k]), k))
    tabs, panels = [], []
    for n, code in enumerate(order):
        rows = sorted(by[code], key=lambda s: s['name'].lower())
        name = rows[0]['state_name']
        tabs.append('      <button type="button" role="tab" data-s="%s" aria-selected="%s" '
                    'aria-controls="vwp-%s">%s <span>%d</span></button>'
                    % (code, 'true' if n == 0 else 'false', code.lower(), esc(name), len(rows)))
        items = ''.join(
            '          <li><b>%s</b><span>%s</span> <span class="vw-ty">%s</span> '
            '<span class="vw-km">%d km</span></li>%s'
            % (esc(s['name']), esc(s['city']), esc(s['type']), s['km'], NL) for s in rows)
        go = ('<a class="vw-go" href="%s">See all %s sites &#8594;</a>' % (slug_state(code), code)
              if code in PAGES else
              '<span class="vw-only">One site, listed here</span>')
        panels.append(NL.join([
            '      <div class="vw-p" id="vwp-%s" data-s="%s" role="tabpanel"%s>'
            % (code.lower(), code, '' if n == 0 else ' hidden'),
            '        <div class="vw-p-head">',
            '          <div>',
            '            <h3>%s</h3>' % esc(name),
            '            <p>%s</p>' % esc(summarise(rows)),
            '          </div>',
            '          %s' % go,
            '        </div>',
            '        <ul class="vw-sites">',
            items.rstrip(NL),
            '        </ul>',
            '      </div>',
        ]))
    return NL.join([
        '<!-- ─── Where we run (state switcher) ───────────────────────────── -->',
        '<!-- Generated by tools/gen_vol_states.py from data/volunteer-sites.json. -->',
        '<section class="v-where" id="where">',
        '  <div class="cw">',
        '    <div class="v-where-h rv">',
        '      <span class="ey">Where we run</span>',
        '      <h2>Our corporate volunteering sites across Australia.</h2>',
        '      <p>%d sites in five states, from harbour bushland and community nurseries to '
        'wetlands, conservation parks and a black cockatoo rehabilitation centre. Pick a state to '
        'see its sites, then open it to see them on a map.</p>' % sum(len(v) for v in by.values()),
        '    </div>',
        '    <div class="vw-tabs" role="tablist" id="vwTabs" aria-label="Choose a state">',
        NL.join(tabs),
        '    </div>',
        '    <div class="vw-panel rv">',
        NL.join(panels),
        '    </div>',
        '  </div>',
        '</section>',
    ])


def patch_hub(by):
    f = 'volunteer.html'
    t = open(f, encoding='utf-8').read()
    orig = t

    a = t.index('<!-- ─── Where we run')
    b = t.index('</section>', t.index('<section class="v-where"')) + len('</section>')
    t = t[:a] + hub_section(by) + t[b:]

    # the old city tab switcher and its data have nothing left to drive
    if '  var CITY={' in t:
        ja = t.index('  var CITY={')
        jb = t.index('  // quick check', ja)
        t = t[:ja] + t[jb:]

    # guard on the handler itself: the markup above has already added 'vwTabs'
    if "getElementById('vwTabs')" not in t:
        anchor = '  // quick check'
        t = t.replace(anchor, HUB_JS + anchor, 1)

    opts = ''.join('<option value="%s">%s</option>' % (c, by[c][0]['state_name'])
                   for c in sorted(by, key=lambda k: (-len(by[k]), k)))
    t = t.replace('<label for="qc-city">City</label>', '<label for="qc-state">State</label>')
    t = t.replace('<select id="qc-city"><option>Sydney</option><option>Melbourne</option>'
                  '<option>Adelaide</option><option>Perth</option></select>',
                  '<select id="qc-state">%s</select>' % opts)
    t = t.replace('<label for="vf-city">Preferred city</label>',
                  '<label for="vf-state">Preferred state</label>')
    t = t.replace('<select id="vf-city">', '<select id="vf-state">')
    t = t.replace('<option>Sydney</option><option>Melbourne</option>'
                  '<option>Adelaide</option><option>Perth</option>', opts)
    t = t.replace("var city=document.getElementById('qc-city').value,",
                  "var state=document.getElementById('qc-state').value,")
    t = t.replace("var c=document.getElementById('vf-city'), z=", "var c=document.getElementById('vf-state'), z=")
    t = t.replace('if(c) c.value=city;', 'if(c) c.value=state;')
    t = t.replace('<b>Enquire</b> Tell us your city, team size and rough dates.',
                  '<b>Enquire</b> Tell us your state, team size and rough dates.')

    # the section's styles, inserted once and refreshed on every run after that
    MARK_A, MARK_B = '/* @vw-start */', '/* @vw-end */'
    css = MARK_A + HUB_CSS + MARK_B
    if MARK_A in t:
        t = t[:t.index(MARK_A)] + css + t[t.index(MARK_B) + len(MARK_B):]
    else:
        i = t.index('</style>')
        t = t[:i] + css + NL + t[i:]

    open(f, 'w', encoding='utf-8').write(t)
    print('volunteer.html: where-we-run section rebuilt by state (%d bytes -> %d)'
          % (len(orig), len(t)))
    leftover = [w for w in ('qc-city', 'vf-city', 'var CITY=', 'data-city') if w in t]
    print('  tab handler wired    : %s' % ("yes" if "getElementById('vwTabs')" in t else 'NO'))
    print('  leftover city wiring : %s' % (leftover or 'none'))
    print('  section styles       : %s' % ('present' if '.vw-tabs{' in t else 'MISSING'))


if __name__ == '__main__':
    main()
