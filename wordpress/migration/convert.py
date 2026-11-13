#!/usr/bin/env python3
"""Static build -> WordPress import package.

Reads the static HTML pages, page-map.csv and data/*.json and writes

    wordpress/migration/package/package.json   the package the FNPW import plugin reads
    wordpress/migration/package/report.md      what was converted and how

and, into the theme, the page <style>/<script> blocks that more than one page shares
(assets/css/shared/, assets/js/shared/).

Rule of the conversion: the front-end HTML must have the same structure as the static
markup, so global.css and the page CSS still match. A piece of markup becomes a core
block only when the block's own output is that same markup (plus the block's class).
Everything else is carried byte for byte in a core/html block.

Run from the repo root:  python3 wordpress/migration/convert.py
Standard library only.
"""
import csv
import hashlib
import html
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page names in WordPress (admin lists, menus) stay short when the SEO title is longer.
PAGE_NAMES = {
    'growing-national-parks.html': 'Growing National Parks',
    'healing-the-land.html': 'Healing the Land',
    'saving-species.html': 'Saving Species',
    'our-impact.html': 'Our Impact',
    'partner-invest.html': 'Partner With Us',
}

# Live posts with an empty title: the import sets this one.
TITLE_FIXES = {'latest-blog-ian-darbyshire-30-by-30-target': 'Ian Darbyshire on the 30 by 30 target'}
from htmltree import parse  # noqa: E402

# --------------------------------------------------------------------------- config

# Where the importer downloads local images and documents from.
MEDIA_BASE = 'https://elyciap.github.io/fnpw-website-2026/'
# Theme files (icons, shared CSS) are addressed root-relative so the content works on
# any host name.
THEME_URI = '/wp-content/themes/fnpw-2026/'
# A style or script block used by at least this many pages becomes a theme file.
SHARED_MIN = 2
JS_SPLIT = '\n/*__FNPW_SCRIPT__*/\n'

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
THEME = os.path.join(REPO, 'wordpress', 'theme', 'fnpw-2026')
OUT = os.path.join(HERE, 'package')

STATE_TERMS = {
    'NSW': 'new-south-wales', 'VIC': 'victoria', 'QLD': 'queensland', 'SA': 'south-australia',
    'WA': 'western-australia', 'TAS': 'tasmania', 'NT': 'northern-territory',
    'ACT': 'australian-capital-territory', 'Australia': 'national',
}
PILLAR_TERMS = {'parks': 'growing-parks', 'species': 'saving-species', 'healing': 'healing-our-land'}

INLINE = {'a', 'strong', 'b', 'em', 'i', 'span', 'br', 'sup', 'sub', 'small', 'code', 'u', 's', 'mark',
          'abbr', 'cite', 'q', 'time', 'kbd'}
CONTAINERS = {'div', 'section', 'article', 'header', 'footer', 'aside'}
HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
LEN = re.compile(r'^(?:0|auto|-?(?:\d+\.?\d*|\.\d+)(?:rem|em|px|%|ch|vw|vh))$')


def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


# --------------------------------------------------------------------------- page map

def load_page_map():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'page-map.csv'), encoding='utf-8')))
    by_file = {}
    for row in rows:
        if row['static_file']:
            by_file[row['static_file']] = row
    return rows, by_file


ROWS, BY_FILE = load_page_map()
IMG_DIMS = {}
EXTRA = {}


def url_for_file(name):
    """WordPress URL of a static file, or None. Redirected and retired pages resolve to
    their redirect target."""
    row = BY_FILE.get(name)
    if not row:
        return None
    if row['action'] in ('redirect', 'retire'):
        return row['redirect_to'] or None
    if row['wp_url']:
        return row['wp_url']
    return None


# --------------------------------------------------------------------------- URL rewriting

class Ctx:
    """Collects what one page refers to."""

    def __init__(self, name):
        self.name = name
        self.media = OrderedDict()      # source url -> alt
        self.unresolved = []
        self.dropped_variants = 0
        self.theme_files = set()


def map_url(url, ctx, in_css_file=False):
    u = url.strip()
    if not u or u.startswith(('#', 'http://', 'https://', 'mailto:', 'tel:', 'data:', '//', 'javascript:', '/')):
        return url
    m = re.match(r'^([A-Za-z0-9_.-]+\.html)([?#].*)?$', u)
    if m:
        name, tail = m.group(1), m.group(2) or ''
        if name == 'search.html':
            q = re.match(r'^\?q=([^#&]*)', tail)
            return '/?s=' + (q.group(1) if q else '')
        target = url_for_file(name)
        if target is None:
            ctx.unresolved.append(u)
            return url
        return target + tail
    if u.startswith('assets/icons/') or u.startswith('assets/js/') or u.startswith('assets/css/') or u.startswith('assets/fonts/'):
        ctx.theme_files.add(u)
        return ('../../' + u[len('assets/'):]) if in_css_file else THEME_URI + u
    if u.startswith('assets/'):
        if in_css_file:
            ctx.theme_files.add(u)
            return '../../' + u[len('assets/'):]
        src = MEDIA_BASE + u
        ctx.media.setdefault(src, '')
        return src
    ctx.unresolved.append(u)
    return url


def rewrite_html(text, ctx):
    # Responsive variants: WordPress makes its own sizes from the sideloaded original.
    def drop_source(m):
        ctx.dropped_variants += 1
        return ''
    text = re.sub(r'<source\b[^>]*\bsrcset="[^"]*assets/img/r/[^"]*"[^>]*>\s*', drop_source, text)

    def drop_srcset(m):
        ctx.dropped_variants += 1
        return ''
    text = re.sub(r'\ssrcset="[^"]*assets/img/r/[^"]*"', drop_srcset, text)

    def attr(m):
        return '%s%s="%s"' % (m.group(1), m.group(2), map_url(html.unescape(m.group(3)), ctx).replace('&', '&amp;') if '&' in m.group(3) else map_url(m.group(3), ctx))
    text = re.sub(r'(\s)(href|src|action|poster|data-src|data-href|data-full)="([^"]*)"', attr, text)

    def srcset(m):
        parts = []
        for cand in m.group(1).split(','):
            bits = cand.strip().split()
            if bits:
                bits[0] = map_url(bits[0], ctx)
                parts.append(' '.join(bits))
        return ' srcset="%s"' % ', '.join(parts)
    text = re.sub(r'\ssrcset="([^"]*)"', srcset, text)
    text = rewrite_css_urls(text, ctx)

    # Alt text for the media list.
    for m in re.finditer(r'<img\b[^>]*>', text):
        tag = m.group(0)
        s = re.search(r'\ssrc="([^"]*)"', tag)
        a = re.search(r'\salt="([^"]*)"', tag)
        if s and s.group(1) in ctx.media and a and a.group(1) and not ctx.media[s.group(1)]:
            ctx.media[s.group(1)] = html.unescape(a.group(1))
    return text


