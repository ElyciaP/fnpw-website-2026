#!/usr/bin/env python3
"""Propagate partials/header.html and partials/footer.html into every page.

Edit the partial, then run:  python3 tools/sync.py
The 'on' (active) nav class is applied per page from ACTIVE below.
"""
import re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVE = {
    'index.html': 'index.html', 'about.html': 'about.html',
    'projects.html': 'projects.html', 'contact.html': 'contact.html',
    'partner.html': 'partner.html', 'volunteer.html': 'volunteer.html',
    'bequests.html': 'bequests.html',
    # no active nav item: articles, news, reports, donate, gift-a-tree, bring-back-the-bush
}
hdr = open(os.path.join(ROOT, 'partials/header.html')).read()
ftr = open(os.path.join(ROOT, 'partials/footer.html')).read()
for p in sorted(f for f in os.listdir(ROOT) if f.endswith('.html')):
    path = os.path.join(ROOT, p)
    t = open(path).read()
    h = hdr
    a = ACTIVE.get(p)
    if a:
        h = h.replace(f'<a href="{a}" class=""', f'<a href="{a}" class=" on"', 1)
    t2 = re.sub(r'<!-- @header -->.*?<!-- /@header -->', lambda m: '<!-- @header -->'+h+'<!-- /@header -->', t, count=1, flags=re.S)
    t2 = re.sub(r'<!-- @footer -->.*?<!-- /@footer -->', lambda m: '<!-- @footer -->'+ftr+'<!-- /@footer -->', t2, count=1, flags=re.S)
    if t2 != t:
        open(path,'w').write(t2)
        print('updated', p)
print('done')
