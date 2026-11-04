#!/usr/bin/env python3
"""Head metadata, structured data and site-level files (WP7).

    python3 tools/meta.py            # rewrite the <head> metadata of every page
    python3 tools/meta.py about.html # one page
    python3 tools/meta.py --site     # pages plus robots.txt, sitemap.xml, feed.xml, llms*.txt

Every page gets, between <!-- @meta --> and <!-- /@meta --> in its <head>: the
<title>, meta description, robots (kept where a page already had noindex),
canonical, Open Graph and Twitter tags, icon links, the RSS link and the
JSON-LD blocks (Organization on every page, WebSite on the home page,
BreadcrumbList where a breadcrumb nav exists, NewsArticle / Project /
AboutPage / Report per template). Generators call apply() from
site_lib.write_page, so a regenerated page comes out with its head complete.
Hand-written overrides for titles and descriptions live in data/meta.json.

SITE_URL is the single switch between the GitHub Pages host used today and
the fnpw.org.au host the site will launch on. WP_PATHS switches the page
paths from the static .html files to the WordPress permalinks.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Switches
# ---------------------------------------------------------------------------
SITE_URL = 'https://elyciap.github.io/fnpw-website-2026/'   # launch: 'https://fnpw.org.au/'
WP_PATHS = False   # True once WordPress serves the pages: /project/<slug>/, /<slug>/, /

SITE_NAME = 'Foundation for National Parks & Wildlife'
SHORT_NAME = 'FNPW'
LOCALE = 'en_AU'
ORG_ID = SITE_URL + '#organization'
WEBSITE_ID = SITE_URL + '#website'
LOGO = 'assets/img/fnpw-logo.png'
LOGO_W, LOGO_H = 900, 246
OG_DEFAULT = 'assets/img/og-default.jpg'
SAME_AS = [
    'https://www.facebook.com/fnpwaustralia/',
    'https://www.instagram.com/fnpwaustralia/',
    'https://au.linkedin.com/company/foundation-for-national-parks-%26-wildlife',
]
PILLAR_NAMES = {'parks': 'Growing National Parks', 'species': 'Saving Species',
                'heal': 'Healing the Land', 'healing': 'Healing the Land'}
STATE_NAMES = {'NSW': 'New South Wales', 'VIC': 'Victoria', 'QLD': 'Queensland',
               'SA': 'South Australia', 'WA': 'Western Australia', 'TAS': 'Tasmania',
               'NT': 'Northern Territory', 'ACT': 'Australian Capital Territory'}
TITLE_MAX = 53          # page part; " | FNPW" brings the whole title to 60
STAGE = int(os.environ.get('META_STAGE', '3'))   # 1 titles+descriptions, 2 +canonical/social, 3 +JSON-LD (default)
NOINDEX_ALWAYS = {'search.html', '404.html'}
SKIP_FILES = set()      # pages never touched by this tool

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def _load(name, default):
    p = os.path.join(ROOT, 'data', name)
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)

ARTICLES = {a['slug']: a for a in _load('articles.json', [])}
PROJECTS = {p['slug']: p for p in _load('projects.json', [])}
OVERRIDES = _load('meta.json', {})

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
          'august', 'september', 'october', 'november', 'december']


def iso_day(d):
    """'2023-07-17' stays; 'July 2023' -> ('2023-07-01', False). Returns (iso, day_known)."""
    d = (d or '').strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', d)
    if m:
        return d, True
    y = re.search(r'(19|20)\d{2}', d)
    if not y:
        return '', False
    low = d.lower()
    for i, mon in enumerate(MONTHS):
        if mon in low:
            return '%s-%02d-01' % (y.group(0), i + 1), False
    return y.group(0) + '-01-01', False


# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------
def page_path(fname):
    """Site-relative path of a page, GitHub .html today, WordPress permalink later."""
    if fname == 'index.html':
        return ''
    if not WP_PATHS:
        return fname
    slug = fname[:-5]
    if slug.startswith('project-'):
        return 'project/%s/' % slug[len('project-'):]
    if slug.startswith('article-'):
        return '%s/' % slug[len('article-'):]
    return '%s/' % slug


def page_url(fname):
    return SITE_URL + page_path(fname)


def abs_url(src):
    """Absolute URL for an asset reference found in a page."""
    if not src:
        return ''
    if re.match(r'^https?://', src):
        return src
    if src.startswith('//'):
        return 'https:' + src
    return SITE_URL + src.lstrip('./')


def search_template():
    return (SITE_URL + '?s={search_term_string}') if WP_PATHS else (SITE_URL + 'search.html?q={search_term_string}')


# ---------------------------------------------------------------------------
# Page parsing
# ---------------------------------------------------------------------------
def text(frag):
    return html.unescape(re.sub(r'<[^>]+>', '', frag or '')).strip()


def attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % name, tag)
    return html.unescape(m.group(1)) if m else ''


def get_h1(doc):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', doc, re.S)
    return re.sub(r'\s+', ' ', text(m.group(1))) if m else ''


def existing_title_part(doc):
    m = re.search(r'<title>(.*?)</title>', doc, re.S)
    t = text(m.group(1)) if m else ''
    return re.sub(r'\s*\|\s*(Foundation for National Parks & Wildlife|FNPW)\s*$', '', t).strip()


def existing_description(doc):
    m = re.search(r'<meta name="description" content="([^"]*)"', doc)
    return html.unescape(m.group(1)).strip() if m else ''


def existing_noindex(doc):
    return bool(re.search(r'<meta name="robots" content="[^"]*noindex', doc))


def hero_image(doc, fname=''):
    """First real photograph inside the page's hero; for an article with the flat
    header, its feature image from data/articles.json when the body shows it; else ''."""
    img = _hero_image(doc)
    if not img and fname.startswith('article-'):
        a = ARTICLES.get(fname[len('article-'):-5], {})
        if a.get('hero') and a['hero'] in doc:
            img = a['hero']
    return img


def _hero_image(doc):
    i = re.search(r'class="[^"]*\bhero\b[^"]*"|class="[^"]*-hero\b[^"]*"', doc)
    if not i:
        return ''
    seg = doc[i.start():]
    end = re.search(r'</section>|</header>', seg)
    seg = seg[:end.start()] if end else seg[:4000]
    for tag in re.findall(r'<img[^>]+>', seg):
        src = attr(tag, 'src')
        if not src or re.search(r'logo|badge|icon|\.svg$', src, re.I):
            continue
        return src
    # heroes that carry their photograph as an inline background-image
    m = re.search(r'''url\(\s*['"]?([^'")]+)['"]?\s*\)''', seg)
    if m and not re.search(r'logo|badge|icon|\.svg$', m.group(1), re.I):
        return m.group(1)
    return ''


def breadcrumb(doc):
    """[(label, href-or-None), ...] from the page's breadcrumb nav, last item is the page."""
    m = re.search(r'<nav[^>]*aria-label="Breadcrumb"[^>]*>(.*?)</nav>', doc, re.S)
    if not m:
        return []
    inner = m.group(1)
    items = []
    for a in re.finditer(r'<a href="([^"]+)">(.*?)</a>', inner, re.S):
        items.append((text(a.group(2)), a.group(1)))
    tail = re.sub(r'<a href="[^"]+">.*?</a>', '', inner, flags=re.S)
    tail = text(re.sub(r'<span[^>]*>.*?</span>', ' ', tail, flags=re.S))
    tail = tail.strip(' /')
    if tail:
        items.append((tail, None))
    return items


