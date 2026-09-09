"""Merge authored article entries into data/articles.json.

Reads every ~/harvest/entries/*.json, merges them into data/articles.json by
slug (an existing entry is replaced, a new one is added), sorts the file newest
first, and fills in the "Keep reading" cards for any entry that has none.

An entry that already carries a hand-written "related" list keeps it, so a
curated pair of cards survives a re-run.

    python3 tools/merge_articles.py            # merge and sort
    python3 tools/merge_articles.py --relink   # also rebuild every related list
"""
import json, os, sys, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ENTRIES = os.path.expanduser('~/harvest/entries')
DATA = 'data/articles.json'

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']


def sortkey(a):
    """Newest first. Dates look like 'August 2026'."""
    d = (a.get('date') or '').lower()
    y = re.search(r'(19|20)\d{2}', d)
    year = int(y.group(0)) if y else 0
    month = 0
    for i, m in enumerate(MONTHS):
        if m in d:
            month = i + 1
            break
    return (-year, -month, a['slug'])


def card(a, cta='Read the story'):
    return {'href': 'article-%s.html' % a['slug'],
            'date': a.get('date', ''),
            'title': a['title'],
            'blurb': a.get('description', ''),
            'img': a['hero'],
            'cta': cta}


def relink(arts):
    """Two 'keep reading' cards: the articles either side of this one by date."""
    for i, a in enumerate(arts):
        picks = []
        for j in (i + 1, i - 1, i + 2, i - 2):
            if 0 <= j < len(arts) and j != i and arts[j]['slug'] not in [p['slug'] for p in picks]:
                picks.append(arts[j])
            if len(picks) == 2:
                break
        a['related'] = [card(p) for p in picks]


def main():
    arts = json.load(open(DATA, encoding='utf-8')) if os.path.exists(DATA) else []
    by_slug = {a['slug']: a for a in arts}

    added, replaced = [], []
    for f in sorted(glob.glob(os.path.join(ENTRIES, '*.json'))):
        e = json.load(open(f, encoding='utf-8'))
        if e['slug'] in by_slug:
            e.setdefault('related', by_slug[e['slug']].get('related', []))
            replaced.append(e['slug'])
        else:
            added.append(e['slug'])
        by_slug[e['slug']] = e

    arts = sorted(by_slug.values(), key=sortkey)

    force = '--relink' in sys.argv
    missing = [a for a in arts if force or not a.get('related')]
    if missing:
        keep = {a['slug']: a.get('related') for a in arts if a.get('related') and not force}
        relink(arts)
        for a in arts:
            if a['slug'] in keep and keep[a['slug']]:
                a['related'] = keep[a['slug']]

    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('articles.json: %d entries (%d added, %d replaced)' % (len(arts), len(added), len(replaced)))
    for a in arts:
        print('  %-58s %-16s %2d blocks' % (a['slug'], a.get('date', ''), len(a['blocks'])))


if __name__ == '__main__':
    main()
