"""Convert the WordPress harvest in ~/harvest2 into data/articles.json entries.

    python3 tools/import_wp.py             # import everything not already curated
    python3 tools/import_wp.py <slug> ...  # re-import just these, curated fields kept
    python3 tools/import_wp.py --force     # re-import everything
    python3 tools/import_wp.py --report    # print what it would do, write nothing

What it does that the first import did not:

- Keeps inline links. The first harvest took text content only, so every link in
  every article was lost. Body copy now carries its <a>, <em> and <strong>.
- Rewrites internal links to the prototype's own pages where one exists, so a
  link to /project/foo/ on WordPress becomes project-foo.html here.
- Unwraps links whose target 404s on the live site. The sentence keeps its words
  and loses the dead anchor.
- Uses the alt text and captions WordPress already holds, rather than inventing
  them. Invented alt text was wrong about half the time when it was checked
  against the actual photographs.

Curated fields on an existing entry (pillar, related, eyebrow, place, credit)
are carried forward, so hand-set values survive a re-import.
"""
import json, os, re, sys, glob, html as htmlmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

HARVEST = os.path.expanduser('~/harvest2')
DATA = 'data/articles.json'
NEWS = 'data/in-the-news.json'

# Live URLs that 404. Their anchors are unwrapped, the words stay.
DEAD = {
    '/project/bushfire-recovery-nurseries/',
    '/project/ecology-support-project/',
    '/grant/community-conservation-grants/',
    '/grant/bushfire-restoration-grants/',
    '/emergency-grants-provide-relief-for-nsw-wildlife-volunteers/',
}
# Live URLs that redirect. Point straight at the destination.
REDIRECT = {'/wildlifeheroes': 'https://fnpw.org.au/grant/wildlife-heroes-grants/'}

# WordPress path -> prototype page
PAGE_MAP = {
    '/': 'index.html', '/about-us/': 'about.html', '/projects/': 'projects.html',
    '/contact-us/': 'contact.html', '/corporate-partnerships/': 'partner.html',
    '/project-partnerships/': 'partner.html', '/corporate-partners/': 'partner.html',
    '/corporate-volunteering/': 'volunteer.html', '/bequest/': 'bequests.html',
    '/news/': 'articles.html', '/faqs/': 'faqs.html',
    '/ways-you-can-get-involved/': 'ways-you-can-get-involved.html',
    '/fundraising-with-fnpw/': 'fundraising-with-fnpw.html',
    '/corporate-governance/': 'corporate-governance.html',
    '/donate-land/': 'donate-land.html', '/gift-a-tree/': 'gift-a-tree.html',
}

PILLAR_WORDS = {
    'parks': ('national park', 'world heritage', 'acquisition', 'acquire', 'reserve',
              'hectares', 'land purchase', 'protected area', 'conservation park'),
    'species': ('species', 'koala', 'bandicoot', 'frog', 'turtle', 'quoll', 'wombat',
                'glider', 'cockatoo', 'endangered', 'threatened', 'wildlife', 'habitat',
                'possum', 'bilby', 'parrot', 'bird'),
    'heal': ('restoration', 'revegetation', 'planting', 'seedling', 'nursery', 'seed',
             'bushfire recovery', 'regeneration', 'tree', 'landcare', 'cultural fire',
             'wetland', 'erosion', 'weed'),
}

CURATED = ('pillar', 'related', 'eyebrow', 'place', 'credit',
           'standfirst', 'description', 'hero_alt')
MARK = '\x00OPEN\x00'
AMP = re.compile(r'&(?![a-zA-Z][a-zA-Z0-9]{1,9};|#[0-9]{1,6};|#x[0-9a-fA-F]{1,6};)')


def strip(h):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h or '')).strip()


def esc_amp(t):
    return AMP.sub('&amp;', t or '')


def norm_path(href):
    """Return the fnpw.org.au path for an internal link, else None."""
    h = href.strip()
    if h.startswith('//'):
        h = 'https:' + h
    if h.startswith('/'):
        return h
    m = re.match(r'https?://(?:www\.)?fnpw\.org\.au(/[^\s]*)?$', h, re.I)
    if m:
        return m.group(1) or '/'
    return None


def rewrite_href(href, slugs, projects):
    """-> (new href, unwrap?)"""
    if href.strip().startswith('#') or not href.strip():
        return href, True                                   # goes nowhere here
    p = norm_path(href)
    if p is None:
        return href, False                                  # external, untouched
    base = p.split('#')[0].split('?')[0]
    if base in DEAD or base.rstrip('/') + '/' in DEAD:
        return href, True
    if base.rstrip('/') in REDIRECT:
        return REDIRECT[base.rstrip('/')], False
    m = re.match(r'/news/[^/]+/([^/]+)/?$', base)
    if m and m.group(1) in slugs:
        return 'article-%s.html' % m.group(1), False
    m = re.match(r'/project/([^/]+)/?$', base)
    if m and m.group(1) in projects:
        return 'project-%s.html' % m.group(1), False
    if base in PAGE_MAP:
        return PAGE_MAP[base], False
    return 'https://fnpw.org.au' + p, False