def pillar_label(doc):
    """The pillar name shown in the hero eyebrow, if any."""
    i = re.search(r'class="[^"]*\bhero\b[^"]*"', doc)
    seg = doc[i.start():i.start() + 3000] if i else doc[:0]
    for m in re.finditer(r'<span class="ey">(.*?)</span>', seg):
        lab = text(m.group(1))
        if lab in PILLAR_NAMES.values():
            return lab
    return ''


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


# ---------------------------------------------------------------------------
# Title and description rules
# ---------------------------------------------------------------------------
def shorten_title(t, limit=TITLE_MAX):
    if len(t) <= limit:
        return t
    for sep in (': ', ' | ', ' – ', ' - ', ', ', ' and ', ' for ', ' to ', ' in ', ' of '):
        i = t.rfind(sep, 0, limit + 1)
        if i >= 20:
            return t[:i].rstrip(' ,:-')
    i = t.rfind(' ', 0, limit + 1)
    return t[:i].rstrip(' ,:-') if i > 0 else t


def title_for(fname, doc):
    o = OVERRIDES.get(fname, {})
    if fname == 'index.html':
        return o.get('title') or SITE_NAME
    part = o.get('title') or existing_title_part(doc) or get_h1(doc)
    part = re.sub(r'\s+', ' ', part).strip().replace(' | ', ': ')
    part = shorten_title(part)
    return '%s | %s' % (part, SHORT_NAME)


