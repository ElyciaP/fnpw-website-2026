"""Round 2 fixes: visible pillar cards, single tab set on projects hub with
clickable cards for all 83 projects, page removals, RAP redesign, nav cleanup."""
import json, os, re, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))

# 1. CSS: guarantee generated card grids are visible regardless of reveal/filter JS
MARK2 = '/* === v2.1 card visibility guarantee === */'
g = open('assets/css/global.css').read()
if MARK2 not in g:
    g += f'''
{MARK2}
.pg{{display:grid !important}}
.pg .pc{{opacity:1 !important;transform:none !important;display:flex;flex-direction:column}}
.pg .pc-link{{display:flex;flex-direction:column;height:100%}}
'''
    open('assets/css/global.css', 'w').write(g)
    print('css: visibility guarantee added')

# 2. remove dropped pages
for f in ['paws-magazine.html', '404.html', 'tax-deductible-charity-donation.html']:
    if os.path.exists(f):
        try:
            os.remove(f)
            print('removed', f)
        except OSError as e:
            open(f, 'w').write('<!-- removed -->')
            print('could not delete, blanked instead:', f, e)

# 3. nav: drop PAWS link
h = open('partials/header.html').read()
h2 = h.replace('        <a href="paws-magazine.html" class="">PAWS Magazine</a>\n', '')
if h2 != h:
    open('partials/header.html', 'w').write(h2)
    print('nav: PAWS removed')

# 4. regenerate pillar/project/static pages
import gen_projects, gen_pages
gen_projects.main()
gen_pages.main()

# 5. projects.html: remove the added pillar band (back to ONE set of tabs)
t = open('projects.html').read()
t2 = re.sub(r'<section class="sec"><div class="cw rv">\s*<span class="ey">Three pillars</span>.*?</section>\n', '', t, flags=re.S)
print('pillar band removed:', t2 != t)
t = t2

# 6. projects.html: replace the 16 static demo cards with all 83 real projects,
#    each card a link to its detail page (no popup)
projects = json.load(open('data/projects.json'))
PIL_MAP = {'parks': ('parks', 'Growing Parks', 'pb-parks'),
           'species': ('species', 'Saving Species', 'pb-species'),
           'healing': ('heal', 'Healing Land', 'pb-healing')}
cards = []
for p in projects:
    data_pil, label, cls = PIL_MAP[p['pillar']]
    cards.append(
        f'<article class="pc" data-pil="{data_pil}">'
        f'<a class="pc-link" href="project-{p["slug"]}.html">'
        f'<div class="pc-im"><img src="{p["img"]}" alt="{p["title"]}" loading="lazy">'
        f'<span class="pc-pb {cls}">{label}</span>'
        f'<span class="pc-lo">{p["state"]}</span></div>'
        f'<div class="pc-bd"><h3>{p["title"]}</h3></div>'
        f'</a></article>')
new_grid = '\n'.join(cards)
gs = t.index('<div class="pg" id="pgrid">') + len('<div class="pg" id="pgrid">')
first_a = t.find('<article', gs)
last_a = t.rfind('</article>') + len('</article>')
assert first_a > 0 and last_a > first_a, 'grid bounds not found'
t = t[:first_a] + new_grid + t[last_a:]

n = len(projects)
t = t.replace('All projects (16)', f'All projects ({n})')
t = t.replace('Showing 16 projects', f'Showing {n} projects')
open('projects.html', 'w').write(t)
print(f'projects.html: grid rebuilt with {n} linked cards, counts updated')

# 7. sync headers/footers, verify
r = subprocess.run(['python3', 'tools/sync.py'], capture_output=True, text=True)
print('sync:', r.stdout.count('updated'), 'pages')

bad = []
for f in sorted(glob.glob('*.html')):
    txt = open(f).read()
    if '<!-- removed -->' in txt:
        continue
    if txt.count('</header>') != 1 or 'paws-magazine.html' in txt:
        bad.append(f)
gnp = open('growing-national-parks.html').read()
print('pillar page cards:', gnp.count('<article class="pc"'), '| intro present:', 'What this pillar does' in gnp)
ph = open('projects.html').read()
print('hub cards:', ph.count('<article class="pc"'), '| popups bound to data-id cards left:', ph.count('data-id='))
print('pages:', len(glob.glob('*.html')), '| problems:', bad if bad else 'NONE')
