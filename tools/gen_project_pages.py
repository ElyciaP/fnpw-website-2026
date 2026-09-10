"""Build the project detail pages from the live site content.

Most project pages were stubs carrying a "To port from live site" note. This
takes the harvested live content in data/projects-content.json and lays it out
in the pj-* project template, the same one the hand-built pages use.

The live copy is used as published. Nothing here rewrites it, invents a
statistic or writes alt text for a photograph it cannot see: projects whose
images arrive without alt text are listed in data/needs-alt-text-projects.json.

    python3 tools/gen_project_pages.py            # write the pages
    python3 tools/gen_project_pages.py --report   # say what it would do
    python3 tools/sync.py                         # then fill header and footer
"""
import json, os, re, sys, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page

NL = chr(10)
CONTENT = 'data/projects-content.json'
INDEX = 'data/projects.json'

PILLAR_NAME = {'parks': 'Growing National Parks', 'species': 'Saving Species',
               'healing': 'Healing the Land'}
PILLAR_PAGE = {'parks': 'growing-national-parks.html', 'species': 'saving-species.html',
               'healing': 'healing-the-land.html'}
FOCUS_TO_PILLAR = [('Growing Parks', 'parks'), ('Saving Species', 'species'),
                   ('Healing our Land', 'healing')]

STATES = {'New South Wales': 'NSW', 'Victoria': 'VIC', 'Queensland': 'QLD',
          'South Australia': 'SA', 'Western Australia': 'WA', 'Tasmania': 'TAS',
          'Northern Territory': 'NT', 'Australian Capital Territory': 'ACT',
          'National': 'Australia'}

# Paragraphs the WordPress template repeats on every project. They are page
# furniture, not project copy, so they come out and the useful ones are turned
# into facts instead.
BOILER = (
    'this project was funded through generous donations from fnpw supporters',
    'fnpw supports projects across australia. in the spirit of reconciliation',
    'further information about our project partner can be found on their website',
    'habitat heroes are a special group of fnpw donors',
    'you can show your support for the long-term restoration',
    'become a habitat hero with a monthly gift',
    'the project is ongoing',
    'the project is on-going',
    'scroll for project updates',
    'please scroll for',
    'get ideas about how you can create a habitat haven',
)
FACT_PAT = [
    ('Funded', re.compile(r'^This project was funded by FNPW in (\d{4})\.?$', re.I)),
    ('Grant round', re.compile(r'^Grant round:\s*(.+?)\.?$', re.I)),
    ('Lead organisation', re.compile(r'^(.+?) is the lead organisation for this project\.?$', re.I)),
    ('Major sponsors', re.compile(r'^Major sponsors?:\s*(.+?)\.?$', re.I)),
    ('Country', re.compile(r'^This project is (?:undertaken|directed) (?:on|by) (.+?)\.?$', re.I)),
]
URL_ONLY = re.compile(r'^https?://\S+$')

# Headings the live template prints on every project. The useful content under
# them is pulled into the facts panel, so the heading has nothing left to lead.
BOILER_H = ('fnpw support', 'acknowledgement of country', 'share this project')


def is_fact_line(t):
    return any(pat.match(t) for _, pat in FACT_PAT)


EM = chr(8212)


def house(t):
    """Two FNPW house rules applied to inherited copy.

    Only the Foundation's own name is corrected to the ampersand. NSW National
    Parks and Wildlife Service is a different organisation and keeps its "and",
    as does the Foundation's former name, the National Parks and Wildlife
    Foundation, where the copy is describing its own history.
    """
    t = t or ''
    t = t.replace('Foundation for National Parks and Wildlife',
                  'Foundation for National Parks & Wildlife')
    if EM in t:
        t = re.sub(r'\s*' + EM + r'\s*', ', ', t)
        t = re.sub(r',\s*,', ',', t)
        t = re.sub(r'\s+,', ',', t)
        t = re.sub(r',\s+([.,;:!?])', r'\1', t)
    return t


def esc(t):
    return H.escape(house(t or ''), quote=True)


def norm(t):
    return re.sub(r'\s+', ' ', (t or '')).strip()


def is_boiler(t):
    low = norm(t).lower()
    return any(b in low for b in BOILER)


def upload_key(url):
    if not url:
        return ''
    base = os.path.basename(url.split('?')[0])
    return re.sub(r'-\d+x\d+(?=\.\w+$)', '', base).lower()