def description_for(fname, doc):
    o = OVERRIDES.get(fname, {})
    d = o.get('description') or existing_description(doc)
    return re.sub(r'\s+', ' ', d).strip()


# ---------------------------------------------------------------------------
# JSON-LD builders
# ---------------------------------------------------------------------------
def org_full():
    return {
        '@type': 'Organization',
        '@id': ORG_ID,
        'name': SITE_NAME,
        'legalName': SITE_NAME,
        'alternateName': SHORT_NAME,
        'url': SITE_URL,
        'logo': {'@type': 'ImageObject', 'url': abs_url(LOGO), 'width': LOGO_W, 'height': LOGO_H},
        'taxID': '90 107 744 771',
        'nonprofitStatus': 'NonprofitType',
        'foundingDate': '1970',
        'sameAs': SAME_AS,
        'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer service',
                         'telephone': '+61 1800 898 626', 'email': 'fnpw@fnpw.org.au',
                         'areaServed': 'AU', 'availableLanguage': 'en'},
        'address': {'@type': 'PostalAddress', 'addressLocality': 'Sydney',
                    'addressRegion': 'NSW', 'addressCountry': 'AU'},
    }


def org_publisher():
    return {'@type': 'Organization', '@id': ORG_ID, 'name': SITE_NAME,
            'logo': {'@type': 'ImageObject', 'url': abs_url(LOGO), 'width': LOGO_W, 'height': LOGO_H}}


def website_ld():
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': WEBSITE_ID,
        'url': SITE_URL,
        'name': SITE_NAME,
        'publisher': {'@id': ORG_ID},
        'inLanguage': 'en-AU',
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {'@type': 'EntryPoint', 'urlTemplate': search_template()},
            'query-input': 'required name=search_term_string',
        },
    }


def breadcrumb_ld(fname, crumbs):
    items = []
    for n, (label, href) in enumerate(crumbs, 1):
        it = {'@type': 'ListItem', 'position': n, 'name': label}
        it['item'] = page_url(href) if href else page_url(fname)
        items.append(it)
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}


def article_ld(fname, doc, title, desc, img):
    slug = fname[len('article-'):-5]
    a = ARTICLES.get(slug, {})
    date_src = a.get('date') or (re.search(r'class="ed-meta">([^<&]+)', doc) or [None, ''])[1]
    date, day_known = iso_day(date_src)
    ld = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': get_h1(doc) or title,
        'description': desc,
        'image': [abs_url(img)] if img else [abs_url(OG_DEFAULT)],
        'author': {'@type': 'Organization', 'name': SITE_NAME},
        'publisher': org_publisher(),
        'mainEntityOfPage': {'@type': 'WebPage', '@id': page_url(fname)},
        'url': page_url(fname),
        'inLanguage': 'en-AU',
    }
    if date:
        ld['datePublished'] = date
        ld['dateModified'] = date
    sec = pillar_label(doc)
    if sec:
        ld['articleSection'] = sec
    return ld, date, day_known


ORG_CREDIT_PATTERNS = [
    # (regex over the credit line, role, group -> organisation names)
    (r'[Ss]upported by (?:the )?([^.]+?)(?: through its [^.]+)?\.', 'sponsor'),
    (r'Funded through FNPW', 'funder-fnpw'),
]


