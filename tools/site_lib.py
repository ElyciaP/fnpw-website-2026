"""Shared page shell + section builders for generated pages.

All generated pages use the same skeleton as the hand-built prototype pages:
global.css + header/footer sync markers + main.js. Run tools/sync.py after
generating to inject the header and footer.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Figtree:wght@300;400;500;600;700&family=Caveat:wght@400;600;700&display=swap" rel="stylesheet">'''

def write_page(fname, title, desc, body, page_css='', extra_js=''):
    html = f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">\n<meta name="referrer" content="no-referrer">
<title>{title} | Foundation for National Parks &amp; Wildlife</title>
<meta name="description" content="{desc}">
{FONTS}
<link rel="stylesheet" href="assets/css/global.css">
<style>
{page_css}
</style>
</head>
<body>
<!-- @header --><!-- /@header -->
<main>
{body}
</main>
<!-- @footer --><!-- /@footer -->
<script src="assets/js/main.js"></script>
{extra_js}
</body>
</html>'''
    with open(os.path.join(ROOT, fname), 'w') as f:
        f.write(html)

def crumb(label):
    return ('<nav style="display:flex;gap:.5em;font-size:.82rem;color:var(--stone);'
            'margin-bottom:1.5rem"><a href="index.html" style="color:var(--euc)">Home</a>'
            f'<span style="opacity:.4">/</span>{label}</nav>')

U_ = 'https://fnpw.org.au/wp-content/uploads/'
# crumb label -> photographic hero (image, alt). Pages not listed fall back to flat.
HERO_IMGS = {
    'Get Involved': (U_+'2021/02/Ascent-37-Woomargama-2000px-Copy.jpg', 'Morning light over Woomargama National Park'),
    'Project Partnerships': (U_+'2021/01/K2W-GER-Aerial.jpg', 'Aerial view of the Great Eastern Ranges'),
    'Workplace Giving': (U_+'2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg', 'Bushcare volunteers at work'),
    'Fundraising': (U_+'2021/02/Phillip-Island-Ambassadors.jpg', 'Youth wildlife ambassadors'),
    'Donate Land': (U_+'2021/02/heritage-Estates-05-lg.jpg', 'Protected bushland at Heritage Estates'),
    'How Your Contributions Help': (U_+'2021/02/KNP-recovery-1-scaled.jpg', 'Bushfire recovery in Kosciuszko National Park'),
    'Why Your Support Is Needed': (U_+'2022/02/Orange-belliedParrot_DPIPWE-scaled.jpg', 'Critically endangered orange-bellied parrot'),
    'Corporate Governance': (U_+'2021/02/Mount-Field-NP-East-Planking-PAWS.jpg', 'Boardwalk in Mount Field National Park'),
    'Reconciliation Action Plan': (U_+'2021/01/Lorina-and-Tinnesha-in-EPBC-protected-sandstone-shrublands_photo-Donal-Sullivan5f911988b9c1d-scaled.jpg', 'Warddeken rangers on Country, photo Donal Sullivan'),
    'FAQs': (U_+'2021/01/Black-chinned-honeyeater-PETER-SAWYER-CYMK.jpg', 'Black-chinned honeyeater'),
    'Media Enquiries': (U_+'2021/02/Caught-on-Camera-Superb-Lyrebird.jpg', 'Superb lyrebird caught on camera'),
    'Newsletter': (U_+'2021/02/WA-Bird-Watering-Stations-Jirdarup-bushland-precinct-Three-cockies.jpeg', 'Three cockatoos at a watering station'),
    'Thank You': (U_+'2021/01/feeding.jpg', 'A wildlife carer feeding a rescued animal'),
    'Privacy Policy': (U_+'2021/02/Ascent-37-Woomargama-2000px-Copy.jpg', 'Woomargama National Park'),
    'Terms &amp; Conditions': (U_+'2021/02/Ascent-37-Woomargama-2000px-Copy.jpg', 'Woomargama National Park'),
    'Search': (U_+'2021/01/Seagrass-Small.jpg', 'Seagrass meadow'),
    'Corporate Volunteering / Sydney': (U_+'2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg', 'Bushcare volunteers'),
    'Corporate Volunteering / Melbourne': (U_+'2021/02/Koala-projects.png', 'Nest box installation'),
    'Corporate Volunteering / Brisbane': (U_+'2021/02/CurrumbinKoala-Erik-Veland.jpg', 'Koala in Queensland'),
    'Corporate Volunteering / Adelaide': (U_+'2022/02/torrens-Island-bird.jpg', 'Birdlife at Torrens Island'),
    'Corporate Volunteering / Perth': (U_+'2021/02/WArangers-lge.jpg', 'Rangers in Western Australia'),
}

def hero(ey, h1, lede, crumb_label):
    if crumb_label in HERO_IMGS:
        img, alt = HERO_IMGS[crumb_label]
        return hero_img(ey, h1, lede, crumb_label, img, alt)
    return f'''<section class="ch">
  <div class="cw rv">
    {crumb(crumb_label)}
    <span class="ey">{ey}</span>
    <h1 style="margin:1rem 0 1.2rem;max-width:22ch">{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''

def hero_img(ey, h1, lede, crumb_label, img, alt):
    return f'''<section class="ch chi" style="--chi:url('{img}')">
  <div class="cw rv">
    {crumb(crumb_label)}
    <span class="ey">{ey}</span>
    <h1 style="margin:1rem 0 1.2rem;max-width:22ch">{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>'''

def sec(inner, variant=''):
    return f'<section class="sec {variant}">\n  <div class="cw rv">\n{inner}\n  </div>\n</section>'

def two(left, right):
    return f'<div class="two">\n<div>{left}</div>\n<div>{right}</div>\n</div>'

def port(note):
    """Visible placeholder for copy that must be ported from the live site."""
    return f'<div class="port-note"><strong>To port from live site:</strong> {note}</div>'

def cta_band(h, p, buttons):
    btns = ''.join(f'<a class="{cls}" href="{href}">{label}</a>' for label, href, cls in buttons)
    return f'''<section class="sec dark">
  <div class="cw rv" style="text-align:center">
    <h2 style="max-width:24ch;margin:0 auto 1rem">{h}</h2>
    <p class="lede" style="margin:0 auto 2rem;max-width:52ch">{p}</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">{btns}</div>
  </div>
</section>'''

def stats(items):
    cells = []
    for n, suf, label in items:
        suf_attr = ' data-suf="{}"'.format(suf) if suf else ''
        cells.append('<div><div class="stat-n" data-count="{}"{}>0</div>'
                     '<div class="stat-l">{}</div></div>'.format(n, suf_attr, label))
    return '<div class="statrow">{}</div>'.format(''.join(cells))

def faq(q, a):
    return f'<details class="fq"><summary>{q}</summary><div class="fq-a"><p>{a}</p></div></details>'

def card(slug, title, img, pillar_label, pillar_class, state, blurb, data_pil=''):
    pil_attr = f' data-pil="{data_pil}"' if data_pil else ''
    blurb_html = f'<p>{blurb}</p>' if blurb else ''
    return f'''<article class="pc"{pil_attr}>
  <a href="project-{slug}.html" class="pc-link">
    <div class="pc-im"><img src="{img}" alt="{title}" loading="lazy">
      <span class="pc-pb {pillar_class}">{pillar_label}</span>
      <span class="pc-lo">{state}</span>
    </div>
    <div class="pc-bd"><h3>{title}</h3>{blurb_html}</div>
  </a>
</article>'''

# Pages owned by gen_exemplars.py; gen_projects.py must not overwrite them.
EXEMPLAR_SLUGS = {'remarkable-southern-flinders',
                  'southern-highlands-koala-conservation',
                  'warddeken-mayh'}

RAISELY_DONATE = 'https://foundation-for-national-parks-and-wildlife.raiselysite.com/'
RAISELY_HERO = 'https://habitat-heroes.raiselysite.com/'
PLACEHOLDER_IMG = 'assets/img/bongil.jpg'