def pillar_for(rec, fallback):
    """The live FOCUS AREAS field is authoritative; the index values were guesses."""
    focus = rec.get('meta', {}).get('FOCUS AREAS', '')
    hits = [p for label, p in FOCUS_TO_PILLAR if label.lower() in focus.lower()]
    if not hits:
        return fallback, False
    if fallback in hits:
        return fallback, True
    if len(hits) == 1:
        return hits[0], True
    # several pillars listed and none of them the one on file: that is a call for
    # a person to make, so the existing value stands and stays marked unconfirmed
    return fallback, False


def sections(blocks):
    """Group the flat block list into sections, each with an optional eyebrow,
    a heading and its body. A bare h3 followed by an h4 is the live site's way
    of writing a label above a heading, so it is read that way."""
    out, cur = [], {'ey': '', 'h': '', 'body': []}
    pending_ey = ''
    for b in blocks:
        t, v = b['t'], b['v']
        if t in ('h2', 'h3', 'h4'):
            txt = norm(v)
            if not txt:
                continue
            if t == 'h3' and not cur['body'] and not pending_ey:
                pending_ey = txt          # might be a label for the h4 that follows
                continue
            if cur['h'] or cur['body']:
                out.append(cur)
                cur = {'ey': '', 'h': '', 'body': []}
            cur['ey'], cur['h'] = pending_ey, txt
            pending_ey = ''
            continue
        if pending_ey:                     # h3 was a heading after all
            if cur['h'] or cur['body']:
                out.append(cur)
                cur = {'ey': '', 'h': '', 'body': []}
            cur['h'] = pending_ey
            pending_ey = ''
        if t == 'list':
            items = [norm(x) for x in v if norm(x) and not is_boiler(x)]
            if items:
                cur['body'].append({'t': 'list', 'v': items})
            continue
        txt = norm(v)
        if not txt or is_boiler(txt) or URL_ONLY.match(txt):
            continue
        if t == 'blockquote' and len(txt) > 1200:
            continue                       # a transcript duplicated below it
        if is_fact_line(txt):
            continue                       # it is in the facts panel instead
        cur['body'].append({'t': t, 'v': txt})
    if pending_ey:
        cur['h'] = cur['h'] or pending_ey
    if cur['h'] or cur['body']:
        out.append(cur)
    keep = []
    for sec in out:
        if not sec['body']:
            continue
        if sec['h'].lower().strip(' .:') in BOILER_H:
            continue
        keep.append(sec)
    return keep


def harvest_facts(blocks):
    facts = {}
    partner_url = ''
    for b in blocks:
        if b['t'] != 'p' or not isinstance(b['v'], str):
            continue
        txt = norm(b['v'])
        if URL_ONLY.match(txt) and 'fnpw.org.au' not in txt:
            partner_url = partner_url or txt
        for label, pat in FACT_PAT:
            m = pat.match(txt)
            if m and label not in facts:
                facts[label] = m.group(1).strip()
    return facts, partner_url


def body_html(items, ind='      '):
    out = []
    for it in items:
        if it['t'] == 'list':
            lis = ''.join('%s  <li>%s</li>%s' % (ind, esc(x), NL) for x in it['v'])
            out.append('%s<ul class="pj-ul">%s%s%s</ul>' % (ind, NL, lis, ind))
        elif it['t'] == 'blockquote':
            out.append('%s<blockquote>%s</blockquote>' % (ind, esc(it['v'])))
        elif it['t'] == 'h4':
            out.append('%s<h4>%s</h4>' % (ind, esc(it['v'])))
        else:
            out.append('%s<p>%s</p>' % (ind, esc(it['v'])))
    return NL.join(out)


def wordcount(items):
    n = 0
    for it in items:
        n += sum(len(x.split()) for x in it['v']) if it['t'] == 'list' else len(it['v'].split())
    return n


def figure(img, cls, ind='      ', lazy=True):
    lz = ' loading="lazy"' if lazy else ''
    cap = ('%s  <figcaption>%s</figcaption>%s' % (ind, esc(img['alt']), NL)) if img.get('alt') else ''
    return ('%s<figure class="%s">%s%s  <img src="%s" alt="%s"%s decoding="async">%s%s%s</figure>'
            % (ind, cls, NL, ind, esc(img['src']), esc(img.get('alt', '')), lz, NL, cap, ind))


