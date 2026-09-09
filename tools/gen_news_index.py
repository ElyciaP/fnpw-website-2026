"""Build in-the-news.html, the press coverage log, from data/in-the-news.json.

These 15 WordPress posts are not articles. They are a coverage log: each one is
titled after the publication that ran the story ("The Daily Telegraph", "K-Zone",
"Studio 10") and runs 31 to 190 words. Given article pages and Stories tiles they
would read as near-empty content named after newspapers, so they get a dated list
of their own instead.

    python3 tools/gen_news_index.py
    python3 tools/sync.py
"""
import json, os, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page

NL = chr(10)

CSS = '''
.nw-hero{background:var(--euc-deep);padding:clamp(3rem,6vw,4.6rem) 0 clamp(2.4rem,4vw,3.2rem)}
.nw-hero .ey{color:var(--wattle)}
.nw-hero h1{color:var(--cream);font-size:clamp(1.9rem,4.4vw,3rem);font-weight:600;letter-spacing:-.028em;line-height:1.07;margin:1rem 0 1.1rem;max-width:20ch}
.nw-hero .lede{color:rgba(250,246,242,.88);max-width:56ch}
.nw-crumb{display:flex;gap:.5em;font-size:.8rem;color:rgba(250,246,242,.72);margin-bottom:1.4rem}
.nw-crumb a{color:var(--euc-soft)}
.nw-list{border-top:1px solid var(--rule);margin-top:2rem}
.nw-row{display:grid;grid-template-columns:9rem 1fr auto;gap:1.5rem;align-items:baseline;padding:1.35rem 0;border-bottom:1px solid var(--rule);transition:.2s}
.nw-row:hover{background:var(--paper)}
.nw-date{font-size:.74rem;letter-spacing:.15em;text-transform:uppercase;font-weight:700;color:var(--stone)}
.nw-pub{font-family:var(--ff-d);font-weight:600;font-size:1.05rem;color:var(--euc-deep);margin:0 0 .3rem}
.nw-blurb{font-size:.92rem;line-height:1.55;color:var(--char);margin:0;max-width:62ch}
.nw-go{font-size:.8rem;font-weight:700;color:var(--euc);white-space:nowrap}
@media(max-width:720px){
  .nw-row{grid-template-columns:1fr;gap:.4rem}
  .nw-go{margin-top:.3rem}
}
'''

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']


def pretty(d):
    try:
        y, m, day = d.split('-')
        return '%s %s %s' % (day.lstrip('0'), MONTHS[int(m) - 1][:3], y)
    except Exception:
        return d


def main():
    items = json.load(open('data/in-the-news.json', encoding='utf-8'))
    rows = []
    for c in items:
        rows.append(
            '      <a class="nw-row" href="%s">%s'
            '        <span class="nw-date">%s</span>%s'
            '        <span><span class="nw-pub">%s</span><p class="nw-blurb">%s</p></span>%s'
            '        <span class="nw-go">Read &#8594;</span>%s'
            '      </a>'
            % (html.escape(c['url'], quote=True), NL, pretty(c['date']), NL,
               html.escape(c['title']), html.escape(c.get('blurb', '')), NL, NL))

    body = (
        '<header class="nw-hero">%s  <div class="cw rv">%s'
        '    <nav class="nw-crumb"><a href="index.html">Home</a><span style="opacity:.45">/</span>'
        '<a href="articles.html">Articles</a><span style="opacity:.45">/</span>In the news</nav>%s'
        '    <span class="ey">Coverage</span>%s'
        '    <h1>In the news</h1>%s'
        '    <p class="lede">Where the Foundation for National Parks &amp; Wildlife has been covered '
        'in the press, on radio and on television.</p>%s  </div>%s</header>%s%s'
        '<section class="sec">%s  <div class="cw rv">%s    <div class="nw-list">%s%s%s    </div>%s  </div>%s</section>%s%s'
        '<section class="pj-back">%s  <div class="cw rv">%s'
        '    <a class="btn-o" href="articles.html">&#8592; All stories</a>%s  </div>%s</section>'
        % (NL, NL, NL, NL, NL, NL, NL, NL, NL,
           NL, NL, NL, NL.join(rows), NL, NL, NL, NL, NL,
           NL, NL, NL, NL))

    write_page('in-the-news.html', 'In the news',
               'Press, radio and television coverage of the Foundation for National Parks &amp; Wildlife.',
               body, page_css=CSS)
    print('in-the-news.html: %d coverage entries' % len(items))


if __name__ == '__main__':
    main()
