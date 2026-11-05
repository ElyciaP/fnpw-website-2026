#!/usr/bin/env python3
"""Responsive local images (WP6, Nov 2026).

Run from the repo root:

    python3 tools/build_images.py          # resize originals, build variants, rewrite HTML
    python3 tools/build_images.py --html   # rewrite HTML only, from the manifest (after any generator)
    python3 tools/build_images.py --report # print the byte totals and stop

What it does, idempotently:

1. Finds every local raster photograph (JPEG/PNG under assets/img) that a root page,
   partial, stylesheet, script or data file references. Logos, partner marks, badges,
   the map artwork (already WebP/PNG/SVG), illustrations with real alpha and anything
   under assets/img/r or assets/img/_to_delete are not photographs and are left alone.
2. Shrinks each photograph in place to at most 1600px on the long side and re-encodes it
   once as a progressive JPEG at q82 (kept only when that is smaller or a resize was needed).
   A PNG photograph without alpha becomes a JPEG and every reference is updated. The
   manifest remembers the processed byte size, so a second run touches nothing.
3. Writes WebP variants at 480, 800, 1200 and 1600 wide (never upscaling; q78) into
   assets/img/r/<name>-<w>.webp and records them in assets/img/r/manifest.json. The
   shrunk original is the JPEG fallback; it is not duplicated into assets/img/r.
4. Rewrites each <img> of such a photograph into a <picture> with a WebP srcset, a sizes
   attribute chosen from the image's role (hero 100vw, card thirds, two-column halves,
   wide content) and the JPEG fallback <img>, keeping alt, class, style, loading and the
   other attributes. Heroes get fetchpriority="high" and no lazy attribute; every other
   photograph gets loading="lazy". All get decoding="async" and width/height from the
   shrunk file.

Generators (gen_*.py, port_live.py, build_gat.py) still emit plain <img> tags. Run
`python3 tools/build_images.py --html` after any of them, the same way apply_alt.py is run.
Pictures this tool wrote are recognised by their assets/img/r/ srcset and are rebuilt from
scratch on every run, so changing WIDTHS or the sizes map here is enough to update the site.
"""
import glob
import json
import os
import re
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = 'assets/img'
OUT = 'assets/img/r'
MANIFEST = os.path.join(OUT, 'manifest.json')
WIDTHS = (480, 800, 1200, 1600)
MAX_SIDE = 1600
JPEG_Q = 82          # the shrunk original
FALLBACK_Q = 80      # the <img> fallback in assets/img/r
WEBP_Q = 78

# Files under assets/img that are artwork rather than photographs.
NOT_PHOTO = re.compile(r'(fnpw-logo|og-default|favicon|apple-touch-icon|icon-/partners/|55-badge|projects-map|impact-tree-|placeholder-|/_to_delete/|^assets/img/r/)')

# sizes by role. Ancestor class names decide the role; the first match wins.
SIZES = {
    'hero': '100vw',
    'card': '(min-width: 900px) 33vw, (min-width: 600px) 50vw, 100vw',
    'two': '(min-width: 880px) 50vw, 100vw',
    'wide': '(min-width: 1280px) 1240px, 100vw',
}
HERO_CLASSES = re.compile(r'(^|\s)(hero|hx-hero|hx-hero-bg|fb-hero-bg|ab-hero-bg|pj-hero-im|gw-hero|ct-hero|proj-hero)(\s|$)')
WIDE_CLASSES = re.compile(r'(^|\s)(pj-wide|gw-im-pano|ip-bush-art|pj-q|imap|ed-bleed|ed-wide)(\s|$)')
CARD_CLASSES = re.compile(r'(^|\s)(pc-im|pcard-im|fl-im|hx-pil-im|art-im|abs-im|pj-rcard|pj-gal|v-car-s|vg-page|gw-pc|gw-pil-g|case-im|'
                          r'opp|aud|rp-cov|rp-g|feat-img|hx-ir-cov|g3|g4|also-g|pj-readgrid|fls-track|gr-im|pw-im|pj-fig|ed-col|pa-g)(\s|$)')
