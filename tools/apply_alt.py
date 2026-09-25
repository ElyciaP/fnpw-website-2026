"""Apply alt text written by looking at each photograph (Sep 2026).

data/alt-text/alt-remote-by-index.txt  index|alt for the WordPress media URLs listed in
                                       data/alt-text/remote-urls.json (same order)
data/alt-text/alt-local.txt            path|alt for images in assets/

Only fills alt text that is missing or empty. Decorative icons get aria-hidden.
Also writes the alt into data/articles.json and data/projects-content.json so the
generators keep it.
"""
import json, os, re, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
D = 'data/alt-text/'

urls = json.load(open(D + 'remote-urls.json'))
ALT = {}
for ln in open(D + 'alt-remote-by-index.txt', encoding='utf-8'):
    if '|' in ln:
        i, a = ln.rstrip('\n').split('|', 1)
        if a.strip() and a.strip() != 'BROKEN':
            ALT[urls[int(i)]] = a.strip()
for ln in open(D + 'alt-local.txt', encoding='utf-8'):
    if '|' in ln:
        p, a = ln.rstrip('\n').split('|', 1)
        ALT[p] = a.strip()


def needs(tag):
    m = re.search(r'\balt="([^"]*)"', tag)
    return not m or not m.group(1).strip()


def fix_tag(tag):
    if 'aria-hidden' in tag:
        return tag
    s = re.search(r'\bsrc="([^"]+)"', tag)
    if not s:
        return tag
    src = html.unescape(s.group(1))
    if not needs(tag):
        return tag
    if src.startswith('assets/icons/'):
        tag = re.sub(r'\salt="[^"]*"', '', tag)
        return tag.replace('<img', '<img alt="" aria-hidden="true"', 1)
    a = ALT.get(src)
    if not a:
        return tag
    a = html.escape(a, quote=True)
    if re.search(r'\balt="[^"]*"', tag):
        return re.sub(r'\balt="[^"]*"', 'alt="%s"' % a, tag, count=1)
    return tag.replace('<img', '<img alt="%s"' % a, 1)


pages = 0
for f in glob.glob('*.html'):
    t = open(f, encoding='utf-8').read()
    n = re.sub(r'<img\b[^>]*>', lambda m: fix_tag(m.group(0)), t)
    if n != t:
        open(f, 'w', encoding='utf-8').write(n)
        pages += 1
print('pages updated:', pages)


def walk(o):
    c = 0
    if isinstance(o, dict):
        for ik, ak in (('img', 'alt'), ('src', 'alt'), ('hero', 'hero_alt'), ('image', 'alt')):
            if isinstance(o.get(ik), str) and not (o.get(ak) or '').strip() and o[ik] in ALT:
                o[ak] = ALT[o[ik]]; c += 1
        for v in o.values():
            c += walk(v)
    elif isinstance(o, list):
        for v in o:
            c += walk(v)
    return c


for jf in ('data/articles.json', 'data/projects-content.json'):
    if os.path.exists(jf):
        d = json.load(open(jf, encoding='utf-8'))
        c = walk(d)
        json.dump(d, open(jf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(jf, 'alt filled:', c)
