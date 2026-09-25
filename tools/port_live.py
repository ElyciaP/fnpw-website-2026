"""Port pages from the live fnpw.org.au site into the static build (Sep 2026).

Source copy lives in data/live-port/<slug>.md, harvested word for word from the
live site. Nothing here rewrites that copy. It is laid out in the site's own
templates:

  privacy-policy.html, terms-and-conditions.html   legal text, verbatim
  grants.html + three grant project pages          project template
  paws-magazine.html                               issue archive
  mitigating-effects-environmental-change.html     eBook page (form still to wire)
  newsletter-thank-you.html                        HubSpot redirect target
  faqs.html                                        new "Tax and your donation" group
  data/articles.json                               three new blog entries
  data/live-port/qld-daisy-hill.html               fragment for the QLD volunteering page

    python3 tools/port_live.py
    python3 tools/merge_articles.py && python3 tools/gen_articles.py \
      && python3 tools/gen_articles_index.py && python3 tools/gen_vol_states.py
"""
import json, os, re, sys, html as H
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from site_lib import write_page

NL = chr(10)
SRC = 'data/live-port/'

# live path -> page in this build
PAGE_MAP = {
    '/': 'index.html', '/about-us/': 'about.html', '/projects/': 'projects.html',
    '/contact-us/': 'contact.html', '/corporate-partnerships/': 'partner.html',
    '/corporate-partners/': 'partner.html', '/project-partnerships/': 'partner.html',
    '/corporate-volunteering/': 'volunteer.html', '/bequest/': 'bequests.html',
    '/news/': 'articles.html', '/faqs/': 'faqs.html', '/grants/': 'grants.html',
    '/ways-you-can-get-involved/': 'ways-you-can-get-involved.html',
    '/fundraising-with-fnpw/': 'fundraising-with-fnpw.html',
    '/corporate-governance/': 'corporate-governance.html',
    '/donate-land/': 'donate-land.html', '/newsletters-sign-up/': 'newsletters-sign-up.html',
    '/workplace-giving/': 'workplace-giving.html', '/paws-magazine/': 'paws-magazine.html',
    '/why-your-support-is-needed/': 'why-your-support-is-needed.html',
    '/how-your-contributions-help/': 'how-your-contributions-help.html',
    '/privacy-policy/': 'privacy-policy.html', '/terms-and-conditions/': 'terms-and-conditions.html',
    '/media-enquiry/': 'media-enquiry.html', '/koala-facts/': 'article-koala-facts.html',
    '/biodiversity-month/': 'article-biodiversity-month.html',
    '/wildlifeheroes': 'project-wildlife-heroes.html',
    '/grant/wildlife-heroes-grants/': 'project-wildlife-heroes.html',
    '/grant/community-conservation-grants/': 'project-community-conservation-grants.html',
}


def local_link(url):
    m = re.match(r'https?://(?:www\.)?fnpw\.org\.au(/[^"#?]*)?', url)
    if not m:
        return url
    path = m.group(1) or '/'
    if not path.endswith('/') and '.' not in path.split('/')[-1]:
        path += '/'
    if path.startswith('/wp-content/'):
        return url
    pm = re.match(r'/project/([^/]+)/$', path)
    if pm and os.path.exists('project-%s.html' % pm.group(1)):
        return 'project-%s.html' % pm.group(1)
    am = re.match(r'/news/[^/]+/([^/]+)/$', path)
    if am and os.path.exists('article-%s.html' % am.group(1)):
        return 'article-%s.html' % am.group(1)
    if path in PAGE_MAP:
        return PAGE_MAP[path]
    return url


def body_md(slug, cut=()):
    """The harvested page body: after the first '---', minus notes and anything past a cut marker."""
    t = open(SRC + slug + '.md', encoding='utf-8').read()
    if '\n---\n' in t:
        t = t.split('\n---\n', 1)[1]
    elif '\n# ' in t:
        t = t[t.index('\n# ') + 1:]
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    for c in ('\nNotes:', '\n## Standard footer', '\nNOT ON LIVE PAGE') + tuple(cut):
        if c in t:
            t = t.split(c, 1)[0]
    # images the harvest could not resolve, and the credit line that followed them
    t = re.sub(r'!\[[^\]]*\]\(URL-UNRESOLVED[^)]*\)\n(\*[^*\n]+\*\n)?', '', t)
    return t.strip() + NL


