"""Small HTML tree builder that keeps source offsets, so unconverted markup can be
carried across byte for byte. Standard library only."""
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class Node:
    __slots__ = ('tag', 'attrs', 'start', 'open_end', 'close_start', 'end', 'children', 'parent', 'kind')

    def __init__(self, kind, tag=None, attrs=None, start=0, parent=None):
        self.kind = kind            # 'el', 'text', 'comment'
        self.tag = tag
        self.attrs = attrs or []
        self.start = start
        self.open_end = start
        self.close_start = start
        self.end = start
        self.children = []
        self.parent = parent

    def attr(self, name, default=None):
        for k, v in self.attrs:
            if k == name:
                return v if v is not None else ''
        return default

    def classes(self):
        return (self.attr('class') or '').split()

    def elements(self):
        return [c for c in self.children if c.kind == 'el']


class TreeBuilder(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for i, ch in enumerate(src):
            if ch == '\n':
                self.lines.append(i + 1)
        self.root = Node('el', '#root', start=0)
        self.root.end = self.root.close_start = len(src)
        self.cur = self.root
        self.errors = []
        self.feed(src)
        self.close()
        while self.cur is not self.root:
            self.errors.append('unclosed <%s>' % self.cur.tag)
            self.cur.close_start = self.cur.end = len(src)
            self.cur = self.cur.parent

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.off()
        raw = self.get_starttag_text()
        n = Node('el', tag, attrs, start, self.cur)
        n.open_end = start + len(raw)
        self.cur.children.append(n)
        if tag in VOID or raw.endswith('/>'):
            n.close_start = n.end = n.open_end
        else:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        start = self.off()
        raw = self.get_starttag_text()
        n = Node('el', tag, attrs, start, self.cur)
        n.open_end = n.close_start = n.end = start + len(raw)
        self.cur.children.append(n)

    def handle_endtag(self, tag):
        start = self.off()
        end = self.src.index('>', start) + 1
        if tag in VOID:
            return
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            self.errors.append('stray </%s> at %d' % (tag, start))
            return
        while self.cur is not n:
            self.errors.append('implicitly closed <%s> by </%s> at %d' % (self.cur.tag, tag, start))
            self.cur.close_start = self.cur.end = start
            self.cur = self.cur.parent
        n.close_start = start
        n.end = end
        self.cur = n.parent

    def _leaf(self, kind, length):
        start = self.off()
        n = Node(kind, None, None, start, self.cur)
        n.end = n.open_end = n.close_start = start + length
        self.cur.children.append(n)

    def handle_data(self, data):
        self._leaf('text', len(data))

    def handle_entityref(self, name):
        start = self.off()
        end = start + 1 + len(name)
        if self.src[end:end + 1] == ';':
            end += 1
        n = Node('text', None, None, start, self.cur)
        n.end = end
        self.cur.children.append(n)

    def handle_charref(self, name):
        start = self.off()
        end = start + 2 + len(name)
        if self.src[end:end + 1] == ';':
            end += 1
        n = Node('text', None, None, start, self.cur)
        n.end = end
        self.cur.children.append(n)

    def handle_comment(self, data):
        self._leaf('comment', len(data) + 7)

    def handle_decl(self, decl):
        self._leaf('comment', len(decl) + 3)


def parse(src):
    tb = TreeBuilder(src)
    return tb.root, tb.errors
