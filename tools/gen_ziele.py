"""Trägt die Bilder aus Manöver-, Artillerie- und Flugabwehr-Trainer in den Ziel-Trainer ein.

Läuft automatisch mit tools/build.py, damit neue oder entfernte Bilder dort sofort ankommen.
Aufruf einzeln:  python3 tools/gen_ziele.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINERS = {'manoever': 'm', 'artillerie': 'a', 'flugabwehr': 'f'}


def const(s, name):
    i = s.index('const %s = ' % name) + len('const %s = ' % name)
    return json.JSONDecoder().raw_decode(s[i:])[0]


def pool():
    out = {}
    for t, short in TRAINERS.items():
        s = open(os.path.join(ROOT, t, 'index.html'), encoding='utf-8').read()
        fams = const(s, 'DATA')['families']
        img = const(s, 'IMG')
        cred = const(s, 'CRED') if 'const CRED = ' in s else {}
        meta = const(s, 'IMETA') if 'const IMETA = ' in s else {}
        for f in fams:
            fid = f['id']
            pics = []
            for i, p in enumerate(img.get(fid, [])):
                m = (meta.get(fid) or [{}] * (i + 1))[i] if i < len(meta.get(fid) or []) else {}
                if m.get('air'):
                    continue  # nur Bodenaufnahmen – Drohnen- und Pod-Bilder sind eine eigene Übung
                c = (cred.get(fid) or [])
                pics.append(['../%s/%s' % (t, p), c[i] if i < len(c) else ''])
            if pics:
                out[fid] = {'n': f['name'], 't': short + ':' + f['cat'], 'img': pics}
    return out


def main():
    p = os.path.join(ROOT, 'ziele', 'index.html')
    s = open(p, encoding='utf-8').read()
    data = json.dumps(pool(), ensure_ascii=False, separators=(',', ':'))
    new, n = re.subn(r'/\*POOL\*/.*?/\*END\*/', lambda m: '/*POOL*/' + data + '/*END*/', s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('Platzhalter /*POOL*/…/*END*/ fehlt in ziele/index.html')
    if new != s:
        open(p, 'w', encoding='utf-8').write(new)
        print('ziele/index.html: Bilder aktualisiert')


if __name__ == '__main__':
    main()
