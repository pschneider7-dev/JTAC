"""Erzeugt blau/index.html (Blau-Trainer) aus dem Manöver-Trainer als Vorlage.
Aufruf: python3 gen_blau.py <jtac-Repo> <blau_imgs.json>
blau_imgs.json: {"<fid>": [{"file": "leo2-0.webp", "ar": 1.5, "v": "a6"|null, "pins": [[x, y, "Text"], ...]|null}, ...]}"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blau_data as B  # noqa: E402

repo, imgs_path = sys.argv[1], sys.argv[2]
IM = json.load(open(imgs_path, encoding='utf-8'))
src = open(os.path.join(repo, 'manoever', 'index.html'), encoding='utf-8').read()
J = lambda o: json.dumps(o, ensure_ascii=False)


def const_json(s, name):
    i = s.index('const %s = ' % name) + len('const %s = ' % name)
    return json.JSONDecoder().raw_decode(s[i:])


def other(trainer):
    return open(os.path.join(repo, trainer, 'index.html'), encoding='utf-8').read()


# ---------- Rot-Gegenstücke aus den anderen Trainern ----------
RED = []
cache = {}
for f in B.F:
    tr, fid, i, name, key = f['red']
    if tr not in cache:
        s = other(tr)
        img = const_json(s, 'IMG')[0] if tr == 'manoever' else None
        if img is None:      # IMG im Artillerie-Trainer ist mehrzeilig, aber gültiges JSON
            img = const_json(s, 'IMG')[0]
        ars = const_json(s, 'ARS')[0]
        pins = const_json(s, 'PINS')[0]
        anno = const_json(s, 'ANNO')[0] if 'const ANNO = ' in s else {}
        cache[tr] = (img, ars, pins, anno)
    img, ars, pins, anno = cache[tr]
    p = (pins.get(fid) or {}).get(str(i)) or (anno.get(fid) if i == 0 else None) or []
    RED.append({"blue": f['id'], "src": '../%s/%s' % (tr, img[fid][i]), "ar": ars[fid][i], "name": name, "key": key, "pins": p})

# ---------- Daten ----------
fams = []
for f in B.F:
    g = {k: f[k] for k in ('id', 'name', 'short', 'cat', 'origin', 'designation', 'users', 'weapons', 'recog', 'confuse', 'jtac', 'vars')}
    fams.append(g)
DATA = {"cats": B.CATS, "catOrder": B.CAT_ORDER, "catExcl": B.CAT_EXCL, "catX": {}, "origins": B.ORIGINS,
        "families": fams, "curated": B.CURATED, "merk": B.MERK}
IMG = {f['id']: ['img/' + x['file'] for x in IM[f['id']]] for f in B.F}
VAR = {f['id']: [x.get('v') for x in IM[f['id']]] for f in B.F}
ARS = {f['id']: [x['ar'] for x in IM[f['id']]] for f in B.F}
ARS['red'] = [r['ar'] for r in RED]
AR = {k: v[0] for k, v in ARS.items() if k != 'red'}
PINS = {f['id']: {str(i): x['pins'] for i, x in enumerate(IM[f['id']]) if x.get('pins')} for f in B.F}
LEIT = {}
for f in B.F:
    if len(f['vars']) > 1:
        LEIT[f['id']] = {u['v']: next(i for i, x in enumerate(IM[f['id']]) if x.get('v') == u['v'] and x.get('pins')) for u in f['vars']}
ANNO = {f['id']: IM[f['id']][0]['pins'] for f in B.F if IM[f['id']][0].get('pins')}
CMP = [{"a": {"fam": r['blue'], "i": 0, "lab": next(f['name'] for f in B.F if f['id'] == r['blue']), "pins": ANNO.get(r['blue'], [])},
        "b": {"fam": "red", "i": k, "lab": r['name'] + ' (KR Rot)', "pins": r['pins']}, "key": r['key']} for k, r in enumerate(RED)]

s = src
s = s.replace('<title>Manöver-Trainer</title>', '<title>Blau-Trainer</title>')
# Datenkonstanten ersetzen
i0 = s.index('const DATA = ')
i1 = s.index('const FAMS = DATA.families;')
data_block = ''.join('const %s = %s;\n' % (n, J(v)) for n, v in (
    ('DATA', DATA), ('IMG', IMG), ('VAR', VAR), ('AR', AR), ('ARS', ARS), ('PINS', PINS), ('LEIT', LEIT),
    ('AIR', []), ('ANNO', ANNO), ('CMP', CMP), ('CMPTXT', {}), ('RED', RED)))
s = s[:i0] + data_block + s[i1:]

g0 = s.index('const GROUPS = [')
g1 = s.index('];', g0) + 2
s = s[:g0] + 'const GROUPS = %s;' % J(B.GROUPS) + s[g1:]
s = s.replace("const KEY = 'manoevertrainer.v1';", "const KEY = 'blautrainer.v1';")

m0 = s.index('const MODES = {')
m1 = s.index('};', m0) + 2
s = s[:m0] + """const MODES = {
  mix:  {name:'Gemischte Runde', kinds:['img','cat','var','ff','org','cur']},
  img:  {name:'Fahrzeuge erkennen', kinds:['img']},
  ff:   {name:'Freund oder Feind', kinds:['ff','cur'], tags:['f-']},
  cat:  {name:'Fahrzeugart erkennen', kinds:['cat','cur'], tags:['r-']},
  org:  {name:'Herkunft', kinds:['org']},
  var:  {name:'Versionen unterscheiden', kinds:['var']},
  conf: {name:'Verwechslungsgefahr', kinds:['img','var'], confusion:true},
};""" + s[m1:]

old_bank = """    bank.push({id:`wpn:${f.id}`, kind:'wpn', fam:f.id});
    f.vars.forEach((u, k) => {
      for (const kind of ['aa', 'lwr', 'tis']) bank.push({id:`${kind}:${f.id}:${k}`, kind, fam:f.id, k});
    });"""
assert old_bank in s
s = s.replace(old_bank, """    bank.push({id:`org:${f.id}`, kind:'org', fam:f.id});""")
old_air = "  AIR.forEach((_, i) => bank.push({id:`air:${i}`, kind:'air', fam:'air', i}));"
assert old_air in s
s = s.replace(old_air, """  RED.forEach((r, i) => {
    bank.push({id:`ff:b:${r.blue}`, kind:'ff', fam:r.blue, red:false, i});
    bank.push({id:`ff:r:${r.blue}`, kind:'ff', fam:r.blue, red:true, i});
  });""")

s = s.replace("const imgSrc = (fid, i) => fid === 'air' ? AIR[i] : IMG[fid][i];",
              "const imgSrc = (fid, i) => fid === 'air' ? AIR[i] : fid === 'red' ? RED[i].src : IMG[fid][i];")

old_cur = """    case 'cur':
      return {prompt:q.q, correct:q.opts[0], wrong:q.opts.slice(1), ex:q.ex};"""
assert old_cur in s
s = s.replace(old_cur, """    case 'ff': {
      const r = RED[q.i];
      const blue = `${f.name} – KR Blau`, red = `${r.name} – KR Rot`;
      const pool = shuffle([...FAMS.filter(x => x.id !== f.id).map(x => `${x.name} – KR Blau`), ...RED.filter(x => x !== r && x.name !== r.name).map(x => `${x.name} – KR Rot`)]);
      const others = uniq(pool).filter(o => o !== blue && o !== red).slice(0, 2);
      return {prompt:'Freund oder Feind – welches Fahrzeug ist das?', img:q.red ? ['red', q.i] : randomImg(f),
        correct:q.red ? red : blue, wrong:[q.red ? blue : red, ...others],
        ex:`${r.key} Der Typ allein entscheidet nie über Freund oder Feind – immer Lage, Kennzeichnung und Meldungen abgleichen.`};
    }
    case 'org':
      return {prompt:`Aus welchem Land stammt der ${f.name}?`, img:randomImg(f), correct:f.origin,
        wrong:shuffle(DATA.origins.filter(o => o !== f.origin)).slice(0, 3), ex:`${f.designation}. Nutzer: ${f.users}.`};