def fix_links(h, slugs, projects, stats):
    def sub(m):
        href = htmlmod.unescape(m.group(1))
        new, unwrap = rewrite_href(href, slugs, projects)
        if unwrap:
            stats['unwrapped'] += 1
            return MARK
        if new != href:
            stats['rewritten'] += 1
        stats['kept'] += 1
        return '<a href="%s">' % htmlmod.escape(new, quote=True)
    out = re.sub(r'<a\s[^>]*href="([^"]*)"[^>]*>', sub, h or '')
    # drop the closing tag of any anchor we unwrapped, keeping every character of
    # the link text (MARK is 6 chars, not 7; getting that wrong ate a letter)
    while MARK in out:
        i = out.index(MARK)
        j = out.find('</a>', i)
        if j == -1:
            out = out.replace(MARK, '', 1)
        else:
            out = out[:i] + out[i + len(MARK):j] + out[j + 4:]
    return out


MEDIA = json.load(open('data/wp-media.json', encoding='utf-8')) \
    if os.path.exists('data/wp-media.json') else {'alt': {}, 'dims': {}}


def og_alt(post):
    """Alt text for the feature image: what WordPress holds for it, else the alt
    on the matching body image. Never invented. Only 43 of 178 posts have one,
    and the rest are listed in the report so a human can write them."""
    a = MEDIA['alt'].get(post['slug'], '').strip()
    if a:
        return a
    key = re.sub(r'-\d+x\d+(?=\.\w+$)', '', os.path.basename(post.get('og', '')))
    for x in post['b']:
        if x['t'] == 'img' and re.sub(r'-\d+x\d+(?=\.\w+$)', '', os.path.basename(x['v'])) == key:
            return x.get('a', '').strip()
    return ''


def hero_size(post):
    d = MEDIA['dims'].get(post['slug'], '')
    m = re.fullmatch(r'(\d+)x(\d+)', d)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def pillar_for(post, text):
    t = text.lower()
    score = {k: sum(t.count(w) for w in ws) for k, ws in PILLAR_WORDS.items()}
    best = max(score, key=score.get)
    if score[best] == 0:
        return 'news'
    return best


def upload_key(url):
    """Basename with the WordPress rendition suffix removed, so 8-1024x537.jpg
    and 8-2560x1344.jpg are recognised as the same upload."""
    if not url:
        return ''
    return re.sub(r'-\d+x\d+(?=\.\w+$)', '', os.path.basename(url.split('?')[0])).lower()


