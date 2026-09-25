"""Site-wide colour alignment to Mali's principles (Sep 2026).
Run from repo root: python3 sitewide.py
Rules are scoped: (file glob, selector regex, [(old, new), ...]) applied only inside matching CSS rule bodies.
"""
import re, glob, sys, collections, fnmatch

W = 'var(--wattle)'; WS = 'var(--wattle-soft)'; WM = 'var(--wattle-mid)'; WD = 'var(--wattle-dk)'
ES = 'var(--euc-soft)'; CR = 'var(--cream)'; BK = 'var(--bark)'; BM = 'var(--bark-mid)'
BT = 'var(--bark-text)'; WR = 'var(--waratah)'; WRD = 'var(--waratah-dk)'
def strip(c):  # solid 3px top line
    return ('background:' + c + ';')

GRAD_TO_BARK = lambda body: re.sub(r'background:linear-gradient\(to right,[^;{}]*?\)(?=;|$|\})', 'background:' + BK, body)
GRAD_TO_WAR = lambda body: re.sub(r'background:linear-gradient\(to right,[^;{}]*?\)(?=;|$|\})', 'background:' + WR, body)

RULES = [
 # ---------- global.css ----------
 ('assets/css/global.css', r'\.ftr li a:hover', [(WS, CR)]),
 ('assets/css/global.css', r'\.sec\.dark \.ey', [(W, ES)]),
 ('assets/css/global.css', r'\.sec\.dark \.ey::before', [(W, ES)]),
 ('assets/css/global.css', r'\.framed::before', [('var(--euc)', BM)]),
 ('assets/css/global.css', r'\.framed\.wt::before', [(W, BM)]),
 ('assets/css/global.css', r'\.sec\.dark \.hx-cta', [(W, ES)]),
 ('assets/css/global.css', r'\.sec\.dark \.hx-cta:hover', [(WM, CR)]),
 ('assets/css/global.css', r'\.sec\.dark \.btn-p', [('background:' + W, 'background:' + WR), ('border-color:' + W, 'border-color:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('assets/css/global.css', r'\.sec\.dark \.btn-p:hover', [('background:' + WS, 'background:' + WRD), ('border-color:' + WS, 'border-color:' + WRD), ('color:var(--euc-deep)', 'color:' + CR)]),
 ('assets/css/global.css', r'\.chi \.btn-p,\.nh \.btn-p,\.ph \.btn-p', [('background:' + W, 'background:' + WR), ('border-color:' + W, 'border-color:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('assets/css/global.css', r'\.hx-tree-tag::before', [(WD, BK)]),
 ('assets/css/global.css', r'\.hx-quote', [(W, BK)]),
 ('assets/css/global.css', r'\.pj-hero \.ey', [(W, ES)]),
 ('assets/css/global.css', r'\.pj-hero \.ey::before', [(W, ES)]),
 ('assets/css/global.css', r'\.pj-story \.ey', [(W, ES)]),
 ('assets/css/global.css', r'\.pj-story \.ey::before', [(W, ES)]),
 # campaign (purple + yellow stays): only calm the three-colour top lines to solid baby yellow
 ('assets/css/global.css', r'\.cmp-hero::before|\.cmp-final::before', [('linear-gradient(to right,var(--wattle) 0,var(--waratah-soft) 50%,var(--reef-soft) 100%)', '#F8EEA9')]),

 # ---------- article pages (163) ----------
 ('article-*.html', r'\.ed-kicker-top', [(W, ES)]),
 ('article-*.html', r'\.ed-pull', [(W, BK)]),
 ('article-*.html', r'\.ed-break \.ed-kicker', [(WM, ES)]),

 # ---------- hero accent phrases: upright, same weight ----------
 ('*.html', r'\.fb-hero-content h1 em|\.v-cta-head h2 em', [('font-style:italic', 'font-style:normal'), ('font-weight:400', 'font-weight:inherit'), ('font-weight:500', 'font-weight:inherit')]),

 # ---------- articles / reports ----------
 ('articles.html', r'\.nh \.deco\.d2', [(W, ES)]),
 ('reports.html', r'\.nh \.deco\.d2', [(W, ES)]),
 ('articles.html', r'\.feat-card::before', [('var(--wattle) 66%', 'var(--bark) 66%')]),
 ('reports.html', r'\.feat-card::before', [('var(--wattle) 66%', 'var(--bark) 66%')]),
 ('articles.html', r'\.nl-strip::before', [GRAD_TO_BARK]),
 ('reports.html', r'\.nl-strip::before', [GRAD_TO_BARK]),
 ('articles.html', r'\.nl-f button', [('background:' + W, 'background:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('reports.html', r'\.nl-f button', [('background:' + W, 'background:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('reports.html', r'\.rpt\.bk::before', [('linear-gradient(to right,var(--bark),var(--wattle))', BK)]),

 # ---------- ways you can get involved ----------
 ('ways-you-can-get-involved.html', r'\.pa-n', [(W, ES)]),

 # ---------- bequests ----------
 ('bequests.html', r'\.suggest::before', [GRAD_TO_BARK]),
 ('bequests.html', r'\.suggest \.lab', [(W, ES)]),
 ('bequests.html', r'\.bq-word \.ey|\.bq-word \.ey::before', [(W, ES)]),
 ('bequests.html', r'\.bform::before', [('linear-gradient(to right,var(--euc),var(--bark),var(--wattle))', WR)]),
 ('bequests.html', r'\.ty\.t-wat', [(W, BK), (WS, 'var(--bark-soft)')]),

 # ---------- index leftovers ----------
 ('index.html', r'\.hx-kicker::before', [(W, ES)]),

 # ---------- about leftovers ----------
 ('about.html', r'\.ap\.hl \.ic', [(WD, BT)]),
 ('about.html', r'\.tl::before', [('var(--euc),var(--wattle),var(--bark)', 'var(--euc),var(--bark)')]),
 ('about.html', r'\.tl-i\.wt \.yr', [('background:' + W, 'background:' + BK), ('color:var(--soil)', 'color:' + CR)]),
 ('about.html', r'\.tc-ph', [(WS, ES)]),

 # ---------- volunteer ----------
 ('volunteer.html', r'\.fb-hero-content \.btn-p', [('background:' + W, 'background:' + WR), ('border-color:' + W, 'border-color:' + WR), ('color:var(--euc-deep)', 'color:' + CR)]),
 ('volunteer.html', r'\.fb-hero-content \.btn-p:hover', [('background:' + WS, 'background:' + WRD), ('border-color:' + WS, 'border-color:' + WRD)]),
 ('volunteer.html', r'\.fb-hero-content \.btn-g:hover', [(WS, ES)]),
 ('volunteer.html', r'\.v-act-im \.badge', [('background:' + WS, 'background:' + BM), ('color:var(--euc-deep)', 'color:' + CR)]),
 ('volunteer.html', r'\.v-act\.flip \.v-act-stat', [(WD, BK)]),
 ('volunteer.html', r'\.v-map-frame::before', [GRAD_TO_BARK]),
 ('volunteer.html', r'\.v-sticky-in b', [(WS, ES)]),
 ('volunteer.html', r'\.v-prog::before', [GRAD_TO_BARK]),
 ('volunteer.html', r'\.v-prog-h \.ey', [(WS, ES)]),
 ('volunteer.html', r'\.v-prog-card \.ic', [('rgba(196,169,39,.18)', 'rgba(198,235,202,.14)'), (WS, ES)]),
 ('volunteer.html', r'\.v-prog-card \.v-prog-big', [(WS, ES)]),
 ('volunteer.html', r'\.v-prog-card ul li::before', [('background:' + WS + ';opacity:.7', 'background:' + BK)]),
 ('volunteer.html', r'\.v-prog-cancel-i strong', [(WS, ES)]),
 ('volunteer.html', r'\.v-ben-card\.c3', [(WD, BK)]),
 ('volunteer.html', r'\.v-ben-card\.c3 \.ic', [('rgba(196,169,39,.14)', 'rgba(171,115,65,.14)'), (WD, BT)]),
 ('volunteer.html', r'\.v-ben-card\.c3 ul li::before', [(WD, BK)]),
 ('volunteer.html', r'\.v-tl-i:nth-child\(3\) \.v-tl-ic', [(W, BK)]),
 ('*.html', r'\.v-cta-card::before', [GRAD_TO_BARK]),

 # ---------- contact ----------
 ('contact.html', r'\.cinfo-card\.c3::before', [(W, BK)]),
 ('contact.html', r'\.cinfo-card\.c3 \.row svg', [(WD, BT)]),
 ('contact.html', r'\.cform-card::before', [GRAD_TO_WAR]),

 # ---------- why your support is needed ----------
 ('why-your-support-is-needed.html', r'\.wy-t:nth-child\(3\)', [(W, BK)]),
 ('why-your-support-is-needed.html', r'\.wy-dark \.ey', [(W, ES)]),
 ('why-your-support-is-needed.html', r'\.wy-n strong', [(W, ES)]),

 # ---------- fundraising / partner / gift a tree / news ----------
 ('fundraising-with-fnpw.html', r'\.fw-p\.b', [(W, BK)]),
 ('partner.html', r'\.gov \.ey', [(W, ES)]),
 ('partner.html', r'\.why-c\.b3', [(W, BK)]),
 ('partner.html', r'\.why-c\.b3 \.num', [(WD, BT)]),
 ('partner.html', r'\.case-strip::before', [GRAD_TO_BARK]),
 ('partner.html', r'\.case-strip \.btn-p', [('background:' + W, 'background:' + WR), ('border-color:' + W, 'border-color:' + WR), ('color:var(--euc-deep)', 'color:' + CR)]),
 ('partner.html', r'\.case-strip \.btn-p:hover', [('background:' + BT, 'background:' + WRD), ('border-color:' + BT, 'border-color:' + WRD)]),
 ('gift-a-tree.html', r'\.gt-hero \.ey|\.gt-hero \.ey::before', [(W, ES)]),
 ('in-the-news.html', r'\.nw-hero \.ey', [(W, ES)]),
 ('how-your-contributions-help.html', r'\.hc-go', [(W, BK)]),

 # ---------- projects ----------
 ('projects.html', r'\.mm\.hl \.ic', [('rgba(196,169,39,.18)', 'rgba(171,115,65,.14)'), (WD, BT)]),
 ('projects.html', r'\.ns-f button', [('background:' + W, 'background:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('projects.html', r'\.ns-f button:hover', [('background:' + WD, 'background:' + WRD)]),
 ('projects.html', r'\.im-chip\.pc-healing', [(WD, BT)]),

 # ---------- donate land ----------
 ('donate-land.html', r'\.fb-hero-content \.ey|\.fb-hero-content \.ey::before', [(WS, ES)]),
 ('donate-land.html', r'\.dl-open-im \.stamp small', [(WS, 'var(--bark-soft)')]),
 ('donate-land.html', r'\.dl-path\.p3', [(W, BK)]),
 ('donate-land.html', r'\.dl-story-pull', [(W, BK)]),
 ('donate-land.html', r'\.dl-form::before', [('linear-gradient(to right,var(--euc),var(--bark),var(--wattle))', WR)]),

 # ---------- workplace giving ----------
 ('workplace-giving.html', r'\.wg-cta \.ey', [(W, ES)]),
 ('workplace-giving.html', r'.*\.wg-cta \.btn-p', [('background:' + W, 'background:' + WR), ('border-color:' + W, 'border-color:' + WR), ('color:var(--soil)', 'color:' + CR)]),
 ('workplace-giving.html', r'\.wg-cta \.btn-p:hover', [('background:' + WS, 'background:' + WRD), ('border-color:' + WS, 'border-color:' + WRD), ('color:var(--soil)', 'color:' + CR)]),

 # ---------- donate ----------
 ('donate.html', r'\.dh \.deco\.d2', [(W, ES)]),
 ('donate.html', r'\.imp\.hl', [(W, BK)]),
 ('donate.html', r'\.imp\.hl \.amt', [(WD, BT)]),
 ('donate.html', r'\.tax::before|\.tax-info::before', [GRAD_TO_BARK]),
 ('donate.html', r'\.don-card::before', [GRAD_TO_WAR]),
 ('donate.html', r'\.freq button \.pill', [('background:' + W, 'background:' + BM), ('color:var(--euc-deep)', 'color:' + CR)]),
 ('donate.html', r'\.cover-fee', [('background:' + WS, 'background:var(--bark-soft)')]),
 ('donate.html', r'\.tax-info \.other a', [(WS, ES)]),
]

# inline / attribute-level swaps (not inside CSS rules)
RAW = [
 ('ways-you-can-get-involved.html', 'style="--rowc:var(--wattle-soft)"', 'style="--rowc:var(--bark-soft)"'),
 ('growing-national-parks.html', 'box-shadow:12px 12px 0 var(--euc-pale)', 'box-shadow:12px 12px 0 var(--bark-mid)'),
 ('healing-the-land.html', 'box-shadow:12px 12px 0 var(--euc-pale)', 'box-shadow:12px 12px 0 var(--bark-mid)'),
 ('saving-species.html', 'box-shadow:12px 12px 0 var(--euc-pale)', 'box-shadow:12px 12px 0 var(--bark-mid)'),
]

def css_regions(t, is_css):
    if is_css: return [(0, len(t))]
    return [(m.start(1), m.end(1)) for m in re.finditer(r'<style[^>]*>(.*?)</style>', t, re.S)]

hits = collections.Counter(); touched = set()
def process(path):
    t = open(path, encoding='utf-8').read(); orig = t
    is_css = path.endswith('.css')
    key = 'assets/css/global.css' if path.endswith('assets/css/global.css') else path
    for gl, sel, reps in RULES:
        if not fnmatch.fnmatch(key, gl): continue
        rx = re.compile(r'\s*(?:' + sel + r')\s*')
        out = []; last = 0
        for a, b in css_regions(t, is_css):
            seg = t[a:b]
            def sub(m):
                s, body = m.group(1), m.group(2)
                s_clean = re.sub(r'/\*.*?\*/', '', s, flags=re.S).strip()
                if not rx.fullmatch(s_clean): return m.group(0)
                nb = body
                for r in reps:
                    nb = r(nb) if callable(r) else nb.replace(r[0], r[1])
                if nb != body: hits[(gl, sel)] += 1
                return s + '{' + nb + '}'
            seg2 = re.sub(r'([^{}]+)\{([^{}]*)\}', sub, seg)
            out.append(t[last:a]); out.append(seg2); last = b
        out.append(t[last:]); t = ''.join(out)
    for f, o, n in RAW:
        if path == f and o in t: t = t.replace(o, n); hits[('RAW', f + o)] += 1
    if t != orig:
        open(path, 'w', encoding='utf-8').write(t); touched.add(path)

files = sorted(glob.glob('*.html')) + ['assets/css/global.css']
if len(sys.argv) > 1 and sys.argv[1] == 'wp': files.append('wp/themes/fnpw-2026/assets/css/global.css')
for f in files:
    process(f)
# wp mirror uses the global.css rules
missing = [(g, s) for g, s, _ in RULES if hits[(g, s)] == 0] + [('RAW', f + o) for f, o, n in RAW if hits[('RAW', f + o)] == 0]
print('files touched:', len(touched))
print('rules with no hit:'); [print('  ', m) for m in missing]
