#!/usr/bin/env python3
"""Remote fnpw.org.au images (WP6, Nov 2026). Run from the repo root, re-runnable.

The pages still load most photographs from the live WordPress media library, and this
sandbox cannot reach fnpw.org.au, so nothing is downloaded or probed. Every <img> whose src
is on fnpw.org.au gets:

* width and height from the WordPress size suffix (-1024x683.jpg) when the file name has
  one, or from data/wp-media.json ("dims", the featured image's upload size, keyed by post
  slug) for the hero of that article, so the browser can reserve the box before the
  photograph arrives;
* when the src is a full-size original or a -scaled file and a 1024px resize of the same
  file is referenced somewhere on the site (so it is known to exist), the src moves to that
  1024px file, with a srcset of every resize the site has seen and a sizes attribute for
  the image's role. Guessed resizes are never written: an earlier srcset built from guessed
  crops 404'd on 312 of 365 files (see gen_articles.srcset);
* article heroes keep fetchpriority="high" and never carry loading="lazy"; every other
  remote image gets decoding="async".

Prints the counts. Run after gen_articles.py / gen_articles_bands.py / port_live.py.
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_images as B  # noqa: E402  (ancestors_of, parse_attrs, build_tag, role_for, SIZES)

ROOT = B.ROOT
URL_RE = re.compile(r'^(https://fnpw\.org\.au/wp-content/uploads/.*?)(-scaled)?(-(\d+)x(\d+))?(\.(?:jpe?g|png|webp|gif))$', re.I)
REMOTE_SRC = re.compile(r'https://fnpw\.org\.au/wp-content/uploads/[^"\s)\'<>]+')
HERO_FIG = re.compile(r'(^|\s)(ed-hero-im|pj-hero-im)(\s|$)')


def known_urls():
    """Every fnpw.org.au upload URL the site mentions, in pages and data files."""
    seen = set()
    pats = ['*.html', 'data/**/*.json', 'data/**/*.md', 'data/**/*.txt', 'tools/*.py']
    for pat in pats:
        for f in glob.glob(os.path.join(ROOT, pat), recursive=True):
            try:
                s = open(f, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            seen.update(REMOTE_SRC.findall(s))
    return seen


def index_variants(urls):
    """{(base, ext): {width: (url, height)}} for the sized resizes the site has seen."""
    idx = collections.defaultdict(dict)
    for u in urls:
        m = URL_RE.match(u)
        if m and m.group(4):
            idx[(m.group(1).lower(), m.group(6).lower())][int(m.group(4))] = (u, int(m.group(5)))
    return idx


def same_shape(sibs, w, h):
    """The resizes that share the aspect ratio of a w x h file: WordPress thumbnails such as
    150x150 are hard crops and would distort inside a srcset."""
    return {k: v for k, v in sibs.items() if abs(k / float(v[1]) - w / float(h)) < 0.02 * (w / float(h))}


def srcset_of(sibs):
    return ', '.join('%s %dw' % (sibs[k][0], k) for k in sorted(sibs))


def main():
    os.chdir(ROOT)
    media = json.load(open('data/wp-media.json', encoding='utf-8'))
    dims = media.get('dims', {})
    idx = index_variants(known_urls())
    n = collections.Counter()
    for path in sorted(glob.glob('*.html')):
        html = open(path, encoding='utf-8').read()
        slug = re.sub(r'^article-|\.html$', '', path)
        edits = []
        for m, anc in B.ancestors_of(html):
            attrs = B.parse_attrs(m.group(0))
            d = dict(attrs)
            src = d.get('src', '')
            um = URL_RE.match(src)
            if not um:
                continue
            n['remote'] += 1
            hero = bool(anc) and bool(HERO_FIG.search(anc[-1]))
            w = h = None
            srcset = None
            new_src = src
            sibs = idx.get((um.group(1).lower(), um.group(6).lower()), {})
            if um.group(4):
                w, h = int(um.group(4)), int(um.group(5))
                sibs = same_shape(sibs, w, h)
                if len(sibs) > 1:      # a resize whose siblings the site also uses
                    srcset = srcset_of(sibs)
            elif 1024 in sibs:
                new_src, h = sibs[1024]
                w = 1024
                sibs = same_shape(sibs, w, h)
                if len(sibs) > 1:
                    srcset = srcset_of(sibs)
                n['rewritten'] += 1
            elif hero and slug in dims:
                w, h = (int(x) for x in dims[slug].split('x'))
                n['dims_from_json'] += 1
            out = []
            for k, v in attrs:
                if k in ('width', 'height', 'decoding', 'fetchpriority', 'srcset') or (k == 'loading' and hero):
                    continue
                if k == 'src':
                    v = new_src
                out.append((k, v))
            if w and h:
                out.append(('width', str(w)))
                out.append(('height', str(h)))
                n['with_dims'] += 1
            if srcset:
                sizes = dict(out).get('sizes') or B.SIZES['hero' if hero else B.role_for(anc, attrs)]
                out = [(k, v) for k, v in out if k != 'sizes'] + [('srcset', srcset), ('sizes', sizes)]
                n['srcset'] += 1
            if hero:
                out.append(('fetchpriority', 'high'))
                n['heroes'] += 1
            out.append(('decoding', 'async'))
            tag = B.build_tag(out)
            if tag != m.group(0):
                edits.append((m.start(), m.end(), tag))
        if edits:
            for s, e, tag in reversed(edits):
                html = html[:s] + tag + html[e:]
            open(path, 'w', encoding='utf-8').write(html)
            n['pages'] += 1
    print('remote fnpw.org.au images: %(remote)d; src moved to a known 1024px resize: %(rewritten)d; '
          'width/height set: %(with_dims)d (of which %(dims_from_json)d from wp-media.json); '
          'srcset written: %(srcset)d; article heroes: %(heroes)d; pages changed: %(pages)d' % n)


if __name__ == '__main__':
    main()
