#!/usr/bin/env python3
"""Page map (task 2 of the handover).

Run from the repo root:  python3 wordpress/migration/build_page_map.py

Matches every live URL in the sitemap snapshot (source/live-sitemaps-2026-11-10.txt)
to a page in the static build, and gives every static page its WordPress URL.
Writes wordpress/migration/page-map.csv. The converter uses wp_url to rewrite
internal .html links, and redirects.csv (task 7) is built from the redirect and
retire rows.

Actions
  replace   the live URL stays and its content is replaced by the static page
  keep      the live URL and its content stay as they are, in the new templates
  redirect  the live URL 301s to redirect_to
  retire    the live page is unpublished and its URL 301s to redirect_to
  new       a static page with no live counterpart, created at wp_url
  template  rendered by a theme template rather than a page (search, 404)

decision = an id in page-map-decisions.md that Ely still has to confirm.
"""
import csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
SNAP = 'wordpress/migration/source/live-sitemaps-2026-11-10.txt'
OUT = 'wordpress/migration/page-map.csv'
BUSH, GAT, HH = 'https://bush.fnpw.org.au', 'https://gift-a-tree.fnpw.org.au', 'https://habitat-heroes.fnpw.org.au'

# Live pages (page-sitemap) -> (static file, action, redirect_to, template, decision, note)
PAGES = {
    '/': ('index.html', 'replace', '', 'front-page', '', ''),
    '/about-us/': ('about.html', 'replace', '', 'page', 'D1', ''),
    '/projects/': ('projects.html', 'replace', '', 'page', '', 'Project map and grid as custom blocks'),
    '/news/': ('articles.html', 'replace', '', 'home', '', 'Posts page under Settings > Reading; the template renders the Stories index'),
    '/contact-us/': ('contact.html', 'replace', '', 'page', 'D1', ''),
    '/corporate-partnerships/': ('partner.html', 'replace', '', 'page', '', ''),
    '/corporate-volunteering/': ('volunteer.html', 'replace', '', 'page', 'D1', ''),
    '/corporate-volunteering/sydney/': ('corporate-volunteering-nsw.html', 'replace', '', 'page', 'D1', 'Child of /corporate-volunteering/'),
    '/corporate-volunteering/melbourne/': ('corporate-volunteering-vic.html', 'replace', '', 'page', 'D1', 'Child of /corporate-volunteering/'),
    '/corporate-volunteering/brisbane/': ('corporate-volunteering-qld.html', 'replace', '', 'page', 'D1', 'Child of /corporate-volunteering/'),
    '/corporate-volunteering/adelaide/': ('corporate-volunteering-sa.html', 'replace', '', 'page', 'D1', 'Child of /corporate-volunteering/'),
    '/corporate-volunteering/perth/': ('corporate-volunteering-wa.html', 'replace', '', 'page', 'D1', 'Child of /corporate-volunteering/'),
    '/bequest/': ('bequests.html', 'replace', '', 'page', 'D1', ''),
    '/annual-reports-financials/': ('reports.html', 'replace', '', 'page', 'D1', ''),
    '/foundation-for-national-parks-and-wildlife-newsletter/': ('newsletters-sign-up.html', 'replace', '', 'page', 'D1', ''),
    '/faqs/': ('faqs.html', 'replace', '', 'page', '', ''),
    '/grants/': ('grants.html', 'replace', '', 'page', '', ''),
    '/ways-you-can-get-involved/': ('ways-you-can-get-involved.html', 'replace', '', 'page', '', ''),
    '/fundraising-with-fnpw/': ('fundraising-with-fnpw.html', 'replace', '', 'page', '', 'Listed as unmatched in the handover; the build has this page'),
    '/donate-land/': ('donate-land.html', 'replace', '', 'page', '', ''),
    '/workplace-giving/': ('workplace-giving.html', 'replace', '', 'page', '', ''),
    '/paws-magazine/': ('paws-magazine.html', 'replace', '', 'page', '', 'Listed as unmatched in the handover; the build has this page'),
    '/mitigating-effects-environmental-change/': ('article-mitigating-effects-environmental-change.html', 'replace', '', 'page-article', 'D6', 'Decided 10 Nov: the eBook becomes an article with a free PDF download and no form; stays at the same URL in the article layout'),
    '/why-your-support-is-needed/': ('why-your-support-is-needed.html', 'replace', '', 'page', '', ''),
    '/how-your-contributions-help/': ('how-your-contributions-help.html', 'replace', '', 'page', '', ''),
    '/reconciliation-action-plan/': ('reconciliation-action-plan.html', 'replace', '', 'page', '', ''),
    '/media-enquiry/': ('media-enquiry.html', 'replace', '', 'page', '', ''),
    '/privacy-policy/': ('privacy-policy.html', 'replace', '', 'page', '', ''),
    '/terms-and-conditions/': ('terms-and-conditions.html', 'replace', '', 'page', '', ''),
    '/corporate-governance/': ('corporate-governance.html', 'replace', '', 'page', '', ''),
    '/newsletter-thank-you/': ('newsletter-thank-you.html', 'replace', '', 'page', '', 'Thank-you page; keep the URL so the newsletter form redirect still works'),
    '/thank-you-volunteer-form/': ('thank-you-volunteer-form.html', 'replace', '', 'page', '', 'Thank-you page; keep the URL so the volunteering form redirect still works'),
    '/thank-you/': ('thank-you.html', 'replace', '', 'page', 'D7', 'Live copy confirms a blog upload; task 8 shows which forms land here'),
    '/biodiversity-month/': ('article-biodiversity-month.html', 'replace', '', 'page-article', 'D6', 'A page on live and an article in the build; stays a page at the same URL in the article layout'),
    '/koala-facts/': ('article-koala-facts.html', 'replace', '', 'page-article', 'D6', 'A page on live and an article in the build; stays a page at the same URL in the article layout'),
    '/project-partnerships/': ('', 'redirect', '/government-partnerships/', '', 'D3', 'Live copy is about government partnerships, which now has its own page'),
    '/tax-deductible-charity-donation/': ('', 'redirect', '/faqs/', '', 'D3', 'Its tax FAQs were ported into the FAQ page'),
    '/annual-reports-financials/our-2024-impact-and-vision/': ('', 'redirect', '/annual-reports-financials/', '', 'D3', '2024 Impact Report and Strategic Plan; the reports page carries the 2024 report'),
    '/tech4forests/': ('', 'redirect', '/corporate-partnerships/', '', 'D3', '2022 corporate fundraising landing page (COP15)'),
    '/welcome-to-fnpw/': ('', 'redirect', '/', '', 'D4', 'Supporter landing page; check with Reef whether it is a Google Ads final URL'),
    '/thank-you-volunteer-for-impact/': ('', 'redirect', '/corporate-volunteering/', '', 'D4', 'Despite the slug this is a Volunteer for Impact landing page; check with Reef'),
    '/upload-your-blog-post/': ('', 'retire', '/contact-us/', '', 'D3', 'Front-end blog upload form (AccessPress Anonymous Post Pro)'),
    '/test-form/': ('', 'retire', '/', '', '', 'Handover recommendation: retire'),
    '/donations/': ('', 'redirect', BUSH, '', '', 'Known retirement: donations go to Raisely'),
}

