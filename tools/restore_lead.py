"""Put each article's opening paragraph back into the body.

The importer lifted the first paragraph out of every article to use as a
standfirst under the headline. On the page that reads as a subhead, but it is not
one: it is the start of the piece. This puts it back as the first paragraph of
the body, taken from the harvest so it keeps its links and its exact wording.

The standfirst field stays in the data because the tiles and the meta description
are built from it, but tools/gen_articles.py no longer prints it in the hero.

    python3 tools/restore_lead.py            # patch data/articles.json
    python3 tools/restore_lead.py --report   # say what it would do, write nothing
"""
import json, os, re, sys, glob, html as htmlmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from import_wp import fix_links, HARVEST

DATA = 'data/articles.json'


def key(t):
    t = htmlmod.unescape(re.sub(r'<[^>]+>', ' ', t or '')).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', t)).strip()


def paragraphs(a):
    out = []
    for b in a.get('blocks', []):
        for it in b.get('flow', []):
            if 'p' in it:
                out.append(it['p'])
        for p in b.get('paras', []):
            out.append(p)
    return out


def main():
    report = '--report' in sys.argv
    arts = json.load(open(DATA, encoding='utf-8'))
    harvest = {}
    for f in glob.glob(os.path.join(HARVEST, '*.json')):
        p = json.load(open(f, encoding='utf-8'))
        harvest[p['slug']] = p
    # an article we renamed by hand still has its harvest under the WordPress slug
    if os.path.exists('data/slug-changes.json'):
        for old_slug, new_slug in json.load(open('data/slug-changes.json', encoding='utf-8')).items():
            if old_slug in harvest and new_slug not in harvest:
                harvest[new_slug] = harvest[old_slug]
    slugs = set(harvest)
    projects = {re.sub(r'^project-|\.html$', '', f) for f in glob.glob('project-*.html')}
    stats = {'kept': 0, 'rewritten': 0, 'unwrapped': 0, 'tables': 0}

    restored, already, nosource = 0, 0, []
    for a in arts:
        h = harvest.get(a['slug'])
        if not h:
            nosource.append(a['slug'])
            continue
        first = next((x['v'] for x in h['b'] if x['t'] == 'p' and key(x['v'])), '')
        if not first:
            continue
        k = key(first)
        if any(key(p) == k for p in paragraphs(a)):
            already += 1
            continue
        para = {'p': fix_links(first, slugs, projects, stats)}
        b0 = a['blocks'][0] if a.get('blocks') else None
        if b0 and b0.get('type') in ('lead', 'text') and b0.get('flow') and 'p' in b0['flow'][0]:
            b0['flow'].insert(0, para)
        else:
            a['blocks'].insert(0, {'type': 'lead', 'flow': [para]})
        restored += 1

    print('opening paragraph restored to the body : %d' % restored)
    print('already in the body, left alone        : %d' % already)
    print('no harvest source (hand-built entries) : %d %s' % (len(nosource), nosource))
    if report:
        return
    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote %s' % DATA)


if __name__ == '__main__':
    main()
