#!/usr/bin/env python3
"""Check every page's <head> metadata (WP7).

    python3 tools/verify_meta.py

Per page: exactly one <title> under 61 characters, one meta description
(120 to 155 characters, 110 to 160 tolerated), one canonical, one og:image,
one og:title, one twitter:card, the icon and RSS links, and every JSON-LD
block parses and uses only schema.org type and property names (release 12.0
list in tools/schemaorg-names.json). Prints counts and exits 1 on any failure.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOCAB = json.load(open(os.path.join(ROOT, 'tools', 'schemaorg-names.json')))
PROPS = set(VOCAB['properties']) | {'@context', '@type', '@id', '@graph'}
TYPES = set(VOCAB['types'])
# schema.org 12.0 ships a few property names only in later releases; none used here.


def walk(obj, errs, where):
    if isinstance(obj, dict):
        t = obj.get('@type')
        for tt in ([t] if isinstance(t, str) else (t or [])):
            if tt not in TYPES:
                errs.append('%s: unknown type %s' % (where, tt))
        for k, v in obj.items():
            # schema.org Actions spec: '<property>-input' / '-output' name a PropertyValueSpecification
            base = re.sub(r'-(input|output)$', '', k)
            if k not in PROPS and base not in PROPS:
                errs.append('%s: unknown property %s' % (where, k))
            walk(v, errs, where)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, errs, where)


def main():
    pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html')))
    fails, warn = [], []
    n_ld, n_types = 0, {}
    desc_strict, title_ok = 0, 0
    for f in pages:
        s = open(os.path.join(ROOT, f)).read()
        head = s[:s.find('</head>')]
        def count(pat):
            return len(re.findall(pat, head))
        titles = re.findall(r'<title>(.*?)</title>', head, re.S)
        if len(titles) != 1:
            fails.append('%s: %d <title>' % (f, len(titles)))
        else:
            t = html.unescape(titles[0])
            if len(t) > 60:
                fails.append('%s: title %d chars' % (f, len(t)))
            else:
                title_ok += 1
        descs = re.findall(r'<meta name="description" content="([^"]*)"', head)
        if len(descs) != 1:
            fails.append('%s: %d descriptions' % (f, len(descs)))
        else:
            d = html.unescape(descs[0])
            if not 110 <= len(d) <= 160:
                fails.append('%s: description %d chars' % (f, len(d)))
            elif 120 <= len(d) <= 155:
                desc_strict += 1
            else:
                warn.append('%s: description %d chars (tolerated)' % (f, len(d)))
        for label, pat in (('canonical', r'<link rel="canonical"'), ('og:image', r'property="og:image"'),
                           ('og:title', r'property="og:title"'), ('og:url', r'property="og:url"'),
                           ('twitter:card', r'name="twitter:card"'), ('icon svg', r'rel="icon" href="favicon.svg"'),
                           ('rss', r'type="application/rss\+xml"'), ('manifest', r'rel="manifest"')):
            c = count(pat)
            if f == '404.html' and label == 'canonical':
                continue
            if c != 1:
                fails.append('%s: %d x %s' % (f, c, label))
        if f == 'search.html' and 'noindex' not in head:
            fails.append('search.html: no noindex')
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            n_ld += 1
            try:
                d = json.loads(m.group(1))
            except Exception as e:
                fails.append('%s: JSON-LD does not parse (%s)' % (f, e))
                continue
            objs = d.get('@graph', [d]) if isinstance(d, dict) else d
            for o in objs:
                n_types[o.get('@type')] = n_types.get(o.get('@type'), 0) + 1
            walk(d, fails, f)
    print('pages checked: %d' % len(pages))
    print('titles under 61 chars: %d' % title_ok)
    print('descriptions 120-155: %d (110-160 tolerated: %d)' % (desc_strict, len(warn)))
    print('JSON-LD blocks parsed: %d' % n_ld)
    print('JSON-LD objects by type: ' + ', '.join('%s %d' % kv for kv in sorted(n_types.items(), key=lambda x: -x[1])))
    for w in warn:
        print('warn:', w)
    for e in fails:
        print('FAIL:', e)
    print('failures: %d' % len(fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