def credit_orgs(doc):
    """funder / sponsor organisations named explicitly in the project credit line."""
    m = re.search(r'<section class="sec pj-credit">(.*?)</section>', doc, re.S)
    if not m:
        return {}
    line = re.sub(r'\s+', ' ', text(m.group(1)))
    out = {}
    for pat, role in ORG_CREDIT_PATTERNS:
        mm = re.search(pat, line)
        if not mm:
            continue
        if role == 'funder-fnpw':
            out.setdefault('funder', []).append({'@type': 'Organization', '@id': ORG_ID, 'name': SITE_NAME})
            continue
        names = [n.strip() for n in re.split(r',\s*| and ', mm.group(1)) if n.strip()]
        for n in names:
            out.setdefault(role, []).append({'@type': 'Organization', 'name': n})
    return out


def project_ld(fname, doc, title, desc, img):
    slug = fname[len('project-'):-5]
    p = PROJECTS.get(slug, {})
    ld = {
        '@context': 'https://schema.org',
        '@type': 'Project',
        'name': get_h1(doc) or title,
        'description': desc,
        'url': page_url(fname),
        'parentOrganization': {'@id': ORG_ID},
    }
    if img:
        ld['image'] = abs_url(img)
    pil = pillar_label(doc) or PILLAR_NAMES.get(p.get('pillar', ''), '')
    if pil:
        ld['about'] = {'@type': 'Thing', 'name': pil}
    state = p.get('state', '')
    if p.get('on_map') and p.get('lat') is not None and p.get('lon') is not None:
        place = {'@type': 'Place',
                 'geo': {'@type': 'GeoCoordinates', 'latitude': p['lat'], 'longitude': p['lon']}}
        addr = {'@type': 'PostalAddress', 'addressCountry': 'AU'}
        if state and state != 'Australia':
            addr['addressRegion'] = state
        place['address'] = addr
        if state in STATE_NAMES:
            place['name'] = STATE_NAMES[state]
        elif state and state != 'Australia':
            place['name'] = state
        ld['location'] = place
    for role, orgs in credit_orgs(doc).items():
        ld[role] = orgs if len(orgs) > 1 else orgs[0]
    return ld


def about_ld(fname, doc, desc):
    groups = re.findall(r'<div class="tm-g">(.*?)\n</div>', doc, re.S)
    people = []
    for gi, g in enumerate(groups[:2]):
        rel = 'worksFor' if gi == 0 else 'memberOf'
        for card in re.findall(r'<div class="tc rv">(.*?)</div></div></div>', g, re.S):
            name = re.search(r'<div class="tc-n">(.*?)</div>', card)
            role = re.search(r'<div class="tc-r">(.*?)</div>', card)
            if not name:
                continue
            person = {'@type': 'Person', 'name': text(name.group(1))}
            if role:
                person['jobTitle'] = text(role.group(1))
            person[rel] = {'@id': ORG_ID}
            people.append(person)
    graph = [{
        '@type': 'AboutPage',
        '@id': page_url(fname) + '#webpage',
        'url': page_url(fname),
        'name': get_h1(doc),
        'description': desc,
        'about': {'@id': ORG_ID},
        'isPartOf': {'@id': WEBSITE_ID},
        'inLanguage': 'en-AU',
    }] + people
    return {'@context': 'https://schema.org', '@graph': graph}


def reports_ld(doc):
    seen, reports = set(), []
    for m in re.finditer(r'<a class="card rp-c" href="([^"]+\.pdf)"[^>]*>(.*?)</a>', doc, re.S):
        url, body = m.group(1), m.group(2)
        if url in seen:
            continue
        seen.add(url)
        h3 = re.search(r'<h3>(.*?)</h3>', body, re.S)
        name = text(h3.group(1)) if h3 else text(body)
        year = re.search(r'(20\d{2}|19\d{2})', text(body))
        r = {'@type': 'Report', 'name': name, 'url': url, 'encodingFormat': 'application/pdf',
             'publisher': {'@id': ORG_ID}, 'inLanguage': 'en-AU'}
        if year:
            r['datePublished'] = year.group(1)
        reports.append(r)
    if not reports:
        return None
    return {'@context': 'https://schema.org', '@type': 'ItemList',
            'name': 'Reports and publications', 'itemListElement': reports}


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