def md_html(t, drop_h1=True, shift=0):
    if drop_h1:
        t = re.sub(r'^# .*\n', '', t, count=1, flags=re.M)
    h = markdown.markdown(t, extensions=['tables'])
    h = re.sub(r'href="([^"]+)"', lambda m: 'href="%s"' % local_link(H.unescape(m.group(1))).replace('&', '&amp;'), h)
    h = h.replace('<img ', '<img loading="lazy" ')
    # h4/h5 subheads read as h3 in our pages
    h = re.sub(r'<(/?)h[45]>', r'<\1h3>', h)
    return h


PROSE_CSS = '''
.prose{max-width:74ch}
.prose h2{font-size:clamp(1.3rem,2vw,1.6rem);margin:2.4rem 0 .9rem;color:var(--euc-deep)}
.prose h3{font-size:1.08rem;margin:2rem 0 .7rem;color:var(--euc-deep);letter-spacing:.01em}
.prose p,.prose li{font-size:1rem;line-height:1.75;color:var(--char)}
.prose p{margin:0 0 1rem}
.prose ul,.prose ol{margin:0 0 1.2rem;padding-left:1.3rem}
.prose li{margin-bottom:.45rem}
.prose a{color:var(--euc);text-decoration:underline;text-underline-offset:2px}
.prose img{max-width:100%;height:auto;display:block;margin:1.6rem 0}
.prose table{width:100%;border-collapse:collapse;margin:1rem 0 2rem;font-size:.92rem}
.prose th,.prose td{text-align:left;padding:.65rem .8rem;border-bottom:1px solid var(--rule);vertical-align:top}
.prose th{font-family:var(--ff-d);color:var(--euc-deep);background:var(--sand)}
.prose blockquote{border-left:3px solid var(--bark);margin:1.6rem 0;padding:.2rem 0 .2rem 1.2rem}
@media(max-width:640px){.prose table{display:block;overflow-x:auto}}
'''


