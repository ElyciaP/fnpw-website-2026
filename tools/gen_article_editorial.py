"""Editorial article template, built for comparison against tools/gen_articles.py.

Same data (data/articles.json), different rendering model.

The v1 template treats an article as a stack of sections, which is the project
page model: each block becomes its own <section> with equal padding, and image
blocks put the text in a half-width column beside the picture. That moves the
body copy's left edge several times per article, which is what makes a long read
feel restless.

This template treats an article as one document. There is a single grid with a
fixed text column, and images break out of that column rather than sitting
beside it, so the left edge is identical from the first word to the last.

    python3 tools/gen_article_editorial.py <slug>
    python3 tools/sync.py

Writes article-<slug>-editorial.html.

Structure it builds, in order:
  header      dark block, same measure as the body, so the page has one spine
  hero        full-bleed photograph
  article     kicker + h2 per section, three image scales, one chapter break
  furniture   keep reading, back, donate, all shared with the rest of the site
"""
import json, os, sys, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page

NL = chr(10)
AMP = re.compile(r'&(?![a-zA-Z][a-zA-Z0-9]{1,9};|#[0-9]{1,6};|#x[0-9a-fA-F]{1,6};)')

# WordPress renditions that exist for this article's uploads (all 2250x1181).
# A general version needs an image manifest, which comes free once the images are
# pulled off WordPress into assets/img/articles/.
WIDE_SET = ((768, 403), (1024, 537), (1536, 806))
COL_SET = ((768, 403), (1024, 537))     # a 608px column never needs 1536, and these files are heavy
SIZES = {'col': '(max-width: 42rem) 100vw, 608px',
         'wide': '(max-width: 66rem) 100vw, 960px',
         'bleed': '100vw'}
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']


def esc(t):
    return AMP.sub('&amp;', t or '')


def srcset(url, kind):
    m = re.match(r'(.*)-(\d+)x(\d+)(\.(?:jpg|jpeg|png))$', url, re.I)
    if not m:
        return ''
    base, ext = m.group(1), m.group(4)
    sizes = COL_SET if kind == 'col' else WIDE_SET
    return ' srcset="%s"' % ', '.join('%s-%dx%d%s %dw' % (base, w, h, ext, w) for w, h in sizes)


def figure(url, alt, kind, caption='', pad='    ', rv=True):
    m = re.search(r'-(\d+)x(\d+)\.', url)
    dim = ' width="%s" height="%s"' % (m.group(1), m.group(2)) if m else ''
    cap = ('%s%s  <figcaption>%s</figcaption>' % (NL, pad, esc(caption))) if caption else ''
    cls = {'col': 'ed-col', 'wide': 'ed-wide', 'bleed': 'ed-bleed'}[kind]
    return ('%s<figure class="%s%s">%s'
            '%s  <img src="%s"%s sizes="%s" alt="%s"%s loading="lazy" decoding="async">%s%s%s</figure>'
            % (pad, cls, ' rv' if rv else '', NL, pad, url, srcset(url, kind),
               SIZES[kind], html.escape(alt or ''), dim, cap, NL, pad))


def words(a):
    n = 0
    for b in a['blocks']:
        for it in (b.get('flow') or [{'p': p} for p in b.get('paras', [])]):
            for k in ('p', 'h', 'q'):
                if k in it:
                    n += len(it[k].split())
            for k in ('ul', 'ol'):
                if k in it:
                    n += sum(len(x.split()) for x in it[k])
    return n


def norm(t):
    return re.sub(r'\s+', ' ', t or '').strip().lower()


def dup_caption(caption, para):
    """The CAP() convention in the import spec lifted the opening sentence of the
    paragraph beside the image, so most captions repeat text the reader is about
    to read anyway. Suppress those rather than printing the same words twice."""
    return not caption or norm(para).startswith(norm(caption)[:60])


def iso_date(d):
    d = (d or '').lower()
    y = re.search(r'(19|20)\d{2}', d)
    for i, m in enumerate(MONTHS):
        if m in d and y:
            return '%s-%02d' % (y.group(0), i + 1)
    return y.group(0) if y else ''