# ---------------------------------------------------------------------------
# Head block
# ---------------------------------------------------------------------------
def build_head(fname, doc):
    title = title_for(fname, doc)
    desc = description_for(fname, doc)
    noindex = existing_noindex(doc) or fname in NOINDEX_ALWAYS
    img = hero_image(doc, fname)
    og_img = abs_url(img) if img else abs_url(OG_DEFAULT)
    is_article = fname.startswith('article-')
    url = page_url(fname)
    crumbs = breadcrumb(doc)

    lines = ['<!-- @meta -->',
             '<title>%s</title>' % esc(title),
             '<meta name="description" content="%s">' % esc(desc)]
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    if STAGE < 2:
        return '\n'.join(lines + ['<!-- /@meta -->'])
    lines.append('<link rel="canonical" href="%s">' % esc(url))
    og = [('og:type', 'article' if is_article else 'website'),
          ('og:site_name', SITE_NAME), ('og:locale', LOCALE),
          ('og:title', title), ('og:description', desc), ('og:url', url), ('og:image', og_img)]
    if not img:
        og += [('og:image:width', '1200'), ('og:image:height', '630')]
    lds = [{'@context': 'https://schema.org', **org_full()}]
    if fname == 'index.html':
        lds.append(website_ld())
    if crumbs:
        lds.append(breadcrumb_ld(fname, crumbs))
    if is_article:
        ld, date, _ = article_ld(fname, doc, title, desc, img)
        if date:
            og += [('article:published_time', date), ('article:modified_time', date)]
        if ld.get('articleSection'):
            og.append(('article:section', ld['articleSection']))
        lds.append(ld)
    elif fname.startswith('project-'):
        lds.append(project_ld(fname, doc, title, desc, img))
    elif fname == 'about.html':
        lds.append(about_ld(fname, doc, desc))
    elif fname == 'reports.html':
        r = reports_ld(doc)
        if r:
            lds.append(r)
    for k, v in og:
        lines.append('<meta property="%s" content="%s">' % (k, esc(v)))
    for k, v in (('twitter:card', 'summary_large_image'), ('twitter:title', title),
                 ('twitter:description', desc), ('twitter:image', og_img)):
        lines.append('<meta name="%s" content="%s">' % (k, esc(v)))
    lines += ['<link rel="icon" href="favicon.svg" type="image/svg+xml">',
              '<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">',
              '<link rel="apple-touch-icon" href="apple-touch-icon.png">',
              '<link rel="manifest" href="site.webmanifest">',
              '<link rel="alternate" type="application/rss+xml" title="%s: news and stories" href="feed.xml">' % esc(SITE_NAME)]
    if STAGE >= 3:
        for ld in lds:
            lines.append('<script type="application/ld+json">%s</script>' % dumps(ld))
    lines.append('<!-- /@meta -->')
    return '\n'.join(lines)


def strip_old(doc):
    """Remove the tags the block replaces: old title, description, robots, Article JSON-LD."""
    doc = re.sub(r'<!-- @meta -->.*?<!-- /@meta -->\n?', '', doc, count=1, flags=re.S)
    doc = re.sub(r'<title>.*?</title>\n?', '', doc, count=1, flags=re.S)
    doc = re.sub(r'<meta name="description" content="[^"]*">\n?', '', doc, count=1)
    doc = re.sub(r'<meta name="robots" content="[^"]*">\n?', '', doc, count=1)
    # Article JSON-LD emitted by the old generator at the end of the body
    if STAGE >= 3:
        doc = re.sub(r'\n?<script type="application/ld+json">\{"@context": "https://schema.org", "@type": "Article".*?</script>', '', doc, count=1, flags=re.S)
    return doc


def apply(fname, write=True):
    path = os.path.join(ROOT, fname)
    with open(path) as f:
        doc = f.read()
    block = build_head(fname, doc)
    new = strip_old(doc)
    # the block goes where the charset/viewport line ends, before referrer/fonts
    m = re.search(r'<meta charset="UTF-8">[^\n]*\n', new)
    if not m:
        m = re.search(r'<head>\n', new)
    new = new[:m.end()] + block + '\n' + new[m.end():]
    if write and new != doc:
        with open(path, 'w') as f:
            f.write(new)
    return new != doc