# ---------------------------------------------------------------- legal pages
def legal(page, slug):
    t = open(page, encoding='utf-8').read()
    if '<div class="prose">' in t:
        print('%-44s already ported' % page); return
    html = md_html(body_md(slug))
    new = '<div class="prose">%s%s%s</div>' % (NL, html, NL)
    t2, n = re.subn(r'<div class="port-note">.*?</div>', lambda m: new, t, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('%s: port-note not found' % page)
    if '.prose{' not in t2:
        t2 = t2.replace('</style>', PROSE_CSS + '</style>', 1)
    open(page, 'w', encoding='utf-8').write(t2)
    print('%-44s ported (%d words)' % (page, len(re.sub('<[^>]+>', ' ', html).split())))


# ---------------------------------------------------------------- shared bits
def crumbs(*items):
    parts = ['<a href="index.html">Home</a>']
    for label, href in items[:-1]:
        parts.append('<a href="%s">%s</a>' % (href, label))
    parts.append(items[-1][0])
    return ('<nav class="breadcrumb" style="display:flex;gap:.5em;font-size:.82rem;flex-wrap:wrap">'
            + '<span>/</span>'.join(parts) + '</nav>')


def photo_hero(ey, h1, lede, crumb_html, img, alt=''):
    return NL.join([
        '<section class="pj-hero">',
        '  <figure class="pj-hero-im"><img src="%s" alt="%s" fetchpriority="high" decoding="async"></figure>' % (img, H.escape(alt)),
        '  <div class="cw rv">',
        '    ' + crumb_html,
        '    <span class="ey">%s</span>' % ey,
        '    <h1>%s</h1>' % h1,
        ('    <p class="lede">%s</p>' % lede) if lede else '',
        '  </div>',
        '</section>'])


DONATE_BAND = NL.join([
    '<section class="sec dark">',
    '  <div class="cw rv" style="text-align:center">',
    '    <h2 style="max-width:24ch;margin:0 auto 1rem">Help fund work like this.</h2>',
    '    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">Every FNPW project is powered by donations, bequests and partnerships.</p>',
    '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap"><a class="btn-p btn-don" href="https://bush.fnpw.org.au">Donate</a><a class="btn-o" href="bequests.html">Leave a gift in your Will</a></div>',
    '  </div>',
    '</section>'])

U = 'https://fnpw.org.au/wp-content/uploads/'


# ---------------------------------------------------------------- grant project pages
GRANTS = {
    'community-conservation-grants': {
        'title': 'Community Conservation Grants', 'pillar': 'Healing the Land', 'meta': 'National &nbsp;&nbsp;&middot;&nbsp;&nbsp; Since 2019',
        'img': U + '2021/02/tree-planting-PATFM.jpg',
        'lede': 'Grants for field projects and education programs with a direct outcome for nature conservation in Australia.',
    },
    'private-land-conservation-grants': {
        'title': 'Private Land Conservation Grants', 'pillar': 'Saving Species', 'meta': 'NSW &nbsp;&nbsp;&middot;&nbsp;&nbsp; Since 2012',
        'img': U + '2021/02/mcbride-margaret-smith-large.jpg',
        'lede': '',
    },
    'bushfire-recovery-small-grants': {
        'title': 'Bushfire Recovery Small Grants', 'pillar': 'Healing the Land', 'meta': 'National &nbsp;&nbsp;&middot;&nbsp;&nbsp; Since 2020',
        'img': U + '2021/02/Alpine-Ash-forest-regrowth-KNP.jpg',
        'lede': '',
    },
}


def grant_page(slug, g):
    md = body_md(slug, cut=('\n## Latest news on this project', '\n## Related Projects'))
    md = re.sub(r'^# .*\n', '', md, count=1, flags=re.M)
    # metadata lines shown in the hero instead
    md = re.sub(r'^(- )?\**(YEAR|STATE|FOCUS AREAS):?\**:?.*\n', '', md, flags=re.M)
    md = re.sub(r'^(NSW|National)\n', '', md, flags=re.M)
    # the hero image is used as the hero, not repeated as the first body image
    md = md.replace('![%s' % '', '![', 1)
    first_img = re.search(r'!\[[^\]]*\]\(([^)]+)\)', md)
    if first_img and first_img.group(1) == g['img']:
        md = md.replace(first_img.group(0), '', 1)
    html = md_html(md, drop_h1=False)
    html = re.sub(r'<p><a href="project-%s\.html">[^<]*</a></p>\s*' % re.escape(slug), '', html)
    # this image no longer loads on the live site; drop it and its credit line
    html = re.sub(r'<p><img[^>]*SA-Seed-Conservation-Centre\.jpg[^>]*>\s*(<em>Photo credit: SA Seed Conservation Centre</em>)?</p>\s*', '', html)
    body = NL.join([
        photo_hero(g['pillar'], g['title'], g['lede'],
                   crumbs(('Projects', 'projects.html'), (g['title'], '')), g['img']).replace(
            '    <h1>%s</h1>' % g['title'],
            '    <h1>%s</h1>\n    <p class="pj-hero-meta">%s</p>' % (g['title'], g['meta'])),
        '',
        '<section class="sec">',
        '  <div class="cw rv">',
        '    <div class="pj-body prose">',
        html,
        '    </div>',
        '  </div>',
        '</section>',
        '',
        '<section class="pj-back">',
        '  <div class="cw rv">',
        '    <a class="btn-o" href="grants.html">&#8592; All grant programs</a>',
        '  </div>',
        '</section>',
        '',
        DONATE_BAND])
    desc = re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', html)).strip()
    desc = H.escape(desc[:155].rsplit(' ', 1)[0] + '.', quote=True)
    write_page('project-%s.html' % slug, g['title'], desc, body, page_css=PROSE_CSS)
    print('%-44s built' % ('project-%s.html' % slug))


# ---------------------------------------------------------------- grants hub
def grants_hub():
    md = body_md('grants')
    intro = md.split('\n---', 1)[0]
    intro = re.sub(r'^# .*\n', '', intro, count=1, flags=re.M)
    intro_html = md_html(intro, drop_h1=False)
    whg = re.search(r'## \[Wildlife Heroes Grants\][^\n]*\n\n(.+?)\n', md)
    whg_text = whg.group(1).strip() if whg else ''

    def first_para(slug):
        b = body_md(slug, cut=('\n## Latest news on this project', '\n## Related Projects'))
        for para in b.split('\n\n'):
            p = para.strip()
            if p and not p.startswith(('#', '!', '-', '*', '|', '[', 'NSW', 'National')):
                return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p).replace('**', '')
        return ''

    cards = [('project-wildlife-heroes.html', 'Wildlife Heroes Grants', whg_text, U + '2020/11/Gimesy_Douglas_Slider_home.jpg')]
    for slug, g in GRANTS.items():
        cards.append(('project-%s.html' % slug, g['title'], first_para(slug), g['img']))
    card_html = NL.join(
        ('      <a class="gr-card rv%s" href="%s">%s'
         '        <div class="gr-im"><img src="%s" alt="" loading="lazy"></div>%s'
         '        <div class="gr-bd"><h3>%s</h3><p>%s</p><span class="art-link">Find out more</span></div>%s'
         '      </a>') % ('' if i == 0 else ' d%d' % min(i, 3), href, NL, img, NL, t, H.escape(p[:220].rsplit(' ', 1)[0] + ('…' if len(p) > 220 else '')), NL)
        for i, (href, t, p, img) in enumerate(cards))
    css = PROSE_CSS + '''
.gr-g{display:grid;grid-template-columns:repeat(2,1fr);gap:1.6rem;margin-top:2.4rem}
@media(max-width:760px){.gr-g{grid-template-columns:1fr}}
.gr-card{display:flex;flex-direction:column;background:var(--white);border:1px solid var(--rule);text-decoration:none;color:inherit;transition:transform .2s ease,box-shadow .2s ease}
.gr-card:hover{transform:translateY(-3px);box-shadow:0 16px 40px -18px rgba(15,49,50,.25);opacity:1}
.gr-im{aspect-ratio:16/9;overflow:hidden;background:var(--sand)}
.gr-im img{width:100%;height:100%;object-fit:cover}
.gr-bd{padding:1.4rem 1.5rem 1.6rem;display:flex;flex-direction:column;gap:.6rem;flex:1}
.gr-bd h3{font-size:1.15rem;color:var(--euc-deep);margin:0}
.gr-bd p{font-size:.93rem;line-height:1.6;color:var(--char);margin:0;flex:1}
'''
    body = NL.join([
        photo_hero('Grants', 'Environmental and wildlife grants.', '',
                   crumbs(('Get Involved', 'ways-you-can-get-involved.html'), ('Grants', '')),
                   U + '2021/02/tree-planting-PATFM.jpg'),
        '',
        '<section class="sec">',
        '  <div class="cw">',
        '    <div class="prose rv">',
        intro_html,
        '    </div>',
        '    <div class="gr-g">',
        card_html,
        '    </div>',
        '  </div>',
        '</section>',
        '',
        DONATE_BAND])
    write_page('grants.html', 'Conservation Grants in Australia',
               'We offer conservation grants in Australia for projects that protect native habitats, wildlife or cultural heritage.',
               body, page_css=css)
    print('%-44s built (%d cards)' % ('grants.html', len(cards)))


