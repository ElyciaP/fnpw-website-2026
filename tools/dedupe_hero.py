"""Stop the feature image appearing a second time inside the article body.

WordPress often uses the same upload as the post's feature image and as the first
picture in the body, so the hero and the opening body image were the same
photograph twice in a row. This drops the body copy of it.

Matching ignores the WordPress size suffix, so 8-1024x537.jpg and 8-2560x1344.jpg
count as the same upload.

A band or story block carries text as well as its picture, so those keep their
heading and paragraphs and simply become a text block. Only a picture-only block
is removed outright. The dark chapter break and the alternating bands are then
reassigned, because removing a band can leave an article without either.

    python3 tools/dedupe_hero.py            # patch data/articles.json
    python3 tools/dedupe_hero.py --report   # say what it would do, write nothing
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

DATA = 'data/articles.json'


def upload_key(url):
    """Basename with the WordPress rendition suffix removed."""
    if not url:
        return ''
    base = os.path.basename(url.split('?')[0])
    return re.sub(r'-\d+x\d+(?=\.\w+$)', '', base).lower()


def restyle(blocks):
    """Alternate the bands and put the dark chapter break back on one of them."""
    for b in blocks:
        b.pop('flip', None)
        if b.get('type') == 'story':
            b['type'] = 'band'
    bands = [i for i, b in enumerate(blocks) if b.get('type') == 'band']
    for n, i in enumerate(bands):
        if n % 2:
            blocks[i]['flip'] = True
    if bands:
        pick = bands[min(len(bands) - 1, max(0, int(len(bands) * 0.65)))]
        blocks[pick]['type'] = 'story'
        blocks[pick].pop('flip', None)
    return blocks


def main():
    report = '--report' in sys.argv
    arts = json.load(open(DATA, encoding='utf-8'))
    removed, demoted, touched = 0, 0, []

    for a in arts:
        hero = upload_key(a.get('hero', ''))
        if not hero:
            continue
        out, hit = [], False
        for b in a.get('blocks', []):
            if b.get('img') and upload_key(b['img']) == hero:
                hit = True
                has_text = bool(b.get('flow') or b.get('paras') or b.get('heading'))
                if has_text:
                    for k in ('img', 'alt', 'caption'):
                        b.pop(k, None)
                    b['type'] = 'text'
                    demoted += 1
                    out.append(b)
                else:
                    removed += 1
                continue
            out.append(b)
        if hit:
            a['blocks'] = restyle(out)
            touched.append(a['slug'])

    print('articles where the feature image also sat in the body : %d' % len(touched))
    print('  picture-only blocks removed                         : %d' % removed)
    print('  band or story blocks kept, picture dropped          : %d' % demoted)
    if report:
        for s in touched[:15]:
            print('    ' + s)
        return
    json.dump(arts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote %s' % DATA)


if __name__ == '__main__':
    main()
