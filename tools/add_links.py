"""Put the inline links back into entries that were imported without them.

The first harvest took text content only, so the twenty hand-authored articles
lost every link in their body copy. Rather than re-import them and throw away
their hand-set section kickers and image choices, this matches each paragraph,
list item and quote back to the same text in ~/harvest2 and swaps in the version
that still has its <a> tags, with the same link rewriting the importer uses.

    python3 tools/add_links.py            # patch data/articles.json
    python3 tools/add_links.py --report   # say what it would do, write nothing
"""
import json, os, re, sys, glob, html as htmlmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from import_wp import fix_links, strip, HARVEST   # same rewriting rules as the importer

DATA = 'data/articles.json'


def key(t):
    """Match on words only. Entities are decoded first, otherwise "&amp;" and "&"
    normalise differently and every paragraph naming the Foundation fails to match."""
    t = htmlmod.unescape(re.sub(r'<[^>]+>', ' ', t or '')).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', t)).strip()


def main():
    report = '--report' in sys.argv
    arts = json.load(open(DATA, encoding='utf-8'))
    posts = [json.load(open(f, encoding='utf-8'))
             for f in sorted(glob.glob(os.path.join(HARVEST, '*.json')))]
    slugs = {p['slug'] for p in posts}
    projects = {re.sub(r'^project-|\.html$', '', f) for f in glob.glob('project-*.html')}
    stats = {'kept': 0, 'rewritten': 0, 'unwrapped': 0, 'tables': 0}

    # every linked fragment in the harvest, indexed by its plain words
    linked = {}
    for p in posts:
        for x in p['b']:
            vals = [x['v']] if isinstance(x['v'], str) else (x['v'] if isinstance(x['v'], list) else [])
            for v in vals:
                if isinstance(v, str) and '<a ' in v:
                    k = key(v)
                    if k and k not in linked:
                        linked[k] = fix_links(v, slugs, projects, stats)

    patched, touched = 0, set()

    def swap(t):
        nonlocal patched
        if not isinstance(t, str) or '<a ' in t:
            return t
        hit = linked.get(key(t))
        if hit:
            patched += 1
            return hit
        return t

    for a in arts:
        before = patched
        for b in a.get('blocks', []):
            for it in b.get('flow', []):
                for k in ('p', 'q', 'h'):
                    if k in it:
                        it[k] = swap(it[k])
                for k in ('ul', 'ol'):
                    if k in it:
                        it[k] = [swap(x) for x in it[k]]
            if b.get('paras'):
                b['paras'] = [swap(x) for x in b['paras']]
        if patched > before:
            touched.add(a['slug'])

    print('linked fragments available in the harvest: %d' % len(linked))
    print('fragments given their links back          : %d' % patched)
    print('articles touched                          : %d' % len(touched))
    for s in sorted(touched):
        print('  ' + s)
    if report:
        return
    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote %s' % DATA)


if __name__ == '__main__':
    main()