# ---------------------------------------------------------------- PAWS archive
def paws():
    md = body_md('paws-magazine')
    head, issues = md.split('\n---\n', 1) if '\n---\n' in md else (md, '')
    head = re.sub(r'^# .*\n', '', head, count=1, flags=re.M)
    sub = re.search(r'^## (.*)$', head, flags=re.M)
    head = re.sub(r'^## .*\n', '', head, count=1, flags=re.M)
    items = re.findall(r'### (.+?)\n!\[([^\]]*)\]\(([^)]+)\)\n\[Download PDF\]\(([^)]+)\)', issues)
    cards = NL.join(
        ('      <a class="pw-card rv" href="%s" target="_blank" rel="noopener">%s'
         '        <div class="pw-im"><img src="%s" alt="Cover of PAWS Magazine, %s" loading="lazy"></div>%s'
         '        <div class="pw-bd"><h3>%s</h3><span class="art-link">Download PDF</span></div>%s'
         '      </a>') % (pdf, NL, img, H.escape(t.title().replace(' Issue', ' issue')), NL,
                          H.escape(t.title().replace(' Issue', ' issue')), NL)
        for t, alt, img, pdf in items)
    css = PROSE_CSS + '''
.pw-g{display:grid;grid-template-columns:repeat(4,1fr);gap:1.6rem;margin-top:2.6rem}
@media(max-width:980px){.pw-g{grid-template-columns:repeat(3,1fr)}}
@media(max-width:640px){.pw-g{grid-template-columns:repeat(2,1fr);gap:1rem}}
.pw-card{display:flex;flex-direction:column;text-decoration:none;color:inherit;background:var(--white);border:1px solid var(--rule);transition:transform .2s ease,box-shadow .2s ease}
.pw-card:hover{transform:translateY(-3px);box-shadow:0 16px 40px -18px rgba(15,49,50,.25);opacity:1}
.pw-im{aspect-ratio:3/4;overflow:hidden;background:var(--sand)}
.pw-im img{width:100%;height:100%;object-fit:cover;display:block}
.pw-bd{padding:1rem 1.1rem 1.2rem;display:flex;flex-direction:column;gap:.4rem}
.pw-bd h3{font-size:1rem;margin:0;color:var(--euc-deep)}
'''
    body = NL.join([
        photo_hero('Newsletter archive', 'PAWS Magazine.', H.escape(sub.group(1)) if sub else '',
                   crumbs(('News', 'articles.html'), ('PAWS Magazine', '')),
                   U + '2021/01/Spring-PAWS-Magazine-2020.png'),
        '',
        '<section class="sec">',
        '  <div class="cw">',
        '    <div class="prose rv">',
        md_html(head, drop_h1=False),
        '    </div>',
        '    <div class="pw-g">',
        cards,
        '    </div>',
        '  </div>',
        '</section>'])
    write_page('paws-magazine.html', 'PAWS Magazine',
               'Read past issues of PAWS Magazine, with updates from conservation projects funded by our partners and supporters.',
               body, page_css=css)
    print('%-44s built (%d issues)' % ('paws-magazine.html', len(items)))


