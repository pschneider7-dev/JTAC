"""BTR-60PB und BTR-70 in den Manöver-Trainer (DATA, IMG, VAR, AR, ARS, PINS, ANNO, CMP).
Aufruf: python3 patch_btr.py <manoever/index.html> <bilder.json>
bilder.json: {"btr60": [{"file", "ar", "pins"?}, ...], "btr70": [...], "anno": {"btr60": [...], "btr70": [...]},
              "cmp": [{"a": {...}, "b": {...}, "key": "..."}]}"""
import json
import sys

path, cfg_path = sys.argv[1], sys.argv[2]
s = open(path, encoding='utf-8').read()
cfg = json.load(open(cfg_path, encoding='utf-8'))


def const_json(name):
    i = s.index('const %s = ' % name) + len('const %s = ' % name)
    obj, n = json.JSONDecoder().raw_decode(s[i:])
    return obj, i, i + n


def put(name, obj):
    global s
    _, i, j = const_json(name)
    s = s[:i] + json.dumps(obj, ensure_ascii=False) + s[j:]


D, _, _ = const_json('DATA')
if any(f['id'] in ('btr60', 'btr70') for f in D['families']):
    raise SystemExit('schon drin')

AA_Q = ["14,5-mm-MG mit nur ca. 30° Rohrerhöhung – geringe Gefahr",
        ["30-mm-Maschinenkanone mit 74° Rohrerhöhung", "Kanonen-Lenkflugkörper durch eine 125-mm-Kanone",
         "Fla-Lenkflugkörper Ataka mit Annäherungszünder (bis ca. 7 km)"]]
BTR60 = {
    "id": "btr60", "name": "BTR-60PB", "short": "B60", "cat": "tpzr", "wcls": "apc",
    "designation": "BTR-60PB – erster Radschützenpanzer 8×8 der Sowjetarmee (1966) mit Kegelturm; der ältere BTR-60P hatte keinen Turm. Heute v. a. Reserve und Ausland",
    "users": "Viele Staaten in Afrika, Asien und Osteuropa; Russland und die Ukraine aus Reservebeständen",
    "weapons": ["14,5-mm-MG KPWT im Kegelturm (Rohrerhöhung nur ca. 30°)", "7,62-mm-MG koaxial"],
    "protection": "Stahl, ca. 7–9 mm – nur gegen Gewehrmunition und Splitter.",
    "weak": "Dünne Panzerung, zwei Benzinmotoren im Heck (brennt leicht), Reifen; Aussteigen nur über die Dachluken.",
    "recog": "Acht Räder, langer spitzer Bug, keine Seitentüren – die Infanterie steigt über Luken im Dach aus; Kegelturm wie beim BRDM-2.",
    "confuse": ["btr70", "btr"],
    "jtac": [
        "Kegelturm wie beim BRDM-2: geringe Rohrerhöhung – für Lfz wenig gefährlich.",
        "Jede Bordkanone und APKWS reichen – keine teuren Panzerabwehrwaffen verschwenden.",
        "Wird von beiden Seiten aus Reservebeständen genutzt – Freund oder Feind nicht am Typ festmachen.",
    ],
    "vars": [{"v": None, "name": "BTR-60PB", "tis": "day", "lwr": "no", "heli": "gering",
              "sight": "Tagvisier für den Richtschützen, einfache IR-Nachtsicht für Fahrer und Kommandant.",
              "aa": "14,5-mm-MG, aber nur ca. 30° Rohrerhöhung – geringe Gefahr für Lfz.", "aaQ": AA_Q}],
}
BTR70 = {
    "id": "btr70", "name": "BTR-70", "short": "B70", "cat": "tpzr", "wcls": "apc",
    "designation": "BTR-70 – Radschützenpanzer 8×8 (1976), Nachfolger des BTR-60PB und Vorgänger des BTR-80; Kegelturm mit 14,5-mm-MG, zahlreiche Modernisierungen",
    "users": "Russland, Ukraine, Belarus und weitere Staaten",
    "weapons": ["14,5-mm-MG KPWT im Kegelturm (Rohrerhöhung nur ca. 30°)", "7,62-mm-MG koaxial"],
    "protection": "Stahl, ca. 7–9 mm – nur gegen Gewehrmunition und Splitter.",
    "weak": "Dünne Panzerung, zwei Benzinmotoren im Heck (brennt leicht), Reifen; nur kleine Seitenluken zum Aussteigen.",
    "recog": "Acht Räder mit Lücke zwischen 2. und 3. Achse, dort eine kleine, tief liegende Seitenluke; Kegelturm wie beim BTR-60PB und BRDM-2.",
    "confuse": ["btr", "btr60"],
    "jtac": [
        "Von Russland und der Ukraine genutzt – Freund oder Feind nicht am Typ erkennen, sondern an Lage, Markierung und Kennung.",
        "Kegelturm mit geringer Rohrerhöhung – für Lfz wenig gefährlich, anders als der BTR-82A mit 30 mm.",
        "Jede Bordkanone und APKWS reichen.",
    ],
    "vars": [{"v": None, "name": "BTR-70", "tis": "ii", "lwr": "no", "heli": "gering",
              "sight": "Tagvisier, Kommandant mit aktivem IR-Nachtsichtgerät – nachts nur kurze Reichweite.",
              "aa": "14,5-mm-MG, aber nur ca. 30° Rohrerhöhung – geringe Gefahr für Lfz.", "aaQ": AA_Q}],
}
fams = D['families']
k = next(n for n, f in enumerate(fams) if f['id'] == 'btr')
fams[k:k] = [BTR60, BTR70]

