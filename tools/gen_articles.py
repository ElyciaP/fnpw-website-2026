"""Generate every article page from data/articles.json.

Adding a new blog post = one entry in data/articles.json, then run this file.
No HTML is written by hand, so every article keeps the same section rhythm.

Block types:
  lead   paras                                  opening paragraphs at reading width
  text   eyebrow? heading? heading_after? paras  reading-width passage
  band   eyebrow heading img alt caption paras   image + text, flip:true / paper:true
  story  eyebrow heading img alt caption paras   dark band, image + text
  quote  text attrib                             centred pull quote
  wide   img alt caption                         full-width image
"""
import json, os, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page  # same skeleton + header/footer markers as every other page

def paras(ps):
    return '\n'.join('      <p>%s</p>' % p for p in ps)

def block_html(b):
    t = b['type']
    if t == 'lead':
        return f'''<section class="sec ">
  <div class="cw rv">
    <div class="pj-body">
{paras(b["paras"])}
    </div>
  </div>
</section>'''
    if t == 'text':
        ey = f'      <span class="ey">{b["eyebrow"]}</span>\n' if b.get('eyebrow') else ''
        ps = b['paras']
        head = f'      <h3>{b["heading"]}</h3>\n' if b.get('heading') else ''
        n = b.get('heading_after', 0)          # let a heading sit mid-passage
        body = (paras(ps[:n]) + '\n' + head + paras(ps[n:])) if (head and n) else (head + paras(ps))
        return f'''<section class="sec ">
  <div class="cw rv">
    <div class="pj-body">
{ey}{body}
    </div>
  </div>
</section>'''
    if t in ('band', 'story'):
        cap = f'\n      <figcaption>{b["caption"]}</figcaption>' if b.get('caption') else ''
        if t == 'story':
            return f'''<section class="pj-story">
  <div class="cw"><div class="pj-story-g rv">
    <figure class="pj-story-im">
      <img src="{b['img']}" alt="{html.escape(b['alt'])}" loading="lazy">{cap}
    </figure>
    <div>
      <span class="ey">{b['eyebrow']}</span>
      <h3>{b['heading']}</h3>
{paras(b['paras'])}
    </div>
  </div></div>
</section>'''
        cls = 'sec paper' if b.get('paper') else ('pj-band alt flip' if b.get('flip') else 'pj-band')
        inner = 'pj-band-g rv'
        return f'''<section class="{cls}">
  <div class="cw"><div class="{inner}">
    <figure class="pj-band-im">
      <img src="{b['img']}" alt="{html.escape(b['alt'])}" loading="lazy">{cap}
    </figure>
    <div class="pj-band-bd">
      <span class="ey">{b['eyebrow']}</span>
      <h3>{b['heading']}</h3>
{paras(b['paras'])}
    </div>
  </div></div>
</section>'''
    if t == 'quote':
        return f'''<section class="pj-qband">
  <div class="cw"><figure class="pj-q rv">
    <blockquote>{b['text']}</blockquote>
    <figcaption>{b['attrib']}</figcaption>
  </figure></div>
</section>'''
    if t == 'wide':
        cap = f'\n      <figcaption>{b["caption"]}</figcaption>' if b.get('caption') else ''
        return f'''<section class="sec ">
  <div class="cw rv">
    <figure class="pj-wide">
      <img src="{b['img']}" alt="{html.escape(b['alt'])}" loading="lazy">{cap}
    </figure>
  </div>
</section>'''
    raise ValueError('unknown block type: %s' % t)

def related_html(items):
    cards = []
    for r in items:
        cards.append(f'''      <a class="pj-rcard" href="{r['href']}">
        <img class="pj-rcard-im" src="{r['img']}" alt="" loading="lazy">
        <div class="pj-rcard-bd">
          <span class="pj-rd">{r['date']}</span>
          <h3>{r['title']}</h3>
          <p>{r['blurb']}</p>
          <span class="pj-rgo">{r.get('cta','Read the story')} &#8594;</span>
        </div>
      </a>''')
    return f'''<section class="sec paper">
  <div class="cw rv">
    <span class="ey">Keep reading</span>
    <h2>More from the field.</h2>
    <div class="pj-readgrid">
{chr(10).join(cards)}
    </div>
  </div>
</section>'''

def build(a):
    body = [f'''<section class="pj-hero">
  <figure class="pj-hero-im"><img src="{a['hero']}" alt="{html.escape(a['hero_alt'])}"></figure>
  <div class="cw rv">
    <nav class="breadcrumb" style="display:flex;gap:.5em;font-size:.82rem"><a href="index.html">Home</a><span style="opacity:.4">/</span><a href="articles.html">Articles</a><span style="opacity:.4">/</span>{a['title']}</nav>
    <span class="ey">{a.get('eyebrow','Story')}</span>
    <h1>{a['title']}</h1>
    <p class="pj-hero-meta">{a['date']}{' &nbsp;&nbsp;&middot;&nbsp;&nbsp; ' + a['place'] if a.get('place') else ''}</p>
    <p class="lede">{a['standfirst']}</p>
  </div>
</section>''']
    body += [block_html(b) for b in a['blocks']]
    if a.get('credit'):
        body.append(f'''<section class="sec ">
  <div class="cw rv">
    <div class="pj-body"><p class="pj-src">{a['credit']}</p></div>
  </div>
</section>''')
    if a.get('related'):
        body.append(related_html(a['related']))
    body.append('''<section class="pj-back">
  <div class="cw rv">
    <a class="btn-o" href="articles.html">&#8592; All articles</a>
  </div>
</section>''')
    body.append('''<section class="sec dark">
  <div class="cw rv" style="text-align:center">
    <h2 style="max-width:24ch;margin:0 auto 1rem">Help fund work like this.</h2>
    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Every FNPW project is powered by donations, bequests and partnerships.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap"><a class="btn-p" href="https://foundation-for-national-parks-and-wildlife.raiselysite.com/">Donate</a><a class="btn-o" href="partner.html">Become a partner</a></div>
  </div>
</section>''')
    write_page('article-%s.html' % a['slug'], a['title'], a['description'], '\n\n'.join(body))
    return 'article-%s.html' % a['slug']

def main():
    arts = json.load(open('data/articles.json', encoding='utf-8'))
    made = [build(a) for a in arts]
    print('articles: %d page%s written' % (len(made), '' if len(made) == 1 else 's'))
    for m in made:
        print('  ' + m)

if __name__ == '__main__':
    main()