# ---------------------------------------------------------------- eBook page
def ebook():
    md = body_md('mitigating-effects-environmental-change', cut=('\n**[FORM',))
    md = re.sub(r'^# .*\n', '', md, count=1, flags=re.M)
    sub = re.search(r'^## (.*)$', md, flags=re.M)
    md = re.sub(r'^## .*\n', '', md, count=1, flags=re.M)
    cover = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', md)
    md = md.replace(cover.group(0), '') if cover else md
    img = U + '2023/05/FNP1009_e-book_thumbnail_shadow.jpg'
    alt = cover.group(1) if cover else ''
    css = PROSE_CSS + '''
.eb-g{display:grid;grid-template-columns:1.2fr .8fr;gap:3.5rem;align-items:start}
@media(max-width:860px){.eb-g{grid-template-columns:1fr;gap:2rem}}
.eb-cover img{width:100%;max-width:420px;height:auto;display:block;margin:0 auto}
.eb-form{background:var(--sand);padding:2rem;margin-top:2.4rem}
.eb-form h3{margin:0 0 .6rem;color:var(--euc-deep)}
.eb-form p{margin:0;font-size:.95rem;color:var(--char)}
'''
    body = NL.join([
        photo_hero('Free eBook', 'Mitigating the effects of environmental change on Australia&rsquo;s fragile ecosystem.',
                   H.escape(sub.group(1)) if sub else '',
                   crumbs(('News', 'articles.html'), ('eBook', '')),
                   U + '2021/02/Alpine-Ash-forest-regrowth-KNP.jpg'),
        '',
        '<section class="sec">',
        '  <div class="cw eb-g">',
        '    <div class="prose rv">',
        md_html(md, drop_h1=False),
        '      <div class="eb-form" id="download">',
        '        <h3>Download the eBook</h3>',
        '        <div class="port-note"><strong>Form still to connect:</strong> the live page uses a WordPress Formidable form '
        '(form 17, "ebooksubmission": first name, last name, email). Add it in WordPress, or give us a HubSpot form ID for the static build.</div>',
        '        <p>By submitting the form, you agree to receive email updates about FNPW&rsquo;s work from time to time.</p>',
        '      </div>',
        '    </div>',
        '    <figure class="eb-cover rv d1"><img src="%s" alt="%s" loading="lazy"></figure>' % (img, H.escape(alt)),
        '  </div>',
        '</section>'])
    write_page('mitigating-effects-environmental-change.html', 'Mitigating the effects of environmental change eBook',
               'Download our free eBook on collaborative strategies to reduce the impacts of environmental change on Australia&rsquo;s ecosystems.',
               body, page_css=css)
    print('%-44s built' % 'mitigating-effects-environmental-change.html')


