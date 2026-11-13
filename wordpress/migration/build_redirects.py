"""Build redirects.csv (Redirection import format) and redirects-review.md.

Merges the redirects exported from live (source/redirection-export-*.csv) with
the redirects page-map.csv calls for, resolves chains to their final target,
drops redirects whose source is a real page in the new site, and flags targets
that could not be confirmed. Optional: source/live-target-check.json, a map of
target path -> [status, final_path] read from the live site.

    python3 wordpress/migration/build_redirects.py
"""
import csv, glob, json, os, urllib.parse as U

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
SITE = 'fnpw.org.au'
BUSH = 'https://bush.fnpw.org.au'
HH = 'https://habitat-heroes.fnpw.org.au'
GAT = 'https://giveatree.fnpw.org.au/'
# The old giving site is retired. Where each of its pages goes now (decision D8).
DEAD_HOST = 'support.fnpw.org.au'
DEAD_MAP = (('habitat-hero', HH), ('plant-a-tree', GAT), ('gift-a-tree', GAT))

# Where a redirect goes when its old target no longer exists and no page has the same slug.
FALLBACKS = (('/project/', '/projects/'), ('/news/', '/news/'), ('/grant/', '/grants/'), ('/category/', '/news/'),
             ('/donation-thank-you', '/thank-you/'))

# Dead targets whose page still exists under a renamed slug (matched by hand, 11 Nov 2026).
RENAMED = {
    '/project/nilpena-station/': '/project/nilpena-nationalpark/',
    '/project/bandicoot-super-highway/': '/project/bandicoot-superhighway-project/',
    '/project/patfm-redlands-koala-planting/': '/project/redlands-koala-planting/',
    '/project/private-land-conservation-grants-2017/': '/project/private-land-conservation-grants/',
    '/grant/community-conservation-grants/': '/project/community-conservation-grants/',
    '/news/latest-news/fnpw-new-chair-new-directors/': '/news/media/fnpw-new-chair-and-new-directors/',
    '/news/latest-news/celebrating-women-in-indigenous-ranger-programs-on-international-womens-day/': '/news/latest-news/first-nations-women-in-ranger-programs/',
    '/news/latest-blogs/september-is-biodiversity-month/': '/biodiversity-month/',
}
# Placeholder and test rows left in Redirection that are not real addresses.
JUNK_SOURCES = ('/source url/', '/news/latest-news/test/')

FIELDS = ['source', 'target', 'regex', 'code', 'type', 'hits', 'title', 'status']


def norm(u):
    """Path form for comparing: internal URLs lose the host, gain a trailing slash, lower case."""
    u = (u or '').strip()
    p = U.urlparse(u)
    if p.netloc and p.netloc.replace('www.', '') != SITE:
        return u.rstrip('/')
    path = p.path or '/'
    if not path.startswith('/'):
        path = '/' + path
    if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
        path += '/'
    return path.lower() + (('?' + p.query) if p.query else '')


def external(u):
    p = U.urlparse(u)
    return bool(p.netloc) and p.netloc.replace('www.', '') != SITE


exp = sorted(glob.glob('source/redirection-export-*.csv'))[-1]
old = list(csv.DictReader(open(exp, encoding='utf-8-sig')))
pm = list(csv.DictReader(open('page-map.csv', encoding='utf-8')))
live_check = {k: v for k, v in json.load(open('source/live-target-check.json')).items() if not k.startswith('_')} if os.path.exists('source/live-target-check.json') else {}

# Every address that is a real page, post, project or archive after launch.
real = {norm(r['wp_url']) for r in pm if r['wp_url'] and r['action'] in ('keep', 'replace', 'new')}
real |= {'/', '/news/'}
new_redirects = {norm(r['live_url']): (r['redirect_to'], r['notes']) for r in pm if r['action'] in ('redirect', 'retire') and r['redirect_to']}

rows, notes = {}, []          # source -> row ; review notes
order = []


def put(src, row):
    if src not in rows:
        order.append(src)
    rows[src] = row


dropped_disabled = 0
for r in old:
    if r['status'] != 'active':
        dropped_disabled += 1
        notes.append(('Dropped (disabled on live)', r['source'], r['target'], ''))
        continue
    if norm(r['source']) in JUNK_SOURCES:
        notes.append(('Dropped (placeholder or test row)', r['source'], r['target'], ''))
        continue
    put(norm(r['source']), dict(r))

for src, (target, why) in new_redirects.items():
    if src in rows and norm(rows[src]['target']) != norm(target):
        notes.append(('Retargeted for the new site', src, target, 'was ' + rows[src]['target']))
    hits = rows[src]['hits'] if src in rows else '0'
    put(src, {'source': src, 'target': target, 'regex': '0', 'code': '301', 'type': 'url', 'hits': hits, 'title': 'Launch 2026', 'status': 'active'})

# Old giving site
for src, r in rows.items():
    if DEAD_HOST in r['target']:
        t = r['target'].lower()
        dest = next((d for k, d in DEAD_MAP if k in t), BUSH)
        notes.append(('Old giving site retired', src, dest, 'was ' + r['target']))
        r['target'], r['code'], r['title'] = dest, '301', 'Launch 2026'