""" + old_cur)
if 'const uniq' not in s:
    s = s.replace("const imgSrc = ", "const uniq = a => a.filter((x, i) => a.indexOf(x) === i);\nconst imgSrc = ", 1)

# Startseite
h0 = s.index('function renderHome(){')
h1 = s.index('\nfunction hudSvg(){')
s = s[:h0] + r"""function renderHome(){
  setBar('Blau-Trainer');
  $('#bar').hidden = true;
  const nImg = BANK.filter(q => q.kind === 'img').length;
  $('#app').innerHTML = `
  <section class="hero"><a class="hublink" href="../">‹ Alle Trainer</a>
    <h1>Blau-Trainer</h1>
    <p>Gängige Landfahrzeuge der eigenen und verbündeten Kräfte (KR Blau) erkennen und von ähnlichen Fahrzeugen KR Rot unterscheiden – damit du nie auf die eigene Truppe wirkst.</p>
  </section>
  <section class="board" aria-label="Lagebild">
    <div class="board-h"><h2>Lagebild</h2><span class="small muted">${S.answered ? `${S.answered} Antworten, ${Math.round(100 * S.correct / Math.max(1, S.answered))} % richtig` : 'Noch keine Antworten'}</span></div>
    ${GROUPS.map(([t, ids]) => `<h3>${esc(t)}</h3>${cellsHtml(ids)}`).join('')}
    <div class="legend"><em style="--c:var(--ok)">ab 80 %</em><em style="--c:var(--cta)">50–79 %</em><em style="--c:var(--bad)">unter 50 %</em><span>gestrichelt: noch nicht geübt</span></div>
  </section>
  <button class="cta" data-start="mix"><span><strong>Gemischte Runde starten</strong><small>${ROUND_LEN} Fragen aus allen Bereichen – schwache Fahrzeuge kommen öfter</small></span><span class="go" aria-hidden="true">›</span></button>
  <nav class="modes" aria-label="Trainingsarten">
    <button class="mode" data-start="img"><span class="mi"><strong>Fahrzeuge erkennen</strong><small>Welches Fahrzeug ist das? Mit markierten Erkennungsmerkmalen</small></span><span class="n">${nImg} Bilder</span></button>
    <button class="mode" data-start="ff"><span class="mi"><strong>Freund oder Feind</strong><small>KR Blau oder das ähnliche Fahrzeug KR Rot – z. B. Leopard 2 oder T-90</small></span><span class="n">${countPool('ff')} Fragen</span></button>
    <button class="mode" data-start="cat"><span class="mi"><strong>Fahrzeugart erkennen</strong><small>Kampfpanzer, Schützenpanzer, Radpanzer, Artillerie</small></span><span class="n">${countPool('cat')} Fragen</span></button>
    <button class="mode" data-start="org"><span class="mi"><strong>Herkunft</strong><small>Aus welchem Land stammt das Fahrzeug?</small></span><span class="n">${countPool('org')} Fragen</span></button>
    <button class="mode" data-start="var"><span class="mi"><strong>Versionen unterscheiden</strong><small>Leopard 2A4 oder 2A6, HMMWV oder JLTV</small></span><span class="n">${countPool('var')} Bilder</span></button>
    <button class="mode" data-start="conf"><span class="mi"><strong>Verwechslungsgefahr</strong><small>Bilder nur gegen ähnliche Fahrzeuge KR Blau</small></span><span class="n">${countPool('conf')} Bilder</span></button>
    <button class="mode" data-act="merk"><span class="mi"><strong>Merkblatt</strong><small>Freund oder Feind, Laufrollen und Räder zählen, Raketenwerfer</small></span><span class="n"></span></button>
    <button class="mode" data-act="cmpall"><span class="mi"><strong>Blau gegen Rot</strong><small>Jedes Fahrzeug neben seinem Gegenstück KR Rot, mit den Unterschieden</small></span><span class="n">${CMP.length} Paare</span></button>
    <button class="mode" data-go="cards"><span class="mi"><strong>Steckbriefe</strong><small>Alle Fahrzeuge zum Nachlesen, mit Bildern und Versionen</small></span><span class="n">${FAMS.length}</span></button>
    <button class="mode" data-go="stats"><span class="mi"><strong>Statistik und gemeldete Fragen</strong><small>Trefferquote je Fahrzeug, markierte Fragen zum Prüfen</small></span><span class="n">${Object.keys(S.flags).length ? Object.keys(S.flags).length + ' gemeldet' : ''}</span></button>
  </nav>
  <a class="guide-link" href="../manoever/"><span class="mi"><strong>Manöver-Trainer</strong><small>Die Fahrzeuge KR Rot im Detail</small></span><span class="n">Trainer ›</span></a>
  <p class="foot">Alle Angaben stammen aus öffentlichen Quellen und sind gerundet. Die Bilder stammen von Wikimedia Commons und sind gemeinfrei. Der Fahrzeugtyp sagt nichts Sicheres über die Seite: Die Ukraine fährt sowjetische und westliche Fahrzeuge, erbeutete Fahrzeuge wechseln die Seite. Falsche oder unklare Fragen kannst du nach der Antwort melden.</p>`;
}
""" + s[h1:]

# Steckbrief-Bausteine ohne Bedrohung, Laser und Panzerung
u0 = s.index('/* Chips: rot = Gefahr für dich')
u1 = s.index('function renderEnd(){')
s = s[:u0] + r"""const unitChips = u => '';
const sideChip = f => `<ul class="chips"><li data-v="1">KR Blau</li><li data-v="?">${esc(CATS[f.cat].label)}</li><li data-v="?">Herkunft: ${esc(f.origin)}</li></ul>`;
function unitsHtml(f, cur){
  if (!multi(f)) return '';
  const list = cur ? [cur, ...f.vars.filter(u => u !== cur)] : f.vars;
  return list.map(u => `<div class="unitrow${u === cur ? ' cur' : ''}"><strong>${esc(u.name)}${u === cur ? ' <span class="tag">im Bild</span>' : ''}</strong><p class="small" style="margin:4px 0 0">${esc(u.recog)}</p></div>`).join('');
}
function profileHtml(f, cur){
  const title = cur && multi(f) ? cur.name : f.name;
  const r = RED.find(x => x.blue === f.id);
  return `<div class="profile">
    <h3>${esc(title)}<small>${esc(CATS[f.cat].label)} · KR Blau</small></h3>
    ${unitsHtml(f, cur)}
    <dl class="kv"><dt>Nutzer</dt><dd>${esc(f.users)}</dd><dt>Erkennung</dt><dd>${esc(f.recog)}</dd>${r ? `<dt>Ähnlich KR Rot</dt><dd>${esc(r.name)}: ${esc(r.key)}</dd>` : ''}</dl>
    <div class="row" style="margin-top:10px">${cur && multi(f) ? `<button class="linkbtn" data-card="${cur.key}">Steckbrief ${esc(cur.name)}</button>` : ''}<button class="linkbtn" data-card="${f.id}">${multi(f) ? `Familie ${esc(f.name)}` : 'Steckbrief öffnen'}</button></div>
  </div>`;
}
""" + s[u1:]

d0 = s.index('function drawCard(){')
d1 = s.index('function openMerk(){')
s = s[:d0] + r"""function redSec(f){
  const k = RED.findIndex(x => x.blue === f.id); if (k < 0) return '';
  const c = CMP[k];
  return `<div class="sec"><h3>Nicht verwechseln mit KR Rot: ${esc(RED[k].name)}</h3>${cmpHtml(c, f.id)}</div>`;
}
function drawCard(){
  const id = cardState.id;
  const isUnit = !!UNIT[id];
  const f = isUnit ? UNIT[id].f : FAM[id];
  const U = isUnit ? UNIT[id].u : null;
  const list = a => `<ul>${a.map(x => `<li>${esc(x)}</li>`).join('')}</ul>`;
  const sec = (h, body) => `<div class="sec"><h3>${h}</h3>${body}</div>`;
  const p = s => `<p style="margin:0">${esc(s)}</p>`;
  const common = `
    ${sec('Bewaffnung', list(f.weapons))}
    ${sec('Als JTAC beachten', list(f.jtac))}
    ${redSec(f)}`;
  let body;
  if (isUnit){
    const others = f.vars.filter(x => x !== U);
    body = `
    <h1 style="font-size:2.6rem;margin-top:16px">${esc(U.name)}</h1>
    <div class="desig">Version der ${esc(f.name)}-Familie · ${esc(CATS[f.cat].label)} · <button class="linkbtn" data-card="${f.id}">alle ${esc(f.name)}-Versionen im Vergleich</button></div>
    ${sideChip(f)}
    ${sec(`Woran erkennst du den ${esc(U.name)}?`, unitAnno(f, U) + `<p style="margin:10px 0 0"><strong>${esc(U.recog)}</strong></p><p class="small muted" style="margin:6px 0 0">Gilt für alle ${esc(f.name)}: ${esc(f.recog)}</p>`)}
    ${sec('Unterschied zu den anderen Versionen', others.map(x => `<div class="vbox"><h4>${esc(x.name)}</h4><p style="margin:4px 0 0">${esc(x.recog)}</p><button class="linkbtn" data-card="${x.key}" style="margin-top:6px">Steckbrief ${esc(x.name)}</button></div>`).join(''))}
    ${common}
    ${confCompare(f)}`;
  } else {
    body = `
    <h1 style="font-size:2.6rem;margin-top:16px">${esc(f.name)}</h1>
    <div class="desig">${esc(f.designation)}</div>
    ${sideChip(f)}
    ${multi(f) ? `<div class="row" style="margin-top:12px">${f.vars.map(u => `<button class="btn" data-card="${u.key}">Steckbrief ${esc(u.name)}</button>`).join('')}</div>` : ''}
    ${sec('Nutzer', p(f.users))}
    ${ANNO[f.id] ? sec('Erkennungsmerkmale', annoHtml(f) + `<p style="margin:10px 0 0">${esc(f.recog)}</p>`) : sec('Erkennung', p(f.recog))}
    ${multi(f) ? sec('Versionen unterscheiden', f.vars.map(u => `<div class="vbox"><h4>${esc(u.name)}</h4><div style="margin-top:8px">${unitAnno(f, u)}</div><p style="margin:8px 0 0"><strong>${esc(u.recog)}</strong></p><button class="btn" data-card="${u.key}" style="margin-top:8px">Steckbrief ${esc(u.name)}</button></div>`).join('')) : ''}
    ${common}
    ${confCompare(f)}`;
  }
  const title = isUnit ? U.name : f.name;
  $('#sheet').innerHTML = `<div class="bar" style="position:sticky"><div class="bar-in"><button class="iconbtn" data-act="closecard" aria-label="Schließen">‹ Zurück</button><div class="t">${esc(title)}</div><span class="muted small">${pct(id)}</span></div>
  <div class="wrap">
    ${carouselHtml(f)}
    ${body}
  </div>`;
}
""" + s[d1:]

# Direktvergleiche: Rot-Seite hat keinen Steckbrief
s = s.replace("${CMP.map(c => `<div class=\"sec\"><h3>${esc(FAM[c.a.fam].name)} oder ${esc(FAM[c.b.fam].name)}?</h3>${cmpHtml(c, c.a.fam)}</div>`).join('')}",
              "${CMP.map((c, k) => `<div class=\"sec\"><h3>${esc(FAM[c.a.fam].name)} oder ${esc(RED[k].name)}?</h3>${cmpHtml(c, c.a.fam)}</div>`).join('')}")
s = s.replace("<div class=\"t\">Direktvergleiche</div>", "<div class=\"t\">Blau gegen Rot</div>")
s = s.replace("<h1 style=\"font-size:2.6rem;margin-top:16px\">Direktvergleiche</h1>", "<h1 style=\"font-size:2.6rem;margin-top:16px\">Blau gegen Rot</h1>")
s = s.replace("Fahrzeuge mit hoher Verwechslungsgefahr nebeneinander, mit den Merkmalen, die sie unterscheiden.",
              "Jedes Fahrzeug KR Blau neben einem ähnlichen Fahrzeug KR Rot, mit den Merkmalen, die sie unterscheiden.")
# confCompare nur mit Blau-Fahrzeugen (Rot steht in redSec)
s = s.replace("const others = [...new Set([...f.confuse, ...cmpFor(f.id).map(c => c.a.fam === f.id ? c.b.fam : c.a.fam)])].filter(c => FAM[c]);",
              "const others = [...new Set(f.confuse)].filter(c => FAM[c]);")
s = s.replace("<h3>Verwechslungsgefahr – Gegenüberstellung</h3>", "<h3>Verwechslungsgefahr innerhalb KR Blau</h3>")
s = s.replace("  rows.push({id:'air', name:'Aus der Luft', card:false, a:famAcc('air'), s:S.fam.air || {c:0, w:0}});\n", "")
for needle in ('DATA.lwr', 'DATA.tis', 'DATA.wcls', 'HELI[', 'TISC['):
    for m in re.finditer(re.escape(needle), s):
        line = s[s.rfind('\n', 0, m.start()) + 1:s.find('\n', m.start())]
        if not line.lstrip().startswith(('case', 'correct', 'const lwrLong', 'const tisLong', 'return {unit', 'ex:')):
            print('Hinweis: verbleibende Stelle:', line.strip()[:100])
os.makedirs(os.path.join(repo, 'blau', 'img'), exist_ok=True)
open(os.path.join(repo, 'blau', 'index.html'), 'w', encoding='utf-8').write(s)
print('blau/index.html geschrieben:', len(B.F), 'Fahrzeuge,', sum(len(v) for v in IMG.values()), 'Bilder,', len(RED), 'Rot-Paare')