PLAIN_PARENT = re.compile(r'(^|\s)(gw-rq)(\s|$)')
TWO_CLASSES = re.compile(r'(^|\s)(pj-band-im|pj-duo|pj-story-im|pj-storypair|pa-im|two|story|gw-im-side|gw-pro-im|ab-proof|ip-cs-img|'
                         r'feat|wpn|gw-feat-im|gw-rq|gw-ty|gt-split-im|ip-rpt|v-act-im|dl-open-im)(\s|$)')

VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'track', 'wbr', 'area', 'base', 'col', 'embed', 'param'}
TAG_RE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*)>', re.S)
IMG_RE = re.compile(r'<img\b[^>]*>', re.I)
PICTURE_RE = re.compile(r'<picture>\s*<source\b[^>]*srcset="assets/img/r/[^"]*"[^>]*>\s*(<img\b[^>]*>)\s*</picture>', re.I)
ATTR_RE = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s"\'=<>`]+))?')


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


def text_files():
    """Every file whose text can reference an image."""
    pats = ['*.html', 'partials/*.html', 'assets/css/*.css', 'assets/js/*.js', 'data/*.json',
            'data/**/*.json', 'data/**/*.md', 'tools/*.py', 'wp/**/*.php', 'wp/**/*.css', 'wp/**/*.json',
            'design/*.html', 'design/*.md', '*.md']
    seen = set()
    for pat in pats:
        for f in glob.glob(os.path.join(ROOT, pat), recursive=True):
            if os.path.isfile(f) and f not in seen:
                seen.add(f)
                yield f