# ---------------------------------------------------------------- newsletter thank-you
def newsletter_thanks():
    body = NL.join([
        '<section class="sec" style="padding:7rem 0 6rem;background:var(--sand)">',
        '  <div class="cw rv" style="max-width:720px;text-align:center">',
        '    <span class="ey" style="justify-content:center">Newsletter</span>',
        '    <h1 style="margin:1rem 0 1.2rem">Thank you for signing up.</h1>',
        '    <p class="lede" style="margin:0 auto 2rem">Thank You For Signing Up and Supporting Australia Parks and Wildlife.</p>',
        '    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">'
        '<a class="btn-p" href="articles.html">Read our latest stories</a><a class="btn-o" href="projects.html">See our projects</a></div>',
        '  </div>',
        '</section>'])
    write_page('newsletter-thank-you.html', 'Thank you for signing up',
               'Thank you for signing up to our newsletter.', body)
    print('%-44s built' % 'newsletter-thank-you.html')


# ---------------------------------------------------------------- FAQ tax group
def faq_tax():
    f = 'faqs.html'
    t = open(f, encoding='utf-8').read()
    if 'id="tax"' in t:
        print('faqs.html: tax group already present'); return
    md = body_md('tax-deductible-charity-donation')
    md = re.sub(r'^# .*\n', '', md, count=1, flags=re.M)
    md = re.sub(r'^\[Make a donation[^\n]*\n|^\[Scroll Down\][^\n]*\n', '', md, flags=re.M)
    parts = re.split(r'^### ', md, flags=re.M)
    intro, qas = parts[0].strip(), parts[1:]
    items = []
    for qa in qas:
        q, a = qa.split('\n', 1)
        items.append('<details class="fq"><summary>%s</summary><div class="fq-a">%s</div></details>'
                     % (H.escape(q.strip()), md_html(a.strip(), drop_h1=False).replace(NL, '')))
    intro_html = md_html(intro, drop_h1=False).replace('<p>', '<p class="fq-intro">')
    grp = ('      <div class="fq-grp rv" id="tax">%s        <h2>Tax and your donation</h2>%s        %s%s        %s%s      </div>%s'
           % (NL, NL, intro_html.replace(NL, ''), NL, ''.join(items), NL, NL))
    anchor = '      <div class="fq-grp rv" id="receipts">'
    if anchor not in t:
        raise SystemExit('faqs.html: receipts group not found')
    t = t.replace(anchor, grp + anchor, 1)
    t = t.replace('<a href="#receipts">', '<a href="#tax">Tax and your donation</a><a href="#receipts">', 1)
    if '.fq-intro{' not in t:
        t = t.replace('</style>', '.fq-intro{font-size:.98rem;line-height:1.7;color:var(--char);margin:0 0 1rem;max-width:68ch}\n</style>', 1)
    open(f, 'w', encoding='utf-8').write(t)
    print('faqs.html: tax group added (%d questions)' % len(items))


