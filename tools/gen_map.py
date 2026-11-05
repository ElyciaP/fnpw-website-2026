#!/usr/bin/env python3
"""Regenerate the interactive map on projects.html from data/projects.json.

THE DATABASE IS data/projects.json. To add/move/remove a pin, edit that file:
  - "lat" / "lon": approximate coordinates (decimal degrees, negative lat)
  - "on_map": false to hide a project's pin (e.g. offshore projects)
  - "pin": [x%, y%] to place a pin by hand (offshore projects at the artwork edge,
    and Wild Heart, a nationwide program, kept clear of the logo in the centre)
  - "state": the state or territory the project sits in ("Australia" for
    nationwide programs). It feeds the mobile state picker and the card badges.
Then run:  python3 tools/gen_map.py

Writes, inside projects.html:
  <!-- @map-pins -->   the pin buttons (desktop map)
  /*@map-data*/        the pin data for the popup script
  <!-- @map-states --> the state picker shown under the artwork on phones
and syncs each project card's data-state / location badge with the database.

Artwork: assets/img/projects-map-brand.webp (+ .png fallback, .svg source),
1500x1289. The calibration below is expressed against the 2461x2115 frame of
the original priority-areas artwork; the brand artwork shares its geometry.
"""
import json, math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# calibration frame (official priority-areas artwork, 2461x2115 source)
CW, CH = 2461, 2115

def px(lat, lon):
    if lat < -40:  # Tasmania has its own frame on this artwork
        return -6571.1 + lon*57.03, -1340.9 + (-lat)*76.92
    return -5535.9 + lon*49.83, -522.2 + (-lat)*56.05

PIL_LABEL = {'parks':('Growing National Parks','pb-parks'),
             'species':('Saving Species','pb-species'),
             'healing':('Healing the Land','pb-healing')}

# Pins sit on their true location. Where several projects share a spot, each
# pin is nudged a short way so it stays visible and clickable, but never far
# enough to leave the landscape it belongs to. Calibration units: the map
# renders about 800px wide at 1440, so 3 units is roughly 1px.
MIN_GAP = 34                # aim for about 11px between pin centres (15px pins)
MAX_DRIFT = 46              # never more than about 15px from the true spot
LABEL_DRIFT = 76            # up to about 25px to step off a region name

# Display order for the state picker. Only states present in the data are
# rendered, each with its project count. "Australia" is nationwide work.
STATE_ORDER = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT',
               'Christmas Island', 'Norfolk Island', 'Lord Howe Island',
               'Australia']
STATE_LABEL = {'Australia': 'Australia-wide'}

projects = json.load(open(os.path.join(ROOT,'data/projects.json')))

# The artwork tells us what sits under each spot (sea, land, priority
# landscape), so a nudged pin can be kept on the same kind of ground as its
# true location. Needs Pillow; without it pins are nudged without that check.
ART = os.path.join(ROOT, 'assets/img/projects-map-brand.png')
try:
    from PIL import Image
    _art = Image.open(ART).convert('RGBA')
except Exception:
    _art = None

def ground(x, y):
    """'pri' for a priority landscape, 'land', 'sea', or None if unknown."""
    if _art is None:
        return None
    W, H = _art.size
    X, Y = int(x / CW * W), int(y / CH * H)
    if not (0 <= X < W and 0 <= Y < H):
        return 'sea'
    r, g, b, a = _art.getpixel((X, Y))
    if a < 128:
        return 'sea'
    return 'pri' if (r + g + b) < 200 else 'land'

# Region names, the logo and the Landscape Priorities pill are read from the
# SVG source so pins can be kept off the lettering. Boxes are in artwork px.
SVG = os.path.join(ROOT, 'assets/img/projects-map-brand.svg')

def _label_boxes():
    try:
        s = open(SVG).read()
    except OSError:
        return []
    boxes = []
    lab = s[s.find('<g id="labels">'):] if '<g id="labels">' in s else ''
    for d in re.findall(r'<path[^>]* d="([^"]+)"', lab):
        xs, ys, cmd, nums = [], [], 'M', []
        for tok in re.findall(r'[MLQHVZ]|-?\d+(?:\.\d+)?', d):
            if tok.isalpha():
                cmd = tok
                continue
            v = float(tok)
            if cmd == 'H':
                xs.append(v)
            elif cmd == 'V':
                ys.append(v)
            else:
                nums.append(v)
                if len(nums) == 2:
                    xs.append(nums[0]); ys.append(nums[1]); nums = []
        if xs and ys:
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
    for tag in re.findall(r'<(?:image|rect)\b[^>]*>', s):
        a = dict(re.findall(r'\b(x|y|width|height)="([\d.]+)"', tag))
        if len(a) == 4:
            x0, y0 = float(a['x']), float(a['y'])
            boxes.append((x0, y0, x0 + float(a['width']), y0 + float(a['height'])))
    return boxes

LABELS = _label_boxes()
PIN_R = 16      # pin radius plus a little air, in artwork px (1500 wide)