def all_pages():
    return sorted(f for f in os.listdir(ROOT) if f.endswith('.html') and f not in SKIP_FILES)


# ---------------------------------------------------------------------------
# Site files
# ---------------------------------------------------------------------------
def is_indexable(fname, doc):
    return not (existing_noindex(doc) or fname in NOINDEX_ALWAYS)


def git_lastmod(fname):
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cI', '--', fname], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        if out:
            return out[:10]
    except Exception:
        pass
    return datetime.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, fname))).isoformat()


def write(name, body):
    with open(os.path.join(ROOT, name), 'w') as f:
        f.write(body)


def sitemap():
    rows = []
    for fname in all_pages():
        doc = open(os.path.join(ROOT, fname)).read()
        if not is_indexable(fname, doc):
            continue
        rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod></url>' % (esc(page_url(fname)), git_lastmod(fname)))
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % '\n'.join(rows))
    return len(rows)


def robots():
    body = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /tools/', 'Disallow: /wp/', 'Disallow: /design/', 'Disallow: /data/',
        'Disallow: /partials/', 'Disallow: /brand-source/', 'Disallow: /Claude%20outputs/',
        'Disallow: /.claude/',
        'Disallow: /*.md$', 'Disallow: /*.docx$', 'Disallow: /*.ai$',
        '',
        'Sitemap: %ssitemap.xml' % SITE_URL,
        ''])
    write('robots.txt', body)


def rfc822(iso):
    d = datetime.datetime.strptime(iso, '%Y-%m-%d').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=10)))
    return d.strftime('%a, %d %b %Y %H:%M:%S +1000')


def feed():
    items = []
    for a in ARTICLES.values():
        date, _ = iso_day(a.get('date', ''))
        if date:
            items.append((date, a))
    items.sort(key=lambda x: x[0], reverse=True)
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
           '<channel>',
           '<title>%s</title>' % esc(SITE_NAME),
           '<link>%s</link>' % esc(SITE_URL),
           '<description>%s</description>' % esc('News and stories from our work growing national parks, saving species and healing the land.'),
           '<language>en-au</language>',
           '<atom:link href="%sfeed.xml" rel="self" type="application/rss+xml"/>' % esc(SITE_URL)]
    for date, a in items[:20]:
        fname = 'article-%s.html' % a['slug']
        url = page_url(fname)
        desc = OVERRIDES.get(fname, {}).get('description') or a.get('description', '')
        out += ['<item>',
                '<title>%s</title>' % esc(a['title']),
                '<link>%s</link>' % esc(url),
                '<guid isPermaLink="true">%s</guid>' % esc(url),
                '<pubDate>%s</pubDate>' % rfc822(date),
                '<description>%s</description>' % esc(desc),
                '</item>']
    out += ['</channel>', '</rss>', '']
    write('feed.xml', '\n'.join(out))
    return min(20, len(items))


KEY_PAGES = [
    ('about.html', 'Who we are, our 55-year story, the executive team and the Board.'),
    ('projects.html', 'Every conservation project we fund, filterable by pillar and state.'),
    ('growing-national-parks.html', 'Land acquisitions and park expansions.'),
    ('saving-species.html', 'Threatened species recovery programs.'),
    ('healing-the-land.html', 'Landscape restoration, nurseries, seedbanks and cultural fire.'),
    ('articles.html', 'News and stories from the field.'),
    ('our-impact.html', 'What your support changed, from our latest Impact Report.'),
    ('reports.html', 'Impact Reports, Year in Review, financial statements and strategy as PDFs.'),
    ('partner-invest.html', 'How businesses, foundations and major donors partner with us.'),
    ('government-partnerships.html', 'How we work with Australian, state and territory governments.'),
    ('bequests.html', 'Gifts in wills, with suggested wording.'),
    ('donate-land.html', 'How to give land to become national park.'),
    ('volunteer.html', 'Corporate volunteering days across five states.'),
    ('workplace-giving.html', 'Regular giving from pre-tax pay.'),
    ('faqs.html', 'Answers on who we are, giving, receipts and getting involved.'),
    ('contact.html', 'How to reach us.'),
]