def build(rec, meta):
    slug = rec['slug']
    title = norm(rec.get('title')) or meta.get('title') or slug
    pillar, confirmed = pillar_for(rec, meta.get('pillar', 'species'))
    m = rec.get('meta', {})
    state = STATES.get(m.get('STATE', ''), m.get('STATE', '') or meta.get('state', ''))
    year = m.get('YEAR', '')
    lede = norm(rec.get('desc'))
    facts, partner_url = harvest_facts(rec['blocks'])
    secs = sections(rec['blocks'])

    hero = rec.get('hero') or ''
    hkey = upload_key(hero)
    gallery, seen = [], {hkey}
    for im in rec.get('imgs', []):
        k = upload_key(im['src'])
        if k and k not in seen:
            seen.add(k)
            gallery.append(im)

    parts = []

    # ---- hero -------------------------------------------------------------
    meta_bits = ' &nbsp;&nbsp;&middot;&nbsp;&nbsp; '.join(
        x for x in (state, ('Since %s' % year) if year else '') if x)
    parts.append(
        '<section class="pj-hero">%s'
        '  <figure class="pj-hero-im"><img src="%s" alt="" fetchpriority="high" decoding="async"></figure>%s'
        '  <div class="cw rv">%s'
        '    <nav class="breadcrumb" style="display:flex;gap:.5em;font-size:.82rem">'
        '<a href="index.html">Home</a><span style="opacity:.4">/</span>'
        '<a href="projects.html">Projects</a><span style="opacity:.4">/</span>%s</nav>%s'
        '    <span class="ey">%s</span>%s'
        '    <h1>%s</h1>%s'
        '%s'
        '%s'
        '  </div>%s</section>'
        % (NL, esc(hero), NL, NL, esc(title), NL, PILLAR_NAME[pillar], NL, esc(title), NL,
           ('    <p class="pj-hero-meta">%s</p>%s' % (meta_bits, NL)) if meta_bits else '',
           ('    <p class="lede">%s</p>%s' % (esc(lede), NL)) if lede else '', NL))

    # ---- intro plus the facts panel ---------------------------------------
    rows = []
    rows.append('      <div class="pmeta-i"><span>Pillar</span><strong>'
                '<a href="%s">%s</a></strong></div>' % (PILLAR_PAGE[pillar], PILLAR_NAME[pillar]))
    if state:
        rows.append('      <div class="pmeta-i"><span>Where</span><strong>%s</strong></div>' % esc(state))
    if year:
        rows.append('      <div class="pmeta-i"><span>Started</span><strong>%s</strong></div>' % esc(year))
    for label in ('Lead organisation', 'Grant round', 'Major sponsors'):
        if facts.get(label):
            rows.append('      <div class="pmeta-i"><span>%s</span><strong>%s</strong></div>'
                        % (label, esc(facts[label])))
    if partner_url:
        host = re.sub(r'^www\.', '', partner_url.split('/')[2])
        rows.append('      <div class="pmeta-i"><span>Partner</span><strong>'
                    '<a href="%s" rel="noopener">%s</a></strong></div>' % (esc(partner_url), esc(host)))

    intro = secs[0] if secs else {'ey': '', 'h': '', 'body': []}
    rest = secs[1:]
    parts.append(NL.join([
        '<section class="sec">',
        '  <div class="cw rv">',
        '    <div class="two">',
        '      <div>',
        '        <span class="ey">The project</span>',
        '        <h2 style="margin:.8rem 0 1.2rem">%s</h2>' % esc(intro['h'] or 'About this project'),
        body_html(intro['body'], '        '),
        '      </div>',
        '      <div><div class="pmeta">',
        NL.join(rows),
        '      </div></div>',
        '    </div>',
        '  </div>',
        '</section>',
    ]))

    # ---- the remaining sections -------------------------------------------
    # A picture goes with a section wherever one is spare; the dark story band
    # lands about two thirds of the way down, as it does on the hand-built pages.
    # A section short enough to sit beside a photograph becomes a band. A long
    # one runs full width instead, with the photograph in the flow, so the
    # measure stays readable rather than a tall column beside a short picture.
    BAND_MAX = 300   # about 65% of live sections; beyond this the text
                     # column runs much taller than the picture beside it
    bandable = [n for n, s in enumerate(rest)
                if wordcount(s['body']) <= BAND_MAX and wordcount(s['body']) >= 40]
    story_at = bandable[int(len(bandable) * 0.6)] if len(bandable) >= 2 else -1
    gi, band = 0, 0
    for n, s in enumerate(rest):
        head = ''
        if s['ey']:
            head += '      <span class="ey">%s</span>%s' % (esc(s['ey']), NL)
        if s['h']:
            head += '      <h3>%s</h3>%s' % (esc(s['h']), NL)
        words = wordcount(s['body'])
        img = gallery[gi] if gi < len(gallery) else None

        if n == story_at and img and words <= BAND_MAX:
            gi += 1
            parts.append('<section class="pj-story">%s  <div class="cw"><div class="pj-story-g rv">%s'
                         '%s%s    <div>%s%s%s    </div>%s  </div></div>%s</section>'
                         % (NL, NL, figure(img, 'pj-story-im', '      '), NL, NL, head,
                            body_html(s['body']), NL, NL))
        elif img and words <= BAND_MAX:
            flip = ' alt flip' if band % 2 else ''
            gi += 1
            band += 1
            parts.append('<section class="pj-band%s">%s  <div class="cw"><div class="pj-band-g rv">%s'
                         '%s%s    <div class="pj-band-bd">%s%s%s    </div>%s  </div></div>%s</section>'
                         % (flip, NL, NL, figure(img, 'pj-band-im', '    '), NL, NL, head,
                            body_html(s['body']), NL, NL))
        else:
            shade = ' paper' if band % 2 else ''
            band += 1
            fig = ''
            if img:
                gi += 1
                fig = NL + figure(img, 'pj-fig', '      ') + NL
            parts.append('<section class="sec%s">%s  <div class="cw rv">%s    <div class="pj-body">%s%s%s%s    </div>%s  </div>%s</section>'
                         % (shade, NL, NL, NL, head, body_html(s['body']), fig, NL, NL))

    # ---- anything left over becomes the gallery ---------------------------
    spare = gallery[gi:]
    if len(spare) >= 2:
        figs = NL.join(figure(im, '', '      ') for im in spare[:9])
        parts.append('<section class="sec paper">%s  <div class="cw rv">%s'
                     '    <span class="ey">Project gallery</span>%s'
                     '    <div class="pj-gal" style="margin-top:1.6rem">%s%s%s    </div>%s  </div>%s</section>'
                     % (NL, NL, NL, NL, figs, NL, NL, NL))

    parts.append('<section class="pj-back">%s  <div class="cw rv">%s'
                 '    <a class="btn-o" href="projects.html">&#8592; All conservation projects</a>%s'
                 '  </div>%s</section>' % (NL, NL, NL, NL))
    parts.append(
        '<section class="sec dark">%s  <div class="cw rv" style="text-align:center">%s'
        '    <h2 style="max-width:24ch;margin:0 auto 1rem">Help fund work like this.</h2>%s'
        '    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Every FNPW project is powered '
        'by donations, bequests and partnerships.</p>%s'
        '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
        '<a class="btn-p" href="https://bush.fnpw.org.au">Donate</a>'
        '<a class="btn-o" href="bequests.html">Leave a gift in your Will</a></div>%s  </div>%s</section>'
        % (NL, NL, NL, NL, NL, NL))

    desc = lede or ('%s, an FNPW conservation project in %s.' % (title, state or 'Australia'))
    return (NL + (NL * 2).join(parts) + NL, title, desc, pillar, confirmed,
            len(gallery), sum(1 for im in gallery if not im.get('alt')))


