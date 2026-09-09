"""Rewrite the featured card and the article grid on articles.html, and the
three "related articles" strips on the pillar pages.

Everything comes straight from data/articles.json, so adding a blog post is one
entry in that file plus:

    python3 tools/gen_articles.py         # the article page
    python3 tools/gen_articles_index.py   # its tile on articles.html and the pillars
    python3 tools/sync.py                 # header and footer

The blocks it owns are marked in the HTML with
<!--ARTFEAT:START--> ... <!--ARTFEAT:END-->   the featured card on articles.html
<!--ARTGRID:START--> ... <!--ARTGRID:END-->   the tile grid on articles.html
<!--ARTREL:START-->  ... <!--ARTREL:END-->    three tiles on each pillar page
Everything outside those markers, including the heroes, the filter bar and the
newsletter strip, is left alone.

"pillar" on an entry drives the coloured category chip, the filter buttons and
which pillar page an article shows up on: parks | species | heal | news.
"""
import json, os, re, html

AMP = re.compile(r'&(?![a-zA-Z][a-zA-Z0-9]{1,9};|#[0-9]{1,6};|#x[0-9a-fA-F]{1,6};)')


def esc(t):
    """Escape a bare & so "National Parks & Wildlife" stays valid HTML."""
    return AMP.sub('&amp;', t or '')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

NL = chr(10)
PILLAR = {'parks': ('parks', 'Growing Parks'),
          'species': ('species', 'Saving Species'),
          'heal': ('heal', 'Healing Land'),
          'news': ('', 'News &amp; Events')}
PILLAR_PAGES = {'growing-national-parks.html': 'parks',
                'saving-species.html': 'species',
                'healing-the-land.html': 'heal'}


def words(a):
    n = 0
    for b in a['blocks']:
        items = b.get('flow') or [{'p': p} for p in b.get('paras', [])]
        for it in items:
            for k in ('p', 'h', 'q'):
                if k in it:
                    n += len(it[k].split())
            for k in ('ul', 'ol'):
                if k in it:
                    n += sum(len(x.split()) for x in it[k])
        n += sum(len(x.split()) for x in b.get('intro', []))
        n += sum(len(x.split()) for x in b.get('items', []))
    return n


def read_time(a):
    return max(2, round(words(a) / 220.0))


def chip(a):
    cls, label = PILLAR.get(a.get('pillar', 'news'), PILLAR['news'])
    return '<span class="cat %s">%s</span>' % (cls, label) if cls else '<span class="cat">%s</span>' % label


def card(a, pad='    ', extra=''):
    return ('%s<a href="article-%s.html" class="art rv%s">%s'
            '%s  <div class="art-im"><img src="%s" alt="%s" loading="lazy">%s</div>%s'
            '%s  <div class="art-bd">%s'
            '%s    <div class="art-date">%s &middot; %s</div>%s'
            '%s    <h3>%s</h3>%s'
            '%s    <p>%s</p>%s'
            '%s    <span class="art-link">Read more</span>%s'
            '%s  </div>%s%s</a>'
            % (pad, a['slug'], extra, NL,
               pad, a['hero'], html.escape(a['title']), chip(a), NL,
               pad, NL,
               pad, a.get('date', ''), a.get('eyebrow', 'Story'), NL,
               pad, html.escape(a['title']), NL,
               pad, esc(a.get('description', '')), NL,
               pad, NL,
               pad, NL, pad))


def featured(a):
    _, label = PILLAR.get(a.get('pillar', 'news'), PILLAR['news'])
    return ('    <div class="feat-card rv">%s'
            '      <div class="feat-img"><img src="%s" alt="%s"></div>%s'
            '      <div class="feat-bd">%s'
            '        <span class="feat-tag">Featured story &middot; %s</span>%s'
            '        <h2>%s</h2>%s'
            '        <p>%s</p>%s'
            '        <div class="feat-meta"><strong>%s</strong><span>&middot; %d min read</span></div>%s'
            '        <a href="article-%s.html" class="btn btn-p" style="align-self:flex-start;margin-top:1.4rem">Read the full story</a>%s'
            '      </div>%s    </div>'
            % (NL, a['hero'], html.escape(a['title']), NL, NL, a.get('date', ''), NL,
               html.escape(a['title']), NL, esc(a.get('description', '')), NL,
               label, read_time(a), NL, a['slug'], NL, NL))


def replace(src, name, payload, where):
    start, end = '<!--%s:START-->' % name, '<!--%s:END-->' % name
    if start not in src or end not in src:
        raise SystemExit('markers %s missing from %s' % (name, where))
    head, rest = src.split(start, 1)
    _, tail = rest.split(end, 1)
    return head + start + NL + payload + NL + end + tail


def main():
    arts = json.load(open('data/articles.json', encoding='utf-8'))

    s = open('articles.html', encoding='utf-8').read()
    s = replace(s, 'ARTFEAT', featured(arts[0]), 'articles.html')
    s = replace(s, 'ARTGRID', NL.join(card(a) for a in arts[1:]), 'articles.html')
    open('articles.html', 'w', encoding='utf-8').write(s)
    print('articles.html: featured "%s" + %d tiles' % (arts[0]['title'], len(arts) - 1))

    for page, pil in sorted(PILLAR_PAGES.items()):
        if not os.path.exists(page):
            continue
        picks = [a for a in arts if a.get('pillar') == pil][:3]
        if len(picks) < 3:
            picks += [a for a in arts if a not in picks][:3 - len(picks)]
        cards = [card(a, '      ', '' if i == 0 else ' d%d' % i) for i, a in enumerate(picks)]
        t = open(page, encoding='utf-8').read()
        t = replace(t, 'ARTREL', NL.join(cards), page)
        open(page, 'w', encoding='utf-8').write(t)
        print('%-30s %d related tiles' % (page, len(picks)))

    counts = {}
    for a in arts:
        counts[a.get('pillar', 'news')] = counts.get(a.get('pillar', 'news'), 0) + 1
    print('  by pillar:', ', '.join('%s %d' % kv for kv in sorted(counts.items())))


if __name__ == '__main__':
    main()
