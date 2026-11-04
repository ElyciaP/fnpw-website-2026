#!/usr/bin/env python3
"""Write the final, formatted value into every [data-count] element.

main.js animates counters from 0 when it runs, but the HTML used to hold a literal "0",
so crawlers, reader modes and no-JS visitors saw zeros. This rewrites the text content of
each [data-count] element in every page to its formatted final value: en-AU thousands
separators, `data-dec` decimal places, `data-pre` prefix and `data-suf` suffix applied
(600,000+ / 1.2M / $3.8M). Safe to re-run; it is idempotent.

    python3 tools/fix_counters.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(r'<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)(?P<attrs>[^>]*\bdata-count=[^>]*)>(?P<text>[^<]*)</(?P=tag)>')
ATTR = re.compile(r'\b(data-count|data-dec|data-pre|data-suf)="([^"]*)"')


def fmt(attrs):
    a = dict(ATTR.findall(attrs))
    if 'data-count' not in a:
        return None
    try:
        value = float(a['data-count'])
    except ValueError:
        return None
    dec = int(a.get('data-dec') or 0)
    body = f'{value:,.{dec}f}'  # en-AU: comma thousands, dot decimals, same as toLocaleString('en-AU')
    return a.get('data-pre', '') + body + a.get('data-suf', '')


def main():
    changed = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith('.html'):
            continue
        path = os.path.join(ROOT, name)
        with open(path, encoding='utf-8') as fh:
            src = fh.read()

        def repl(m):
            out = fmt(m.group('attrs'))
            if out is None or m.group('text') == out:
                return m.group(0)
            return f'<{m.group("tag")}{m.group("attrs")}>{out}</{m.group("tag")}>'

        new = TAG.sub(repl, src)
        if new != src:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new)
            changed += 1
            print('updated', name)
    print(f'done: {changed} file(s) changed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
