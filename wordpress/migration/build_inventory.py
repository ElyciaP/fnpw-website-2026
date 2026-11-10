#!/usr/bin/env python3
"""Repo inventory for the WordPress build (task 1 of the handover).

Run from the repo root:  python3 wordpress/migration/build_inventory.py

Writes wordpress/migration/inventory.md and wordpress/migration/inventory-pages.csv.
Only the part of inventory.md between the @generated markers is rewritten, so the
admin audit findings added by hand under it (task 8) survive a re-run.
Reads the static build only; changes nothing outside wordpress/migration/.
"""
import collections, csv, datetime, glob, json, os, re, subprocess
from urllib.parse import urlparse
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'wordpress', 'migration')
os.chdir(ROOT)

PILLARS = {'growing-national-parks.html', 'saving-species.html', 'healing-the-land.html'}
HUBS = {'projects.html', 'articles.html', 'in-the-news.html', 'reports.html'}
UTIL = {'search.html', '404.html'}
LEGAL = {'privacy-policy.html', 'terms-and-conditions.html', 'corporate-governance.html'}

def page_type(f):
    if f == 'index.html': return 'home'
    if f in PILLARS: return 'pillar'
    if f.startswith('project-') and f.endswith('-grants.html'): return 'grant programme'
    if f.startswith('project-'): return 'project'
    if f.startswith('article-'): return 'article'
    if f in HUBS: return 'hub'
    if f in UTIL: return 'utility'
    if f in LEGAL: return 'legal'
    if 'thank-you' in f: return 'thank-you'
    if f.startswith('corporate-volunteering-'): return 'volunteering state'
    return 'content'

# Interactive components: (name, test on page source, how it works, proposed WordPress treatment)
COMPONENTS = [
    ('Project map', lambda s, f: 'IMAP=' in s, 'Inline IMAP data (from data/projects.json via tools/gen_map.py) plus inline map script; pins open project cards',
     'Custom block fnpw/project-map (block.json + render.php), reads a JSON file generated at import, live project data after launch'),
    ('Project grid with pillar filter', lambda s, f: "getElementById('pgrid')" in s, 'Inline script filters #pgrid tiles by state and type',
     'Custom block fnpw/project-grid, server-rendered tiles, filter script enqueued only where used'),
    ('Projects page tiles and filters', lambda s, f: f == 'projects.html' and 'const PD=' in s, 'Inline script on projects.html (popup data retired Nov 2026, cards link to project pages)',
     'Part of fnpw/project-grid'),
    ('Stories filter, sort and paging', lambda s, f: 'assets/js/articles.js' in s, 'assets/js/articles.js over .art-grid tiles',
     'Core Query Loop for posts plus a small filter script, or a custom block if the sort must stay client-side'),
    ('Article reading bar', lambda s, f: "querySelector('.ed')" in s, 'Inline script adds a progress bar to the .ed article body',
     'One script in the single post template, not per post'),
    ('Volunteer sites map', lambda s, f: '.vm-pin' in s, 'Inline script toggles state map pins and the site list',
     'Custom block fnpw/volunteer-map with data/volunteer-sites.json'),
    ('Where-we-run state tabs', lambda s, f: 'Where we run: one panel' in s, 'Inline tab switcher on volunteer.html',
     'Custom block fnpw/tabs (shared with the other tab sets)'),
    ('Photo carousel', lambda s, f: 'assets/js/carousel.js' in s, 'assets/js/carousel.js, scroll-snap track #volTrack, auto-advance',
     'Pattern with carousel.js enqueued where the pattern is used'),
    ('Photo gallery (pages of six)', lambda s, f: 'assets/js/gallery.js' in s, 'assets/js/gallery.js, scroll-snap track',
     'Pattern with gallery.js enqueued on use'),
    ('Project slider (homepage)', lambda s, f: 'data-fls' in s, 'Inline script on [data-fls] with previous and next buttons',
     'Custom block fnpw/project-slider, or a pattern plus script'),
    ('Tabs (government partnerships)', lambda s, f: "querySelectorAll('.jt')" in s, 'Inline tab switcher .jt', 'fnpw/tabs'),
    ('Tabs (partner and invest)', lambda s, f: '.piw [role="tablist"]' in s, 'Inline ARIA tablist', 'fnpw/tabs'),
    ('Read more toggles', lambda s, f: ('.jd-more' in s or '.tc-more' in s), 'Inline expanders (.jd-more, .tc-more on bios)',
     'Core Details block where the markup allows, else a small shared script'),
    ('Load more list', lambda s, f: "getElementById('lmq')" in s, 'Inline load-more on #lmq', 'Shared theme script, enqueued on use'),
    ('Timeline rail (drag to scroll)', lambda s, f: "getElementById('htRail')" in s, 'Inline drag-scroll on #htRail', 'Pattern plus small script'),
    ('Card arrows', lambda s, f: "querySelectorAll('.abs-arr')" in s, 'Inline scroll buttons on .abs-arr', 'Pattern plus small script'),
    ('Reports filter', lambda s, f: '#rpf .fp' in s, 'Inline filter buttons #rpf', 'Custom block, or Query Loop with a taxonomy filter'),
    ('Site search (client-side index)', lambda s, f: 'const IDX' in s, 'Inline 28 KB index of every page, searched in the browser',
     'Retired: the WordPress search template replaces it'),
    ('Section snap', lambda s, f: 'assets/js/snap.js' in s, 'assets/js/snap.js settles onto section edges', 'Enqueue snap.js on the About page only'),
    ('Accordions (details)', lambda s, f: '<details' in s, 'Native details and summary', 'Core Details block'),
    ('Animated counters', lambda s, f: 'data-count=' in s, 'main.js animates [data-count]', 'Keep in main.js; data-count carried on the converted markup'),
    ('HubSpot form embed', lambda s, f: 'hsforms.net' in s, 'HubSpot embed script (portal 441704788, region ap1)',
     'Keep the HubSpot embed in a Custom HTML block or small fnpw/hubspot-form block (live pages use the same HubSpot forms)'),
    ('Video embed', lambda s, f: 'youtube' in s and '<iframe' in s, 'YouTube no-cookie iframe', 'Core Embed block'),
    ('Podcast embed', lambda s, f: 'omny.fm' in s, 'Omny iframe', 'Core Embed or Custom HTML'),
    ('Google map embed', lambda s, f: 'google.com/maps' in s, 'Google Maps iframe', 'Custom HTML block'),
]

