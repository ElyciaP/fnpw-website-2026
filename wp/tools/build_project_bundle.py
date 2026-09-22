#!/usr/bin/env python3
"""
Build wp/data/projects-bundle.json from the live static project pages.

The static project-*.html files are the source of truth for project copy.
Re-run this any time you edit a project page, then re-run the WordPress
import. The import matches on slug, so it updates rather than duplicates.

    python3 wp/tools/build_project_bundle.py

What it takes from each page:
  title        the hero <h1>
  excerpt      the hero lede
  hero image   becomes the featured image
  credit       the "With thanks" lede, copied to the credit field for the
               REST API (the section itself stays in the page)
  content      every other section, in order, with links rewritten to
               WordPress paths and local images listed for upload

What it drops, because the WordPress template renders them itself:
  the hero, the "More from this pillar" row, the back link and the closing
  "Help fund work like this" donate band.

Map data (pillar, state, lat, lon, on_map, live URL) comes from
data/projects.json and is joined on slug.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "wp", "data", "projects-bundle.json")

PILLAR_FROM_DATA = {"parks": "growing-national-parks", "species": "saving-species", "healing": "healing-the-land"}
PILLAR_FROM_LABEL = {"growing national parks": "growing-national-parks", "saving species": "saving-species", "healing the land": "healing-the-land"}

SPECIAL_PAGES = {
    "index": "/",
    "articles": "/news/",
    "projects": "/projects/",
    "reports": "/reports/",
}

SECTION_RE = re.compile(r"<section\b[^>]*>.*?</section>", re.S | re.I)


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def first(pattern, s, flags=re.S | re.I):
    m = re.search(pattern, s, flags)
    return m.group(1) if m else ""


def rewrite_links(fragment):
    def repl(m):
        attr, target = m.group(1), m.group(2)
        path, _, anchor = target.partition("#")
        anchor = ("#" + anchor) if anchor else ""
        name = os.path.basename(path)[:-5]
        if name.startswith("project-"):
            new = "/project/%s/" % name[len("project-"):]
        elif name.startswith("article-"):
            new = "fnpw-article:%s" % name[len("article-"):]
        elif name in SPECIAL_PAGES:
            new = SPECIAL_PAGES[name]
        else:
            new = "/%s/" % name
        return '%s="%s%s"' % (attr, new, anchor)

    return re.sub(r'(href)="(?!https?:|mailto:|tel:|#)([^"]+?\.html(?:#[^"]*)?)"', repl, fragment)


def local_images(fragment):
    found = re.findall(r'(?:src|href)="(assets/img/[^"]+)"', fragment)
    found += re.findall(r"url\(['\"]?(assets/img/[^'\")]+)", fragment)
    return sorted(set(found))


def is_hero(section):
    head = section[:300]
    return bool(re.search(r'class="[^"]*\b(pj-hero|ch)\b', head))


def ey_of(section):
    return strip_tags(first(r'<span class="ey[^"]*">(.*?)</span>', section)).lower()


def main():
    data = {}
    try:
        for row in json.load(open(os.path.join(ROOT, "data", "projects.json"))):
            data[row["slug"]] = row
    except FileNotFoundError:
        print("data/projects.json not found, map data will be empty", file=sys.stderr)

    bundle, warnings = [], []

    for path in sorted(glob.glob(os.path.join(ROOT, "project-*.html"))):
        slug = os.path.basename(path)[len("project-"):-5]
        page = open(path, encoding="utf-8").read()
        if 'http-equiv="refresh"' in page:
            continue  # redirect stub for a renamed project, not a project itself
        main_html = first(r"<main[^>]*>(.*)</main>", page)
        if not main_html:
            warnings.append("%s: no <main> element, skipped" % slug)
            continue

        sections = SECTION_RE.findall(main_html)
        hero = next((s for s in sections if is_hero(s)), "")

        title = strip_tags(first(r"<h1[^>]*>(.*?)</h1>", hero or main_html))
        excerpt = strip_tags(first(r'<p class="lede[^"]*">(.*?)</p>', hero))
        hero_img = first(r'<img[^>]*\bsrc="([^"]+)"', hero) or first(r"--chi:url\('([^']+)'\)", hero)
        hero_alt = html.unescape(first(r'<img[^>]*\balt="([^"]*)"', hero))
        hero_label = strip_tags(first(r'<span class="ey[^"]*">(.*?)</span>', hero)).lower()

        credit, body = "", []
        for s in sections:
            if s is hero:
                continue
            label = ey_of(s)
            if label == "more from this pillar":
                continue  # template renders "More projects"
            if 'class="pj-back"' in s[:200]:
                continue  # back link, template handles navigation
            if 'class="sec dark"' in s[:200] and "Help fund work like this" in s:
                continue  # template renders the donate band
            if label == "with thanks":
                credit = strip_tags(first(r'<p class="lede[^"]*">(.*?)</p>', s))
            body.append(rewrite_links(s.strip()))

        meta = data.get(slug, {})
        pillar = PILLAR_FROM_DATA.get(meta.get("pillar", ""), "") or PILLAR_FROM_LABEL.get(hero_label, "")

        if not title:
            warnings.append("%s: no title found" % slug)
        if not hero_img:
            warnings.append("%s: no hero image found" % slug)
        if slug not in data:
            warnings.append("%s: not in data/projects.json, so no map pin or location" % slug)

        images = set(local_images("\n".join(body)))
        if hero_img.startswith("assets/img/"):
            images.add(hero_img)

        bundle.append({
            "slug": slug,
            "title": title or meta.get("title", slug),
            "excerpt": excerpt,
            "pillar": pillar,
            "state": meta.get("state", ""),
            "lat": meta.get("lat", 0),
            "lon": meta.get("lon", 0),
            "on_map": bool(meta.get("on_map", False)),
            "legacy_url": meta.get("live_url", ""),
            "hero_image": hero_img,
            "hero_alt": hero_alt,
            "credit": credit,
            "sections": body,
            "images": sorted(images),
            "source_modified": int(os.path.getmtime(path)),
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, ensure_ascii=False, indent=1)

    print("Wrote %d projects to %s" % (len(bundle), os.path.relpath(OUT, ROOT)))
    print("  with credit line: %d" % sum(1 for b in bundle if b["credit"]))
    print("  local images to upload: %d" % len({i for b in bundle for i in b["images"]}))
    if warnings:
        print("\nCheck these:")
        for w in warnings:
            print("  " + w)


if __name__ == "__main__":
    main()
