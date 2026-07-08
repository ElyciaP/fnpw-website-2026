# FNPW Website Rebuild (2026)

A complete rebuild of [fnpw.org.au](https://fnpw.org.au) for the Foundation for National
Parks & Wildlife, designed and built in-house, aligned to the 2025 Brand Guidelines.

**Preview:** open `index.html`, or view the GitHub Pages link in this repo's About panel.

## What's here

- 121 pages: homepage, About (real team and board), Projects hub with map, three pillar
  pages, all 85 project pages (three fully written exemplars), Articles, Reports
  (21 real publications, 2018-2025), Get Involved suite, campaign template, legal pages
- One shared design system: `assets/css/global.css` + `partials/` header and footer
- Donations remain on Raisely: every donate action links to existing payment flows
- `data/projects.json`: the project dataset that generates pillar and project pages

## Key documents

- `PLAYBOOK.md` — week-by-week plan to WordPress launch
- `TROUBLESHOOTING.md` — failure modes and fixes for a non-developer maintainer
- `design/` — Claude design handoff pack and brand design brief
- `tools/` — page generators and the header/footer sync script

## Working on the site

```bash
python3 -m http.server 8000   # preview at http://localhost:8000
python3 tools/sync.py         # after editing partials/header.html or footer
```

Status: static build ~70% launch-ready. Remaining: content/message pass, WordPress
theme conversion on staging, QA, launch. See PLAYBOOK.md.
