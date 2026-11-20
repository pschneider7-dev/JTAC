"""Baut die Website nach _site/ und trägt die Offline-Liste in den Service Worker ein.

Aufruf:  python3 tools/build.py
Testen:  python3 -m http.server -d _site 8000   →  http://localhost:8000/
"""
import datetime
import hashlib
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site')
SKIP_DIRS = {'.git', '.github', '_site', 'tools'}
SKIP_FILES = {'README.md', '.gitignore'}
NOT_PRECACHED = ('.txt', '.md')
IMG_EXT = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.svg')
TEXT_EXT = ('.html', '.js', '.css', '.json', '.webmanifest')
IMG_REF = re.compile(r'(?<![\w/.-])((?:\.\./)*(?:[\w-]+/)*img/)([\w.-]+?\.(?:webp|jpe?g|png|gif|svg))(?![\w.-])')


def hash_images():
    """Gibt jedem Bild in einem img/-Ordner einen Namen mit Prüfsumme (t90-8.webp → t90-8.3fa91c2e.webp)
    und trägt die neuen Namen in alle Seiten und Skripte ein. Ein geändertes Bild bekommt so immer eine neue
    Adresse: Eine zwischengespeicherte alte Seite kann nie das neue Bild mit den alten Markierungen zeigen."""
    names = {}
    for dirpath, _, filenames in os.walk(OUT):
        if os.path.basename(dirpath) != 'img':
            continue
        for name in filenames:
            if not name.lower().endswith(IMG_EXT):
                continue
            path = os.path.join(dirpath, name)
            with open(path, 'rb') as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()[:8]
            base, ext = os.path.splitext(name)
            new = f'{base}.{digest}{ext}'
            os.rename(path, os.path.join(dirpath, new))
            names[os.path.relpath(path, OUT).replace(os.sep, '/')] = new
    broken = []
    for dirpath, _, filenames in os.walk(OUT):
        for name in filenames:
            if not name.endswith(TEXT_EXT) or name == 'sw.js':
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding='utf-8') as fh:
                text = fh.read()
            here = os.path.relpath(dirpath, OUT)

            def swap(m):
                target = os.path.normpath(os.path.join(here, m.group(1), m.group(2))).replace(os.sep, '/')
                if target in names:
                    return m.group(1) + names[target]
                broken.append(f'{os.path.relpath(path, OUT)}: {m.group(0)}')
                return m.group(0)
            new_text = IMG_REF.sub(swap, text)
            if new_text != text:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(new_text)
    if broken:
        raise SystemExit('Bildverweise ohne Datei:\n  ' + '\n  '.join(sorted(set(broken))[:40]))
    return len(names)


def site_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.'))
        for name in sorted(filenames):
            if name in SKIP_FILES or name.startswith('.'):
                continue
            path = os.path.join(dirpath, name)
            yield os.path.relpath(path, ROOT).replace(os.sep, '/')


def main():
    import gen_ziele  # Ziel-Trainer aus den Bildern der anderen Trainer füllen
    gen_ziele.main()
    import gen_symbole  # Symbol-Trainer: Fahrzeugnamen und -bilder aus den Rot-Trainern
    gen_symbole.main()
    shutil.rmtree(OUT, ignore_errors=True)
    for rel in site_files():
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), dest)
    n_img = hash_images()
    entries = []
    for dirpath, dirnames, filenames in os.walk(OUT):
        dirnames.sort()
        for name in sorted(filenames):
            dest = os.path.join(dirpath, name)
            rel = os.path.relpath(dest, OUT).replace(os.sep, '/')
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

    print(f'_site/ gebaut: {len(entries)} Dateien offline verfügbar ({n_img} Bilder mit Prüfsummen-Namen), Version {version}')


if __name__ == '__main__':
    main()
