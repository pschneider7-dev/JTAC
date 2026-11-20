"""Kolonnen aus der Drohne (Draufsicht) und Seitenansichten fürs Fernglas.
Aufruf: compose.py <sprite-dir> <out-dir>"""
import json, math, random, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
SP, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
META = {m['key']: m for m in json.load(open(os.path.join(SP, 'sprites.json')))}
# key -> (Familie, Version, Name in der Meldung, Kategorie)
VEH = {'t72-A': ('t72', 'ab', 'T-72', 'kpz'), 't72-B': ('t72', 'ab', 'T-72', 'kpz'), 't72-B3': ('t72', 'b3', 'T-72', 'kpz'), 't72-B3M': ('t72', 'b3m', 'T-72', 'kpz'),
       't90m-x': ('t90', 'm', 'T-90M', 'kpz'), 'btr-80': ('btr', '80', 'BTR-80', 'rad'), 'btr-82A': ('btr', '82', 'BTR-82A', 'rad'), 'btr-82AT': ('btr', '82', 'BTR-82A', 'rad'),
       'bmp-1': ('bmp1', 'std', 'BMP-1', 'spz'), 'bmp-1AM': ('bmp1', 'am', 'BMP-1AM', 'spz'), 'bmp-2': ('bmp2', 'std', 'BMP-2', 'spz'), 'bmp-2M': ('bmp2', 'm', 'BMP-2M', 'spz'),
       'bmp3-3': ('bmp3', None, 'BMP-3', 'spz'), 'brdm-BRDM': ('brdm2', None, 'BRDM-2', 'spae'), 'brdm-SA9': (None, None, 'SA-9 Strela-1', 'fla')}
TEMPL = [  # (Name, Hauptfahrzeuge, Zusatz)
    ('Panzer', ['t72-B3', 't72-B3M', 't72-B3', 't72-B'], ['bmp-2', 'brdm-SA9']),
    ('Panzer T-90M', ['t90m-x', 't90m-x', 't90m-x'], ['bmp3-3', 'brdm-SA9', 'btr-82A']),
    ('Mot-Schützen BTR', ['btr-82A', 'btr-82A', 'btr-82AT', 'btr-80'], ['brdm-BRDM', 't72-B3', 'brdm-SA9']),
    ('Mot-Schützen BMP-2', ['bmp-2', 'bmp-2', 'bmp-2M', 'bmp-2'], ['t72-B3', 'brdm-SA9', 'brdm-BRDM']),
    ('Mot-Schützen BMP-3', ['bmp3-3', 'bmp3-3', 'bmp3-3'], ['t90m-x', 'brdm-SA9']),
    ('Aufklärung', ['brdm-BRDM', 'brdm-BRDM', 'bmp-1'], ['btr-80', 'bmp-1AM']),
]
PXM_TOP = 720 / (2 * 22 * math.tan(math.radians(15)))  # Pixel je Meter in der Draufsicht-Aufnahme

def sprite_top(key, ir):
    im = Image.open(os.path.join(SP, f'{key}-{"topir" if ir else "top"}.png')).convert('RGBA'); m = META[key]['top']
    cx, cy = m['center']; bx, by = m['bow']; ang = math.degrees(math.atan2(bx - cx, -(by - cy)))  # Bug-Richtung, 0 = oben
    im = im.rotate(ang, resample=Image.BICUBIC, center=(cx, cy), translate=(480 - cx, 360 - cy))  # Bug zeigt nach oben, Mitte im Bild
    a = np.asarray(im)[..., 3]; ys, xs = np.nonzero(a > 8)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)), (480 - xs.min(), 360 - ys.min())