# Static pages with no live counterpart -> proposed WordPress URL (D5)
NEW_PAGES = {
    'growing-national-parks.html': '/growing-national-parks/', 'saving-species.html': '/saving-species/',
    'healing-the-land.html': '/healing-the-land/', 'government-partnerships.html': '/government-partnerships/',
    'partner-invest.html': '/partner-with-us/', 'our-impact.html': '/our-impact/', 'in-the-news.html': '/in-the-news/',
    'bequests-professional-advisers.html': '/bequest/professional-advisers/',
}
TEMPLATES = {'search.html': ('/?s=', 'search'), '404.html': ('', '404')}

PROJECT_RULES = {  # live project slug -> (action, redirect_to, decision, note)
    'nectarlovers': ('redirect', '/project/nectar-sippers/', '', 'Known retirement: renamed Nectar Sippers in the build'),
    'form-test': ('retire', '/projects/', 'D3', 'Not a test: the contractor expression of interest page with a Formidable form'),
}
DONATIONS = {  # live path -> (redirect_to, decision, note)
    '/donation/': (BUSH, '', 'Known retirement. Live already sends this to /donations/'),
    '/donation/donate-to-growing-parks-and-saving-species/': (BUSH, '', 'Known retirement'),
    '/donation/healing-our-land-2/': (BUSH, '', 'Known retirement. Already redirects off-site on live'),
    '/donation/become-a-habitat-hero-with-a-monthly-gift/': (HH, 'D8', 'Monthly giving; CLAUDE.md sends Habitat Heroes to its own Raisely page. Already redirects off-site on live'),
    '/donation/plant-a-tree/': (GAT, 'D8', 'Tree gift; proposed Give a Tree. Already redirects off-site on live'),
}
GRANTS = {'/grant/wildlife-heroes-grants/': ('redirect', '/project/wildlife-heroes/', 'D3', 'The build folds this into the Wildlife Heroes project (as tools/port_live.py does)')}

def read_snapshot():
    rows, sm = [], None
    for line in open(SNAP, encoding='utf-8'):
        line = line.strip()
        if line.startswith('#') and line.endswith('-sitemap.xml'):
            sm = line[1:-len('-sitemap.xml')]; continue
        if line.startswith('/'):
            url, lastmod = line.split()
            rows.append((url, sm, lastmod))
    return rows

static = set(glob.glob('*.html'))
articles = {a['slug'] for a in json.load(open('data/articles.json', encoding='utf-8'))}
news = {n['slug']: n for n in json.load(open('data/in-the-news.json', encoding='utf-8'))}
out = []

