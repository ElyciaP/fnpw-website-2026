"""Audit pass: IR cover, reveal-threshold fix, header normalization, real team on
About + gallery band, FNPW imagery replacing every remaining Unsplash photo."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
U = 'https://fnpw.org.au/wp-content/uploads/'

# ---------- 1. Impact Report cover from the real PDF ----------
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('../FNPW_ImpactReport2025_V2_Digital_FA2-Medium.pdf')
page = pdf[0]
img = page.render(scale=2).to_pil()
w = 800
img = img.convert('RGB').resize((w, int(img.size[1] * w / img.size[0])))
img.save('assets/img/impact-report-cover.jpg', quality=88)
print('IR cover rendered:', img.size)

t = open('index.html').read()
t = t.replace('src="assets/img/impact-report-2026.jpg" alt="Cover of the FNPW Impact Report 2026"',
              'src="assets/img/impact-report-cover.jpg" alt="Cover of the FNPW Impact Report 2025"')
t = t.replace('Our Impact Report 2026 is out:', 'Our latest Impact Report is out:')
t = t.replace('<a class="btn-p" href="reports.html">Read the Impact Report</a>',
              '<a class="btn-p" href="https://fnpw.org.au/wp-content/uploads/2026/04/FNPW_ImpactReport2025_V2_Digital_FA2-Medium.pdf">Read the Impact Report</a>')
open('index.html', 'w').write(t)
print('homepage IR section: real cover + PDF link')

# ---------- 2. reveal threshold fix (pillar dead-space bug) ----------
js = open('assets/js/main.js').read()
js2 = js.replace("{threshold:.12,rootMargin:'0px 0px -50px 0px'}",
                 "{threshold:0.01,rootMargin:'0px 0px -40px 0px'}")
assert js2 != js, 'reveal threshold not found'
open('assets/js/main.js', 'w').write(js2)
print('main.js: reveal threshold fixed (tall grids now appear immediately)')

# ---------- 3. normalize flat/light heroes to the dark photographic system ----------
HERO_NORM = {
    'news.html':     ('nh', U + '2021/01/Featured-projects-Penguins-lge.jpg'),
    'articles.html': ('nh', U + '2021/02/Eastern-Bristlebird.jpg'),
    'reports.html':  ('nh', U + '2021/02/Mount-Field-NP-East-Planking-PAWS.jpg'),
    'partner.html':  ('ph', U + '2021/01/K2W-GER-Aerial.jpg'),
}
for page_f, (cls, img_url) in HERO_NORM.items():
    t = open(page_f).read()
    if 'v3.2 hero-normalize' in t:
        continue
    i = t.rindex('</style>')
    t = t[:i] + f'''
/* v3.2 hero-normalize */
.{cls}{{position:relative;isolation:isolate;overflow:hidden;color:#fff;background:var(--euc-deep)}}
.{cls}::before{{content:"";position:absolute;inset:0;z-index:-2;background:url('{img_url}') center/cover}}
.{cls}::after{{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(15,49,50,.55),rgba(15,49,50,.88))}}
.{cls} h1{{color:#fff}}
.{cls} .lede{{color:rgba(255,255,255,.87)}}
.{cls} .ey{{color:var(--euc-soft)}}
.{cls} nav,.{cls} nav a{{color:rgba(255,255,255,.75)!important}}
''' + t[i:]
    open(page_f, 'w').write(t)
    print(page_f, 'hero normalized')

# ---------- 4. About: real team + founder + elevated gallery ----------
t = open('about.html').read()

def tc(img_file, name, role, note=''):
    src = U + img_file
    note_html = f'<div class="tc-r" style="font-size:.78rem;opacity:.75">{note}</div>' if note else ''
    return (f'<div class="tc rv"><div class="tc-ph"><img src="{src}" alt="{name}" loading="lazy"></div>'
            f'<div class="tc-in"><div class="tc-n">{name}</div><div class="tc-r">{role}</div>{note_html}</div></div>')

EXEC = [
    ('2021/03/Ian-Darbyshire-FNPW-CEO-e1614899323722-1022x1024.jpg', 'Ian Darbyshire', 'Chief Executive Officer'),
    ('2022/04/suzana-01.jpg', 'Suzana Majstorovic', 'Chief Operations Officer'),
    ('2024/09/Glenn-Murray.png', 'Glenn Murray', 'Chief Financial Officer'),
    ('2025/02/Mark-Cairns.png', 'Mark Cairns', 'Chief Biodiversity Officer'),
    ('2025/06/Ian-Laing.png', 'Ian Laing', 'Chief Commercial Officer'),
]
BOARD = [
    ('2026/02/Kelly-OShanassy.png', 'Kelly O&rsquo;Shanassy', 'Chair', 'Elected Chair 2026'),
    ('2026/02/Mark-Arnold.png', 'Mark Arnold', 'Treasurer &amp; Deputy Chair', 'Appointed 2026'),
    ('2020/11/Jane-Daziger_POS@2x.png', 'Jane Danziger', 'Director', 'Appointed 2020'),
    ('2023/05/Tim-Jarvis-FNPW-director-1024x814.jpg', 'Tim Jarvis AM', 'Director', 'Appointed 2023'),
    ('2023/05/Natalie-Kyrogiou-FNPW-Director.jpg', 'Natalie Kyriacou OAM', 'Director', 'Appointed 2024'),
    ('2025/02/leisa-bacon-1024x1024.jpg', 'Leisa Bacon', 'Director', 'Appointed 2025'),
    ('2025/02/Staff-Profiles.png', 'Dr Lucas Carmody', 'Director', 'Appointed 2025'),
    ('2026/02/Kinjia.png', 'Kinjia Munkara-Murray', 'Director', 'Appointed 2026'),
    ('2026/02/Nick-Tubb.png', 'Nick Tubb', 'Director', 'Appointed 2026'),
]

# replace the two tm-g grids (first = exec, second = board)
grids = re.findall(r'<div class="tm-g">.*?</div>\s*</div>\s*</div>', t, re.S)
tm_blocks = re.split(r'(<div class="tm-g">)', t)
# safer approach: find each tm-g block by matching balanced-ish region up to the closing of the grid
matches = list(re.finditer(r'<div class="tm-g">(.*?)(</div>\s*){1}\s*</section>', t, re.S))
# fall back to a simpler strategy: replace grid contents between <div class="tm-g"> and </section>
parts = t.split('<div class="tm-g">')
assert len(parts) >= 3, f'expected 2 tm-g grids, found {len(parts)-1}'
def rebuild(seg, cards):
    j = seg.find('</section>')
    tail = seg[j:]
    # grid closes with </div> just before </section>; rebuild cleanly
    return cards + '\n</div>\n' + tail.lstrip()
new = parts[0] + '<div class="tm-g">' + rebuild(parts[1], ''.join(tc(*e) for e in EXEC))
new += '<div class="tm-g">' + rebuild(parts[2], ''.join(tc(*b) for b in BOARD))
t = new

# founder feature after the exec section
founder = f'''
<section class="sec paper">
  <div class="cw">
    <div class="two" style="align-items:center">
      <div class="rv" style="max-width:320px;justify-self:center"><img src="{U}2020/11/Founder_Positional@2x.png" alt="The late Hon. Tom Lewis AO" loading="lazy" style="display:block;width:100%;box-shadow:12px 12px 0 var(--wattle-soft)"></div>
      <div class="rv d1"><span class="ey">Founder &amp; Patron</span>
      <h2 style="margin:.8rem 0 1rem">The late Hon. Tom Lewis AO</h2>
      <p>As NSW lands minister, Tom Lewis set up the National Parks and Wildlife Service in 1967, then established the Foundation for National Parks &amp; Wildlife in 1970 as its fundraising arm. Today the Foundation he started is an apolitical, independent conservation organisation working Australia-wide.</p></div>
    </div>
  </div>
</section>'''
# insert before the board section (the section containing 'Our Board of Directors')
bi = t.find('Our Board of Directors')
si = t.rfind('<section', 0, bi)
t = t[:si] + founder + '\n' + t[si:]

# elevated gallery band before the closing CTA
gallery_css = '''
/* v3.2 gallery + team photos */
.tc-ph img{width:100%;height:100%;object-fit:cover;display:block}
.abg{background:var(--euc-deep);padding:5.5rem 0;overflow:hidden}
.abg .ey{color:var(--euc-soft)}
.abg h2{color:#fff;font-family:var(--ff-d);font-weight:700;font-size:clamp(1.6rem,2.8vw,2.3rem);letter-spacing:-.02em;margin:.8rem 0 2rem}
.abg-rail{display:flex;gap:1.2rem;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:1rem;scrollbar-width:thin;scrollbar-color:var(--euc) transparent}
.abg-i{flex:0 0 auto;scroll-snap-align:start;position:relative}
.abg-i img{display:block;height:340px;width:auto;object-fit:cover}
.abg-i span{position:absolute;left:.8rem;bottom:.8rem;background:rgba(15,49,50,.78);color:#fff;font-size:.78rem;padding:.3rem .7rem}
@media(max-width:700px){.abg-i img{height:230px}}
'''
gallery_html = f'''
<section class="abg">
  <div class="cw">
    <span class="ey rv">The country we work for</span>
    <h2 class="rv">Fifty-five years of views like these.</h2>
    <div class="abg-rail rv d1">
      <div class="abg-i"><img src="assets/img/hero-golden.jpg" alt="Golden hour over spinifex country" loading="lazy"><span>Outback at golden hour</span></div>
      <div class="abg-i"><img src="{U}2021/02/square.jpg" alt="Southern Flinders Ranges" loading="lazy"><span>Southern Flinders Ranges, SA</span></div>
      <div class="abg-i"><img src="assets/img/bongil.jpg" alt="Bongil Bongil National Park" loading="lazy"><span>Bongil Bongil National Park, NSW</span></div>
      <div class="abg-i"><img src="{U}2021/01/Lorina-and-Tinnesha-in-EPBC-protected-sandstone-shrublands_photo-Donal-Sullivan5f911988b9c1d-scaled.jpg" alt="Warddeken rangers on Country" loading="lazy"><span>Warddeken IPA, NT</span></div>
      <div class="abg-i"><img src="{U}2021/02/Southern-Koala-05-scaled.jpg" alt="Koala" loading="lazy"><span>Southern Highlands, NSW</span></div>
      <div class="abg-i"><img src="{U}2021/02/sturt-national-park-08_Amanda-Cutlack-DPIE.jpg" alt="Sturt National Park" loading="lazy"><span>Sturt National Park, NSW</span></div>
      <div class="abg-i"><img src="{U}2021/01/LittlePenguins.jpg" alt="Little penguins" loading="lazy"><span>Granite Island, SA</span></div>
    </div>
  </div>
</section>'''
i = t.rindex('</style>')
t = t[:i] + gallery_css + t[i:]
ci = t.find('<section class="ab-cta"')
assert ci > 0
t = t[:ci] + gallery_html + '\n' + t[ci:]
open('about.html', 'w').write(t)
print('about.html: real exec + board with headshots, founder feature, gallery band')

# ---------- 5. replace every remaining Unsplash image with FNPW photography ----------
KEY = [
    ('koala', U+'2021/02/Southern-Koala-05-scaled.jpg'),
    ('wetland', U+'2021/02/NSW-NPWS-Yarrahapinni-Wetlands-National-Park-1.jpg'),
    ('coorong', U+'2021/02/NSW-NPWS-Yarrahapinni-Wetlands-National-Park-1.jpg'),
    ('penguin', U+'2021/01/Featured-projects-Penguins-lge.jpg'),
    ('wallaby', U+'2021/02/Brush-tailed-Rock-wallaby-school-education-KVPS-puppet-show-18-scaled.jpg'),
    ('parrot', U+'2022/02/Orange-belliedParrot_DPIPWE-scaled.jpg'),
    ('bird', U+'2021/01/Black-chinned-honeyeater-PETER-SAWYER-CYMK.jpg'),
    ('cockatoo', U+'2021/01/Black-Cockatoo-Too_big_nestling_240420-rotated-e1746404683346.jpg'),
    ('ranger', U+'2021/02/WArangers-lge.jpg'),
    ('volunteer', U+'2021/02/Lane-Cove-Bushcare-Program-2018-scaled.jpg'),
    ('planting', U+'2021/02/Koala-Alyson-Boyer-1-scaled.jpg'),
    ('nursery', U+'2022/03/Wail-Nursery.jpg'),
    ('devil', U+'2021/02/TasmanianDevil-MelanieWagner.jpg'),
    ('quoll', U+'2020/12/Quoll-lge.jpg'),
    ('flinders', U+'2021/02/square.jpg'),
    ('desert', U+'2021/02/sturt-national-park-08_Amanda-Cutlack-DPIE.jpg'),
    ('outback', U+'2021/02/sturt-national-park-08_Amanda-Cutlack-DPIE.jpg'),
    ('island', U+'2022/02/torrens-Island-bird.jpg'),
    ('fire', U+'2021/02/KNP-recovery-1-scaled.jpg'),
    ('forest', 'assets/img/bongil.jpg'),
    ('bush', 'assets/img/bongil.jpg'),
    ('tree', 'assets/img/bongil.jpg'),
]
POOL = ['assets/img/bongil.jpg', U+'2021/02/square.jpg', U+'2021/02/KNP-recovery-1-scaled.jpg',
        U+'2021/02/Ascent-37-Woomargama-2000px-Copy.jpg', U+'2021/01/feeding.jpg',
        U+'2021/02/heritage-Estates-05-lg.jpg', U+'2021/01/K2W-GER-Aerial.jpg']
import glob, itertools
pool_cycle = itertools.cycle(POOL)
total = 0
for f in glob.glob('*.html'):
    t = open(f).read()
    if 'images.unsplash.com' not in t:
        continue
    def swap(m):
        global total
        total += 1
        start = max(0, m.start()-300)
        ctx = t[start:m.end()+200].lower()
        for k, url in KEY:
            if k in ctx:
                return url
        return next(pool_cycle)
    t2 = re.sub(r'https://images\.unsplash\.com/[^"\'\s\\]+', swap, t)
    open(f, 'w').write(t2)
print(f'unsplash images replaced with FNPW photography: {total}')

print('AUDIT PASS COMPLETE')
