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
import json, math, os, sys, html as H

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
        '        <li class="vs-card" data-i="%d" data-type="%s" tabindex="0">%s'
        '          <span class="vs-num">%d</span>%s'
        '          <div class="vs-bd">%s'
        '            <h3>%s</h3>%s'
        '            <p class="vs-meta">%s</p>%s'
        '            <p class="vs-addr">%s</p>%s'
        '            <p class="vs-mgr"><span>Managed with</span> %s</p>%s'
        '          </div>%s        </li>'
        % (i, esc(s['type']), NL, i, NL, NL, esc(s['name']), NL,
           '<span class="vs-dot"></span>'.join(bits), NL,
           esc(', '.join(x for x in (s['address'], s['postcode']) if x)), NL,
           esc(s['manager']), NL, NL))


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

.vs-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.8rem}
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
.vs-count{font-size:.82rem;color:var(--stone);margin:0 0 1rem}
'''

PAGE_JS = '''<script>
(function () {
  var pins = [].slice.call(document.querySelectorAll('.vm-pin'));
  var cards = [].slice.call(document.querySelectorAll('.vs-card'));
  if (!pins.length) return;

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

  // Clicking a pin brings its entry into view, which is the point of the map
  // on a phone, where the two are stacked rather than side by side.
  pins.forEach(function (p) {
    p.addEventListener('click', function () {
      var c = cards.filter(function (x) { return x.dataset.i === p.dataset.i; })[0];
      if (c) { c.scrollIntoView({ behavior: 'smooth', block: 'center' }); c.focus({ preventScroll: true }); }
    });
    p.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); p.click(); }
    });
  });

  var btns = [].slice.call(document.querySelectorAll('.vs-filter button'));
  var count = document.getElementById('vsCount');
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      btns.forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      var f = b.dataset.f, shown = 0;
      cards.forEach(function (c) {
        var hit = (f === 'all' || c.dataset.type === f);
        c.hidden = !hit;
        if (hit) shown++;
        pins.forEach(function (p) {
          if (p.dataset.i === c.dataset.i) p.style.opacity = hit ? '' : '.18';
        });
      });
      if (count) count.textContent = shown + (shown === 1 ? ' site' : ' sites');
    });
  });
})();
</script>'''


def state_page(code, outline, sites):
    types = sorted({s['type'] for s in sites})
    tally = ''.join('        <li>%d %s</li>%s'
                    % (sum(1 for s in sites if s['type'] == t), esc(t + ('s' if not t.endswith('s') else '')), NL)
                    for t in types)
    filters = ''.join('        <button type="button" data-f="%s">%s</button>%s' % (esc(t), esc(t), NL)
                      for t in types)
    body = NL.join([
        '<section class="vs-hero">',
        '  <div class="cw rv">',
        '    <nav class="vs-crumb"><a href="index.html">Home</a><span style="opacity:.45">/</span>'
        '<a href="volunteer.html">Corporate Volunteering</a><span style="opacity:.45">/</span>%s</nav>' % esc(outline['name']),
        '    <span class="ey">Corporate volunteering</span>',
        '    <h1>%s sites</h1>' % esc(outline['name']),
        '    <p class="lede">%d sites across %s where your team can spend a day on the ground. '
        'Pick one from the map or the list, then tell us your dates and we will arrange the rest.</p>'
        % (len(sites), esc(outline['name'])),
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
        '        <p class="vm-cap">The map is zoomed to where the sites actually are; the small inset '
        'shows that area within %s. Pin positions are approximate. Hover a pin to find it in the '
        'list, or tap one to jump straight to it.</p>' % esc(outline['name']),
        '      </div>',
        '      <div class="rv d1">',
        '        <div class="vs-filter">',
        '        <button type="button" data-f="all" class="on">All sites</button>',
        filters.rstrip(NL),
        '        </div>',
        '        <p class="vs-count" id="vsCount">%d sites</p>' % len(sites),
        '        <ul class="vs-list">',
        NL.join(card(i, s) for i, s in enumerate(sites, 1)),
        '        </ul>',
        '      </div>',
        '    </div>',
        '  </div>',
        '</section>',
        '',
        '<section class="sec dark">',
        '  <div class="cw rv" style="text-align:center">',
        '    <h2 style="max-width:22ch;margin:0 auto 1rem">Bring your team to one of these sites.</h2>',
        '    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Tell us your team size and '
        'rough dates and we will match you to a site and a land manager.</p>',
        '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
        '<a class="btn-p" href="volunteer.html#enquire">Enquire about a day</a>'
        '<a class="btn-o" href="volunteer.html">All corporate volunteering</a></div>',
        '  </div>',
        '</section>',
    ])
    desc = ('%d corporate volunteering sites across %s, from national parks and community nurseries '
            'to wetlands and conservation centres.' % (len(sites), outline['name']))
    write_page(slug_state(code), '%s Volunteering Sites' % code, esc(desc), body,
               page_css=PAGE_CSS, extra_js=PAGE_JS)
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

    for code in PAGES:
        n = state_page(code, outlines[code], by[code])
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
.vw-states{display:flex;flex-direction:column;gap:1.4rem;margin-top:2rem}
.vw-state{background:var(--white);border:1px solid var(--rule);padding:1.6rem 1.8rem}
@media(max-width:600px){.vw-state{padding:1.3rem 1.2rem}}
.vw-head{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;
  padding-bottom:1rem;margin-bottom:1.1rem;border-bottom:1px solid var(--rule)}
.vw-head h3{font-size:1.3rem;margin:0;color:var(--euc-deep)}
.vw-n{font-size:.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--euc-deep);background:var(--euc-soft);padding:.35em .7em}
.vw-go{margin-left:auto;font-size:.8rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--euc-deep);border:1.5px solid var(--euc-deep);padding:.65em 1.1em;transition:.2s;
  white-space:nowrap}
.vw-go:hover{background:var(--euc-deep);color:var(--cream);opacity:1}
.vw-only{margin-left:auto;font-size:.8rem;color:var(--stone)}
.vw-sites{list-style:none;margin:0;padding:0;columns:3;column-gap:2rem}
@media(max-width:1000px){.vw-sites{columns:2}}
@media(max-width:620px){.vw-sites{columns:1}}
.vw-sites li{break-inside:avoid;margin:0 0 .9rem;padding-left:.9rem;position:relative;line-height:1.45}
.vw-sites li::before{content:"";position:absolute;left:0;top:.5em;width:5px;height:5px;
  border-radius:50%;background:var(--euc)}
.vw-sites b{display:block;font-weight:600;color:var(--euc-deep);font-size:.94rem}
.vw-sites span{font-size:.82rem;color:var(--stone)}
.vw-sites .vw-ty{color:var(--euc);font-weight:600}
'''


