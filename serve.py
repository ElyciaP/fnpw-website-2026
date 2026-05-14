#!/usr/bin/env python3
"""Live-reload dev server. Serves static files and auto-reloads the browser on any .html save."""
import http.server
import os
import queue
import threading
import time
from pathlib import Path

PORT = 8000
ROOT = Path(__file__).parent

_SCRIPT = (
    b'<script>(function(){'
    b'var s=new EventSource("/__lr");'
    b's.onmessage=function(){window.location.reload()};'
    b's.onerror=function(){setTimeout(function(){window.location.reload()},2000)}'
    b'})()</script>'
)

_clients = []
_lock = threading.Lock()


def _broadcast():
    with _lock:
        for q in list(_clients):
            try:
                q.put_nowait('reload')
            except queue.Full:
                pass


def _watcher():
    seen = {}
    while True:
        changed = False
        for f in ROOT.glob('*.html'):
            m = f.stat().st_mtime
            if f in seen and seen[f] != m:
                changed = True
            seen[f] = m
        if changed:
            print('  ↻  Change detected — reloading browser...')
            _broadcast()
        time.sleep(0.4)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split('?')[0] == '/__lr':
            self._sse()
            return
        fspath = self.translate_path(self.path)
        if os.path.isdir(fspath):
            fspath = os.path.join(fspath, 'index.html')
        if fspath.endswith('.html') and os.path.isfile(fspath):
            self._html(fspath)
        else:
            super().do_GET()

    def _html(self, path):
        try:
            raw = Path(path).read_bytes()
        except OSError:
            self.send_error(404)
            return
        body = raw.replace(b'</body>', _SCRIPT + b'</body>', 1)
        if body == raw:
            body = raw + _SCRIPT
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _sse(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        q = queue.Queue(maxsize=4)
        with _lock:
            _clients.append(q)
        try:
            while True:
                try:
                    data = q.get(timeout=25)
                    self.wfile.write(f'data: {data}\n\n'.encode())
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b': keep-alive\n\n')
                    self.wfile.flush()
        except Exception:
            pass
        finally:
            with _lock:
                try:
                    _clients.remove(q)
                except ValueError:
                    pass

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    threading.Thread(target=_watcher, daemon=True).start()
    print(f'\n  Dev server ready →  http://localhost:{PORT}')
    print(f'  Watching {ROOT}/*.html for changes')
    print('  Press Ctrl+C to stop.\n')
    with http.server.ThreadingHTTPServer(('', PORT), Handler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\n  Server stopped.')