def split_sections(a):
    """Group blocks into sections. A section starts at a heading and runs until
    the next one, so a section that begins in the chapter break also ends there."""
    secs, cur = [], None
    for b in a['blocks']:
        items = list(b.get('flow') or [{'p': p} for p in b.get('paras', [])])
        head = b.get('heading')
        if not head and items and 'h' in items[0]:
            head = items.pop(0)['h']
        if head or cur is None:
            cur = {'kicker': b.get('eyebrow', '') if head else '', 'heading': head,
                   'dark': False, 'parts': []}
            secs.append(cur)
        if b['type'] == 'story':
            cur['dark'] = True
        if b.get('img'):
            first = next((it['p'] for it in items if 'p' in it), '')
            cur['parts'].append({'img': b['img'], 'alt': b.get('alt', ''),
                                 'cap': '' if dup_caption(b.get('caption'), first) else b['caption']})
        cur['parts'] += items
    return secs


def render_parts(parts, pad):
    """An image that opens a section, with no text before it, breaks wide and acts
    as the section's picture. Every other image stays at column width, because it
    is evidence inside a passage rather than a headline moment."""
    out = []
    for n, it in enumerate(parts):
        if 'img' in it and 'p' not in it:
            kind = 'wide' if n == 0 else 'col'
            out.append(figure(it['img'], it.get('alt', ''), kind, it.get('cap', ''), pad))
        elif 'p' in it:
            out.append('%s<p>%s</p>' % (pad, esc(it['p'])))
        elif 'h' in it:
            out.append('%s<h3>%s</h3>' % (pad, esc(it['h'])))
        elif 'ul' in it or 'ol' in it:
            tag = 'ul' if 'ul' in it else 'ol'
            rows = NL.join('%s  <li>%s</li>' % (pad, esc(x)) for x in it[tag])
            out.append('%s<%s>%s%s%s%s</%s>' % (pad, tag, NL, rows, NL, pad, tag))
        elif 'q' in it:
            out.append('%s<blockquote class="ed-pull">%s</blockquote>' % (pad, esc(it['q'])))
    return out


def build(a):
    read = max(2, round(words(a) / 220.0))
    meta = ' &nbsp;&middot;&nbsp; '.join(x for x in
                                        [a.get('date', ''), a.get('place', ''), '%d min read' % read] if x)

    head = ('  <header class="ed-top">%s    <div class="ed-in">%s'
            '      <nav class="ed-crumb"><a href="index.html">Home</a><span>/</span>'
            '<a href="articles.html">Articles</a></nav>%s'
            '      <span class="ed-kicker ed-kicker-top">%s</span>%s'
            '      <h1>%s</h1>%s'
            '      <p class="ed-stand">%s</p>%s'
            '      <p class="ed-meta">%s</p>%s    </div>%s  </header>'
            % (NL, NL, NL, esc(a.get('eyebrow', 'Story')), NL, esc(a['title']), NL,
               esc(a['standfirst']), NL, meta, NL, NL))

    hero = ('  <figure class="ed-hero">%s    <img src="%s"%s sizes="100vw" alt="%s" '
            'width="1024" height="537" fetchpriority="high" decoding="async">%s  </figure>'
            % (NL, a['hero'], srcset(a['hero'], 'wide'), html.escape(a['hero_alt']), NL))

    secs = split_sections(a)
    body = []
    for s in secs:
        pad = '      ' if s['dark'] else '    '
        parts = render_parts(s['parts'], pad)

        title = []
        if s['heading']:
            if s['kicker']:
                title.append('%s<span class="ed-kicker">%s</span>' % (pad, esc(s['kicker'])))
            title.append('%s<h2>%s</h2>' % (pad, esc(s['heading'])))

        if s['dark']:
            # the picture leads the chapter break, then the whole section runs inside it
            lead_fig = [p for p in parts if p.lstrip().startswith('<figure')][:1]
            rest = [p for p in parts if p not in lead_fig]
            body.append('  <section class="ed-break rv">%s%s%s    <div class="ed-in">%s%s%s    </div>%s  </section>'
                        % (NL, (lead_fig[0].replace(pad, '    ', 1) if lead_fig else ''), NL,
                           NL, NL.join(title + rest), NL, NL))
        else:
            body += title + parts

    if a.get('credit'):
        body.append('    <p class="ed-credit">%s</p>' % esc(a['credit']))

    art = '<article class="ed-art">%s%s%s%s%s  <div class="ed">%s%s%s  </div>%s</article>' % (
        NL, head, NL, hero, NL, NL, NL.join(body), NL, NL)

    out = [art]

    if a.get('related'):
        cards = []
        for r in a['related']:
            cards.append('      <a class="pj-rcard" href="%s">%s'
                         '        <img class="pj-rcard-im" src="%s" alt="" loading="lazy">%s'
                         '        <div class="pj-rcard-bd">%s'
                         '          <span class="pj-rd">%s</span>%s'
                         '          <h3>%s</h3>%s'
                         '          <p>%s</p>%s'
                         '          <span class="pj-rgo">%s &#8594;</span>%s'
                         '        </div>%s      </a>'
                         % (r['href'], NL, r['img'], NL, NL, r['date'], NL, esc(r['title']), NL,
                            esc(r['blurb']), NL, r.get('cta', 'Read the story'), NL, NL))
        out.append('<section class="sec paper">%s  <div class="cw rv">%s'
                   '    <span class="ey">Keep reading</span>%s'
                   '    <h2>More from the field.</h2>%s'
                   '    <div class="pj-readgrid">%s%s%s    </div>%s  </div>%s</section>'
                   % (NL, NL, NL, NL, NL, NL.join(cards), NL, NL, NL))

    out.append('<section class="pj-back">%s  <div class="cw rv">%s'
               '    <a class="btn-o" href="articles.html">&#8592; All articles</a>%s  </div>%s</section>'
               % (NL, NL, NL, NL))
    out.append('<section class="sec dark">%s  <div class="cw rv" style="text-align:center">%s'
               '    <h2 style="max-width:24ch;margin:0 auto 1rem">Help fund work like this.</h2>%s'
               '    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Every FNPW project is '
               'powered by donations, bequests and partnerships.</p>%s'
               '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
               '<a class="btn-p" href="https://foundation-for-national-parks-and-wildlife.raiselysite.com/">Donate</a>'
               '<a class="btn-o" href="partner.html">Become a partner</a></div>%s  </div>%s</section>'
               % (NL, NL, NL, NL, NL, NL))

    ld = {"@context": "https://schema.org", "@type": "Article",
          "headline": a['title'], "description": a.get('description', ''),
          "image": [a['hero']], "datePublished": iso_date(a.get('date', '')),
          "publisher": {"@type": "Organization",
                        "name": "Foundation for National Parks & Wildlife"},
          "mainEntityOfPage": {"@type": "WebPage",
                               "@id": "https://fnpw.org.au/article-%s.html" % a['slug']}}
    js = JS + NL + '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)

    name = 'article-%s-editorial.html' % a['slug']
    write_page(name, esc(a['title']), esc(a['description']),
               (NL + NL).join(out), page_css=CSS, extra_js=js)
    return name, read