def main():
    report = '--report' in sys.argv
    recs = json.load(open(CONTENT, encoding='utf-8'))
    index = {p['slug']: p for p in json.load(open(INDEX, encoding='utf-8'))}

    written, skipped, repointed, need_alt = [], [], [], {}
    for rec in recs:
        if rec.get('error'):
            skipped.append('%s (%s)' % (rec['slug'], rec['error']))
            continue
        slug = rec['slug']
        meta = index.get(slug, {})
        fname = 'project-%s.html' % slug
        if not os.path.exists(fname):
            skipped.append('%s (no stub on disk)' % slug)
            continue
        body, title, desc, pillar, confirmed, nimg, nalt = build(rec, meta)
        if meta.get('pillar') and meta['pillar'] != pillar:
            repointed.append('%s: %s -> %s' % (slug, meta['pillar'], pillar))
        if nalt:
            need_alt[slug] = nalt
        if not report:
            write_page(fname, esc(title), esc(desc), body)
            if slug in index:
                index[slug]['pillar'] = pillar
                index[slug]['pillar_confirmed'] = confirmed
        written.append(slug)

    print('project pages written        : %d' % len(written))
    print('pillar corrected from live   : %d' % len(repointed))
    for r in repointed[:12]:
        print('    ' + r)
    print('images with no alt text      : %d across %d projects' % (sum(need_alt.values()), len(need_alt)))
    print('skipped                      : %d %s' % (len(skipped), skipped))
    if report:
        return
    json.dump(list(index.values()), open(INDEX, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(need_alt, open('data/needs-alt-text-projects.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('wrote %s and data/needs-alt-text-projects.json' % INDEX)
    print('now run: python3 tools/sync.py')


if __name__ == '__main__':
    main()