def hub_section(by):
    order = sorted(by, key=lambda k: (-len(by[k]), k))
    blocks = []
    for code in order:
        rows = by[code]
        name = rows[0]['state_name']
        items = ''.join(
            '          <li><b>%s</b><span>%s</span> <span class="vw-ty">%s</span></li>%s'
            % (esc(s['name']), esc(s['city']), esc(s['type']), NL)
            for s in sorted(rows, key=lambda s: s['name'].lower()))
        go = ('<a class="vw-go" href="%s">See all %s sites &#8594;</a>' % (slug_state(code), code)
              if code in PAGES else
              '<span class="vw-only">One site, listed here</span>')
        blocks.append(
            '      <article class="vw-state rv">%s'
            '        <header class="vw-head">%s'
            '          <h3>%s</h3>%s'
            '          <span class="vw-n">%d site%s</span>%s'
            '          %s%s'
            '        </header>%s'
            '        <ul class="vw-sites">%s%s        </ul>%s'
            '      </article>'
            % (NL, NL, esc(name), NL, len(rows), '' if len(rows) == 1 else 's', NL, go, NL, NL,
               NL, items, NL))
    return NL.join([
        '<!-- ─── Where we run (by state) ─────────────────────────────────── -->',
        '<!-- Generated by tools/gen_vol_states.py from data/volunteer-sites.json. -->',
        '<section class="v-where" id="where">',
        '  <div class="cw">',
        '    <div class="v-where-h rv">',
        '      <span class="ey">Where we run</span>',
        '      <h2>Our corporate volunteering sites across Australia.</h2>',
        '      <p>%d sites in five states, from harbour bushland and community nurseries to '
        'wetlands, conservation parks and a black cockatoo rehabilitation centre. Open a state to '
        'see each site on a map.</p>' % sum(len(v) for v in by.values()),
        '    </div>',
        '    <div class="vw-states">',
        NL.join(blocks),
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

    # the tab switcher and its city data have nothing left to drive
    ja = t.index('  var CITY={')
    jb = t.index('  // quick check', ja)
    t = t[:ja] + t[jb:]

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
    leftover = [w for w in ('qc-city', 'vf-city', 'var CITY=', 'vTabs', 'data-city') if w in t]
    print('  leftover city wiring : %s' % (leftover or 'none'))
    print('  section styles       : %s' % ('present' if '.vw-states{' in t else 'MISSING'))


if __name__ == '__main__':
    main()