def llms():
    lines = ['# Foundation for National Parks & Wildlife (FNPW)', '']
    lines += ['> We are an independent Australian conservation charity, founded in 1970, that grows national parks, saves threatened species and heals damaged country. We bring Traditional Custodians, governments, scientists, communities and funders together to protect Australia\'s most important landscapes and wildlife.', '']
    lines += ['- Legal name: Foundation for National Parks & Wildlife. ABN 90 107 744 771. Registered charity and Deductible Gift Recipient.',
              '- Contact: fnpw@fnpw.org.au, 1800 898 626. Head office in Sydney, NSW, Australia.',
              '- Three pillars: Growing National Parks, Saving Species, Healing the Land.',
              '- Tree goal: 9 million trees by 2030, grown through a network of more than 30 community nurseries.', '']
    lines += ['## Key pages', '']
    for fname, blurb in KEY_PAGES:
        if os.path.exists(os.path.join(ROOT, fname)):
            lines.append('- [%s](%s): %s' % (text(existing_title_part(open(os.path.join(ROOT, fname)).read())) or fname, page_url(fname), blurb))
    lines += ['', '## Donations (all giving is handled on Raisely, not on this site)', '',
              '- Donate: https://bush.fnpw.org.au',
              '- Give a Tree: https://gift-a-tree.fnpw.org.au',
              '- Habitat Heroes (monthly giving): https://habitat-heroes.fnpw.org.au', '']
    lines += ['## Data endpoints', '',
              '- Sitemap: %ssitemap.xml' % SITE_URL,
              '- RSS (latest 20 stories): %sfeed.xml' % SITE_URL,
              '- Full text summary of every page: %sllms-full.txt' % SITE_URL,
              '- Structured data: JSON-LD (Organization, WebSite, BreadcrumbList, NewsArticle, Project) in every page head.', '']
    lines += ['## Policies', '',
              '- Privacy policy: %s' % page_url('privacy-policy.html'),
              '- Terms and conditions: %s' % page_url('terms-and-conditions.html'),
              '- Reconciliation Action Plan: %s' % page_url('reconciliation-action-plan.html'),
              '- Please quote statistics only from our published Impact Reports and link back to the source page.', '']
    write('llms.txt', '\n'.join(lines))
    return len(lines)


def excerpt(fname, doc):
    if fname.startswith('article-'):
        a = ARTICLES.get(fname[len('article-'):-5], {})
        return a.get('standfirst', '')
    m = re.search(r'<p class="lede[^"]*"[^>]*>(.*?)</p>', doc, re.S)
    return re.sub(r'\s+', ' ', text(m.group(1))) if m else ''


def llms_full():
    out = ['# Foundation for National Parks & Wildlife: every page', '',
           'Generated from each page\'s heading, meta description and lead paragraph. Canonical host: %s' % SITE_URL, '']
    n = 0
    for fname in all_pages():
        doc = open(os.path.join(ROOT, fname)).read()
        if not is_indexable(fname, doc):
            continue
        h = get_h1(doc) or existing_title_part(doc)
        d = description_for(fname, doc)
        ex = excerpt(fname, doc)
        out += ['## %s' % h, page_url(fname), '']
        if d:
            out.append(d)
        if ex and ex != d:
            out.append(ex)
        out.append('')
        n += 1
    write('llms-full.txt', '\n'.join(out))
    return n


# ---------------------------------------------------------------------------
def main(argv):
    site = '--site' in argv
    pages = [a for a in argv if a.endswith('.html')] or all_pages()
    changed = 0
    for fname in pages:
        if apply(fname):
            changed += 1
    print('meta: %d of %d pages updated' % (changed, len(pages)))
    if site:
        robots()
        print('sitemap.xml: %d urls' % sitemap())
        print('feed.xml: %d items' % feed())
        print('llms.txt: %d lines' % llms())
        print('llms-full.txt: %d pages' % llms_full())


if __name__ == '__main__':
    main(sys.argv[1:])
