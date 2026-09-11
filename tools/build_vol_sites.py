"""Turn Helen's site list into data/volunteer-sites.json.

Source: "Vol Site LocationsSheet1 2.csv", the updated corporate volunteering
site list. The CSV is the record; this only normalises it. Coordinates are
added separately by tools/geocode_vol_sites.py.
"""
import csv, json, os, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'Vol Site Locations.csv'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data/volunteer-sites.json'

STATE_NAME = {'NSW': 'New South Wales', 'VIC': 'Victoria', 'QLD': 'Queensland',
              'SA': 'South Australia', 'WA': 'Western Australia',
              'TAS': 'Tasmania', 'NT': 'Northern Territory', 'ACT': 'Australian Capital Territory'}

# Helen writes the manager with its acronym in brackets. The long name is what
# reads on the page; the acronym is kept in case the team wants it.
ACRO = re.compile(r'\s*\(([^)]{2,12})\)\s*$')


def clean(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', clean(s).lower())
    return re.sub(r'^-|-$', '', s)


def main():
    rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
    sites, seen = [], {}
    for r in rows:
        name = clean(r.get('Site Name'))
        if not name:
            continue
        state = clean(r.get('Site State')).upper()
        mgr = clean(r.get('Site Manager'))
        acro = ''
        m = ACRO.search(mgr)
        if m:
            acro = m.group(1)
            mgr = clean(ACRO.sub('', mgr))
        mgr = mgr.rstrip('.')
        rec = {
            'id': '',
            'name': name,
            'type': clean(r.get('Site Type')),
            'address': clean(r.get('Site Address')),
            'city': clean(r.get('Site City')),
            'state': state,
            'state_name': STATE_NAME.get(state, state),
            'postcode': clean(r.get('Site Post Code')),
            'manager': mgr,
            'manager_short': acro,
            'lat': None,
            'lon': None,
        }
        # Lane Cove National Park appears twice with different managers and
        # meeting points, so the id carries the suburb to keep them apart.
        base = slug(name)
        n = seen.get(base, 0)
        seen[base] = n + 1
        rec['id'] = base if not n else '%s-%s' % (base, slug(rec['city']))
        sites.append(rec)

    sites.sort(key=lambda s: (s['state'], s['name'].lower()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(sites, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    by = {}
    for s in sites:
        by.setdefault(s['state'], []).append(s)
    print('sites: %d' % len(sites))
    for st in sorted(by, key=lambda k: -len(by[k])):
        types = sorted({x['type'] for x in by[st]})
        print('  %-4s %2d sites   %s' % (st, len(by[st]), ', '.join(types)))
    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        print('  same name more than once (kept separate): %s' % dupes)
    print('wrote %s' % OUT)


if __name__ == '__main__':
    main()