CSS = '''
/* ---------------------------------------------------------------------------
   Editorial article layout.
   One grid, one text column, images break out of it. The left edge of the body
   copy is identical from the first word to the last, which is the whole point.
   --------------------------------------------------------------------------- */
.ed-prog{position:fixed;top:0;left:0;height:2px;width:0;background:var(--euc);z-index:41}

/* opening block: same measure as the body, so the page has a single spine */
.ed-top{background:var(--euc-deep);padding:clamp(3rem,6vw,4.6rem) 0 clamp(2.4rem,4vw,3.2rem)}
.ed-in{max-width:min(38rem,100% - 2.5rem);margin:0 auto}
.ed-crumb{display:flex;gap:.5em;font-size:.8rem;color:rgba(250,246,242,.62);margin-bottom:1.5rem}
.ed-crumb a{color:var(--euc-soft)}
.ed-crumb span{opacity:.45}
.ed-kicker{display:block;font-family:var(--ff-b);font-size:.74rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--stone)}
.ed-kicker-top{color:var(--wattle);margin-bottom:.5rem}
.ed-top h1{font-family:var(--ff-d);color:var(--cream);font-size:clamp(1.9rem,4.4vw,2.75rem);font-weight:600;line-height:1.08;letter-spacing:-.028em;margin:0 0 1.05rem}
.ed-stand{font-size:clamp(1.05rem,1.5vw,1.2rem);line-height:1.55;color:rgba(250,246,242,.88);margin:0 0 1.6rem}
.ed-meta{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:rgba(250,246,242,.62);margin:0}

.ed-hero{margin:0;background:var(--sand)}
.ed-hero img{width:100%;height:auto;display:block;max-height:74vh;object-fit:cover}

.ed{
  --m:38rem;   /* text measure, about 66 characters at 19px */
  --w:60rem;   /* wide breakout */
  display:grid;
  grid-template-columns:
    [full-start] minmax(1.25rem,1fr)
    [wide-start] minmax(0,calc((var(--w) - var(--m)) / 2))
    [text-start] min(var(--m),100% - 2.5rem) [text-end]
    minmax(0,calc((var(--w) - var(--m)) / 2)) [wide-end]
    minmax(1.25rem,1fr) [full-end];
  font-size:19px;
  line-height:1.68;
  color:var(--char);
  padding:clamp(2.6rem,5vw,3.6rem) 0 1rem;
}
.ed > *{grid-column:text}
.ed > .ed-wide{grid-column:wide}
.ed > .ed-bleed,.ed > .ed-break{grid-column:full}

.ed p{margin:0 0 1.25em}
.ed h2{font-family:var(--ff-d);font-weight:600;font-size:clamp(1.45rem,2.6vw,1.9rem);line-height:1.16;letter-spacing:-.022em;color:var(--euc-deep);margin:3.4rem 0 1rem}
.ed h3{font-family:var(--ff-d);font-weight:600;font-size:clamp(1.08rem,1.5vw,1.2rem);line-height:1.32;letter-spacing:-.01em;color:var(--euc-deep);margin:2.2rem 0 .5rem}
.ed .ed-kicker{margin:3.4rem 0 .4rem}
.ed .ed-kicker + h2{margin-top:0}
.ed > *:first-child{margin-top:0}

.ed ul,.ed ol{margin:0 0 1.4em;padding-left:1.25rem}
.ed li{margin:0 0 .6rem;padding-left:.15rem}
.ed li:last-child{margin-bottom:0}
.ed li::marker{color:var(--euc)}

.ed-pull{margin:2.7rem 0;padding:1.3rem 0 0;border-top:2px solid var(--wattle);font-family:var(--ff-d);font-weight:500;font-size:1.3em;line-height:1.38;letter-spacing:-.015em;color:var(--euc-deep)}
.ed-credit{font-size:.82rem;color:var(--stone);border-top:1px solid var(--rule);padding-top:1.1rem;margin-top:2.6rem}

.ed figure{margin:2.9rem 0}
.ed figure img{width:100%;height:auto;display:block;background:var(--sand)}
.ed figcaption{font-size:.78rem;line-height:1.5;color:var(--stone);margin-top:.7rem;max-width:52ch}
.ed .ed-bleed figcaption{max-width:min(38rem,100% - 2.5rem);margin-left:auto;margin-right:auto}

/* the one chapter break, kept from the project pages because it earns its place */
.ed-break{background:var(--euc-deep);color:rgba(250,246,242,.9);padding:clamp(3rem,6vw,4.4rem) 0;margin:3.6rem 0}
.ed-break > figure{margin:0 auto 2.4rem;max-width:min(60rem,100% - 2.5rem)}
.ed-break h2{color:var(--cream);margin:0 0 1rem}
.ed-break h3{color:var(--cream)}
.ed-break .ed-kicker{color:var(--wattle-mid);margin:0 0 .4rem}
.ed-break p:last-child{margin-bottom:0}
.ed-break figcaption{color:rgba(250,246,242,.62)}
.ed-break li::marker{color:var(--euc-mid)}

@media(max-width:640px){
  .ed{font-size:17.5px}
  .ed figure{margin:2.2rem 0}
  .ed h2,.ed .ed-kicker{margin-top:2.8rem}
}
@media(prefers-reduced-motion:reduce){
  .rv{opacity:1;transform:none;transition:none}
  .ed-prog{display:none}
}
'''

JS = '''<script>
(function(){
  var art=document.querySelector('.ed'); if(!art)return;
  var bar=document.createElement('div'); bar.className='ed-prog'; document.body.appendChild(bar);
  var tick=function(){
    var r=art.getBoundingClientRect(), h=window.innerHeight;
    var total=r.height-h, done=Math.min(Math.max(-r.top,0),Math.max(total,1));
    bar.style.width=(total<=0?0:(done/total)*100)+'%';
  };
  tick(); addEventListener('scroll',tick,{passive:true}); addEventListener('resize',tick);
})();
</script>'''


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else 'your-backyard-is-habitat-too-help-native-wildlife'
    arts = {a['slug']: a for a in json.load(open('data/articles.json', encoding='utf-8'))}
    if slug not in arts:
        raise SystemExit('no such slug: %s' % slug)
    name, read = build(arts[slug])
    print('wrote %s  (%d words, %d min read)' % (name, words(arts[slug]), read))


if __name__ == '__main__':
    main()