def blocks_for(post, slugs, projects, stats):
    # the feature image runs as the hero, so drop it where it also sits in the body
    hero_key = upload_key(post.get('og', ''))
    b = [x for x in post['b']
         if not (x['t'] == 'img' and hero_key and upload_key(x['v']) == hero_key)]
    levels = [int(x['t'][1]) for x in b if re.fullmatch(r'h[1-6]', x['t'])]
    top = min(levels) if levels else 0

    def L(x):
        return fix_links(x, slugs, projects, stats)

    # standfirst: the opening paragraph, unless it is long enough to be real body copy
    paras = [x for x in b if x['t'] == 'p']
    stand, consume = '', False
    if paras:
        first = paras[0]['v']
        words = len(strip(first).split())
        if words <= 70:
            stand, consume = strip(first), True
        else:
            sents = re.split(r'(?<=[.!?])\s+', strip(first))
            stand = sents[0]
            if len(stand.split()) < 18 and len(sents) > 1:
                stand += ' ' + sents[1]

    items = list(b)
    if consume:
        items.remove(paras[0])

    # group into sections at the top heading level
    secs, cur = [], {'head': None, 'parts': []}
    secs.append(cur)
    for x in items:
        if top and x['t'] == 'h%d' % top:
            cur = {'head': strip(x['v']), 'parts': []}
            secs.append(cur)
        else:
            cur['parts'].append(x)

    out = []
    for s in secs:
        parts, flow, pending_head = s['parts'], [], s['head']
        if not parts and not pending_head:
            continue
        opened = False

        def flush(force=False):
            nonlocal flow, opened, pending_head
            if not flow and not (pending_head and not opened):
                return
            blk = {'type': 'text', 'flow': flow}
            if pending_head and not opened:
                blk['flow'] = [{'h': esc_amp(pending_head)}] + flow
                opened = True
            out.append(blk)
            flow = []

        for x in parts:
            t = x['t']
            if t == 'img':
                flush()
                blk = {'type': 'band' if (pending_head and not opened) else 'wide',
                       'img': x['v'], 'alt': x.get('a', '').strip(),
                       'caption': strip(x.get('cap', '')), 'flow': []}
                if blk['type'] == 'band':
                    blk['heading'] = esc_amp(pending_head)
                    opened = True
                out.append(blk)
            elif t == 'p':
                flow.append({'p': L(x['v'])})
            elif re.fullmatch(r'h[1-6]', t):
                flow.append({'h': esc_amp(strip(x['v']))})
            elif t in ('ul', 'ol'):
                flow.append({t: [L(v) for v in x['v']]})
            elif t == 'q':
                flow.append({'q': L(x['v'])})
            elif t == 'table':
                stats['tables'] += 1
        flush()

    # a band block absorbs the paragraphs that follow it, so the picture and its
    # text read as one section rather than two
    merged = []
    for blk in out:
        if merged and merged[-1]['type'] in ('band', 'wide') and not merged[-1]['flow'] \
                and blk['type'] == 'text' and not any('h' in i for i in blk['flow'][:1]):
            merged[-1]['flow'] = blk['flow']
        else:
            merged.append(blk)

    # rhythm: alternate the bands, make one of them the dark chapter break
    bands = [i for i, x in enumerate(merged) if x['type'] == 'band']
    for n, i in enumerate(bands):
        if n % 2:
            merged[i]['flip'] = True
    if bands:
        pick = bands[min(len(bands) - 1, max(0, int(len(bands) * 0.65)))]
        merged[pick]['type'] = 'story'
        merged[pick].pop('flip', None)
    elif len(merged) > 3:
        merged[len(merged) // 2]['paper'] = True

    if merged and merged[0]['type'] == 'text':
        merged[0]['type'] = 'lead'
    return merged, stand


def describe(stand):
    t = strip(stand)
    if len(t) <= 200:
        return t
    cut = t[:200]
    dot = max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
    return (cut[:dot + 1] if dot > 90 else cut.rsplit(' ', 1)[0] + '...').strip()


def is_clipping(post, words):
    return 'media' in post.get('cats', []) and words < 220 and post['date'] < '2021-07'


def main():
    force = '--force' in sys.argv
    report = '--report' in sys.argv
    existing = {a['slug']: a for a in json.load(open(DATA, encoding='utf-8'))} \
        if os.path.exists(DATA) else {}
    projects = {re.sub(r'^project-|\.html$', '', f) for f in glob.glob('project-*.html')}
    posts = [json.load(open(f, encoding='utf-8'))
             for f in sorted(glob.glob(os.path.join(HARVEST, '*.json')))]
    renames = json.load(open('data/slug-changes.json', encoding='utf-8')) \
        if os.path.exists('data/slug-changes.json') else {}
    for post in posts:
        post['slug'] = renames.get(post['slug'], post['slug'])
    only = {x for x in sys.argv[1:] if not x.startswith('-')}
    slugs = {p['slug'] for p in posts}
    stats = {'kept': 0, 'rewritten': 0, 'unwrapped': 0, 'tables': 0}

    arts, clips, skipped = [], [], []
    for p in posts:
        text = ' '.join(strip(x['v']) if isinstance(x['v'], str) else ' '.join(map(strip, x['v']))
                        for x in p['b'])
        words = len(text.split())
        if is_clipping(p, words):
            clips.append({'slug': p['slug'], 'date': p['date'], 'title': strip(p['title']),
                          'url': p['url'], 'words': words,
                          'blurb': describe(next((strip(x['v']) for x in p['b'] if x['t'] == 'p'), ''))})
            continue
        if p['slug'] in existing and not force and p['slug'] not in only:
            skipped.append(p['slug'])
            arts.append(existing[p['slug']])
            continue
        blocks, stand = blocks_for(p, slugs, projects, stats)
        e = {'slug': p['slug'], 'title': esc_amp(strip(p['title'])),
             'eyebrow': 'Story' if 'blogs' in p.get('cats', []) else 'News',
             'date': p['date'], 'place': '',
             'pillar': pillar_for(p, text),
             'standfirst': esc_amp(stand), 'hero': p['og'], 'hero_alt': og_alt(p),
             'hero_w': hero_size(p)[0], 'hero_h': hero_size(p)[1],
             'description': esc_amp(describe(stand)), 'credit': '', 'blocks': blocks}
        if p['slug'] in existing:
            for k in CURATED:
                if existing[p['slug']].get(k):
                    e[k] = existing[p['slug']][k]
        arts.append(e)

    for slug, e in existing.items():
        if slug not in slugs and slug not in {a['slug'] for a in arts}:
            arts.append(e)
            skipped.append(slug)

    noalt = sorted(a['slug'] for a in arts if not a.get('hero_alt'))
    json.dump(noalt, open('data/needs-alt-text.json', 'w', encoding='utf-8'), indent=1)

    print('harvested posts      : %d' % len(posts))
    print('article entries      : %d  (%d already present and left alone)' % (len(arts), len(skipped)))
    print('press clippings      : %d  -> %s' % (len(clips), NEWS))
    print('links kept           : %d' % stats['kept'])
    print('  of those rewritten : %d' % stats['rewritten'])
    print('dead links unwrapped : %d' % stats['unwrapped'])
    print('tables dropped       : %d' % stats['tables'])
    print('entries with no hero alt: %d  -> data/needs-alt-text.json' % len(noalt))
    small = [a['slug'] for a in arts if 0 < a.get('hero_w', 0) < 1200]
    print('feature images under 1200px wide: %d (too small for a full-bleed hero)' % len(small))
    if report:
        return
    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(sorted(clips, key=lambda c: c['date'], reverse=True),
              open(NEWS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote %s and %s' % (DATA, NEWS))


if __name__ == '__main__':
    main()