def rewrite_css_urls(text, ctx, in_css_file=False):
    def url(m):
        q, u = m.group(1), m.group(2)
        if u.startswith('assets/'):
            return 'url(%s%s%s)' % (q, map_url(u, ctx, in_css_file), q)
        return m.group(0)
    return re.sub(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', url, text)


# --------------------------------------------------------------------------- block conversion

class Stats:
    def __init__(self):
        self.core = Counter()
        self.html_blocks = 0
        self.reasons = Counter()


def inline_only(node):
    for child in node.children:
        if child.kind == 'comment':
            return False
        if child.kind == 'el':
            if child.tag not in INLINE:
                return False
            if not inline_only(child):
                return False
    return True


def rich(src, node):
    text = src[node.open_end:node.close_start]
    return re.sub(r'\s+', ' ', text).strip()


def margin_style(value):
    """A style attribute made only of margins -> block spacing support, else None."""
    out = {}
    for decl in value.split(';'):
        decl = decl.strip()
        if not decl:
            continue
        if ':' not in decl:
            return None
        prop, val = [x.strip() for x in decl.split(':', 1)]
        vals = val.split()
        if not vals or any(not LEN.match(v) for v in vals):
            return None
        if prop == 'margin':
            if len(vals) == 1:
                t = r = b = l = vals[0]
            elif len(vals) == 2:
                t = b = vals[0]
                r = l = vals[1]
            elif len(vals) == 3:
                t, r, b = vals
                l = r
            elif len(vals) == 4:
                t, r, b, l = vals
            else:
                return None
            out.update({'top': t, 'right': r, 'bottom': b, 'left': l})
        elif prop in ('margin-top', 'margin-right', 'margin-bottom', 'margin-left') and len(vals) == 1:
            out[prop[7:]] = vals[0]
        else:
            return None
    if not out:
        return None
    ordered = OrderedDict((k, out[k]) for k in ('top', 'right', 'bottom', 'left') if k in out)
    css = ';'.join('margin-%s:%s' % kv for kv in ordered.items())
    return ordered, css


def attrs_ok(node, allowed):
    for k, v in node.attrs:
        if k not in allowed:
            return False
        if v is None:
            return False
    return True


def jattrs(d):
    if not d:
        return ''
    s = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    # Same escaping as WordPress serialize_block_attributes().
    s = s.replace('--', '\\u002d\\u002d').replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return ' ' + s


def text_block(src, node, stats, why):
    """Heading or paragraph, or None."""
    is_h = node.tag in HEADINGS
    if not attrs_ok(node, {'class', 'style'}):
        why.append('<%s> has attributes a block cannot hold (%s)' % (node.tag, ', '.join(k for k, v in node.attrs if k not in ('class', 'style'))))
        return None
    if not inline_only(node):
        why.append('<%s> holds non-inline markup' % node.tag)
        return None
    classes = node.classes()
    if any(c.startswith(('wp-', 'has-', 'is-')) for c in classes):
        return None
    battrs = OrderedDict()
    style_css = ''
    style = node.attr('style')
    if style is not None:
        ms = margin_style(style)
        if not ms:
            why.append('<%s> inline style beyond margins (%s)' % (node.tag, style))
            return None
        battrs['style'] = {'spacing': {'margin': ms[0]}}
        style_css = ms[1]
    inner = rich(src, node)
    if not inner:
        return None
    if is_h:
        level = int(node.tag[1])
        if level != 2:
            battrs['level'] = level
            battrs.move_to_end('level', last=False)
        if classes:
            battrs['className'] = ' '.join(classes)
        cls = ' '.join(['wp-block-heading'] + classes)
        out = '<!-- wp:heading%s -->\n<%s class="%s"%s>%s</%s>\n<!-- /wp:heading -->' % (
            jattrs(battrs), node.tag, cls, ' style="%s"' % style_css if style_css else '', inner, node.tag)
        stats.core['heading'] += 1
        return out
    if classes:
        battrs['className'] = ' '.join(classes)
    open_tag = '<p'
    if classes:
        open_tag += ' class="%s"' % ' '.join(classes)
    if style_css:
        open_tag += ' style="%s"' % style_css
    stats.core['paragraph'] += 1
    return '<!-- wp:paragraph%s -->\n%s>%s</p>\n<!-- /wp:paragraph -->' % (jattrs(battrs), open_tag, inner)


def list_block(src, node, stats, why):
    if not attrs_ok(node, {'class'}):
        why.append('<%s> has attributes a List block cannot hold' % node.tag)
        return None
    items = []
    for child in node.children:
        if child.kind == 'text':
            if src[child.start:child.end].strip():
                return None
            continue
        if child.kind == 'comment' or child.tag != 'li' or not attrs_ok(child, {'class'}):
            why.append('list items carry attributes or are not plain <li>')
            return None
        # Inline content, optionally followed by one nested list.
        nested = [c for c in child.children if c.kind == 'el' and c.tag in ('ul', 'ol')]
        if nested:
            why.append('nested list')
            return None
        if not inline_only(child):
            why.append('list items hold block markup')
            return None
        inner = rich(src, child)
        ia = {'className': ' '.join(child.classes())} if child.classes() else {}
        items.append('<!-- wp:list-item%s -->\n<li%s>%s</li>\n<!-- /wp:list-item -->' % (
            jattrs(ia), ' class="%s"' % ' '.join(child.classes()) if child.classes() else '', inner))
    if not items:
        return None
    classes = node.classes()
    battrs = OrderedDict()
    if node.tag == 'ol':
        battrs['ordered'] = True
    if classes:
        battrs['className'] = ' '.join(classes)
    stats.core['list'] += 1
    return '<!-- wp:list%s -->\n<%s class="%s">%s</%s>\n<!-- /wp:list -->' % (
        jattrs(battrs), node.tag, ' '.join(['wp-block-list'] + classes), '\n\n'.join(items), node.tag)


def html_block(raw, stats):
    stats.html_blocks += 1
    return '<!-- wp:html -->\n%s\n<!-- /wp:html -->' % raw.strip('\n')


def convert_children(src, parent, stats, why):
    """Blocks for the children of a container. Returns (markup, core_count) or None when
    the container holds loose text and so cannot be a Group."""
    pieces = []     # ('core', markup) | ('html', start, end)
    core = 0
    for child in parent.children:
        if child.kind == 'text':
            if src[child.start:child.end].strip():
                why.append('<%s> holds loose text beside its elements' % parent.tag)
                return None
            continue
        if child.kind == 'comment':
            if pieces and pieces[-1][0] == 'html':
                pieces[-1] = ('html', pieces[-1][1], child.end)
            continue
        before = sum(stats.core.values())
        sub = Stats()
        block = try_block(src, child, sub, why)
        if block is None:
            if pieces and pieces[-1][0] == 'html':
                pieces[-1] = ('html', pieces[-1][1], child.end)
            else:
                pieces.append(('html', child.start, child.end))
        else:
            stats.core.update(sub.core)
            stats.html_blocks += sub.html_blocks
            core += sum(sub.core.values())
            pieces.append(('core', block))
    out = []
    for piece in pieces:
        if piece[0] == 'core':
            out.append(piece[1])
        else:
            out.append(html_block(src[piece[1]:piece[2]], stats))
    return '\n\n'.join(out), core


def try_block(src, node, stats, why):
    tag = node.tag
    if tag in HEADINGS or tag == 'p':
        return text_block(src, node, stats, why)
    if tag in ('ul', 'ol'):
        return list_block(src, node, stats, why)
    if tag in CONTAINERS:
        if not attrs_ok(node, {'class', 'id'}):
            why.append('<%s class="%s"> has attributes a Group block cannot hold (%s)' % (
                tag, node.attr('class', ''), ', '.join(k for k, v in node.attrs if k not in ('class', 'id'))))
            return None
        classes = node.classes()
        if any(c.startswith(('wp-', 'has-', 'is-', 'align')) for c in classes):
            return None
        sub = Stats()
        res = convert_children(src, node, sub, why)
        if res is None:
            return None
        inner, core = res
        if core == 0:
            # Nothing editable inside: carry the element whole rather than wrap raw HTML.
            return None
        stats.core.update(sub.core)
        stats.core['group'] += 1
        stats.html_blocks += sub.html_blocks
        battrs = OrderedDict()
        if tag != 'div':
            battrs['tagName'] = tag
        if classes:
            battrs['className'] = ' '.join(classes)
        battrs['layout'] = {'type': 'default'}
        ident = node.attr('id')
        if ident:
            battrs['anchor'] = ident
        return '<!-- wp:group%s -->\n<%s%s class="%s">%s</%s>\n<!-- /wp:group -->' % (
            jattrs(battrs), tag, ' id="%s"' % ident if ident else '', ' '.join(['wp-block-group'] + classes), inner, tag)
    why.append('<%s> has no core block with the same markup' % tag)
    return None


def convert_sections(src, ctx):
    """Top-level conversion of a <main> (or .ed) inner HTML. Returns (content, info)."""
    root, errors = parse(src)
    stats = Stats()
    sections = []
    out = []
    hoisted_css, hoisted_js = [], []
    pending_html = None     # (start, end) of a run of raw nodes
    bad_spans = []
    for err in errors:
        m = re.search(r'at (\d+)$', err)
        if m:
            bad_spans.append(int(m.group(1)))

    def flush():
        nonlocal pending_html
        if pending_html:
            raw = src[pending_html[0]:pending_html[1]]
            if raw.strip():
                out.append(html_block(raw, stats))
            pending_html = None

    for child in root.children:
        if child.kind == 'text':
            if src[child.start:child.end].strip():
                pending_html = (pending_html[0] if pending_html else child.start, child.end)
            continue
        if child.kind == 'comment':
            if pending_html:
                pending_html = (pending_html[0], child.end)
            continue
        if child.tag == 'style':
            hoisted_css.append(src[child.open_end:child.close_start])
            continue
        if child.tag == 'script' and child.attr('src') is None and 'json' not in (child.attr('type') or ''):
            hoisted_js.append(src[child.open_end:child.close_start])
            continue
        label = child.tag + ('.' + '.'.join(child.classes()) if child.classes() else '')
        why = []
        broken = any(child.start <= pos <= child.end for pos in bad_spans) or (errors and not bad_spans)
        block = None
        sub = Stats()
        if broken:
            why.append('markup is not well formed (%s), carried untouched' % '; '.join(errors)[:160])
        else:
            block = try_block(src, child, sub, why)
        if block is None:
            pending_html = (pending_html[0] if pending_html else child.start, child.end)
            reason = Counter(why).most_common(1)[0][0] if why else 'no editable text inside'
            sections.append({'label': label, 'as': 'html', 'reason': reason})
            # one html block per section
            flush()
        else:
            flush()
            stats.core.update(sub.core)
            stats.html_blocks += sub.html_blocks
            out.append(block)
            sections.append({'label': label, 'as': 'blocks', 'core': sum(v for k, v in sub.core.items() if k != 'group'),
                             'html_inside': sub.html_blocks})
    flush()
    return '\n\n'.join(out), {
        'sections': sections, 'core': dict(stats.core), 'html_blocks': stats.html_blocks,
        'css': hoisted_css, 'js': hoisted_js, 'errors': errors,
    }


# --------------------------------------------------------------------------- page reading

def strip_regions(body):
    return re.sub(r'<!-- @(header|footer) -->.*?<!-- /@\1 -->', '', body, flags=re.S)


class Page:
    def __init__(self, name):
        self.name = name
        self.src = read(os.path.join(REPO, name))
        head_end = self.src.index('</head>')
        self.head = self.src[:head_end]
        m = re.search(r'<main([^>]*)>', self.src)
        self.main_attrs = m.group(1)
        self.main = self.src[m.end():self.src.index('</main>')]
        rest = strip_regions(self.src[head_end:m.start()] + self.src[self.src.index('</main>') + 7:])
        self.styles = [s for s in re.findall(r'<style[^>]*>(.*?)</style>', self.head, re.S) if s.strip()]
        self.styles += [s for s in re.findall(r'<style[^>]*>(.*?)</style>', rest, re.S) if s.strip()]
        self.scripts = []        # inline
        self.ext = []            # (src, attrs)
        for sm in re.finditer(r'<script([^>]*)>(.*?)</script>', rest, re.S):
            a = sm.group(1)
            if 'ld+json' in a:
                continue
            s = re.search(r'src="([^"]+)"', a)
            if s:
                self.ext.append(s.group(1))
            elif sm.group(2).strip():
                self.scripts.append(sm.group(2))
        t = re.search(r'<title>(.*?)</title>', self.head, re.S)
        self.title = html.unescape(t.group(1).strip()) if t else ''
        d = re.search(r'<meta name="description" content="([^"]*)"', self.head)
        self.description = html.unescape(d.group(1)) if d else ''
        o = re.search(r'<meta property="og:image" content="([^"]*)"', self.head)
        self.og_image = html.unescape(o.group(1)) if o else ''


def norm(text):
    return text.strip()


def digest(text):
    return hashlib.md5(norm(text).encode('utf-8')).hexdigest()[:8]


def text_of(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


# --------------------------------------------------------------------------- main

def main():
    articles = {a['slug']: a for a in json.load(open(os.path.join(REPO, 'data', 'articles.json'), encoding='utf-8'))}
    projects = {p['slug']: p for p in json.load(open(os.path.join(REPO, 'data', 'projects.json'), encoding='utf-8'))}
    real_assets = set()
    asset_list = os.path.join(REPO, '..', 'asset-list.txt')
    if os.path.exists(asset_list):
        real_assets = set(l.strip() for l in open(asset_list, encoding='utf-8') if l.strip())
    else:
        for base, _dirs, files in os.walk(os.path.join(REPO, 'assets')):
            for f in files:
                real_assets.add(os.path.relpath(os.path.join(base, f), REPO).replace(os.sep, '/'))

    todo = [r for r in ROWS if r['static_file'] and r['action'] in ('replace', 'new')]
    pages = {r['static_file']: Page(r['static_file']) for r in todo}
    # Pixel sizes the static build knows for remote images (from its img tags).
    for page in list(pages.values()):
        for tag in re.findall(r'<img\b[^>]*>', page.src):
            sm = re.search(r'\ssrc="([^"]*)"', tag)
            wm = re.search(r'\swidth="(\d+)"', tag)
            hm = re.search(r'\sheight="(\d+)"', tag)
            if sm and wm and hm:
                IMG_DIMS.setdefault(html.unescape(sm.group(1)), (int(wm.group(1)), int(hm.group(1))))

    theme_article_css = read(os.path.join(THEME, 'assets', 'css', 'article.css'))
    theme_stories_css = read(os.path.join(THEME, 'assets', 'css', 'stories.css'))
    theme_progress_js = read(os.path.join(THEME, 'assets', 'js', 'article-progress.js'))

    # Which style and script blocks are shared.
    css_use, js_use = defaultdict(list), defaultdict(list)
    hoisted = {}
    for name, page in pages.items():
        root, _ = parse(page.main)
        extra_css = [page.main[c.open_end:c.close_start] for c in root.children if c.kind == 'el' and c.tag == 'style']
        extra_js = [page.main[c.open_end:c.close_start] for c in root.children
                    if c.kind == 'el' and c.tag == 'script' and c.attr('src') is None]
        hoisted[name] = (extra_css, extra_js)
        for s in page.styles + extra_css:
            css_use[digest(s)].append(name)
        for s in extra_js + page.scripts:
            js_use[digest(s)].append(name)

    def stem(name):
        s = name[:-5]
        if s.startswith('article-'):
            return 'article'
        if s.startswith('project-'):
            return 'project'
        return re.sub(r'-(nsw|vic|qld|sa|wa)$', '', s)

    shared_ctx = Ctx('(shared theme files)')
    shared_css_files, shared_js_files = {}, {}
    for directory in ('assets/css/shared', 'assets/js/shared'):
        full = os.path.join(THEME, directory)
        os.makedirs(full, exist_ok=True)
        for f in os.listdir(full):
            os.remove(os.path.join(full, f))

    items, report_rows, media = [], [], OrderedDict()
    totals = Counter()
    all_unresolved = Counter()
    html_carried_components = defaultdict(set)

    def css_plan(name, page, blocks, ctx, is_article):
        files, own, notes = [], [], []
        for s in blocks:
            d = digest(s)
            if is_article and norm(s) in theme_article_css:
                notes.append('article.css (theme, by template)')
                continue
            if name == 'articles.html':
                continue
            if len(set(css_use[d])) >= SHARED_MIN:
                if d not in shared_css_files:
                    fname = '%s-%s.css' % (stem(css_use[d][0]), d)
                    body = rewrite_css_urls(norm(s), shared_ctx, in_css_file=True)
                    with open(os.path.join(THEME, 'assets', 'css', 'shared', fname), 'w', encoding='utf-8') as fh:
                        fh.write('/* Shared page styles lifted unchanged from the static build by convert.py (%d pages, first: %s).\n   Do not edit: change the static source and re-run the converter. */\n%s\n' % (
                            len(set(css_use[d])), css_use[d][0], body))
                    shared_css_files[d] = fname
                files.append(shared_css_files[d])
                notes.append('shared file %s' % shared_css_files[d])
            else:
                own.append(rewrite_css_urls(norm(s), ctx))
        if own:
            notes.append('page CSS in _fnpw_page_css (%d bytes)' % sum(len(x) for x in own))
        return files, '\n'.join(own), notes

    def js_plan(name, page, blocks, ctx, is_article):
        files, own, notes = [], [], []
        for s in blocks:
            d = digest(s)
            body = norm(s)
            if is_article and body in theme_progress_js:
                notes.append('article-progress.js (theme, by template)')
                continue
            if 'var IMAP=' in body:
                notes.append('map script dropped: the fnpw/project-map block has its own')
                continue
            if len(set(js_use[d])) >= SHARED_MIN:
                if d not in shared_js_files:
                    label = 'hs-fallback' if 'hsFallback' in body and len(body) < 400 else stem(js_use[d][0])
                    fname = '%s-%s.js' % (label, d)
                    with open(os.path.join(THEME, 'assets', 'js', 'shared', fname), 'w', encoding='utf-8') as fh:
                        fh.write('/* Shared page script lifted unchanged from the static build by convert.py (%d pages, first: %s). */\n%s\n' % (
                            len(set(js_use[d])), js_use[d][0], body))
                    shared_js_files[d] = fname
                files.append(shared_js_files[d])
                notes.append('shared file %s' % shared_js_files[d])
            else:
                if re.search(r"['\"`][\w./-]*\.html", body):
                    notes.append('page script still builds .html links: check')
                own.append(body)
        if own:
            notes.append('%d page script(s) in _fnpw_page_js (%d bytes)' % (len(own), sum(len(x) for x in own)))
        return files, JS_SPLIT.join(own), notes

    for row in todo:
        name = row['static_file']
        page = pages[name]
        ctx = Ctx(name)
        template = row['wp_template']
        post_type = row['wp_post_type']
        path = row['wp_url'].strip('/')
        segs = [s for s in path.split('/') if s]
        is_article = template in ('single', 'page-article')
        existing = bool(row['live_url'])

        item = OrderedDict()
        item['source'] = name
        item['post_type'] = post_type
        item['expect'] = 'update' if existing else 'create'
        item['status'] = 'publish'
        meta = OrderedDict()

        if post_type == 'page':
            item['slug'] = segs[-1] if segs else 'home'
            item['parent_path'] = '/'.join(segs[:-1])
            item['template'] = template if template == 'page-article' else ''
            if template == 'front-page':
                item['role'] = 'front_page'
            if template == 'home':
                item['role'] = 'posts_page'
        else:
            item['slug'] = segs[-1]
        item['key'] = '%s:%s' % (post_type, path or '/')

        main_src = rewrite_html(page.main, ctx)
        if name == 'projects.html':
            # The map becomes the dynamic block fnpw/project-map (FNPW Core), which draws
            # the same markup from the project posts.
            main_src, n_map = re.subn(r'<section class="map-sec" id="map">.*?</section>', '<fnpw-project-map></fnpw-project-map>', main_src, count=1, flags=re.S)
        info = None

        if template == 'home':
            # The Stories index is drawn by the theme (templates/home.html) from real posts.
            item['content'] = ''
            if not existing:
                item['title'] = 'Articles'
            css_files, page_css, css_notes = [], '', ['stories.css (theme, by template)']
            js_files, page_js, js_notes = [], '', ['articles.js (theme, by template); newsletter band pattern carries the HubSpot embed']
            ext = []
            info = {'sections': [{'label': 'whole page', 'as': 'theme'}], 'core': {}, 'html_blocks': 0}
            if norm(page.styles[0]) not in theme_stories_css and len(norm(page.styles[0])) != 0:
                css_notes.append('NOTE: stories.css in the theme differs from the static block only by asset paths (checked by length %d vs %d)' % (
                    len(norm(page.styles[0])), len(theme_stories_css)))
        else:
            if is_article:
                root, errs = parse(main_src)
                art = root.elements()[0]
                header, ed = art.elements()[0], art.elements()[1]
                hero_html = main_src[header.start:header.end]
                body_src = main_src[ed.open_end:ed.close_start]
                content, info = convert_sections(body_src, ctx)
                k = re.search(r'<span class="ed-kicker ed-kicker-top">(.*?)</span>', hero_html, re.S)
                st = re.search(r'<p class="ed-stand">(.*?)</p>', hero_html, re.S)
                im = re.search(r'<figure class="ed-hero-im"><img\b[^>]*\ssrc="([^"]*)"[^>]*>', hero_html)
                mt = re.search(r'<p class="ed-meta">(.*?)</p>', hero_html, re.S)
                meta['fnpw_kicker'] = text_of(k.group(1)) if k else ''
                meta['fnpw_standfirst'] = text_of(st.group(1)) if st else ''
                if st:
                    item['excerpt'] = text_of(st.group(1))
                slug_static = name[len('article-'):-5]
                a = articles.get(slug_static, {})
                # Every article has a feature image (cards use it); the page hero shows it
                # only when it is large enough, otherwise the hero is "flat".
                hero_url = im.group(1) if im else (a.get('hero') or '')
                alt = re.search(r'\salt="([^"]*)"', im.group(0)) if im else None
                meta['fnpw_hero_url'] = hero_url
                meta['fnpw_hero_alt'] = html.unescape(alt.group(1)) if alt else (a.get('hero_alt') or '')
                meta['fnpw_hero_flat'] = '0' if im else '1'
                dims = IMG_DIMS.get(hero_url)
                if dims:
                    meta['fnpw_hero_w'], meta['fnpw_hero_h'] = dims
                if hero_url:
                    if hero_url.startswith('assets/'):
                        hero_url = MEDIA_BASE + hero_url
                    item['featured_image'] = hero_url
                    item['featured_alt'] = meta['fnpw_hero_alt']
                if mt:
                    parts = [p.strip() for p in text_of(mt.group(1)).split('·')]
                    rm = re.match(r'(\d+) min read', parts[-1])
                    meta['fnpw_read_min'] = int(rm.group(1)) if rm else 0
                    meta['fnpw_place'] = parts[1] if len(parts) == 3 else ''
                    item['static_date'] = parts[0]
                meta['fnpw_pillar'] = a.get('pillar', '') or 'news'
                if a.get('description'):
                    # The card text on the Stories index and under "Keep reading".
                    meta['fnpw_summary'] = a['description']
                related = []
                more = re.search(r'<section class="sec sand ed-more">(.*?)</section>', main_src, re.S)
                if more:
                    for href in re.findall(r'<a class="pj-rcard" href="([^"]+)"', more.group(1)):
                        related.append(href.strip('/').split('/')[-1])
                meta['fnpw_related'] = related
                if not existing:
                    item['title'] = text_of(re.search(r'<h1>(.*?)</h1>', hero_html, re.S).group(1))
                item['static_title'] = text_of(re.search(r'<h1>(.*?)</h1>', hero_html, re.S).group(1))
                if post_type == 'page':
                    # A page keeps its short page title; the article hero shows the headline.
                    meta['fnpw_headline'] = item['static_title']
            else:
                content, info = convert_sections(main_src, ctx)
                if post_type == 'project':
                    meta['_fnpw_full_main'] = '1'
                    slug_static = name[len('project-'):-5]
                    p = projects.get(slug_static, {})
                    if p.get('pillar'):
                        meta['pillar'] = p['pillar']
                    credit = re.search(r'<section class="sec pj-credit"[^>]*>(.*?)</section>', main_src, re.S)
                    if credit:
                        meta['partner_credit'] = text_of(credit.group(1))
                    lede = re.search(r'<p class="lede">(.*?)</p>', main_src, re.S)
                    if lede:
                        item['excerpt'] = text_of(lede.group(1))
                    img = p.get('img', '')
                    if img:
                        if img.startswith('assets/'):
                            img = MEDIA_BASE + img
                            ctx.media.setdefault(img, p.get('title', ''))
                        item['featured_image'] = img
                        item['featured_alt'] = p.get('title', '')
                    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', main_src, re.S)
                    item['static_title'] = text_of(h1.group(1)) if h1 else p.get('title', '')
                    if not existing:
                        item['title'] = p.get('title') or item['static_title']
                        terms = {}
                        if p.get('state') in STATE_TERMS:
                            terms['project_state'] = [STATE_TERMS[p['state']]]
                        if p.get('pillar') in PILLAR_TERMS:
                            terms['project_focus_area'] = [PILLAR_TERMS[p['pillar']]]
                        if terms:
                            item['terms'] = terms
                        if p.get('lat') is not None:
                            meta['project_details_project_latitude'] = str(p['lat'])
                            meta['project_details_project_longitude'] = str(p['lon'])
                else:
                    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', main_src, re.S)
                    item['static_title'] = text_of(h1.group(1)) if h1 else page.title
                    if not existing:
                        item['title'] = PAGE_NAMES.get(name) or re.sub(r'\s*\|\s*FNPW\s*$', '', page.title) or item['static_title']
                    if template == 'front-page' and not existing:
                        item['title'] = 'Home'
            item['content'] = content

            styles = page.styles + info['css']
            scripts = info['js'] + page.scripts
            if name == 'projects.html':
                new, n = re.subn(r'<!-- wp:html -->\s*<fnpw-project-map></fnpw-project-map>\s*<!-- /wp:html -->',
                                 '<!-- wp:fnpw/project-map /-->', item['content'], count=1)
                if not n:
                    raise SystemExit('projects.html: the map section was not found')
                item['content'] = new
                info['html_blocks'] -= 1
                for sec in info['sections']:
                    if sec['label'].startswith('fnpw-project-map'):
                        sec['as'] = 'block fnpw/project-map'
                        sec['label'] = 'section.map-sec'
            if name == 'search.html':
                scripts = []
            css_files, page_css, css_notes = css_plan(name, page, styles, ctx, is_article)
            js_files, page_js, js_notes = js_plan(name, page, scripts, ctx, is_article)
            ext = [u for u in page.ext if u.startswith('https://')]
            local_js = [u for u in page.ext if not u.startswith('https://') and u != 'assets/js/main.js']
            for u in local_js:
                js_notes.append('%s (theme, enqueued where its markup is used)' % u)
                if u.endswith('snap.js'):
                    meta['fnpw_snap'] = '1'
            if ext:
                js_notes.append('external: ' + ', '.join(ext))

        if css_files:
            meta['_fnpw_css_files'] = css_files
        if page_css:
            meta['_fnpw_page_css'] = page_css
        if js_files:
            meta['_fnpw_js_files'] = js_files
        if page_js:
            meta['_fnpw_page_js'] = page_js
        if ext:
            meta['_fnpw_ext_js'] = ext
        if page.title:
            meta['_yoast_wpseo_title'] = page.title
        if page.description:
            meta['_yoast_wpseo_metadesc'] = page.description
        item['meta'] = meta
        item['media'] = list(ctx.media.keys())
        items.append(item)

        for src, alt in ctx.media.items():
            if src not in media or (alt and not media[src]):
                media[src] = alt
        missing = [m[len(MEDIA_BASE):] for m in ctx.media if m.startswith(MEDIA_BASE) and m[len(MEDIA_BASE):] not in real_assets]
        for u in ctx.unresolved:
            all_unresolved[u] += 1
        secs = info['sections']
        n_blocks = sum(1 for s in secs if s['as'] == 'blocks')
        n_html = sum(1 for s in secs if s['as'] == 'html')
        n_other = len(secs) - n_blocks - n_html
        core = {k: v for k, v in info.get('core', {}).items()}
        totals['sections'] += len(secs)
        totals['sections_blocks'] += n_blocks
        totals['sections_html'] += n_html
        totals['sections_theme'] += n_other
        totals['core_editable'] += sum(v for k, v in core.items() if k != 'group')
        totals['core_group'] += core.get('group', 0)
        totals['html_blocks'] += info.get('html_blocks', 0)
        totals['pages'] += 1
        kind = 'article' if is_article else ('project' if post_type == 'project' else 'page')
        totals['pages_' + kind] += 1
        totals[kind + '_sections'] += len(secs)
        totals[kind + '_sections_blocks'] += n_blocks
        report_rows.append({
            'file': name, 'url': row['wp_url'], 'kind': kind, 'expect': item['expect'], 'sections': secs,
            'n_blocks': n_blocks, 'n_html': n_html, 'n_other': n_other, 'core': core, 'html_blocks': info.get('html_blocks', 0),
            'css': css_notes, 'js': js_notes, 'unresolved': list(ctx.unresolved), 'media': len(ctx.media),
            'missing': missing, 'dropped': ctx.dropped_variants, 'errors': info.get('errors', []),
        })

    # Parents before children; pages before posts so links resolve as they are created.
    order = {'page': 0, 'post': 1, 'project': 2}
    items.sort(key=lambda i: (order.get(i['post_type'], 9), i.get('parent_path', '').count('/') + (1 if i.get('parent_path') else 0), i['key']))

    media_list = []
    for src, alt in media.items():
        entry = OrderedDict(url=src, alt=alt)
        if src.startswith(MEDIA_BASE):
            entry['path'] = src[len(MEDIA_BASE):]
            entry['sideload'] = True
        else:
            entry['sideload'] = False
        media_list.append(entry)
    # Featured images on the live media library are listed too, so the importer can look
    # them up, but never sideloaded.
    listed = set(m['url'] for m in media_list)
    for item in items:
        f = item.get('featured_image')
        if f and f not in listed:
            listed.add(f)
            media_list.append(OrderedDict(url=f, alt=item.get('featured_alt', ''), sideload=f.startswith(MEDIA_BASE)))

    EXTRA['iso_dates'] = sum(1 for i in items if re.match(r'\d{4}-', str(i.get('static_date', ''))))
    EXTRA['flat'] = sum(1 for i in items if i['meta'].get('fnpw_hero_flat') == '1')
    package = OrderedDict()
    package['format'] = 'fnpw-migrate/1'
    package['generated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    package['source'] = 'convert.py from the static build'
    package['media_base'] = MEDIA_BASE
    package['create_terms'] = False
    package['settings'] = {'front_page': 'page:/', 'posts_page': 'page:news'}
    package['media'] = media_list
    package['items'] = items
    os.makedirs(OUT, exist_ok=True)
    # Posts keep their live titles, except where the live post has none (Nov 2026).
    for item in package['items']:
        if item.get('slug') in TITLE_FIXES and not item.get('title'):
            item['title'] = item.get('static_title') or TITLE_FIXES[item['slug']]
    with open(os.path.join(OUT, 'package.json'), 'w', encoding='utf-8') as fh:
        json.dump(package, fh, ensure_ascii=False, indent=1)

    write_report(report_rows, totals, media_list, all_unresolved, shared_css_files, shared_js_files, shared_ctx, real_assets)
    print('items: %d  media: %d (sideload %d)  sections: %d (blocks %d, html %d, theme %d)  editable core blocks: %d  html blocks: %d' % (
        len(items), len(media_list), sum(1 for m in media_list if m['sideload']), totals['sections'], totals['sections_blocks'],
        totals['sections_html'], totals['sections_theme'], totals['core_editable'], totals['html_blocks']))
    print('unresolved links: %d distinct' % len(all_unresolved))


def write_report(rows, totals, media_list, unresolved, css_files, js_files, shared_ctx, real_assets):
    L = []
    w = L.append
    pct = lambda a, b: ('%.0f%%' % (100.0 * a / b)) if b else 'n/a'
    w('# Conversion report')
    w('')
    w('Written by `convert.py` on %s. Regenerate rather than edit.' % datetime.now().strftime('%d %B %Y'))
    w('')
    w('## Summary')
    w('')
    w('| | Count |')
    w('|---|---|')
    w('| Pages converted | %d (%d articles, %d projects, %d pages) |' % (totals['pages'], totals['pages_article'], totals['pages_project'], totals['pages_page']))
    w('| Top-level sections | %d |' % totals['sections'])
    w('| Sections converted to core blocks (Group with editable Heading, Paragraph or List inside) | %d (%s) |' % (totals['sections_blocks'], pct(totals['sections_blocks'], totals['sections'])))
    w('| Sections carried whole in one Custom HTML block | %d (%s) |' % (totals['sections_html'], pct(totals['sections_html'], totals['sections'])))
    w('| Sections drawn by the theme or a dynamic block | %d |' % totals['sections_theme'])
    w('| Editable core blocks (Heading, Paragraph, List) | %d |' % totals['core_editable'])
    w('| Group blocks | %d |' % totals['core_group'])
    w('| Custom HTML blocks in total (whole sections plus pieces inside converted sections) | %d |' % totals['html_blocks'])
    side = [m for m in media_list if m['sideload']]
    missing = [m['path'] for m in side if m.get('path') and m['path'] not in real_assets]
    w('| Images and documents to sideload from GitHub Pages | %d |' % len(side))
    w('| ...of which are not in the repo asset list | %d |' % len(missing))
    w('| Images left on the live media library (URL unchanged) | %d |' % (len(media_list) - len(side)))
    w('| Unresolved internal links | %d |' % len(unresolved))
    w('')
    w('For articles a "section" is one child of the article body (`.ed`): a paragraph, heading, figure or band. The hero, standfirst, related stories, back link and donate band of an article come from the theme template, not the post content.')
    w('')
    w('| Kind | Sections | As core blocks |')
    w('|---|---|---|')
    for kind in ('page', 'project', 'article'):
        w('| %s | %d | %d (%s) |' % (kind, totals[kind + '_sections'], totals[kind + '_sections_blocks'], pct(totals[kind + '_sections_blocks'], totals[kind + '_sections'])))
    w('')
    w('## How the conversion decides')
    w('')
    w('- A heading, paragraph or plain list becomes a core block when it has nothing but a class (and, for headings and paragraphs, a margin-only inline style, which maps to the block spacing setting). A `div`, `section`, `article`, `header`, `footer` or `aside` with only a class and id becomes a Group when something inside it is editable.')
    w('- Anything else is carried byte for byte in Custom HTML: images and figures (the Image block adds its own wrapper and drops `sizes`, `loading` and dimensions), links styled as buttons (the Button block wraps the link in a div), cards that are links, elements with inline styles beyond margins, `data-` attributes, `hidden`, forms, iframes, SVG, tabs, carousels, maps and accordions.')
    w('- Responsive variants (`<source>` and `srcset` pointing at `assets/img/r/`) are dropped from the HTML; the importer sideloads the fallback image and WordPress makes its own sizes. CSS backgrounds keep both files.')
    w('')
    w('## Interactive components carried as HTML with their scripts')
    w('')
    w('| Component | Pages | Script handling |')
    w('|---|---|---|')
    comp = [
        ('Project map', 'projects', 'Dynamic block `fnpw/project-map` (FNPW Core); the static map script is dropped'),
        ('Project grid, pillar filter, search and sort', 'projects', 'HTML + page script in `_fnpw_page_js`'),
        ('Project grid with pillar filter', 'growing-national-parks, healing-the-land, saving-species', 'HTML + shared theme script'),
        ('Stories filter, sort and paging', 'news', 'Theme block `fnpw/stories-index` from real posts + `articles.js`'),
        ('Volunteer sites map, photo gallery', 'five city volunteering pages', 'HTML + shared theme scripts + `gallery.js`'),
        ('State tabs, photo carousel, accordions', 'corporate-volunteering', 'HTML + page script + `carousel.js`'),
        ('Tabs', 'government-partnerships, partner-with-us', 'HTML + page script'),
        ('Read more toggles, timeline rail, card arrows, section snap', 'about-us', 'HTML + page scripts + `snap.js` (meta `fnpw_snap`)'),
        ('Load more list', 'our-impact, corporate-partnerships', 'HTML + page script'),
        ('Reports filter', 'annual-reports-financials', 'HTML + page script'),
        ('Project slider, animated counters', 'home', 'HTML + page script; counters in `main.js`'),
        ('Accordions (details)', 'bequest, donate-land, faqs, government-partnerships, corporate-volunteering', 'HTML (native details, no script)'),
        ('HubSpot forms', '18 pages', 'HTML markup + embed script in `_fnpw_ext_js` + shared fallback script'),
        ('Article reading bar', 'all articles', 'Theme script `article-progress.js` by template'),
        ('Video, podcast and Google map embeds', 'about-us, koala-facts, contact-us', 'HTML (iframe)'),
    ]
    for c in comp:
        w('| %s | %s | %s |' % c)
    w('')
    w('No custom blocks were built for these beyond the project map and the Stories index.')
    w('')
    w('## Differences from the static pages, by design')
    w('')
    w('- **Article dates.** The theme prints the post date as "Month YYYY" in the article hero and on cards. %d static articles print the raw date (2022-07-06) instead; in WordPress they read the same way as the rest.' % EXTRA.get('iso_dates', 0))
    w('- **Article titles.** A post that already exists keeps its WordPress title, and the article hero prints that title. The static headline is in the package as `static_title` for checking, not imported. The three pages shown in the article layout keep their short page title and carry the headline in `fnpw_headline`.')
    w('- **Flat heroes.** %d articles have a feature image too small for a full-width hero. They carry `fnpw_hero_flat` so the theme leaves the image off the hero even though the post has a featured image.' % EXTRA.get('flat', 0))
    w('- **Stories index.** Drawn from published posts plus the pages that use the article template. Press-coverage posts in the `media` category that were not imported stay off it (they are on In the news). Card order follows the WordPress post dates.')
    w('- **Search.** The static page searched an index in the browser; WordPress search answers instead, so result counts differ.')
    w('- **Images inside content.** `<img>` tags keep one file (the fallback). WordPress does not add `srcset` to them because they are not Image blocks, so they are heavier on phones than the static `r/` variants were. Featured images and CSS backgrounds are unaffected.')
    w('- **Theme photos.** Three photos are used by theme files, not by content, and must be copied into the theme by hand because they are not in this copy of the repo: `assets/img/articles-hero-kookaburra.jpg`, `assets/img/r/articles-hero-kookaburra-1600.webp` (Stories hero) and `assets/img/search-hero-koala.jpg` (Search hero).')
    w('')
    w('## Shared files written into the theme')
    w('')
    for d, f in sorted(css_files.items(), key=lambda x: x[1]):
        w('- `assets/css/shared/%s`' % f)
    for d, f in sorted(js_files.items(), key=lambda x: x[1]):
        w('- `assets/js/shared/%s`' % f)
    if shared_ctx.theme_files:
        w('')
        w('Shared CSS refers to these files, which must sit in the theme (`assets/...`): ' + ', '.join('`%s`' % f for f in sorted(shared_ctx.theme_files)))
    w('')
    w('## Unresolved links')
    w('')
    if unresolved:
        for u, n in unresolved.most_common():
            w('- `%s` (%d)' % (u, n))
    else:
        w('None. Every internal `.html` link maps to a WordPress URL in page-map.csv.')
    w('')
    w('## Images not in the repo asset list')
    w('')
    if missing:
        for m in sorted(missing):
            w('- `%s`' % m)
    else:
        w('None: every local image and document the pages use is in the asset list.')
    w('')
    w('## Per page')
    w('')
    w('| File | WordPress URL | Sections: blocks / HTML / theme | Editable blocks | HTML blocks | CSS | JS | Unresolved links | Media (missing) |')
    w('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        w('| %s | %s | %d / %d / %d | %d | %d | %s | %s | %s | %d (%d) |' % (
            r['file'], r['url'], r['n_blocks'], r['n_html'], r['n_other'], sum(v for k, v in r['core'].items() if k != 'group'), r['html_blocks'],
            '; '.join(sorted(set(r['css']))) or 'none', '; '.join(sorted(set(r['js']))) or 'none',
            ', '.join(sorted(set(r['unresolved']))) or 'none', r['media'], len(r['missing'])))
    w('')
    w('## Sections carried as HTML, with the reason')
    w('')
    w('Site pages and projects only (article bodies are listed in the table above by count). Identical runs across project pages are grouped.')
    w('')
    grouped = defaultdict(list)
    for r in rows:
        if r['kind'] == 'article':
            continue
        for s in r['sections']:
            if s['as'] == 'html':
                grouped[(s['label'], s['reason'])].append(r['file'])
    for (label, reason), files in sorted(grouped.items(), key=lambda x: (-len(x[1]), x[0])):
        shown = ', '.join(files[:4]) + (' and %d more' % (len(files) - 4) if len(files) > 4 else '')
        w('- `%s` (%d): %s. Pages: %s' % (label, len(files), reason, shown))
    w('')
    with open(os.path.join(OUT, 'report.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))


if __name__ == '__main__':
    main()