def git(*a):
    try: return subprocess.check_output(['git', '--no-optional-locks', *a], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception: return ''

def kb(n): return f'{n/1024:.0f} KB'

css = open('assets/css/global.css', encoding='utf-8').read()
tokens = []
for m in re.finditer(r':root\s*\{(.*?)\}', css, re.S):
    tokens += re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', m.group(1))
tokdict = dict(tokens)

files = sorted(glob.glob('*.html'))
rows, sec_pages, sec_where = [], collections.defaultdict(set), {}
comp_pages = collections.defaultdict(list)
hs_forms = collections.defaultdict(set)
img_hosts = collections.Counter()
seq_counter = {'project': collections.Counter(), 'article': collections.Counter(), 'grant programme': collections.Counter()}
shared_js = collections.defaultdict(list)

for f in files:
    raw = open(f, encoding='utf-8').read()
    soup = BeautifulSoup(raw, 'html.parser')
    t = page_type(f)
    title = (soup.title.string or '').split(' | ')[0].strip() if soup.title else ''
    h1 = soup.find('h1')
    h1t = re.sub(r'\s+', ' ', h1.get_text(' ', strip=True)) if h1 else ''
    main = soup.find('main')
    seq = []
    if main:
        for ch in main.find_all(recursive=False):
            cl = [c for c in (ch.get('class') or []) if c != 'rv']
            seq.append(ch.name + ('.' + '.'.join(cl) if cl else ''))
            for c in cl: sec_pages[c].add(f)
    if t in seq_counter: seq_counter[t][' > '.join(seq)] += 1
    page_css = ''.join(st.get_text() for st in soup.find_all('style'))
    for c in set(c for s in seq for c in s.split('.')[1:]):
        where = sec_where.setdefault(c, set())
        if re.search(r'\.' + re.escape(c) + r'(?![\w-])', css): where.add('global.css')
        if re.search(r'\.' + re.escape(c) + r'(?![\w-])', page_css): where.add('page')
    js_inline = sum(len(sc.string or '') for sc in soup.find_all('script') if not sc.get('src') and sc.get('type') != 'application/ld+json')
    for sc in soup.find_all('script', src=True):
        shared_js[sc['src'].split('?')[0]].append(f)
    comps = []
    for name, test, _, _ in COMPONENTS:
        if test(raw, f):
            comps.append(name); comp_pages[name].append(f)
    for fid in re.findall(r'data-form-id="([^"]+)"', raw) + re.findall(r'formId:\s*["\']([0-9a-f-]{36})', raw):
        hs_forms[fid].add(f)
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', raw) + re.findall(r'url\((?:&quot;|["\'])?(https?://[^)"\'&]+)', raw)
    local = sum(1 for i in imgs if not urlparse(i).netloc)
    live = sum(1 for i in imgs if urlparse(i).netloc == 'fnpw.org.au')
    for i in imgs: img_hosts[urlparse(i).netloc or '(local assets/)'] += 1
    words = len((main.get_text(' ', strip=True) if main else '').split())
    rows.append(dict(file=f, type=t, title=title, h1=h1t, main_sections=' > '.join(seq), components='; '.join(comps),
                     hubspot='yes' if 'hsforms' in raw else '', images_local=local, images_live_uploads=live,
                     images_other=len(imgs) - local - live, page_css_bytes=len(page_css), inline_js_bytes=js_inline, words=words))

with open(os.path.join(OUT, 'inventory-pages.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------------------------------------------------------------- markdown
types = collections.Counter(r['type'] for r in rows)
commit = git('rev-parse', '--short', 'HEAD'); cdate = git('log', '-1', '--format=%ad', '--date=short')
other_hosts = sum(n for h, n in img_hosts.items() if h not in ('fnpw.org.au', '(local assets/)'))
L = []; A = L.append
A('<!-- @generated: written by build_inventory.py; edit the script, not this block -->')
A('# Repo inventory')
A('')
A(f'Generated {datetime.date.today():%d %B %Y} from commit `{commit}` ({cdate}). Per-page detail is in `inventory-pages.csv`. '
  'Re-run `python3 wordpress/migration/build_inventory.py` after changes to the static build; the admin audit section at the end is kept.')
A('')
A('## Summary')
A('')
A(f'- **{len(rows)} HTML pages**: ' + ', '.join(f'{n} {k}' for k, n in types.most_common()) + '.')
A(f'- **Design layer**: `assets/css/global.css` ({kb(len(css.encode()))}, {len(tokens)} tokens) plus a page `<style>` block on most pages '
  f'({kb(sum(r["page_css_bytes"] for r in rows))} in total).')
A('- **Partials**: `partials/header.html` and `partials/footer.html`, injected into every page by `tools/sync.py` between `@header` and `@footer` markers.')
A(f'- **Scripts**: `assets/js/main.js` on every page, four feature scripts, and inline component scripts on {sum(1 for r in rows if r["inline_js_bytes"])} pages.')
A('- **Fonts are local.** Sora and Figtree variable woff2 files sit in `assets/fonts/` with `@font-face` in global.css, and no page links Google Fonts. Caveat is gone: `--ff-h` now points at Figtree.')
A(f'- **Images**: {img_hosts["fnpw.org.au"]} references to the live media library (fnpw.org.au/wp-content/uploads), {img_hosts["(local assets/)"]} to local files, {other_hosts} to other hosts.')
A(f'- **Forms**: HubSpot embeds on {len(comp_pages["HubSpot form embed"])} pages. Live pages embed the same HubSpot forms (admin audit, 10 November), so the embeds carry over as they are.')
A('')
A('## Pages')
A('')
A('### Site pages')
A('')
A('| File | Type | Title | Sections in `<main>` | Interactive |')
A('|---|---|---|---|---|')
for r in rows:
    if r['type'] in ('project', 'article', 'grant programme'): continue
    secs = ', '.join(s.split('.', 1)[1] if '.' in s else s for s in r['main_sections'].split(' > ') if s)
    A(f'| {r["file"]} | {r["type"]} | {r["title"]} | {secs} | {r["components"].replace("; ", ", ")} |')
A('')
for t, label in (('project', 'Projects'), ('grant programme', 'Grant programme pages'), ('article', 'Articles')):
    A(f'### {label} ({types[t]})')
    A('')
    if t == 'grant programme':
        A('Built from live harvests by `tools/port_live.py`. On live these three sit in the project post type at /project/{slug}/.')
        A('')
    A('Section sequences inside `<main>`, most common first:')
    A('')
    A('| Pages | Sequence |')
    A('|---|---|')
    top = seq_counter[t].most_common(10)
    for seqs, c in top:
        A(f'| {c} | {seqs.replace("section.", "").replace(" > ", " → ")} |')
    rest = sum(seq_counter[t].values()) - sum(c for _, c in top)
    if rest: A(f'| {rest} | other sequences (see the csv) |')
    A('')
A('## Partials')
A('')
A('- `partials/header.html`: skip link; Acknowledgement of Country strip (`.ack`); header (`.hdr`) with logo, mobile search icon, menu button and the main nav: '
  'About; Projects (All Projects and the three pillars); Partner With Us (Ways to Partner, Government Partnerships, Corporate Partnerships); Impact (Our Impact, Impact Reports); '
  'Get Involved (Ways to Get Involved, Corporate Volunteering, Workplace Giving, Fundraising, Gifts in Wills, Donate Land); Stories (Articles); Contact Us; a visible Search link; and the Donate button to https://bush.fnpw.org.au.')
A('- `partials/footer.html`: logo and line, social links, Explore, Get Involved (Donate and Give a Tree go to Raisely), Visit Us (fnpw@fnpw.org.au, 1800 898 626, ABN 90 107 744 771), and legal links (Privacy, Terms, RAP).')
A('- The Acknowledgement of Country sits in the strip above the header rather than in the footer, and the newsletter signup is a page band (`.nl-strip`) rather than part of the footer. The theme parts keep that arrangement.')
A('- `tools/sync.py` sets the active-nav `on` class per page; the Navigation block does this itself in WordPress.')
A('')
A('## Design layer')
A('')
A('Tokens in the `:root` blocks of `global.css`, which become the theme.json palette, font families and spacing:')
A('')
A('| Token | Value |')
A('|---|---|')
for k, v in tokens:
    A(f'| `{k}` | `{v.strip()}` |')
A('')
dups = [(k, v) for k, v in [('--euc-pale', '--euc-soft'), ('--waratah-pale', '--waratah-soft'), ('--reef-pale', '--reef-soft'),
        ('--hovea-pale', '--hovea-soft'), ('--paper', '--sand'), ('--char', '--ink')]
        if tokdict.get(k, '').strip().lower() == tokdict.get(v, '').strip().lower()]
A('These tokens carry the same value as another, so theme.json lists each colour once and keeps the alias as a CSS variable: ' + ', '.join(f'`{k}` = `{v}`' for k, v in dups) + '.')
A('')
A('## Section classes')
A('')
A("Classes on the direct children of `<main>`, with the number of pages using each and where its CSS lives. \"page\" means it is styled only in that page's own `<style>` block, so those rules travel with the page or its pattern.")
A('')
A('| Class | Pages | Defined in |')
A('|---|---|---|')
for c, ps in sorted(sec_pages.items(), key=lambda x: (-len(x[1]), x[0])):
    where = ', '.join(sorted(sec_where.get(c, ()))) or 'no rule found (modifier or script hook)'
    A(f'| `{c}` | {len(ps)} | {where} |')
A('')
A('## Scripts')
A('')
A('| File | Pages | Purpose |')
A('|---|---|---|')
purpose = {'assets/js/main.js': 'Base: mobile drawer, header shadow, scroll reveal (.rv), [data-count] counters, dropdown and accordion nav',
           'assets/js/carousel.js': 'Photo carousel (scroll-snap, auto-advance)', 'assets/js/gallery.js': 'Photo gallery in pages of six',
           'assets/js/articles.js': 'Stories page filter, sort and paging', 'assets/js/snap.js': 'Section snap (About page)'}
for src, ps in sorted(shared_js.items(), key=lambda x: -len(x[1])):
    A(f'| `{src}` | {len(ps)} | {purpose.get(src, "HubSpot form embed (external)" if "hsforms" in src else "")} |')
A('')
A('## Interactive components')
A('')
A('The treatment column is the build-spec proposal, confirmed as each one is built.')
A('')
A('| Component | Pages | How it works now | Proposed WordPress treatment |')
A('|---|---|---|---|')
for name, _, how, wp in COMPONENTS:
    ps = comp_pages.get(name, [])
    if not ps: continue
    shown = ', '.join(p.replace('.html', '') for p in ps[:5]) + (f' and {len(ps)-5} more' if len(ps) > 5 else '')
    A(f'| {name} | {len(ps)}: {shown} | {how} | {wp} |')
A('')
A('## Forms')
A('')
A('HubSpot form IDs in the static build and the pages they sit on. The admin audit at the end compares them with live.')
A('')
A('| HubSpot form ID | Pages |')
A('|---|---|')
for fid, ps in sorted(hs_forms.items(), key=lambda x: -len(x[1])):
    A(f'| `{fid}` | {", ".join(sorted(p.replace(".html", "") for p in ps))} |')
nohs = [r['file'] for r in rows if r['hubspot'] and not any(r['file'] in ps for ps in hs_forms.values())]
if nohs:
    A('')
    A('Pages loading HubSpot with the form ID set somewhere this script does not read: ' + ', '.join(nohs) + '.')
A('')
A('## Assets')
A('')
def count(path):
    fs = [p for p in glob.glob(path + '/**/*', recursive=True) if os.path.isfile(p)]
    return len(fs), sum(os.path.getsize(p) for p in fs)
for path, note in [('assets/img', 'all images'), ('assets/img/r', 'responsive webp sizes from tools/build_images.py'),
                   ('assets/img/projects', 'project heroes'), ('assets/img/partners', 'partner logos'),
                   ('assets/img/volunteering', 'volunteering photos'), ('assets/img/reports', 'report covers'),
                   ('assets/icons', 'icons'), ('assets/fonts', 'Sora and Figtree woff2'), ('assets/docs', 'PDFs')]:
    n, b = count(path)
    A(f'- `{path}`: {n} files, {b/1048576:.1f} MB ({note})')
A('- Repo root: favicon.svg, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png and site.webmanifest go into the theme. robots.txt, sitemap.xml, feed.xml, llms.txt and llms-full.txt come from `tools/meta.py --site`; WordPress and Yoast produce their own at launch.')
A('- Image hosts: ' + ', '.join(f'{h} ({n})' for h, n in img_hosts.most_common()) + '.')
A('')
A('## Data and generators')
A('')
A('- `data/projects.json` (85 projects with slug, pillar, state, coordinates and live URL) feeds the map and project pages; `data/projects-content.json` holds harvested live project copy (72 projects).')
A('- `data/articles.json` (166 articles) feeds the article pages and the Stories index. `data/live-port/` holds word-for-word harvests used by `tools/port_live.py`.')
A('- `data/meta.json` holds the hand-written titles and descriptions that `tools/meta.py` writes into every head. Yoast owns these in WordPress, so this file is the source for setting them there.')
A('- `data/alt-text/` holds alt text written from the photographs and applied by `tools/apply_alt.py`; `data/wp-media.json` has featured-image alt and sizes from the live REST API.')
A('')
A('## Flags for Ely')
A('')
A(f'- **Page count.** The handover says 121 pages. The repo has {len(rows)}: {types["article"]} articles and {len(rows) - types["article"]} site, project and grant pages. How the articles import is a page-map decision.')
A('- **Forms.** Live pages use the same HubSpot forms as the static build, so nothing is swapped. Three Formidable forms are still on live pages; see the admin audit.')
A('- **Old WordPress scaffold.** `wp/` (September) holds an earlier block theme and plugin. Its fnpw-core registers its own `project` post type and taxonomies, which would clash with Template Required Plugins. Decision pending on whether to build fresh in `wordpress/` and borrow from it.')
A('- **CLAUDE.md is out of date in two places.** It says images come from Unsplash (none do now) and lists Caveat as a typeface (removed).')
A('<!-- /@generated -->')
gen = '\n'.join(L) + '\n'

path = os.path.join(OUT, 'inventory.md')
old = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
m = re.search(r'<!-- /@generated -->\n?(.*)\Z', old, re.S)
tail = m.group(1) if m else '\n## Admin audit (task 8)\n\nAdded once Ely is logged in to wp-admin.\n'
open(path, 'w', encoding='utf-8').write(gen + tail)
print('wrote', path, len(gen + tail), 'chars;', len(rows), 'pages')
