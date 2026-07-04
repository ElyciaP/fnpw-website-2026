"""One-off build step: extend global.css with shared components, generate all
pages, add the pillar band to the projects hub, upgrade sync.py's active-nav
logic, then inject headers/footers everywhere."""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MARK = '/* === v2 shared components (generated) === */'

def rules_from(fname, pattern):
    css = ''.join(re.findall(r'<style[^>]*>(.*?)</style>', open(fname).read(), re.S))
    out = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        sel = m.group(1).strip()
        if re.search(pattern, sel) and '@media' not in sel:
            out.append(f'{sel}{{{m.group(2).strip()}}}')
    return out

g = open('assets/css/global.css').read()
if MARK not in g:
    pc = rules_from('projects.html', r'\.(pc|pg|ps)(\b|-)')
    cmp_ = rules_from('bring-back-the-bush.html', r'\.cmp-')
    seen, dedup = set(), []
    for r in pc + cmp_:
        if r not in seen:
            seen.add(r); dedup.append(r)
    extra = '''
.ch{padding:8.5rem 0 4rem;background:var(--paper)}
.chi{position:relative;background:var(--euc-deep);color:#fff}
.chi::before{content:"";position:absolute;inset:0;background:var(--chi) center/cover;opacity:.28}
.chi .cw{position:relative}
.chi h1{color:#fff}
.chi .lede{color:rgba(255,255,255,.85)}
.port-note{border:2px dashed var(--wattle-dk);background:var(--wattle-soft);color:var(--ink);padding:.9rem 1.1rem;border-radius:10px;font-size:.9rem;margin:1.2rem 0}
.pg{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:1.6rem}
.pc-link{display:block;color:inherit;text-decoration:none;height:100%}
.pb-parks{background:var(--euc)}.pb-species{background:var(--waratah)}.pb-healing{background:var(--bark)}
.pmeta{background:var(--paper);border:1px solid var(--rule);border-radius:14px;padding:1.4rem}
.pmeta-i{display:flex;justify-content:space-between;gap:1rem;padding:.7rem 0;border-bottom:1px solid var(--rule)}
.pmeta-i:last-child{border-bottom:0}
.pmeta-i span{color:var(--stone);font-size:.85rem}
.lcg{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1.4rem}
.lc{position:relative;display:block;background:#fff;border:1px solid var(--rule);border-radius:14px;padding:1.5rem 2.6rem 1.5rem 1.5rem;color:inherit;text-decoration:none;transition:transform .18s,box-shadow .18s}
.lc:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(15,49,50,.12)}
.lc h3{margin-bottom:.4rem;color:var(--euc-deep)}
.lc p{font-size:.92rem;color:var(--stone)}
.lc-go{position:absolute;right:1.1rem;top:50%;transform:translateY(-50%);font-size:1.6rem;color:var(--euc)}
.fq{border:1px solid var(--rule);border-radius:12px;background:#fff;margin-bottom:.8rem;overflow:hidden}
.fq summary{cursor:pointer;padding:1.05rem 1.3rem;font-family:var(--ff-d);font-weight:600;list-style:none;position:relative}
.fq summary::after{content:"+";position:absolute;right:1.2rem;color:var(--euc);font-size:1.2rem}
.fq[open] summary::after{content:"\\2212"}
.fq-a{padding:0 1.3rem 1.1rem;color:var(--char)}
.prog-wrap{margin-top:1.6rem;max-width:420px}
.prog{height:13px;background:rgba(255,255,255,.25);border-radius:99px;overflow:hidden}
.prog i{display:block;height:100%;background:linear-gradient(90deg,var(--wattle),var(--wattle-soft));border-radius:99px}
.prog-lbl{font-size:.9rem;margin-top:.5rem}
.statrow{display:flex;gap:2.4rem;flex-wrap:wrap;margin:1.6rem 0}
.srch{width:100%;max-width:560px;font:inherit;padding:.9rem 1.2rem;border:2px solid var(--euc);border-radius:12px;background:#fff}
.srch-res{list-style:none;margin-top:1.4rem;max-width:560px}
.srch-res li{border-bottom:1px solid var(--rule);padding:.7rem 0}
.pilband{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem;margin:0 0 2.4rem}
'''
    g += f'\n{MARK}\n{extra}\n' + '\n'.join(dedup) + '\n'
    open('assets/css/global.css', 'w').write(g)
    print(f'global.css extended: +{len(dedup)} extracted rules')

# generate pages
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import gen_projects, gen_pages
gen_projects.main()
gen_pages.main()

# pillar band on the projects hub
t = open('projects.html').read()
if 'pilband' not in t:
    band = '''<section class="sec"><div class="cw rv">
<span class="ey">Three pillars</span>
<h2 style="margin:.8rem 0 1.4rem">Explore projects by pillar</h2>
<div class="pilband">
<a class="lc" href="growing-national-parks.html"><h3>Growing National Parks</h3><p>Adding land to the protected estate.</p><span class="lc-go">&rsaquo;</span></a>
<a class="lc" href="saving-species.html"><h3>Saving Species</h3><p>Recovery work for threatened plants and animals.</p><span class="lc-go">&rsaquo;</span></a>
<a class="lc" href="healing-the-land.html"><h3>Healing the Land</h3><p>Restoring habitat, waterways and cultural land care.</p><span class="lc-go">&rsaquo;</span></a>
</div></div></section>
'''
    anchor = '<section style="background:var(--cream)">'
    assert anchor in t, 'projects.html anchor not found'
    t = t.replace(anchor, band + anchor, 1)
    open('projects.html', 'w').write(t)
    print('projects.html: pillar band added')

# upgrade sync.py active-nav logic
s = open('tools/sync.py').read()
if 'def active_for' not in s:
    s = s.replace(
        "    a = ACTIVE.get(p)",
        "    a = active_for(p)")
    s = s.replace(
        "hdr = open(os.path.join(ROOT, 'partials/header.html')).read()",
        '''PILLARS = ('growing-national-parks.html', 'saving-species.html', 'healing-the-land.html')

def active_for(p):
    if p.startswith('project-') or p in PILLARS:
        return 'projects.html'
    if p.startswith('corporate-volunteering-'):
        return 'volunteer.html'
    return ACTIVE.get(p)

hdr = open(os.path.join(ROOT, 'partials/header.html')).read()''')
    open('tools/sync.py', 'w').write(s)
    print('sync.py upgraded')

r = subprocess.run(['python3', 'tools/sync.py'], capture_output=True, text=True)
updated = r.stdout.count('updated')
print(f'sync: {updated} pages injected')

# verify
import glob
from html.parser import HTMLParser
bad = []
for f in sorted(glob.glob('*.html')):
    t = open(f).read()
    if '<!-- @header -->' not in t or t.count('</header>') != 1:
        bad.append((f, 'header'))
    if 'assets/css/global.css' not in t:
        bad.append((f, 'css'))
    try:
        HTMLParser().feed(t)
    except Exception as e:
        bad.append((f, f'parse:{e}'))
print('pages total:', len(glob.glob('*.html')), '| problems:', bad if bad else 'NONE')