# ---------------------------------------------------------------- QLD fragment
def qld_fragment():
    md = open(SRC + 'brisbane.md', encoding='utf-8').read()
    main = md.split('## Main content (verbatim, in order)', 1)[1]
    main = main.split('\n## FAQs', 1)[0]
    main = re.sub(r'^# .*\n', '', main.strip() + NL, count=1, flags=re.M)
    html = md_html(main, drop_h1=False)
    frag = NL.join([
        '<section class="sec vs-site">',
        '  <div class="cw">',
        '    <div class="prose rv">',
        html,
        '    </div>',
        '  </div>',
        '</section>'])
    open(SRC + 'qld-daisy-hill.html', 'w', encoding='utf-8').write(frag + NL)
    print('data/live-port/qld-daisy-hill.html written')


# ---------------------------------------------------------------- blog entries
def md_blocks(md, story_heading=None):
    """Harvested markdown to the article block model (see ARTICLES.md)."""
    blocks, cur = [], {'type': 'lead', 'flow': []}

    def inline(s):
        s = H.escape(s.strip(), quote=False)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![*\w])\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                      lambda m: '<a href="%s">%s</a>' % (local_link(m.group(2)), m.group(1)), s)

    def push():
        if cur['flow'] or cur.get('img'):
            blocks.append(dict(cur))

    lines = md.strip().split(NL)
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln:
            i += 1; continue
        hm = re.match(r'^#{2,5} (.*)$', ln)
        im = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', ln)
        if hm:
            push()
            head = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', hm.group(1)).strip()
            cur = {'type': 'story' if story_heading and head.startswith(story_heading) else 'text',
                   'flow': [{'h': inline(head)}]}
        elif im:
            cap = ''
            if i + 1 < len(lines) and re.match(r'^\*[^*].*\*$', lines[i + 1].strip()):
                cap = lines[i + 1].strip().strip('*'); i += 1
            if cur['type'] in ('text', 'story') and len(cur['flow']) == 1 and 'h' in cur['flow'][0] and cur['type'] == 'text':
                cur = {'type': 'band', 'heading': cur['flow'][0]['h'], 'img': im.group(2),
                       'alt': im.group(1), 'caption': cap, 'flow': []}
            else:
                push()
                blocks.append({'type': 'wide', 'img': im.group(2), 'alt': im.group(1), 'caption': cap})
                cur = {'type': 'text', 'flow': []}
        elif ln.startswith('- ') or re.match(r'^\d+\. ', ln):
            key = 'ul' if ln.startswith('- ') else 'ol'
            items = []
            while i < len(lines) and (lines[i].startswith('- ') or re.match(r'^\d+\. ', lines[i])):
                items.append(inline(re.sub(r'^(- |\d+\. )', '', lines[i]))); i += 1
            cur['flow'].append({key: items}); continue
        elif ln.startswith('[AUDIO EMBED'):
            src = re.search(r'src="([^"]+)"', ln).group(1)
            cur['flow'].append({'p': '<iframe src="%s" title="Podcast: One Animal at a Time, Koalas" '
                                     'loading="lazy" style="width:100%%;max-width:420px;height:420px;border:0" '
                                     'allow="autoplay; clipboard-write"></iframe>' % src})
        else:
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^(#|!\[|- |\d+\. |\[AUDIO)', lines[i + 1]):
                para.append(lines[i + 1].strip()); i += 1
            cur['flow'].append({'p': inline(' '.join(para))})
        i += 1
    push()
    return blocks


def articles():
    arts = json.load(open('data/articles.json', encoding='utf-8'))
    have = {a['slug'] for a in arts}
    new = []

    # 1. The number almost no one publishes (Sep 2026)
    if 'the-number-almost-no-one-publishes' not in have:
        md = body_md('the-number-almost-no-one-publishes', cut=('\n#### [Bring Back the Bush]',))
        new.append({
            'slug': 'the-number-almost-no-one-publishes',
            'title': 'The number almost no one publishes',
            'eyebrow': 'Story', 'date': 'September 2026', 'place': '',
            'standfirst': 'Trees planted is an easy number to produce and a difficult one to stand behind.',
            'hero': U + '2026/09/55438801356_d02802b757_o-scaled-e1790059797143-1024x502.jpg',
            'hero_alt': '',
            'description': 'A tree planted is not the same as a tree that lived. Why we have partnered with veritree to plant and verify 100,000 native trees across the Yarra Valley, South Gippsland and Hindmarsh Valley.',
            'credit': '', 'pillar': 'heal',
            'blocks': md_blocks(md, story_heading='The part that doesn'),
        })

    # 2. Koala facts (was /koala-facts/)
    if 'koala-facts' not in have:
        md = body_md('koala-facts', cut=('\n[Donate Today]',))
        tail = body_md('koala-facts').split('## One Animal at a Time', 1)
        md = md + NL + ('## One Animal at a Time' + tail[1].split('\n---')[0] if len(tail) > 1 else '')
        md = re.sub(r'^# .*\n', '', md, count=1, flags=re.M)
        md = md.replace('koalas-facts-300x212.png', 'koalas-facts.png')
        new.append({
            'slug': 'koala-facts',
            'title': 'Exploring koala facts: unveiling the secrets of Australia’s iconic marsupials',
            'eyebrow': 'Story', 'date': 'August 2023', 'place': '',
            'standfirst': 'Koalas are more than just cuddly creatures. They are fascinating and complex inhabitants of Australia’s eucalypt forests.',
            'hero': U + '2023/08/koala-fun-facts.png', 'hero_alt': '',
            'description': 'Nine koala facts, from fussy eating and hydration to breeding calls, the threats koalas face and simple ways you can help protect them.',
            'credit': '', 'pillar': 'species',
            'blocks': md_blocks(md),
        })

    # 3. Biodiversity Month (was /biodiversity-month/)
    if 'biodiversity-month' not in have:
        md = body_md('biodiversity-month', cut=('\n[DONATE TODAY]',))
        md = re.sub(r'^## Biodiversity Month.*\n', '', md, count=1, flags=re.M)
        md = re.sub(r'^\[Donate to protect biodiversity\][^\n]*\n', '', md, flags=re.M)
        new.append({
            'slug': 'biodiversity-month',
            'title': 'Biodiversity Month: celebrating life’s rich diversity',
            'eyebrow': 'Story', 'date': 'September 2023', 'place': '',
            'standfirst': 'Every September, Biodiversity Month highlights why we must protect diverse ecosystems.',
            'hero': U + '2023/08/gondwana-rainforest.png', 'hero_alt': '',
            'description': 'Why biodiversity matters, Australia’s two global biodiversity hotspots, and how everyone can help protect the species that live nowhere else.',
            'credit': '', 'pillar': 'species',
            'blocks': md_blocks(md),
        })

    if new:
        arts = new + arts
        json.dump(arts, open('data/articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('articles.json: %d added (%s)' % (len(new), ', '.join(a['slug'] for a in new)))


if __name__ == '__main__':
    legal('privacy-policy.html', 'privacy-policy')
    legal('terms-and-conditions.html', 'terms-and-conditions')
    for s, g in GRANTS.items():
        grant_page(s, g)
    grants_hub()
    paws()
    ebook()
    newsletter_thanks()
    faq_tax()
    qld_fragment()
    articles()