def referenced_paths():
    refs = set()
    for f in text_files():
        try:
            s = open(f, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for m in re.finditer(r'assets/img/[A-Za-z0-9_./ -]+?\.(?:jpe?g|png|webp)', s, re.I):
            refs.add(m.group(0))
    return refs


def has_alpha(im):
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        a = im.convert('RGBA').getchannel('A')
        lo, hi = a.getextrema()
        return lo < 250
    return False


def photo_sources(refs):
    """Local photographs referenced somewhere, as repo-relative paths."""
    out = []
    for p in sorted(refs):
        if NOT_PHOTO.search(p):
            continue
        full = os.path.join(ROOT, p)
        if not os.path.isfile(full):
            continue
        if not re.search(r'\.(jpe?g|png)$', p, re.I):
            continue
        out.append(p)
    return out


def variant_name(src):
    base = os.path.splitext(os.path.basename(src))[0]
    folder = os.path.basename(os.path.dirname(src))
    # subfolders keep their name so two photos called hero.jpg cannot collide
    return base if folder == 'img' else '%s-%s' % (folder, base)


def shrink_in_place(src, manifest):
    """Shrink the original to MAX_SIDE and re-encode it once at JPEG_Q.

    Returns (path, w, h, old_path_or_None); the path changes for a PNG photograph, which
    becomes a JPEG. A file whose byte size matches the manifest was processed by an
    earlier run and is left exactly as it is, so repeated runs never re-encode."""
    full = os.path.join(ROOT, src)
    rec = manifest.get(src)
    if rec and rec.get('size') == os.path.getsize(full):
        return src, rec['w'], rec['h'], None
    im = Image.open(full)
    im = ImageOps.exif_transpose(im)
    is_png = src.lower().endswith('.png')
    if is_png and has_alpha(im):
        return None  # artwork with transparency: not a photograph
    w, h = im.size
    resized = False
    if max(w, h) > MAX_SIDE:
        scale = MAX_SIDE / float(max(w, h))
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        w, h = im.size
        resized = True
    icc = im.info.get('icc_profile')
    if is_png:
        new = re.sub(r'\.png$', '.jpg', src, flags=re.I)
        im.convert('RGB').save(os.path.join(ROOT, new), 'JPEG', quality=JPEG_Q, optimize=True, progressive=True)
        os.remove(full)
        return new, w, h, src
    tmp = full + '.tmp'
    im.convert('RGB').save(tmp, 'JPEG', quality=JPEG_Q, optimize=True, progressive=True, icc_profile=icc)
    if resized or os.path.getsize(tmp) < os.path.getsize(full):
        os.replace(tmp, full)       # smaller, or had to shrink anyway
    else:
        os.remove(tmp)              # the source was already lighter than q82: keep it
    return src, w, h, None


def build_variants(src, w, h, manifest):
    """WebP at each width below the source width, plus the native width. The JPEG fallback
    that the <img> carries is the shrunk original itself (one file, shared with CSS and JSON
    references, instead of a duplicate in assets/img/r)."""
    full = os.path.join(ROOT, src)
    name = variant_name(src)
    size = os.path.getsize(full)
    rec = manifest.get(src)
    widths = [x for x in WIDTHS if x < w]
    if w not in widths:
        widths.append(w)
    want = ['%s/%s-%d.webp' % (OUT, name, x) for x in widths]
    fresh = (rec and rec.get('size') == size and rec.get('w') == w and rec.get('widths') == widths
             and all(os.path.isfile(os.path.join(ROOT, v)) for v in want))
    if fresh:
        return rec
    im = ImageOps.exif_transpose(Image.open(full)).convert('RGB')
    for x, out in zip(widths, want):
        v = im if x == w else im.resize((x, max(1, round(h * x / float(w)))), Image.LANCZOS)
        v.save(os.path.join(ROOT, out), 'WEBP', quality=WEBP_Q, method=6)
    rec = {'w': w, 'h': h, 'size': size, 'widths': widths, 'webp': want}
    manifest[src] = rec
    return rec


def parse_attrs(tag):
    inner = tag[4:].rstrip('>').rstrip('/').strip()
    attrs = []
    for m in ATTR_RE.finditer(inner):
        k, v = m.group(1), m.group(2)
        if v is None:
            attrs.append((k, None))
        else:
            attrs.append((k, v.strip('"\'')))
    return attrs


def build_tag(attrs):
    parts = []
    for k, v in attrs:
        parts.append(k if v is None else '%s="%s"' % (k, v))
    return '<img ' + ' '.join(parts) + '>'


def role_for(ancestors, attrs):
    """ancestors: list of class strings from the outermost to the parent."""
    d = dict(attrs)
    if d.get('fetchpriority') == 'high':
        return 'hero'
    own = d.get('class', '')
    near = ' '.join(ancestors[-3:]) + ' ' + own
    if HERO_CLASSES.search(near):
        return 'hero'
    for a in reversed(ancestors[-4:]):
        if WIDE_CLASSES.search(a):
            return 'wide'
        if CARD_CLASSES.search(a):
            return 'card'
        if TWO_CLASSES.search(a):
            return 'two'
    return 'two'


def ancestors_of(html):
    """Yield (match, ancestor_classes) for every <img> in the document, using a tolerant tag stack."""
    stack = []
    for m in TAG_RE.finditer(html):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if name in ('script', 'style'):
            continue
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
            continue
        if name == 'img':
            yield m, [c for _, c in stack]
            continue
        if name in VOID or attrs.rstrip().endswith('/'):
            continue
        c = re.search(r'\bclass\s*=\s*"([^"]*)"', attrs)
        stack.append((name, c.group(1) if c else ''))


def unwrap_pictures(html, manifest):
    """Turn pictures written by an earlier run back into plain <img> tags pointing at the source."""
    def repl(m):
        # drop the attributes this tool adds, so the role is read from the markup again
        attrs = [(k, v) for k, v in parse_attrs(m.group(1)) if k not in ('fetchpriority', 'decoding')]
        return build_tag(attrs)
    return PICTURE_RE.sub(repl, html)


def rewrite_html(path, manifest, renames, stats):
    html = open(path, encoding='utf-8').read()
    orig = html
    for old, new in renames.items():
        html = html.replace(old, new)
    html = unwrap_pictures(html, manifest)
    # collect rewrites first, then apply from the end so offsets stay valid
    edits = []
    for m, anc in ancestors_of(html):
        tag = m.group(0)
        attrs = parse_attrs(tag)
        d = dict(attrs)
        src = d.get('src', '').split('?')[0]   # old ?v= cache-busters fall away
        rec = manifest.get(src)
        if not rec:
            continue
        role = role_for(anc, attrs)
        hero = role == 'hero'
        # a parent styled with a child combinator (.x>img) in a page style block cannot take
        # a <picture> wrapper without a CSS change, so that image stays a plain <img>
        plain = bool(anc) and bool(PLAIN_PARENT.search(anc[-1]))
        out = []
        for k, v in attrs:
            if k in ('width', 'height', 'loading', 'decoding', 'fetchpriority', 'sizes', 'srcset'):
                continue
            if k == 'src':
                v = src
            out.append((k, v))
        out.append(('width', str(rec['w'])))
        out.append(('height', str(rec['h'])))
        if hero:
            out.append(('fetchpriority', 'high'))
        else:
            # every photograph that is not a hero is lazy (WP6 brief); heroes are the only
            # images that must be in the first request wave
            out.append(('loading', 'lazy'))
        out.append(('decoding', 'async'))
        if plain:
            edits.append((m.start(), m.end(), build_tag(out)))
            stats['plain'] += 1
            continue
        srcset = ', '.join('%s %dw' % (v, w) for v, w in zip(rec['webp'], rec['widths']))
        pic = ('<picture><source type="image/webp" srcset="%s" sizes="%s">%s</picture>'
               % (srcset, SIZES[role], build_tag(out)))
        edits.append((m.start(), m.end(), pic))
        stats['roles'][role] = stats['roles'].get(role, 0) + 1
    for s, e, pic in reversed(edits):
        html = html[:s] + pic + html[e:]
    if html != orig:
        open(path, 'w', encoding='utf-8').write(html)
        stats['pages'] += 1
    stats['pictures'] += len(edits)


def apply_renames(renames):
    """PNG photographs that became JPEGs: fix every non-HTML reference (HTML is done in rewrite_html)."""
    if not renames:
        return
    for f in text_files():
        if f.endswith('.html') and os.path.dirname(f) == ROOT:
            continue
        try:
            s = open(f, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        n = s
        for old, new in renames.items():
            n = n.replace(old, new)
        if n != s:
            open(f, 'w', encoding='utf-8').write(n)


def folder_bytes(folder):
    total = 0
    for root, _, files in os.walk(os.path.join(ROOT, folder)):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total


def main(argv):
    os.chdir(ROOT)
    if '--report' in argv:
        print('assets/img %d bytes (%.1f MB), of which assets/img/r %d bytes'
              % (folder_bytes(IMG), folder_bytes(IMG) / 1e6, folder_bytes(OUT) if os.path.isdir(OUT) else 0))
        return
    os.makedirs(OUT, exist_ok=True)
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    renames = {}
    if '--html' not in argv:
        before = folder_bytes(IMG)
        refs = referenced_paths()
        for src in photo_sources(refs):
            if src in manifest and not os.path.isfile(src):
                continue
            r = shrink_in_place(src, manifest)
            if r is None:
                continue
            new, w, h, old = r
            if old:
                renames[old] = new
                manifest.pop(old, None)
            build_variants(new, w, h, manifest)
        # drop manifest rows whose source vanished, and their variants
        for src in list(manifest):
            if not os.path.isfile(src):
                for v in manifest[src]['webp']:
                    if os.path.isfile(v):
                        os.remove(v)
                del manifest[src]
        json.dump(manifest, open(MANIFEST, 'w'), indent=1, sort_keys=True)
        apply_renames(renames)
        print('photographs: %d, webp variants: %d files' % (len(manifest), sum(len(r['webp']) for r in manifest.values())))
        print('assets/img before %d bytes, after %d bytes' % (before, folder_bytes(IMG)))
    stats = {'pages': 0, 'pictures': 0, 'plain': 0, 'roles': {}}
    for f in sorted(glob.glob('*.html')):
        rewrite_html(f, manifest, renames, stats)
    print('pictures: %d on %d pages changed, roles %s, plain img kept: %d'
          % (stats['pictures'] - stats['plain'], stats['pages'], stats['roles'], stats['plain']))


if __name__ == '__main__':
    main(sys.argv[1:])