def on_label(x, y):
    """True if a pin at (x, y) would sit on a region name or the logo."""
    X, Y = x / CW * 1500, y / CH * 1289
    return any(x0 - PIN_R < X < x1 + PIN_R and y0 - PIN_R < Y < y1 + PIN_R
               for x0, y0, x1, y1 in LABELS)

def declutter(x, y, placed):
    """Keep (x, y) if it is clear of every pin already placed. Otherwise try
    a few close rings around it and take the spot that is furthest from its
    neighbours while staying on the same ground. Crowded spots keep a small
    overlap rather than drifting away from where the project is."""
    def gap(ax, ay):
        return min((math.hypot(ax-bx, ay-by) for bx, by in placed), default=1e9)
    if gap(x, y) >= MIN_GAP and not on_label(x, y):
        return x, y
    home = ground(x, y)
    best, best_d = (x, y), (gap(x, y) if not on_label(x, y) else -1)
    reach = MAX_DRIFT
    if on_label(x, y):  # the colour under lettering says nothing about the ground
        reach, home = LABEL_DRIFT, ('ashore' if home != 'sea' else 'sea')
    r = MIN_GAP * 0.5
    while r <= reach:
        steps = 16
        for k in range(steps):
            a = 2*math.pi*k/steps
            ax, ay = x + r*math.cos(a), y + r*math.sin(a)
            g = ground(ax, ay)
            if home == 'ashore' and g == 'sea':
                continue
            if home not in (None, 'sea', 'ashore') and g != home:
                continue
            if on_label(ax, ay):
                continue
            d = gap(ax, ay)
            if d >= MIN_GAP:
                return ax, ay
            if d > best_d + 2:
                best, best_d = (ax, ay), d
        r += MIN_GAP * 0.25
    return best

pins, placed = [], []
for p in projects:
    if not p.get('on_map'): continue
    label, cls = PIL_LABEL[p['pillar']]
    if p.get('pin'):  # placed by hand: offshore islands at the artwork edge, Wild Heart off the logo
        pins.append(dict(s=p['slug'], t=p['title'], st=p['state'], pl=label, pc=cls,
                         x=p['pin'][0], y=p['pin'][1]))
        continue
    x, y = px(p['lat'], p['lon'])
    x, y = declutter(x, y, placed)
    placed.append((x, y))
    pins.append(dict(s=p['slug'], t=p['title'], st=p['state'], pl=label, pc=cls,
                     x=round(x/CW*100,2), y=round(y/CH*100,2)))

pin_html = '\n'.join(
    f'<button class="im-pin {p["pc"]}" style="left:{p["x"]}%;top:{p["y"]}%" data-i="{i}" '
    f'aria-label="{p["t"]}, {p["st"]}" title="{p["t"]}"></button>'
    for i,p in enumerate(pins))

# ---- state picker (phones) ----
counts = {}
for p in projects:
    counts[p['state']] = counts.get(p['state'], 0) + 1
extra = sorted(s for s in counts if s not in STATE_ORDER)
state_btns = [f'<button type="button" class="im-st on" data-st="all" aria-pressed="true">All ({len(projects)})</button>']
for s in STATE_ORDER + extra:
    if s not in counts: continue
    state_btns.append(f'<button type="button" class="im-st" data-st="{s}" aria-pressed="false">'
                      f'{STATE_LABEL.get(s, s)} ({counts[s]})</button>')
states_html = '\n'.join(state_btns)

f = os.path.join(ROOT,'projects.html')
t = open(f).read()
t = re.sub(r'<!-- @map-pins -->.*?<!-- /@map-pins -->',
           '<!-- @map-pins -->\n'+pin_html+'\n<!-- /@map-pins -->', t, count=1, flags=re.S)
t = re.sub(r'/\*@map-data\*/.*?/\*/@map-data\*/',
           '/*@map-data*/'+json.dumps(pins)+'/*/@map-data*/', t, count=1, flags=re.S)
t, n_states = re.subn(r'<!-- @map-states -->.*?<!-- /@map-states -->',
           '<!-- @map-states -->\n'+states_html+'\n<!-- /@map-states -->', t, count=1, flags=re.S)
t = re.sub(r'\d+ projects(<span class="im-leg-click">)', f'{len(pins)} projects\\1', t)

# ---- sync card badges with the database ----
by_slug = {p['slug']: p for p in projects}
n_cards = 0
def fix_card(m):
    global n_cards
    card = m.group(0)
    slug = m.group(1)
    p = by_slug.get(slug)
    if not p: return card
    n_cards += 1
    card = re.sub(r'<article class="pc"( data-pil="[^"]*")?( data-state="[^"]*")?',
                  lambda mm: f'<article class="pc"{mm.group(1) or ""} data-state="{p["state"]}"', card, count=1)
    card = re.sub(r'<span class="pc-lo">[^<]*</span>', f'<span class="pc-lo">{p["state"]}</span>', card, count=1)
    return card
t = re.sub(r'<article class="pc"[^>]*><a class="pc-link" href="project-([^"]+)\.html">.*?</article>',
           fix_card, t, flags=re.S)
open(f,'w').write(t)
print(f'map regenerated: {len(pins)} pins, {len(state_btns)} state buttons'
      f'{"" if n_states else " (no @map-states region found)"}, {n_cards} cards synced')