# BTR-80/82A: Verwechslung mit BTR-70 ergänzen
btr = fams[k + 2]
if 'btr70' not in btr['confuse']:
    btr['confuse'].insert(0, 'btr70')

D['curated'].append(
    ["r-9", "btr70", "Woran unterscheidest du BTR-60PB, BTR-70 und BTR-80 von der Seite?",
     ["BTR-60PB ohne Seitentür, BTR-70 mit kleiner tiefer Luke, BTR-80 mit großer zweiteiliger Tür zwischen 2. und 3. Achse",
      "Gar nicht – alle drei sehen gleich aus", "An der Zahl der Räder", "Nur der BTR-80 hat einen Turm"],
     "Die Seitentür ist das sicherste Merkmal: Beim BTR-60PB steigt die Infanterie über das Dach aus, der BTR-70 hat eine kleine, tief liegende Luke, der BTR-80 eine große Tür zwischen 2. und 3. Achse. BTR-60PB und BTR-70 tragen den Kegelturm mit nur ca. 30° Rohrerhöhung."])
if any(c[0] == 'r-9' for c in D['curated'][:-1]):
    raise SystemExit('ID r-9 schon vergeben')
put('DATA', D)

# IMG ist mehrzeilig: vor "btr" einfügen
for fid in ('btr60', 'btr70'):
    line = '"%s": [%s],\n' % (fid, ', '.join('"img/%s"' % x['file'] for x in cfg[fid]))
    k = s.index('"btr": ["img/btr-0.webp"')
    s = s[:k] + line + s[k:]

for name, fn in (('VAR', lambda L: [None] * len(L)), ('ARS', lambda L: [x['ar'] for x in L])):
    obj, _, _ = const_json(name)
    for fid in ('btr60', 'btr70'):
        obj[fid] = fn(cfg[fid])
    put(name, obj)
AR, _, _ = const_json('AR')
for fid in ('btr60', 'btr70'):
    AR[fid] = cfg[fid][0]['ar']
put('AR', AR)
PINS, _, _ = const_json('PINS')
for fid in ('btr60', 'btr70'):
    PINS[fid] = {str(i): x['pins'] for i, x in enumerate(cfg[fid]) if x.get('pins')}
put('PINS', PINS)
ANNO, _, _ = const_json('ANNO')
ANNO.update(cfg['anno'])
put('ANNO', ANNO)
CMP, _, _ = const_json('CMP')
CMP += cfg['cmp']
put('CMP', CMP)

open(path, 'w', encoding='utf-8').write(s)
print('ok')
