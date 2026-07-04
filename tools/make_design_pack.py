"""Build design/ pack: self-contained single-file versions of the 8 template
pages that define the whole site, for pasting into Claude design one at a time.

Each file inlines global.css, main.js, header and footer, so it renders
standalone. Design there, bring the file back, and the deltas get merged into
global.css / partials / generators (do not hand-edit the 121 real pages).

Re-run any time:  python3 tools/make_design_pack.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TEMPLATES = [
    ('index.html', 'home'),
    ('about.html', 'long-form content page'),
    ('projects.html', 'projects hub: filters, map, 83 cards'),
    ('saving-species.html', 'pillar page (template for all 3)'),
    ('project-warddeken-mayh.html', 'project detail, long (template for all 83)'),
    ('donate.html', 'donate front door to Raisely'),
    ('campaign.html', 'campaign landing template'),
    ('workplace-giving.html', 'simple content page (template for ~15 pages)'),
]

os.makedirs('design', exist_ok=True)
css = open('assets/css/global.css').read()
js = open('assets/js/main.js').read()

for fname, note in TEMPLATES:
    t = open(fname).read()
    t = t.replace('<link rel="stylesheet" href="assets/css/global.css">',
                  f'<style>\n/* === global.css (inlined for design) === */\n{css}\n</style>')
    t = t.replace('<script src="assets/js/main.js"></script>',
                  f'<script>\n{js}\n</script>')
    # local image paths -> keep (logo will 404 in the design tool; harmless)
    out = os.path.join('design', fname)
    open(out, 'w').write(f'<!-- DESIGN PACK: {note}. Source of truth is the repo; '
                         'merge changes back via Claude, do not copy this file over the original. -->\n' + t)
    print('packed', out, f'({os.path.getsize(out)//1024}KB)')
print('done. Pair each file with design/DESIGN-BRIEF.md when prompting.')