def ground(seed, ir, W=960, H=720):
    r = random.Random(seed); rng = np.random.default_rng(seed)
    base = np.array([34, 34, 34.]) if ir else np.array(r.choice([[86, 98, 60], [104, 96, 70], [74, 88, 52]]), float)
    n = rng.normal(0, 1, (H // 12, W // 12)); n = np.array(Image.fromarray(((n - n.min()) / (np.ptp(n)) * 255).astype('uint8')).resize((W, H), Image.BICUBIC)) / 255.
    a = base * (0.8 + 0.4 * n)[..., None] + rng.normal(0, 4 if ir else 6, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))

def bez(p0, p1, p2, t): return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

DIRS = ['Norden', 'Nordosten', 'Osten', 'Südosten', 'Süden', 'Südwesten', 'Westen', 'Nordwesten']
def compass(dx, dy):  # Bildkoordinaten: Norden = oben
    a = (math.degrees(math.atan2(dx, -dy)) + 360) % 360; return DIRS[int((a + 22.5) // 45) % 8]

def column(k, seed, ir):
    r = random.Random(seed); W, H = 960, 720; pxm = r.uniform(15, 17.5)
    name, main, extra = r.choice(TEMPL); n = r.randint(3, 4)
    keys = [r.choice(main) for _ in range(n)]
    for e in extra:
        if r.random() < 0.4 and len(keys) < 6: keys.insert(r.randint(0, len(keys)), e)
    img = ground(seed, ir); d = ImageDraw.Draw(img, 'RGBA')
    # Straße als Bezierkurve quer durchs Bild
    side = r.choice(['lr', 'diag', 'diag']); m = 60
    if side == 'lr': p0, p2 = (-m, r.uniform(150, 570)), (W + m, r.uniform(150, 570))
    elif side == 'tb': p0, p2 = (r.uniform(200, 760), -m), (r.uniform(200, 760), H + m)
    else: p0, p2 = (-m, r.uniform(500, 760)), (W + m, r.uniform(-40, 220))
    p1 = (W / 2 + r.uniform(-200, 200), H / 2 + r.uniform(-160, 160))
    pts = [bez(p0, p1, p2, t / 200) for t in range(201)]
    rw = r.uniform(5.5, 7.5) * pxm; col = (48, 48, 48, 255) if ir else r.choice([(118, 106, 82, 255), (96, 94, 90, 255)])
    def edge(off):
        e = []
        for i in range(len(pts)):
            a0, a1 = pts[max(0, i - 3)], pts[min(len(pts) - 1, i + 3)]; L = math.hypot(a1[0] - a0[0], a1[1] - a0[1]) or 1
            e.append((pts[i][0] - (a1[1] - a0[1]) / L * off, pts[i][1] + (a1[0] - a0[0]) / L * off))
        return e
    d.polygon(edge(rw / 2 + 0.4 * pxm) + edge(-rw / 2 - 0.4 * pxm)[::-1], fill=(col[0] - 12, col[1] - 12, col[2] - 12, 255))
    d.polygon(edge(rw / 2) + edge(-rw / 2)[::-1], fill=col)
    for off in (-0.24, 0.24):  # Fahrspuren: Versatz mit geglätteten Normalen
        sp = []
        for i in range(len(pts)):
            a0, a1 = pts[max(0, i - 3)], pts[min(len(pts) - 1, i + 3)]; L = math.hypot(a1[0] - a0[0], a1[1] - a0[1]) or 1
            nx, ny = -(a1[1] - a0[1]) / L, (a1[0] - a0[0]) / L; sp.append((pts[i][0] + nx * off * rw, pts[i][1] + ny * off * rw))
        d.line(sp, fill=(col[0] - 14, col[1] - 14, col[2] - 14, 110), width=max(2, int(0.45 * pxm)), joint='curve')
    # Bogenlänge
    acc = [0.0]
    for i in range(1, len(pts)): acc.append(acc[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    def at(s):
        i = max(1, min(len(acc) - 1, next((j for j in range(len(acc)) if acc[j] >= s), len(acc) - 1)))
        f = (s - acc[i - 1]) / max(1e-6, acc[i] - acc[i - 1]); x = pts[i - 1][0] + f * (pts[i][0] - pts[i - 1][0]); y = pts[i - 1][1] + f * (pts[i][1] - pts[i - 1][1])
        return x, y, pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
    gaps = [r.uniform(9, 12) * pxm for _ in keys]; total = sum(gaps[:-1])
    for _ in range(120):  # Startpunkt so wählen, dass alle Fahrzeuge im Bild liegen
        s0 = r.uniform(0, max(1, acc[-1] - total)); ss = [s0 + sum(gaps[:i]) for i in range(len(keys))]
        P = [at(s) for s in ss]
        if all(80 < x < W - 80 and 80 < y < H - 80 for x, y, _, _ in P): break
    else: return None
    fwd = r.random() < 0.5  # Fahrtrichtung entlang oder gegen die Kurve
    order = keys if fwd else list(reversed(keys))
    vehicles = []
    for key, (x, y, tx, ty) in zip(order, P):
        hx, hy = (tx, ty) if fwd else (-tx, -ty); ang = math.degrees(math.atan2(hx, -hy))
        sp, (ox, oy) = sprite_top(key, ir); f = pxm / PXM_TOP
        sp = sp.resize((max(1, int(sp.width * f)), max(1, int(sp.height * f))), Image.LANCZOS); ox *= f; oy *= f
        rot = sp.rotate(-ang, resample=Image.BICUBIC, expand=True)
        # Mittelpunkt nach Drehung
        cxs, cys = sp.width / 2, sp.height / 2; dx0, dy0 = ox - cxs, oy - cys; a = math.radians(ang)
        rx, ry = dx0 * math.cos(a) - dy0 * math.sin(a), dx0 * math.sin(a) + dy0 * math.cos(a)
        lat = r.uniform(-0.4, 0.4) * pxm; L = math.hypot(tx, ty) or 1; nx, ny = -ty / L, tx / L
        px, py = x + nx * lat, y + ny * lat
        img.paste(rot, (int(px - rot.width / 2 - rx), int(py - rot.height / 2 - ry)), rot)
        vehicles.append({'key': key, 'x': round(px / W * 100, 1), 'y': round(py / H * 100, 1)})
    dirn = compass(*(lambda t: (t[2], t[3]) if fwd else (-t[2], -t[3]))(at(sum(ss) / len(ss))))
    # Sensor-Look
    if ir:
        g = ImageOps.autocontrast(img.convert('L'), cutoff=1).filter(ImageFilter.GaussianBlur(0.9)); a = np.asarray(g).astype(float) + np.random.default_rng(seed).normal(0, 7, (H, W))
        img = Image.fromarray(np.clip(a, 0, 255).astype('uint8')).convert('RGB')
    else:
        img = ImageEnhance.Color(img).enhance(0.85).filter(ImageFilter.GaussianBlur(0.6)); a = np.asarray(img).astype(float) + np.random.default_rng(seed).normal(0, 5, (H, W, 1))
        img = Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
    img = img.resize((720, 540), Image.LANCZOS); fn = f'kol-{k}.webp'; img.save(os.path.join(OUT, fn), 'WEBP', quality=76, method=6)
    vs = [dict(v, fam=VEH[v['key']][0], v=VEH[v['key']][1], name=VEH[v['key']][2], cat=VEH[v['key']][3]) for v in vehicles]
    return {'src': 'img/' + fn, 'ir': ir, 'dir': dirn, 'veh': vs, 'm': round(pxm, 1)}

kol = []; seed = 100
while len(kol) < 24:
    seed += 1; c = column(len(kol), seed, len(kol) % 3 == 2)
    if c: kol.append(c)
json.dump(kol, open(os.path.join(OUT, 'kol.json'), 'w'), ensure_ascii=False)

# Seitenansichten fürs Fernglas: Sprite (mit Turm) eng zuschneiden, Wannenbereich (ohne Turm/Rohr) als Anteil
side = {}
for key in ['t72-B3', 't72-A', 't90m-x', 'btr-82A', 'btr-80', 'bmp-2', 'bmp-1', 'bmp3-3', 'brdm-BRDM']:
    full = Image.open(os.path.join(SP, f'{key}-side.png')).convert('RGBA'); hull = Image.open(os.path.join(SP, f'{key}-sidehull.png')).convert('RGBA')
    af = np.asarray(full)[..., 3] > 8; ah = np.asarray(hull)[..., 3] > 8
    ys, xs = np.nonzero(af); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    hys, hxs = np.nonzero(ah); hx0, hx1 = hxs.min(), hxs.max() + 1
    bow = META[key]['side']['bow'][0]; bowRight = bow > (hx0 + hx1) / 2
    sp = full.crop((x0, y0, x1, y1)); sc = 480 / sp.width; sp = sp.resize((480, max(1, round(sp.height * sc))), Image.LANCZOS)
    fn = f'side-{key}.webp'; sp.save(os.path.join(OUT, fn), 'WEBP', quality=82, method=6)
    side[key] = {'src': 'img/' + fn, 'ar': round(sp.width / sp.height, 4), 'h0': round((hx0 - x0) / (x1 - x0), 4), 'h1': round((hx1 - x0) / (x1 - x0), 4), 'bowRight': bool(bowRight)}
json.dump(side, open(os.path.join(OUT, 'side.json'), 'w'), ensure_ascii=False, indent=0)
# Hintergründe fürs Fernglas (Horizont, Baumreihe, Feld)
for k in range(3):
    r = random.Random(500 + k); W, H = 960, 720; im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    hz = int(H * r.uniform(0.40, 0.50))
    for y in range(hz): t = y / hz; d.line([(0, y), (W, y)], fill=(int(150 + 60 * t), int(175 + 45 * t), int(205 + 30 * t)))
    for y in range(hz, H): t = (y - hz) / (H - hz); c = [(96, 108, 66), (120, 112, 80), (88, 100, 64)][k]; d.line([(0, y), (W, y)], fill=tuple(int(v * (0.85 + 0.25 * t)) for v in c))
    x = 0
    while x < W:  # Baumreihe
        w = r.uniform(18, 46); h = r.uniform(14, 40); d.ellipse([x, hz - h, x + w, hz + 6], fill=(54 + r.randint(-8, 8), 66 + r.randint(-8, 8), 40)); x += w * 0.6
    a = np.asarray(im).astype(float) + np.random.default_rng(k).normal(0, 4, (H, W, 1)); im = Image.fromarray(np.clip(a, 0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))
    im.save(os.path.join(OUT, f'land-{k}.webp'), 'WEBP', quality=72, method=6)
print('Kolonnen', len(kol), '| Seitenansichten', len(side))
