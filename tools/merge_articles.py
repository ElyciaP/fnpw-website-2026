"""Merge authored article entries into data/articles.json.

Reads every ~/harvest/entries/*.json, adds any article not already in
data/articles.json, sorts the file newest first, and tops up the "Keep reading"
cards so every article has three.

data/articles.json is the source of truth. An article that is already in it is
NOT re-imported, because the file carries later editing (image cuts, corrected
alt text, pillars) that the raw harvest entries do not have. Pass --reimport to
deliberately overwrite from the entries again.

A hand-written "related" list is kept and simply filled out to three, so a
curated pair of cards survives a re-run. Pass --relink to throw those away and
rebuild every list from the dates.

    python3 tools/merge_articles.py             # add new articles, top up related
    python3 tools/merge_articles.py --relink    # rebuild every related list
    python3 tools/merge_articles.py --reimport  # re-read entries over existing articles
"""
import json, os, sys, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ENTRIES = os.path.expanduser('~/harvest/entries')
DATA = 'data/articles.json'
N_RELATED = 3

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


def relink(arts, force=False):
    """Top every article's 'keep reading' list up to N_RELATED cards.

    Existing cards are kept and the list is filled from the nearest articles by
    date, skipping the article itself and anything already linked. force throws
    the existing cards away and rebuilds from scratch.
    """
    for i, a in enumerate(arts):
        have = [] if force else list(a.get('related') or [])
        seen = {r.get('href') for r in have}
        seen.add('article-%s.html' % a['slug'])
        for j in (i + 1, i - 1, i + 2, i - 2, i + 3, i - 3, i + 4, i - 4):
            if len(have) >= N_RELATED:
                break
            if 0 <= j < len(arts):
                c = card(arts[j])
                if c['href'] not in seen:
                    have.append(c)
                    seen.add(c['href'])
        a['related'] = have[:N_RELATED]


def main():
    arts = json.load(open(DATA, encoding='utf-8')) if os.path.exists(DATA) else []
    by_slug = {a['slug']: a for a in arts}

    reimport = '--reimport' in sys.argv
    added, replaced, skipped = [], [], []
    for f in sorted(glob.glob(os.path.join(ENTRIES, '*.json'))):
        e = json.load(open(f, encoding='utf-8'))
        if e['slug'] in by_slug:
            if not reimport:
                skipped.append(e['slug'])       # data/articles.json is the source of truth
                continue
            for k in ('related', 'pillar'):     # keep the fields the entries never carried
                if k in by_slug[e['slug']]:
                    e.setdefault(k, by_slug[e['slug']][k])
            replaced.append(e['slug'])
        else:
            added.append(e['slug'])
        by_slug[e['slug']] = e

    arts = sorted(by_slug.values(), key=sortkey)
    relink(arts, force='--relink' in sys.argv)

    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('articles.json: %d entries (%d added, %d replaced, %d already present and left alone)'
          % (len(arts), len(added), len(replaced), len(skipped)))
    for a in arts:
        print('  %-58s %-16s %2d blocks' % (a['slug'], a.get('date', ''), len(a['blocks'])))


if __name__ == '__main__':
    main()
