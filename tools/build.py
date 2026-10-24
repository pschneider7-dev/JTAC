"""Baut die Website nach _site/ und trägt die Offline-Liste in den Service Worker ein.

Aufruf:  python3 tools/build.py
Testen:  python3 -m http.server -d _site 8000   →  http://localhost:8000/
"""
import datetime
import hashlib
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site')
SKIP_DIRS = {'.git', '.github', '_site', 'tools'}
SKIP_FILES = {'README.md', '.gitignore'}
NOT_PRECACHED = ('.txt', '.md')


def site_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.'))
        for name in sorted(filenames):
            if name in SKIP_FILES or name.startswith('.'):
                continue
            path = os.path.join(dirpath, name)
            yield os.path.relpath(path, ROOT).replace(os.sep, '/')


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    entries = []
    for rel in site_files():
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dest)
        if rel == 'sw.js' or rel.endswith(NOT_PRECACHED):
            continue
        with open(dest, 'rb') as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()[:12]
        # Seiten werden über ihren Ordner aufgerufen („manoever/“ statt „manoever/index.html“)
        url = rel[:-len('index.html')] if rel.endswith('index.html') else rel
        entries.append([url or './', digest])

    # Seiten und Skripte zuerst, Bilder danach
    entries.sort(key=lambda e: ('/img/' in e[0], e[0]))
    total = hashlib.sha256(json.dumps(entries).encode()).hexdigest()[:8]
    version = f'{datetime.date.today().isoformat()}-{total}'

    sw_path = os.path.join(OUT, 'sw.js')
    with open(sw_path, encoding='utf-8') as fh:
        sw = fh.read()
    for old, new in [("const VERSION = 'dev';", f'const VERSION = {json.dumps(version)};'),
                     ('const PRECACHE = [];', 'const PRECACHE = ' + json.dumps(entries, separators=(',', ':')) + ';')]:
        if old not in sw:
            raise SystemExit(f'Platzhalter fehlt in sw.js: {old}')
        sw = sw.replace(old, new)
    with open(sw_path, 'w', encoding='utf-8') as fh:
        fh.write(sw)

    print(f'_site/ gebaut: {len(entries)} Dateien offline verfügbar, Version {version}')


if __name__ == '__main__':
    main()