# Resolve chains
def final(target, seen=()):
    n = norm(target)
    if external(target) or n in seen:
        return target, n in seen
    if n in rows and n not in real:
        return final(rows[n]['target'], seen + (n,))
    return target, False

for src, r in list(rows.items()):
    t, loop = final(r['target'], (src,))
    if loop:
        notes.append(('Loop removed', src, r['target'], 'source and target point at each other'))
        del rows[src]; order.remove(src); continue
    if norm(t) != norm(r['target']):
        notes.append(('Chain shortened', src, t, 'was ' + r['target']))
        r['target'] = t

# A redirect must not sit on top of a real page, or point at itself
for src in list(rows):
    r = rows[src]
    if src in real and src not in new_redirects:
        notes.append(('Dropped (source is a page in the new site)', src, r['target'], ''))
        del rows[src]; order.remove(src)
    elif norm(r['target']) == src:
        notes.append(('Dropped (points at itself)', src, r['target'], ''))
        del rows[src]; order.remove(src)

# Targets: known, confirmed on live, or to check
unknown = []
for src in order:
    r = rows[src]
    if external(r['target']):
        continue
    n = norm(r['target'])
    if n in real:
        continue
    chk = live_check.get(n)
    if chk and chk[0] == 200:
        fin = norm(chk[1]) if chk[1] else n
        if fin != n and (fin in real or fin == '/'):
            notes.append(('Target moved on live, followed', src, fin, 'was ' + r['target']))
            r['target'] = fin
        elif fin in real or fin == n:
            notes.append(('Target is outside the page map but works on live', src, r['target'], 'check on staging'))
        continue
    if chk:
        slug = n.rstrip('/').rsplit('/', 1)[-1]
        same = sorted(u for u in real if u.rstrip('/').rsplit('/', 1)[-1] == slug) if slug else []
        if len(same) == 1:
            notes.append(('Broken on live, repaired (same page found at its current address)', src, same[0], 'was ' + r['target']))
            r['target'] = same[0]
            continue
        if n in RENAMED and RENAMED[n] in real:
            notes.append(('Broken on live, repaired (page was renamed, please review the match)', src, RENAMED[n], 'was ' + r['target']))
            r['target'] = RENAMED[n]
            continue
        fallback = next((d for pre, d in FALLBACKS if n.startswith(pre)), '/')
        notes.append(('Broken on live, sent to the closest page (please review)', src, fallback, 'was ' + r['target'] + ', which returns %s' % chk[0]))
        r['target'] = fallback
    else:
        unknown.append(n)
        notes.append(('Target not in the page map', src, r['target'], 'check on staging'))

for src in list(order):
    r = rows[src]
    t, loop = final(r['target'], (src,))
    if not loop and norm(t) != norm(r['target']):
        r['target'] = t
    if loop or norm(r['target']) == src:
        notes.append(('Dropped (points at itself)', src, r['target'], ''))
        del rows[src]; order.remove(src)

# Reef's review, 13 Nov 2026: three destinations corrected, and the general giving
# addresses made temporary (302) so they can follow each appeal.
REEF_TARGETS = {
    '/donation/leave-a-legacy-for-the-future': '/bequest/',
    '/donation/donate-to-outdoors-for-a-cause': 'https://bush.fnpw.org.au',
    '/fnpw/fnpw/fundraising/donate-pages/appeals.aspx': 'https://bush.fnpw.org.au',
}
REEF_TEMPORARY = {'/donations', '/donation', '/appeals', '/appeals/current-appeal', '/donation/plant-a-tree'}
for src in order:
    key = src.lower().rstrip('/')
    if key in REEF_TARGETS:
        rows[src]['target'] = REEF_TARGETS[key]
    if key in REEF_TEMPORARY:
        rows[src]['code'] = '302'

with open('redirects.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, FIELDS, quoting=csv.QUOTE_ALL)
    w.writeheader()
    for src in order:
        r = rows[src]
        r['source'] = r['source'] if norm(r['source']) == src else src
        w.writerow({k: r.get(k, '') for k in FIELDS})

json.dump(sorted(set(unknown)), open('source/redirect-targets-to-check.json', 'w'), indent=0)

groups = {}
for kind, s, t, extra in notes:
    groups.setdefault(kind, []).append((s, t, extra))
out = ['# Redirect map review', '',
       'Written by `build_redirects.py`. `redirects.csv` is the full set for launch: %d redirects, from %d on live plus %d the new site needs.' % (len(order), len(old), len(new_redirects)), '',
       'Because Redirection adds imported rows without replacing old ones, the launch step is: export a backup, delete the existing redirects, then import `redirects.csv`.', '',
       '| Change | Count |', '|---|---|']
for k in sorted(groups, key=lambda k: (not k.startswith('DEAD'), k)):
    out.append('| %s | %d |' % (k, len(groups[k])))
for k in sorted(groups, key=lambda k: (not k.startswith('DEAD'), k)):
    out += ['', '## %s' % k, '', '| Source | Target | Note |', '|---|---|---|']
    out += ['| %s | %s | %s |' % x for x in groups[k]]
open('redirects-review.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('%d redirects written; %d targets to check' % (len(order), len(set(unknown))))
for k, v in sorted(groups.items()):
    print('  %-48s %d' % (k, len(v)))
