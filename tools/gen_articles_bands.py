"""Generate every article page from data/articles.json.

Adding a new blog post = one entry in data/articles.json, then run this file.
No HTML is written by hand, so every article keeps the same section rhythm.

Block types (one <section> each, so the padding is identical everywhere):
  lead   flow                                     opening passage at reading width
  text   eyebrow? flow                            reading-width passage
  band   eyebrow heading img alt caption flow     image + text, flip:true / paper:true
  story  eyebrow heading img alt caption flow     dark band, image + text
  list   eyebrow? heading? intro? items ordered?  standalone list section
  quote  text attrib                              centred pull quote
  wide   img alt caption                          full-width image

"flow" is the body of a block: an ordered list of small items, so one section
can hold paragraphs, subheadings, lists and an inline figure without splitting
into extra sections (which would double the space between them).

  {"p": "..."}                                   paragraph
  {"h": "..."}                                   subheading (h3)
  {"ul": ["...", "..."]}                         bullet list
  {"ol": ["...", "..."]}                         numbered list
  {"q": "..."}                                   inline pull quote
  {"img": "...", "alt": "...", "caption": "..."} inline figure at reading width

Legacy "paras": ["...", "..."] still works and is read as a flow of paragraphs.
"""
import json, os, sys, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page  # same skeleton + header/footer markers as every other page

NL = chr(10)


AMP = re.compile(r'&(?![a-zA-Z][a-zA-Z0-9]{1,9};|#[0-9]{1,6};|#x[0-9a-fA-F]{1,6};)')

def esc(t):
    """Escape a bare & so headings like "Fire & Flood" stay valid HTML."""
    return AMP.sub('&amp;', t or '')


def flow_items(b):
    """Normalise a block body into a flow list."""
    if b.get('flow'):
        return b['flow']
    items = [{'p': x} for x in (b.get('paras') or [])]
    if b.get('heading') and b.get('type') == 'text':
        items.insert(b.get('heading_after', 0), {'h': b['heading']})
    return items


def li_html(items, ordered=False):
    tag = 'ol' if ordered else 'ul'
    rows = NL.join('        <li>%s</li>' % x for x in items)
    return '      <%s class="pj-%s">%s%s%s      </%s>' % (tag, tag, NL, rows + NL, '', tag)


def flow_html(b, indent='      '):
    out = []
    seen_h = bool(b.get('heading'))          # a band already supplies the section heading
    for it in flow_items(b):
        if 'p' in it:
            out.append('%s<p>%s</p>' % (indent, esc(it['p'])))
        elif 'h' in it:
            tag = 'h4' if seen_h else 'h3'
            seen_h = True
            out.append('%s<%s>%s</%s>' % (indent, tag, esc(it['h']), tag))
        elif 'ul' in it:
            out.append(li_html([esc(x) for x in it['ul']]))
        elif 'ol' in it:
            out.append(li_html([esc(x) for x in it['ol']], True))
        elif 'q' in it:
            out.append('%s<blockquote class="pj-pull">%s</blockquote>' % (indent, esc(it['q'])))
        elif 'img' in it:
            cap = ('%s%s  <figcaption>%s</figcaption>' % (NL, indent, it['caption'])) if it.get('caption') else ''
            out.append('%s<figure class="pj-fig"><img src="%s" alt="%s" loading="lazy">%s</figure>'
                       % (indent, it['img'], html.escape(it.get('alt', '')), cap))
        else:
            raise ValueError('unknown flow item: %r' % it)
    return NL.join(out)


def block_html(b):
    t = b['type']
    body = flow_html(b)
    ey = '      <span class="ey">%s</span>%s' % (b['eyebrow'], NL) if b.get('eyebrow') else ''

    if t in ('lead', 'text', 'list'):
        if t == 'list':
            parts = []
            if b.get('heading'):
                parts.append('      <h3>%s</h3>' % b['heading'])
            parts += ['      <p>%s</p>' % esc(x) for x in b.get('intro', [])]
            parts.append(li_html([esc(x) for x in b['items']], b.get('ordered', False)))
            body = NL.join(parts)
        cls = 'sec paper' if b.get('paper') else 'sec'
        return ('<section class="%s">%s  <div class="cw rv">%s    <div class="pj-body">%s%s%s%s'
                '    </div>%s  </div>%s</section>'
                % (cls, NL, NL, NL, ey, body, NL, NL, NL))

    if t in ('band', 'story'):
        cap = ('%s      <figcaption>%s</figcaption>' % (NL, esc(b['caption']))) if b.get('caption') else ''
        fig_cls = 'pj-story-im' if t == 'story' else 'pj-band-im'
        img = ('    <figure class="%s">%s      <img src="%s" alt="%s" loading="lazy">%s%s    </figure>'
               % (fig_cls, NL, b['img'], html.escape(b.get('alt', '')), cap, NL))
        head = '      <h3>%s</h3>%s' % (esc(b['heading']), NL) if b.get('heading') else ''
        if t == 'story':
            return ('<section class="pj-story">%s  <div class="cw"><div class="pj-story-g rv">%s%s%s'
                    '    <div>%s%s%s%s%s    </div>%s  </div></div>%s</section>'
                    % (NL, NL, img, NL, NL, ey, head, body, NL, NL, NL))
        cls = 'pj-band alt' if b.get('paper') else 'pj-band'
        if b.get('flip'):
            cls += ' flip'
        return ('<section class="%s">%s  <div class="cw"><div class="pj-band-g rv">%s%s%s'
                '    <div class="pj-band-bd">%s%s%s%s%s    </div>%s  </div></div>%s</section>'
                % (cls, NL, NL, img, NL, NL, ey, head, body, NL, NL, NL))

    if t == 'quote':
        return ('<section class="pj-qband">%s  <div class="cw"><figure class="pj-q rv">%s'
                '    <blockquote>%s</blockquote>%s    <figcaption>%s</figcaption>%s'
                '  </figure></div>%s</section>'
                % (NL, NL, b['text'], NL, b.get('attrib', ''), NL, NL))

    if t == 'wide':
        cap = ('%s      <figcaption>%s</figcaption>' % (NL, esc(b['caption']))) if b.get('caption') else ''
        return ('<section class="sec">%s  <div class="cw rv">%s    <figure class="pj-wide">%s'
                '      <img src="%s" alt="%s" loading="lazy">%s%s    </figure>%s  </div>%s</section>'
                % (NL, NL, NL, b['img'], html.escape(b.get('alt', '')), cap, NL, NL, NL))

    raise ValueError('unknown block type: %s' % t)


