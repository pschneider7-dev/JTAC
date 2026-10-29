"""2S43 Malva in den Artillerie-Trainer (DATA, IMG, IMETA, ARS, PINS).
Aufruf: python3 patch_malva.py <artillerie/index.html> <bilder.json>
bilder.json: {"imgs": [{"file", "f", "ar", "pins"?}], "cmp": {"i": 0, "pins": [...]} | null}"""
import json
import sys

path, cfg_path = sys.argv[1], sys.argv[2]
s = open(path, encoding='utf-8').read()
cfg = json.load(open(cfg_path, encoding='utf-8'))
imgs = cfg['imgs']


def const_json(name):
    i = s.index('const %s = ' % name) + len('const %s = ' % name)
    obj, n = json.JSONDecoder().raw_decode(s[i:])
    return obj, i, i + n


def put(name, obj):
    global s
    _, i, j = const_json(name)
    s = s[:i] + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + s[j:]


D, _, _ = const_json('DATA')
if any(f['id'] == '2s43' for f in D['families']):
    raise SystemExit('schon drin')

D['cats']['rdh'] = {"label": "Radhaubitze (Lkw-Fahrgestell)",
                    "cap": "Rohrartillerie auf schwerem Radfahrgestell, nur die Kabine geschützt – schnell in und aus Stellung"}
D['catOrder'].insert(D['catOrder'].index('sph') + 1, 'rdh')
D['catExcl']['rdh'] = ['sph']
D['catExcl'].setdefault('sph', []).append('rdh')
D['posRules']['rdh'] = D['posRules']['sph']

MALVA = {
    "id": "2s43", "name": "2S43 Malva", "short": "2S43", "cat": "rdh", "wcls": "soft", "pos": "mid",
    "rng": "ca. 25 km", "rngKm": 25,
    "designation": "2S43 Malva – 152-mm-Radhaubitze auf dem 8×8-Fahrgestell BAZ-6010 (seit 2023 in der Truppe), soll die gezogene 2A65 Msta-B ablösen",
    "users": "Russland",
    "weapons": ["152-mm-Haubitze 2A64 – dieselbe Kanone wie bei 2S19 Msta-S und 2A65 Msta-B",
                "Kann lasergelenkte Krasnopol-Granaten verschießen"],
    "protection": "Nur die Kabine ist gegen Gewehrmunition und Splitter geschützt, Geschütz und Munition liegen offen.",
    "weak": "Geschütz, Munition und Reifen ungeschützt; großes, auffälliges Fahrzeug, auf Straßen angewiesen.",
    "recog": "Großes 8×8-Radfahrzeug mit gepanzerter Kabine vorn und langem 152-mm-Rohr mit Mündungsbremse offen auf dem Heck.",
    "confuse": ["2s19", "2a65"],
    "jtac": [
        "Neu und noch selten – im Zweifel wie eine 2S19 einplanen: gleiche Kanone, ca. 25 km Reichweite.",
        "Schießt und fährt schnell wieder ab; zwischen den Stellungen auf Straßen und Feldwegen unterwegs.",
        "Nur die Kabine ist geschützt – Splitterwirkung reicht, Munitionsfahrzeuge stehen in der Nähe.",
        "Nicht mit westlichen Radhaubitzen verwechseln, z. B. CAESAR oder 2S22 Bohdana der Ukraine.",
    ],
    "vars": [{"v": None, "name": "2S43 Malva"}],
}
fams = D['families']
fams.insert(next(k for k, f in enumerate(fams) if f['id'] == '2s7') + 1, MALVA)
for g in D['groups']:
    if '2s19' in g[1]:
        g[1].append('2s43')
D['curated'].append(
    ["r-8", "2s43", "Was unterscheidet die 2S43 Malva von der 2S19 Msta-S?",
     ["Räder statt Ketten: gleiche 152-mm-Kanone offen auf einem 8×8-Lkw, nur die Kabine ist geschützt",
      "Die Malva hat eine größere Kanone (203 mm)", "Die Malva ist ein Raketenwerfer", "Kein Unterschied – nur ein anderer Name"],
     "Die 2S43 Malva trägt dieselbe 152-mm-Kanone 2A64 wie die 2S19 Msta-S, aber offen auf dem Radfahrgestell BAZ-6010. Reichweite gleich (ca. 25 km), Schutz geringer: Splitterwirkung reicht."])
if [c[0] for c in D['curated']].count('r-8') > 1:
    raise SystemExit('ID r-8 schon vergeben')
if cfg.get('cmp'):
    msta = next(c for c in D['compare'] if c['b']['fam'] == '2s19')['b']
    D['compare'].append({"a": {"fam": "2s43", "f": imgs[cfg['cmp']['i']]['f'], "lab": "2S43 Malva", "pins": cfg['cmp']['pins'], "i": cfg['cmp']['i']},
                         "b": msta,
                         "key": "Gleiche 152-mm-Kanone, anderes Fahrzeug: Die Malva fährt auf acht Rädern und trägt das Geschütz offen auf dem Heck, die Msta-S auf Ketten mit großem, geschlossenem Turm."})
put('DATA', D)

line = '"2s43": [%s],\n' % ', '.join('"img/%s"' % x['file'] for x in imgs)
k = s.index('"2s9": ["img/2s9-0.webp"')
s = s[:k] + line + s[k:]
IMETA, _, _ = const_json('IMETA')
IMETA['2s43'] = [{"f": x['f'], "v": None, "e": None, "air": False, "ask": None} for x in imgs]
put('IMETA', IMETA)
ARS, _, _ = const_json('ARS')
ARS['2s43'] = [x['ar'] for x in imgs]
put('ARS', ARS)
PINS, _, _ = const_json('PINS')
PINS['2s43'] = {str(i): x['pins'] for i, x in enumerate(imgs) if x.get('pins')}
put('PINS', PINS)
open(path, 'w', encoding='utf-8').write(s)
print('ok')
