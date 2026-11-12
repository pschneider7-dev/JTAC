"""Trägt Namen und Bodenbilder der Fahrzeuge aus Manöver-, Artillerie- und Flugabwehr-Trainer in den Symbol-Trainer ein.

Läuft automatisch mit tools/build.py, damit neue oder entfernte Bilder dort sofort ankommen.
Aufruf einzeln:  python3 tools/gen_symbole.py
"""
import json
import os
import re

import gen_ziele

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    p = os.path.join(ROOT, 'symbole', 'index.html')
    s = open(p, encoding='utf-8').read()
    pool = {fid: {'n': f['n'], 'img': f['img']} for fid, f in gen_ziele.pool().items()}
    data = json.dumps(pool, ensure_ascii=False, separators=(',', ':'))
    new, n = re.subn(r'/\*VIMG\*/.*?/\*END\*/', lambda m: '/*VIMG*/' + data + '/*END*/', s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('Platzhalter /*VIMG*/…/*END*/ fehlt in symbole/index.html')
    if new != s:
        open(p, 'w', encoding='utf-8').write(new)
        print('symbole/index.html: Fahrzeugbilder aktualisiert')


if __name__ == '__main__':
    main()
