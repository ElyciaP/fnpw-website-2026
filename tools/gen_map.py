#!/usr/bin/env python3
"""Regenerate the interactive map on projects.html from data/projects.json.

THE DATABASE IS data/projects.json. To add/move/remove a pin, edit that file:
  - "lat" / "lon": approximate coordinates (decimal degrees, negative lat)
  - "on_map": false to hide a project's pin (e.g. offshore projects)
  - "pin": [x%, y%] to place a pin by hand (offshore projects at the artwork edge)
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

# Minimum centre-to-centre distance between pins, in calibration units.
# The map renders about 800px wide at 1440, so 74 units is roughly 24px:
# 22px pins with a couple of pixels of air between them.
MIN_GAP = 74
MAX_DRIFT = MIN_GAP * 4     # how far a pin may be nudged from its true spot

# Display order for the state picker. Only states present in the data are
# rendered, each with its project count. "Australia" is nationwide work.
STATE_ORDER = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT',
               'Christmas Island', 'Norfolk Island', 'Lord Howe Island',
               'Australia']
STATE_LABEL = {'Australia': 'Australia-wide'}

projects = json.load(open(os.path.join(ROOT,'data/projects.json')))

def declutter(x, y, placed):
    """Return the nearest free spot to (x, y) that keeps MIN_GAP from every
    pin already placed, searching outward on a spiral."""
    def clear(ax, ay):
        return all(math.hypot(ax-bx, ay-by) >= MIN_GAP for bx, by in placed)
    if clear(x, y):
        return x, y
    best, best_d = (x, y), min(math.hypot(x-bx, y-by) for bx, by in placed)
    r = MIN_GAP
    while r <= MAX_DRIFT:
        steps = max(8, int(2*math.pi*r/(MIN_GAP*0.6)))
        for k in range(steps):
            a = 2*math.pi*k/steps + r*0.01
            ax, ay = x + r*math.cos(a), y + r*math.sin(a)
            if clear(ax, ay):
                return ax, ay
            d = min(math.hypot(ax-bx, ay-by) for bx, by in placed)
            if d > best_d:
                best, best_d = (ax, ay), d
        r += MIN_GAP*0.5
    return best  # crowded: the least-overlapping spot within reach

pins, placed = [], []
for p in projects:
    if not p.get('on_map'): continue
    label, cls = PIL_LABEL[p['pillar']]
    if p.get('pin'):  # offshore projects sit at the edge of the artwork, nearest their island
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