def row(live_url='', live_type='', lastmod='', static_file='', wp_url='', wp_type='', template='', action='', redirect_to='', decision='', note=''):
    out.append(dict(live_url=live_url, live_type=live_type, live_lastmod=lastmod, static_file=static_file, wp_url=wp_url,
                    wp_post_type=wp_type, wp_template=template, action=action, redirect_to=redirect_to, decision=decision, notes=note))

for url, sm, lastmod in read_snapshot():
    if sm == 'page':
        f, action, to, tpl, dec, note = PAGES[url]
        row(url, 'page', lastmod, f, url if action == 'replace' else '', 'page' if action == 'replace' else '', tpl, action, to, dec, note)
    elif sm == 'post':
        slug = url.rstrip('/').split('/')[-1]
        f = f'article-{slug}.html' if f'article-{slug}.html' in static else ''
        if f:
            row(url, 'post', lastmod, f, url, 'post', 'single', 'replace', '', 'D2', 'Decided 10 Nov (option B): the build version replaces the live body, old body saved on the post for rollback')
        else:
            note = 'Press coverage item, listed on In the news' if slug in news else 'No static article'
            row(url, 'post', lastmod, '', url, 'post', 'single', 'keep', '', '', note)
    elif sm == 'project':
        slug = url.split('/')[2]
        if slug in PROJECT_RULES:
            action, to, dec, note = PROJECT_RULES[slug]
            row(url, 'project', lastmod, '', '', '', '', action, to, dec, note)
        else:
            f = f'project-{slug}.html'
            assert f in static, f
            note = 'Grant programme page (port_live.py)' if f.endswith('-grants.html') else ''
            row(url, 'project', lastmod, f, url, 'project', 'single-project', 'replace', '', '', note)
    elif sm == 'grant':
        action, to, dec, note = GRANTS[url]
        row(url, 'grant', lastmod, '', '', '', '', action, to, dec, note)
    elif sm == 'donation':
        to, dec, note = DONATIONS[url]
        row(url, 'donation', lastmod, '', '', '', '', 'redirect', to, dec, note)
    elif sm in ('category', 'post_tag'):
        row(url, sm, lastmod, '', url, sm, 'archive', 'keep', '', '', '')
    elif sm in ('project_state', 'project_focus_area', 'project_year'):
        note = 'Duplicates /news/projects/state/queensland/; merge after launch' if url.endswith('/qld/') else ''
        row(url, sm, lastmod, '', url, sm, 'taxonomy', 'keep', '', 'D9', note)
    else:
        raise SystemExit(f'unknown sitemap {sm}')

used = {r['static_file'] for r in out if r['static_file']}
for f in sorted(static - used):
    if f in NEW_PAGES:
        row(static_file=f, wp_url=NEW_PAGES[f], wp_type='page', template='page', action='new', decision='D5')
    elif f in TEMPLATES:
        u, t = TEMPLATES[f]
        row(static_file=f, wp_url=u, template=t, action='template', note='Theme template, not a page')
    elif f.startswith('project-'):
        slug = f[8:-5]
        row(static_file=f, wp_url=f'/project/{slug}/', wp_type='project', template='single-project', action='new',
            note='Replaces /project/nectarlovers/' if slug == 'nectar-sippers' else 'New project')
    else:
        raise SystemExit(f'static page with no rule: {f}')

# ---------------------------------------------------------------- checks
import collections
errors = []
sf = collections.Counter(r['static_file'] for r in out if r['static_file'])
errors += [f'static file used twice: {f}' for f, n in sf.items() if n > 1]
errors += [f'static file missing: {f}' for f in static - set(sf)]
lu = collections.Counter(r['live_url'] for r in out if r['live_url'])
errors += [f'live URL twice: {u}' for u, n in lu.items() if n > 1]
if len(lu) != len(read_snapshot()): errors.append('live URL count mismatch')
wu = collections.Counter(r['wp_url'] for r in out if r['wp_url'])
errors += [f'wp_url twice: {u}' for u, n in wu.items() if n > 1]
live_targets = {r['wp_url'] for r in out if r['action'] in ('replace', 'keep', 'new') and r['wp_url']}
for r in out:
    to = r['redirect_to']
    if not to: 
        if r['action'] in ('redirect', 'retire'): errors.append(f'no target: {r["live_url"]}')
        continue
    if to.startswith('http'):
        if to not in (BUSH, GAT, HH): errors.append(f'unexpected external target {to}')
    elif to not in live_targets:
        errors.append(f'redirect target is not a live page (chain or dead): {r["live_url"]} -> {to}')
if errors:
    raise SystemExit('\n'.join(errors))

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

summary = collections.Counter((r['live_type'] or 'static only', r['action']) for r in out)
print(f'wrote {OUT}: {len(out)} rows, {len(lu)} live URLs, {len(sf)} static files')
for (t, a), n in sorted(summary.items()):
    print(f'  {t:20} {a:9} {n}')
print('decisions:', dict(collections.Counter(r['decision'] for r in out if r['decision'])))
