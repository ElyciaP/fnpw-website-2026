#!/usr/bin/env python3
"""Regenerate the interactive map pins on projects.html from data/projects.json.

THE DATABASE IS data/projects.json. To add/move/remove a pin, edit that file:
  - "lat" / "lon": approximate coordinates (decimal degrees, negative lat)
  - "on_map": false to hide a project's pin (e.g. offshore projects)
Then run:  python3 tools/gen_map.py
"""
import json, math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CX0, CY0, CW, CH = 40, 270, 1960, 1420   # calibration of assets/img/projects-map.png

def px(lat, lon):
    x = 330 + (lon-113)*34.85 - CX0
    y = 300 + (-10.7-lat)*40.37 - CY0
    if lat < -40: x -= 140   # stylised Tasmania offset
    return x, y

PIL_LABEL = {'parks':('Growing National Parks','pb-parks'),
             'species':('Saving Species','pb-species'),
             'healing':('Healing the Land','pb-healing')}

projects = json.load(open(os.path.join(ROOT,'data/projects.json')))
pins, cells = [], {}
for p in projects:
    if not p.get('on_map'): continue
    x, y = px(p['lat'], p['lon'])
    key = (int(x//34), int(y//34))
    n = cells.get(key,0); cells[key]=n+1
    if n:
        ang=n*2.4; r=16+7*(n//6)
        x+=r*math.cos(ang); y+=r*math.sin(ang)
    label, cls = PIL_LABEL[p['pillar']]
    pins.append(dict(s=p['slug'], t=p['title'], st=p['state'], pl=label, pc=cls,
                     x=round(x/CW*100,2), y=round(y/CH*100,2)))

pin_html = '\n'.join(
    f'<button class="im-pin {p["pc"]}" style="left:{p["x"]}%;top:{p["y"]}%" data-i="{i}" '
    f'aria-label="{p["t"]}, {p["st"]}" title="{p["t"]}"></button>'
    for i,p in enumerate(pins))

f = os.path.join(ROOT,'projects.html')
t = open(f).read()
t = re.sub(r'<!-- @map-pins -->.*?<!-- /@map-pins -->',
           '<!-- @map-pins -->\n'+pin_html+'\n<!-- /@map-pins -->', t, count=1, flags=re.S)
t = re.sub(r'/\*@map-data\*/.*?/\*/@map-data\*/',
           '/*@map-data*/'+json.dumps(pins)+'/*/@map-data*/', t, count=1, flags=re.S)
open(f,'w').write(t)
print(f'map regenerated: {len(pins)} pins')