def related_html(items):
    cards = []
    for r in items:
        cards.append(
            '      <a class="pj-rcard" href="%s">%s'
            '        <img class="pj-rcard-im" src="%s" alt="" loading="lazy">%s'
            '        <div class="pj-rcard-bd">%s'
            '          <span class="pj-rd">%s</span>%s'
            '          <h3>%s</h3>%s'
            '          <p>%s</p>%s'
            '          <span class="pj-rgo">%s &#8594;</span>%s'
            '        </div>%s      </a>'
            % (r['href'], NL, r['img'], NL, NL, r['date'], NL, esc(r['title']), NL,
               esc(r['blurb']), NL, r.get('cta', 'Read the story'), NL, NL))
    return ('<section class="sec paper">%s  <div class="cw rv">%s'
            '    <span class="ey">Keep reading</span>%s'
            '    <h2>More from the field.</h2>%s'
            '    <div class="pj-readgrid">%s%s%s    </div>%s  </div>%s</section>'
            % (NL, NL, NL, NL, NL, NL.join(cards), NL, NL, NL))


def build(a):
    place = ' &nbsp;&nbsp;&middot;&nbsp;&nbsp; ' + a['place'] if a.get('place') else ''
    body = ['<section class="pj-hero">%s'
            '  <figure class="pj-hero-im"><img src="%s" alt="%s"></figure>%s'
            '  <div class="cw rv">%s'
            '    <nav class="breadcrumb" style="display:flex;gap:.5em;font-size:.82rem">'
            '<a href="index.html">Home</a><span style="opacity:.4">/</span>'
            '<a href="articles.html">Articles</a><span style="opacity:.4">/</span>%s</nav>%s'
            '    <span class="ey">%s</span>%s'
            '    <h1>%s</h1>%s'
            '    <p class="pj-hero-meta">%s%s</p>%s'
            '    <p class="lede">%s</p>%s  </div>%s</section>'
            % (NL, a['hero'], html.escape(a['hero_alt']), NL, NL, esc(a['title']), NL,
               a.get('eyebrow', 'Story'), NL, esc(a['title']), NL, a['date'], place, NL,
               esc(a['standfirst']), NL, NL)]
    body += [block_html(b) for b in a['blocks']]
    if a.get('credit'):
        body.append('<section class="sec">%s  <div class="cw rv">%s'
                    '    <div class="pj-body"><p class="pj-src">%s</p></div>%s  </div>%s</section>'
                    % (NL, NL, a['credit'], NL, NL))
    if a.get('related'):
        body.append(related_html(a['related']))
    body.append('<section class="pj-back">%s  <div class="cw rv">%s'
                '    <a class="btn-o" href="articles.html">&#8592; All articles</a>%s'
                '  </div>%s</section>' % (NL, NL, NL, NL))
    body.append('<section class="sec dark">%s  <div class="cw rv" style="text-align:center">%s'
                '    <h2 style="max-width:24ch;margin:0 auto 1rem">Help fund work like this.</h2>%s'
                '    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Every FNPW project is '
                'powered by donations, bequests and partnerships.</p>%s'
                '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
                '<a class="btn-p" href="https://foundation-for-national-parks-and-wildlife.raiselysite.com/">Donate</a>'
                '<a class="btn-o" href="partner.html">Become a partner</a></div>%s  </div>%s</section>'
                % (NL, NL, NL, NL, NL, NL))
    name = 'article-%s.html' % a['slug']
    write_page(name, esc(a['title']), esc(a['description']), (NL + NL).join(body))
    return name


def main():
    arts = json.load(open('data/articles.json', encoding='utf-8'))
    seen = set()
    for a in arts:
        if a['slug'] in seen:
            raise SystemExit('duplicate slug in data/articles.json: %s' % a['slug'])
        seen.add(a['slug'])
    made = [build(a) for a in arts]
    print('articles: %d page%s written' % (len(made), '' if len(made) == 1 else 's'))
    for m in made:
        print('  ' + m)


if __name__ == '__main__':
    main()
