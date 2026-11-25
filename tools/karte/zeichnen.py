"""Übungskarte 1:50 000 zeichnen (A4 hoch, Originalmaßstab beim Druck in 100 %)."""
import sys
import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.patches import Polygon, Rectangle, Circle
import matplotlib.patheffects as pe
from matplotlib.colors import LightSource
from scipy import ndimage
from scipy.interpolate import RegularGridInterpolator
from pyproj import Transformer

OUT = sys.argv[1] if len(sys.argv) > 1 else 'uebungskarte'
plt.rcParams['font.family'] = 'Liberation Sans'
plt.rcParams['pdf.fonttype'] = 42
d = np.load('fein.npz')
h = d['h'].astype(float); xs, ys = d['xs'], d['ys']; river = d['river']
M = pickle.load(open('merkmale.pkl', 'rb'))
X, Y = np.meshgrid(xs, ys)
Hf = RegularGridInterpolator((ys, xs), h)

# ---------------- Geodäsie ----------------
T = Transformer.from_crs('EPSG:4326', 'EPSG:32632', always_xy=True)
TI = Transformer.from_crs('EPSG:32632', 'EPSG:4326', always_xy=True)
LON0, LON1, LAT0, LAT1 = 7 + 7.5 / 60, 7 + 15 / 60, 49 + 39.5 / 60, 49 + 45.5 / 60
E_SW, N_SW = T.transform(LON0, LAT0)
lc, pc = (LON0 + LON1) / 2, (LAT0 + LAT1) / 2
e1, n1 = T.transform(lc, pc); e2, n2 = T.transform(lc, pc + 0.01)
TH = np.arctan2(e2 - e1, n2 - n1)                     # Winkel GN -> TN (rad), + = TN östlich von GN
CT, ST = np.cos(TH), np.sin(TH)
def utm2pl(E, N):
    dx, dy = (np.asarray(E) - E_SW) / 1000, (np.asarray(N) - N_SW) / 1000
    return dx * CT - dy * ST, dx * ST + dy * CT
def pl2utm(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return E_SW + 1000 * (x * CT + y * ST), N_SW + 1000 * (-x * ST + y * CT)
def geo2pl(lon, lat): return utm2pl(*T.transform(lon, lat))
corners = {k: np.array(geo2pl(*v)) for k, v in dict(SW=(LON0, LAT0), SE=(LON1, LAT0), NE=(LON1, LAT1), NW=(LON0, LAT1)).items()}
FW, FH = corners['SE'][0], corners['NW'][1]

# ---------------- Seite ----------------
MM = 1 / 25.4
PW, PH = 210, 297
KM = 20.0                                              # mm je km bei 1:50 000
L0 = (PW - FW * KM) / 2
B0 = 57.0
fig = plt.figure(figsize=(PW * MM, PH * MM))
pg = fig.add_axes([0, 0, 1, 1]); pg.set_xlim(0, PW); pg.set_ylim(0, PH); pg.axis('off')
ax = fig.add_axes([L0 / PW, B0 / PH, FW * KM / PW, FH * KM / PH])
ax.set_xlim(0, FW); ax.set_ylim(0, FH); ax.axis('off')
def mm(x, y): return L0 + np.asarray(x) * KM, B0 + np.asarray(y) * KM
halo = lambda w=1.4: [pe.withStroke(linewidth=w, foreground='white')]
ext = (xs[0], xs[-1], ys[0], ys[-1])

C = dict(paper='#fffffb', wald='#d4e9bf', waldrand='#a6c98f', ort='#f6dccf', geb='#7a463a', hl='#bd8a58', hl_z='#a36c3a',
         wasser='#2a7bc1', wasser_f='#a9d4f2', gitter='#1d57ab', B='#e55233', L='#ffd23a', K='#fff7c2', weg='#3a3a3a')

ax.add_patch(Rectangle((0, 0), FW, FH, facecolor=C['paper'], edgecolor='none', zorder=0))
def fill(mask, color, z, edge=None, lw=0.25, sm=0.8):
    f = ndimage.gaussian_filter(mask.astype(float), sm)
    ax.contourf(X, Y, f, levels=[0.5, 2], colors=[color], zorder=z, antialiased=True)
    if edge: ax.contour(X, Y, f, levels=[0.5], colors=[edge], linewidths=lw, zorder=z + 0.01)
fill(M['forest'], C['wald'], 1, C['waldrand'], 0.3)
fill(M['vine'], '#eef3d6', 1)
fill(M['ort'], C['ort'], 1.2)
# Obstwiesen und Weinberg als Signaturen
rng = np.random.default_rng(5)
def pattern(mask, step, jitter=0.0):
    gx, gy = np.meshgrid(np.arange(0, FW, step), np.arange(0, FH, step))
    gx = gx + (np.arange(gx.shape[0])[:, None] % 2) * step / 2
    p = np.column_stack([gx.ravel(), gy.ravel()]) + rng.uniform(-jitter, jitter, (gx.size, 2))
    ii = np.clip(np.round((p[:, 1] - ys[0]) / 0.02).astype(int), 0, len(ys) - 1)
    jj = np.clip(np.round((p[:, 0] - xs[0]) / 0.02).astype(int), 0, len(xs) - 1)
    return p[mask[ii, jj]]
op = pattern(M['orchard'], 0.055, 0.004)
ax.scatter(op[:, 0], op[:, 1], s=0.9, facecolors='none', edgecolors='#5f9a45', linewidths=0.3, zorder=1.3)
vp = pattern(M['vine'], 0.045)
ax.add_collection(LineCollection([[(p[0], p[1] - 0.01), (p[0], p[1] + 0.01)] for p in vp], colors='#6f8a2e', linewidths=0.35, zorder=1.3))
ax.add_collection(LineCollection([[(p[0] - 0.008, p[1] + 0.006), (p[0], p[1] + 0.012), (p[0] + 0.008, p[1] + 0.006)] for p in vp], colors='#6f8a2e', linewidths=0.3, zorder=1.3))

# Schummerung (nur Schatten, Ebenen bleiben hell)
ls = LightSource(azdeg=315, altdeg=42)
hs = 0.6 * ls.hillshade(h, vert_exag=2.2, dx=20, dy=20) + 0.4 * LightSource(azdeg=350, altdeg=50).hillshade(h, vert_exag=2.2, dx=20, dy=20)
flat = 0.6 * np.sin(np.radians(42)) + 0.4 * np.sin(np.radians(50))
a = np.clip((flat - hs) * 0.75, 0, 0.30)
rgba = np.zeros(h.shape + (4,)); rgba[..., :3] = [0.32, 0.30, 0.36]; rgba[..., 3] = a
ax.imshow(rgba, extent=ext, origin='lower', zorder=1.5, interpolation='bilinear')

# Höhenlinien
hs_ = ndimage.gaussian_filter(h, 0.6)
lv = np.arange(240, 700, 20)
ax.contour(X, Y, hs_, levels=[v for v in lv if v % 100], colors=C['hl'], linewidths=0.26, zorder=2)
cz = ax.contour(X, Y, hs_, levels=[v for v in lv if v % 100 == 0], colors=C['hl_z'], linewidths=0.55, zorder=2)
for t in ax.clabel(cz, fmt='%d', fontsize=4.3, colors='#8b5a2b', inline=True, inline_spacing=1.5):
    t.set_zorder(2.1)

# Gewässer
for p, a_ in M['streams']:
    w = np.interp(a_, [0.15, 1, 5, 30], [0.32, 0.5, 0.75, 1.05])
    segs = np.stack([p[:-1], p[1:]], axis=1)
    ax.add_collection(LineCollection(segs, linewidths=w[:-1], colors=C['wasser'], capstyle='round', zorder=3))
ax.plot(river[:, 0], river[:, 1], color=C['wasser'], lw=2.3, solid_capstyle='round', zorder=3.1)
ax.plot(river[:, 0], river[:, 1], color=C['wasser_f'], lw=1.5, solid_capstyle='round', zorder=3.2)

# Wege
for kind, p in M['tracks']:
    if kind == 'fuss':
        ax.plot(p[:, 0], p[:, 1], color=C['weg'], lw=0.35, ls=(0, (3, 2)), zorder=4)
    else:
        ax.plot(p[:, 0], p[:, 1], color=C['weg'], lw=0.38, zorder=4, solid_capstyle='round')
# Bahn
rail, tun = M['rail'], M['tunnel']
lab, n = ndimage.label(~tun)
for k in range(1, n + 1):
    s = rail[lab == k]
    ax.plot(s[:, 0], s[:, 1], color='#111', lw=1.25, zorder=5, solid_capstyle='butt')
    ax.plot(s[:, 0], s[:, 1], color='white', lw=0.55, ls=(0, (4, 4)), zorder=5.1)
lab, n = ndimage.label(tun)
for k in range(1, n + 1):
    s = rail[lab == k]
    ax.plot(s[:, 0], s[:, 1], color='#111', lw=0.6, ls=(0, (2.2, 1.4)), zorder=5)
    for e, f in ((s[0], s[min(3, len(s) - 1)]), (s[-1], s[max(-4, -len(s))])):
        t = f - e; t /= np.hypot(*t) + 1e-9; nn = np.array([-t[1], t[0]]) * 0.035
        ax.plot([e[0] - nn[0], e[0] + nn[0]], [e[1] - nn[1], e[1] + nn[1]], color='#111', lw=0.8, zorder=5)
# Straßen: erst alle Ränder, dann Füllungen
STY = dict(B=(2.5, 1.75, C['B']), L=(2.05, 1.35, C['L']), K=(1.75, 1.05, C['K']), G=(1.35, 0.72, 'white'))
for cls in ('G', 'K', 'L', 'B'):
    for r in M['roads']:
        if r['cls'] == cls: ax.plot(r['p'][:, 0], r['p'][:, 1], color='#2b2b2b', lw=STY[cls][0], solid_capstyle='round', solid_joinstyle='round', zorder=6)
    for ln in (M['lanes'] if cls == 'G' else []):
        ax.plot(ln[:, 0], ln[:, 1], color='#2b2b2b', lw=1.15, solid_capstyle='round', zorder=6)
for cls in ('G', 'K', 'L', 'B'):
    for ln in (M['lanes'] if cls == 'G' else []):
        ax.plot(ln[:, 0], ln[:, 1], color='white', lw=0.6, solid_capstyle='round', zorder=6.5)
    for r in M['roads']:
        if r['cls'] == cls: ax.plot(r['p'][:, 0], r['p'][:, 1], color=STY[cls][2], lw=STY[cls][1], solid_capstyle='round', solid_joinstyle='round', zorder=6.5 + 'GKLB'.index(cls) * 0.1)
# Gebäude
ax.add_collection(PolyCollection([b for _, b in M['buildings']], facecolors=C['geb'], edgecolors='none', zorder=7))
# Sonderobjekte
SP = M['specials']
for p in SP.get('kirche', []):
    ax.add_patch(Circle(p, 0.022, facecolor='white', edgecolor='#111', lw=0.45, zorder=8))
    ax.plot([p[0], p[0]], [p[1] - 0.014, p[1] + 0.014], color='#111', lw=0.45, zorder=8.1)
    ax.plot([p[0] - 0.01, p[0] + 0.01], [p[1] + 0.004, p[1] + 0.004], color='#111', lw=0.45, zorder=8.1)
for p, a_ in SP.get('friedhof', []):
    r = np.array([[-0.03, -0.022], [0.03, -0.022], [0.03, 0.022], [-0.03, 0.022]])
    cs, sn = np.cos(a_), np.sin(a_); r = r @ np.array([[cs, sn], [-sn, cs]]) + p
    ax.add_patch(Polygon(r, facecolor='#e9f1df', edgecolor='#333', lw=0.3, zorder=7.5))
    for q in (p + [-0.012, 0], p + [0.012, 0]):
        ax.plot([q[0], q[0]], [q[1] - 0.008, q[1] + 0.008], color='#333', lw=0.3, zorder=7.6)
        ax.plot([q[0] - 0.005, q[0] + 0.005], [q[1] + 0.003, q[1] + 0.003], color='#333', lw=0.3, zorder=7.6)
for p in SP.get('sportplatz', []):
    ax.add_patch(Rectangle(p - [0.05, 0.032], 0.1, 0.064, facecolor='#e3efd2', edgecolor='#333', lw=0.35, zorder=7.5))
    ax.plot([p[0], p[0]], [p[1] - 0.032, p[1] + 0.032], color='#333', lw=0.25, zorder=7.6)
for p in M['wka']:
    ax.add_patch(Circle(p, 0.012, facecolor='white', edgecolor='#111', lw=0.4, zorder=8))
    for k in range(3):
        a_ = np.radians(90 + 120 * k)
        ax.plot([p[0], p[0] + 0.05 * np.cos(a_)], [p[1], p[1] + 0.05 * np.sin(a_)], color='#111', lw=0.45, zorder=8.1)
tw = M['tower']
ax.add_patch(Circle(tw, 0.028, facecolor='white', edgecolor='#111', lw=0.5, zorder=8))
ax.add_patch(Circle(tw, 0.009, facecolor='#111', edgecolor='none', zorder=8.1))
for k in range(4):
    a_ = np.radians(45 + 90 * k)
    ax.plot([tw[0] + 0.03 * np.cos(a_), tw[0] + 0.055 * np.cos(a_)], [tw[1] + 0.03 * np.sin(a_), tw[1] + 0.055 * np.sin(a_)], color='#111', lw=0.45, zorder=8.1)
for p, t in SP.get('bahnhof', []):
    t = t / np.hypot(*t); n_ = np.array([-t[1], t[0]])
    q = p + n_ * 0.03
    ax.add_patch(Polygon([q - t * 0.045 - n_ * 0.009, q + t * 0.045 - n_ * 0.009, q + t * 0.045 + n_ * 0.009, q - t * 0.045 + n_ * 0.009], facecolor='#111', zorder=8))
    ax.text(*(q + n_ * 0.07), 'Bf', fontsize=5.2, fontweight='bold', ha='center', va='center', zorder=10, path_effects=halo(1.2))
ms = M['masts']
ax.plot(ms[:, 0], ms[:, 1], color='#222', lw=0.4, zorder=8)
ax.plot(ms[:, 0], ms[:, 1], 'o', ms=1.6, mfc='white', mec='#222', mew=0.4, zorder=8.1)

# Höhenpunkte
lab_anchor = [M['V'][k] for k in M['V']]
peaks_ok = [p for p in M['peaks'] if min(np.hypot(p[0] - q[0], p[1] - q[1]) for q in lab_anchor) > 0.45]
for x, y, z in peaks_ok:
    ax.plot(x, y, 'o', ms=1.3, color='#111', zorder=9)
    ax.text(x + 0.04, y - 0.02, f'{z:.0f}', fontsize=4.8, va='top', zorder=9, path_effects=halo(1.2))
tz = Hf((tw[1], tw[0]))
ax.text(tw[0] + 0.07, tw[1] - 0.05, f'{tz:.0f}', fontsize=5.2, fontweight='bold', va='top', zorder=9, path_effects=halo(1.2))

# ---------------- Schrift ----------------
V = M['V']
NAMES = {'Ilsenau': (9.5, 'bold', (-0.75, 0.42)), 'Niederilsen': (6.8, 'bold', (0.05, 0.3)), 'Hohenscheid': (7.0, 'bold', (0.12, 0.12)),
         'Lindenweiler': (6.8, 'bold', (0.12, 0.12)), 'Elmenhausen': (6.8, 'bold', (-0.55, 0.3)), 'Wolfsrath': (6.8, 'bold', (0.12, 0.12)),
         'Gräfenrath': (6.8, 'bold', (0.12, 0.14)), 'Buchholz': (5.8, 'normal', (-0.5, 0.1)), 'Heidehof': (5.4, 'normal', (0.08, 0.06))}
for nm, (fs, fw_, off) in NAMES.items():
    c = V[nm]
    ax.text(c[0] + off[0], c[1] + off[1], nm, fontsize=fs, fontweight=fw_, zorder=10, path_effects=halo(1.8))
def italic(x, y, s, fs=5.6, col='#1d5fa0', rot=0, sp=False, **kw):
    ax.text(x, y, (' '.join(s) if sp else s), fontsize=fs, style='italic', color=col, rotation=rot, zorder=10,
            ha='center', va='center', rotation_mode='anchor', path_effects=halo(1.4), **kw)
italic(tw[0] + 0.05, tw[1] + 0.13, 'Hohe Warte', 6.2, '#3b2a14')
ax.text(tw[0] + 0.07, tw[1] + 0.02, 'Fernmeldeturm', fontsize=4.4, zorder=10, path_effects=halo(1.2))


# ---------------- Gewässernamen, Berg- und Flurnamen ----------------
def resample_(p, step):
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    u = np.arange(0, s[-1], step)
    return np.column_stack([np.interp(u, s, p[:, 0]), np.interp(u, s, p[:, 1])])

def upright(deg):
    deg = (deg + 180) % 360 - 180
    return deg + 180 if deg > 90 else deg - 180 if deg < -90 else deg
Bp = next(r['p'] for r in M['roads'] if r['cls'] == 'B')
from scipy.spatial import cKDTree as _KD
btree = _KD(Bp)
obst = np.vstack([resample_(r['p'], 0.01) for r in M['roads']] + [rail] + [resample_(l, 0.01) for l in M['lanes']] + [np.array(b) for _, b in M['buildings']])
otree = _KD(obst)
cands = []
for k in range(10, len(river) - 10, 8):
    p = river[k]
    if not (0.4 < p[0] < FW - 0.4 and 0.4 < p[1] < FH - 0.4): continue
    t = river[k + 8] - river[k - 8]; t /= np.hypot(*t); n_ = np.array([-t[1], t[0]])
    for s_ in (-1, 1):
        c = p + s_ * 0.13 * n_
        if min(np.hypot(*(c - v)) for v in M['V'].values()) < 0.6: continue
        probe = np.array([c + t * u + s_ * n_ * w for u in np.linspace(-0.16, 0.16, 9) for w in (-0.04, 0, 0.04)])
        clr = otree.query(probe)[0].min()
        cands.append((clr, c, np.degrees(np.arctan2(t[1], t[0]))))
cands.sort(key=lambda z_: -z_[0])
placed = []
for clr, c, ang in cands:
    if len(placed) >= 3 or clr < 0.04: break
    if any(np.hypot(*(c - q)) < 2.5 for q in placed): continue
    placed.append(c)
    italic(c[0], c[1], 'Ilse', 7.0, '#1d5fa0', upright(ang), sp=True)
STREAMS = {'Elmbach': (7.6, 6.85), 'Steinbach': (6.4, 9.95), 'Kehrbach': (0.85, 10.75), 'Dornbach': (4.75, 5.1), 'Mühlbach': (7.55, 1.25)}
for nm, P in STREAMS.items():
    best = None
    for p, a_ in M['streams']:
        if a_.max() < 1.0: continue
        dd = np.hypot(*(p - P).T); k = int(np.argmin(dd))
        if best is None or dd[k] < best[0]: best = (dd[k], p, k)
    _, p, k = best
    k = int(np.clip(k, 6, len(p) - 7))
    t = p[k + 6] - p[k - 6]; ang = np.degrees(np.arctan2(t[1], t[0]))
    n_ = np.array([-t[1], t[0]]) / (np.hypot(*t) + 1e-9)
    q = p[k] + 0.055 * n_
    italic(q[0], q[1], nm, 5.6, '#1d5fa0', upright(ang))
italic(1.25, 6.55, 'HOCHWALD', 8.0, '#47603a', 70, sp=True)
pk_named = sorted(peaks_ok, key=lambda p: -p[2])[:3]
for (x, y, z_), nm in zip(pk_named, ['Hahnenkopf', 'Eichkopf', 'Kahlenberg']):
    italic(x, y + 0.13, nm, 5.6, '#3b2a14')
for (x, y), nm in {(4.05, 1.95): 'Auf der Heide', (1.75, 2.95): 'Im Bruch', (6.85, 7.5): 'Lange Hecke',
                   (3.55, 4.55): 'Am Galgenberg', (8.35, 7.95): 'Hinterm Busch', (5.6, 3.3): 'Rotes Feld'}.items():
    italic(x, y, nm, 5.0, '#444')

# ---------------- Straßennummern ----------------
for r in M['roads']:
    if not r['name']: continue
    p = r['p']; inside = (p[:, 0] > 0.3) & (p[:, 0] < FW - 0.3) & (p[:, 1] > 0.3) & (p[:, 1] < FH - 0.3)
    idx = np.where(inside)[0]
    if len(idx) < 10: continue
    picks = [0.5] if r['cls'] != 'B' else [0.22, 0.55, 0.85]
    for f in picks:
        k = idx[int(len(idx) * f)]
        if min(np.hypot(*(p[k] - q)) for q in lab_anchor) < 0.45 or min(np.hypot(p[k][0] - q[0], p[k][1] - q[1]) for q in peaks_ok) < 0.3: continue
        fc = '#ffd23a' if r['cls'] == 'B' else 'white'
        ax.text(p[k][0], p[k][1], r['name'], fontsize=4.4, fontweight='bold', ha='center', va='center', zorder=10.5,
                bbox=dict(boxstyle='square,pad=0.18', facecolor=fc, edgecolor='#111', lw=0.35))

# ---------------- Brücken ----------------
rtree_ = _KD(river)
lines = [(r['p'], STY[r['cls']][0]) for r in M['roads']] + [(rail, 1.25)]
rt = river[1:] - river[:-1]
for p, lw_ in lines:
    q = resample_(p, 0.004)
    dd, kk = rtree_.query(q)
    kk = np.clip(kk, 0, len(rt) - 1)
    side = np.sign(rt[kk, 0] * (q[:, 1] - river[kk, 1]) - rt[kk, 1] * (q[:, 0] - river[kk, 0]))
    for k in np.where((side[1:] != side[:-1]) & (dd[1:] < 0.02))[0]:
        if k < 5 or k > len(q) - 6: continue
        t = q[k + 4] - q[k - 4]; t /= np.hypot(*t); n_ = np.array([-t[1], t[0]])
        off = (lw_ / 72 * 25.4 / 2 + 0.25) / KM
        for s_ in (-1, 1):
            a0 = q[k] + s_ * off * n_ - t * 0.045; a1 = q[k] + s_ * off * n_ + t * 0.045
            f0 = a0 - t * 0.012 + s_ * n_ * 0.012; f1 = a1 + t * 0.012 + s_ * n_ * 0.012
            ax.plot([f0[0], a0[0], a1[0], f1[0]], [f0[1], a0[1], a1[1], f1[1]], color='#111', lw=0.5, zorder=6.9, solid_joinstyle='miter')

# ---------------- Gitter ----------------
Emin, Nmin = pl2utm([0, FW, 0, FW], [0, 0, FH, FH])
for E in range(int(min(Emin) // 1000) * 1000, int(max(Emin) // 1000 + 2) * 1000, 1000):
    x, y = utm2pl([E, E], [N_SW - 2000, N_SW + 14000])
    ax.plot(x, y, color=C['gitter'], lw=0.32, zorder=11)
for N in range(int(min(Nmin) // 1000) * 1000, int(max(Nmin) // 1000 + 2) * 1000, 1000):
    x, y = utm2pl([E_SW - 2000, E_SW + 12000], [N, N])
    ax.plot(x, y, color=C['gitter'], lw=0.32, zorder=11)
# Weißer Rand zwischen Achsenrechteck und Blattrahmen (Trapez)
cn = [corners[k] for k in ('SW', 'SE', 'NE', 'NW')]
for poly in ([(-1, -1), (cn[0][0], -1), cn[0], cn[3], (cn[3][0], FH + 1), (-1, FH + 1)],
             [(FW + 1, -1), (cn[1][0], -1), cn[1], cn[2], (cn[2][0], FH + 1), (FW + 1, FH + 1)]):
    ax.add_patch(Polygon(poly, facecolor='white', edgecolor='none', zorder=12, clip_on=True))

# ---------------- Rahmen mit Minuteneinteilung ----------------
cm = np.array([mm(*c) for c in cn])
pg.add_patch(Polygon(cm, closed=True, fill=False, edgecolor='#111', lw=0.5, zorder=20))
BAND = 1.6
pg.add_patch(Polygon(cm + np.array([[-BAND, -BAND], [BAND, -BAND], [BAND, BAND], [-BAND, BAND]]), closed=True, fill=False, edgecolor='#111', lw=0.9, zorder=20))
def breaks(v0, v1):
    m = np.arange(np.ceil(v0 * 60 - 1e-9), v1 * 60 + 1e-9, 1.0)
    return np.unique(np.r_[v0 * 60, m, v1 * 60])
for lat, side in ((LAT0, -1), (LAT1, 1)):
    bk = breaks(LON0, LON1)
    for m0, m1 in zip(bk[:-1], bk[1:]):
        if int(np.floor(m0 + 1e-9)) % 2 == 0:
            a0 = np.array(mm(*geo2pl(m0 / 60, lat))); a1 = np.array(mm(*geo2pl(m1 / 60, lat)))
            pg.add_patch(Polygon([a0, a1, a1 + [0, side * BAND], a0 + [0, side * BAND]], facecolor='#111', edgecolor='none', zorder=20))
    for s10 in np.arange(np.ceil(LON0 * 360), LON1 * 360 + 1e-6, 1):
        a0 = np.array(mm(*geo2pl(s10 / 360, lat)))
        pg.plot([a0[0], a0[0]], [a0[1] + side * BAND, a0[1] + side * (BAND + 0.8)], color='#111', lw=0.25, zorder=21)
for lon, side in ((LON0, -1), (LON1, 1)):
    bk = breaks(LAT0, LAT1)
    for m0, m1 in zip(bk[:-1], bk[1:]):
        if int(np.floor(m0 + 1e-9)) % 2 == 0:
            a0 = np.array(mm(*geo2pl(lon, m0 / 60))); a1 = np.array(mm(*geo2pl(lon, m1 / 60)))
            pg.add_patch(Polygon([a0, a1, a1 + [side * BAND, 0], a0 + [side * BAND, 0]], facecolor='#111', edgecolor='none', zorder=20))
    for s10 in np.arange(np.ceil(LAT0 * 360), LAT1 * 360 + 1e-6, 1):
        a0 = np.array(mm(*geo2pl(lon, s10 / 360)))
        pg.plot([a0[0] + side * BAND, a0[0] + side * (BAND + 0.8)], [a0[1], a0[1]], color='#111', lw=0.25, zorder=21)
def dms(v, lon):
    d_ = int(v); m_ = int(round((v - d_) * 3600)) // 60; s_ = int(round((v - d_) * 3600)) % 60
    return f"{d_}°{m_:02d}'" + (f"{s_:02d}''" if s_ else '')
# Ecken- und Minutenbeschriftung
GEO = dict(fontsize=5.6, color='#111', zorder=21)
for lon in np.arange(np.ceil(LON0 * 60 + 1e-6), LON1 * 60 - 1e-6, 1) / 60:
    for lat, va, dy in ((LAT0, 'top', -8.2), (LAT1, 'bottom', 8.2)):
        x, y = mm(*geo2pl(lon, lat))
        pg.text(x, y + dy, f"{int(round(lon * 60)) % 60}'", ha='center', va='center', **GEO)
for lat in np.arange(np.ceil(LAT0 * 60 + 1e-6), LAT1 * 60 - 1e-6, 1) / 60:
    for lon, dx in ((LON0, -9.6), (LON1, 9.6)):
        x, y = mm(*geo2pl(lon, lat))
        pg.text(x + dx, y, f"{int(round(lat * 60)) % 60}'", ha='center', va='center', rotation=90, **GEO)
for (lon, lat), (dx, dy) in {(LON0, LAT0): (-9.6, -8.2), (LON1, LAT0): (9.6, -8.2), (LON0, LAT1): (-9.6, 8.2), (LON1, LAT1): (9.6, 8.2)}.items():
    x, y = mm(*geo2pl(lon, lat))
    pg.text(x, y + dy, dms(lon, True), ha='center', va='center', fontweight='bold', **{**GEO, 'fontsize': 5.6})
    pg.text(x + dx, y + (5 if dy > 0 else -5) * 0, '', **GEO)
    pg.text(x + dx, y, dms(lat, False), ha='center', va='center', rotation=90, fontweight='bold', **GEO)
# Gitterbeschriftung (blau)
GR = dict(fontsize=6.3, color=C['gitter'], fontweight='bold', zorder=21, ha='center', va='center')
def cross(E=None, N=None):
    """Schnittpunkte einer Gitterlinie mit den Blatträndern (Ebene)."""
    out = {}
    if E is not None:
        for nm, yy in (('S', 0.0), ('N', FH)):
            ts = np.linspace(-1, FW + 1, 2001)
            xx, yv = utm2pl(np.full(2, E), [N_SW - 3000, N_SW + 15000])
            # Gerade x(y) linear
            f = (yy - yv[0]) / (yv[1] - yv[0]); out[nm] = xx[0] + f * (xx[1] - xx[0])
    else:
        for nm, xx in (('W', 0.0), ('E', FW)):
            xv, yv = utm2pl([E_SW - 3000, E_SW + 13000], np.full(2, N))
            f = (xx - xv[0]) / (xv[1] - xv[0]); out[nm] = yv[0] + f * (yv[1] - yv[0])
    return out
first = True
for E in range(int(min(Emin) // 1000 + 1) * 1000, int(max(Emin) // 1000 + 1) * 1000, 1000):
    c_ = cross(E=E)
    for side, yy, dy in (('S', 0, -4.3), ('N', FH, 4.3)):
        xpos = c_[side]
        if 0.05 < xpos < FW - 0.05:
            x, y = mm(xpos, yy)
            lab_ = f'{(E // 1000) % 100:02d}'
            if first and side == 'S':
                pg.text(x, y + dy, r'$^{\mathbf{' + str(E // 100000) + r'}}$' + lab_ + r'$^{\mathbf{000\,m\,E}}$', **{**GR, 'ha': 'left'}, )
                pg.texts[-1].set_position((x - 2.6, y + dy))
            else:
                pg.text(x, y + dy, lab_, **GR)
    first = False
first = True
for N in range(int(min(Nmin) // 1000 + 1) * 1000, int(max(Nmin) // 1000 + 1) * 1000, 1000):
    c_ = cross(N=N)
    for side, xx, dx in (('W', 0, -4.3), ('E', FW, 4.3)):
        ypos = c_[side]
        if 0.05 < ypos < FH - 0.05:
            x, y = mm(xx, ypos)
            lab_ = f'{(N // 1000) % 100:02d}'
            if first and side == 'W':
                pg.text(x + dx + 2.2, y, r'$^{\mathbf{' + str(N // 100000) + r'}}$' + lab_, **{**GR, 'ha': 'right'})
            else:
                pg.text(x + dx, y, lab_, **GR)
    first = False

# ---------------- Kartenrand ----------------
def tx(x, y, s, **kw): pg.text(x, y, s, **{'fontsize': 5.8, 'va': 'center', **kw})
top = B0 + FH * KM
tx(L0, 292.2, 'ÜBUNGSKARTE 1 : 50 000', fontsize=11.5, fontweight='bold')
tx(105, 292.2, 'Ilsetal', fontsize=13, fontweight='bold', ha='center')
tx(L0 + FW * KM, 292.2, '32U LA', fontsize=11.5, fontweight='bold', ha='right', color=C['gitter'])
# Maßstabsleiste
y0 = 39
tx(L0, 45.5, 'Maßstab 1 : 50 000', fontsize=7.5, fontweight='bold')
SB = L0 + 3
for j in range(10):
    pg.add_patch(Rectangle((SB + j * 2, y0), 2, 1.4, facecolor='#111' if j % 2 == 0 else 'white', edgecolor='#111', lw=0.3))
for k in range(2):
    pg.add_patch(Rectangle((SB + 20 + k * 20, y0), 20, 1.4, facecolor='#111' if k % 2 else 'white', edgecolor='#111', lw=0.3))
for lab_, xx in (('1', SB), ('0', SB + 20), ('1', SB + 40), ('2 km', SB + 60)):
    tx(xx, y0 + 3.0, lab_, fontsize=5.6, ha='center')
kir = min(M['specials']['kirche'], key=lambda p: np.hypot(*(p - M['V']['Hohenscheid'])))
kE, kN = pl2utm(*kir)
bsp = f'32U LA {int(kE) % 100000 // 10:04d} {int(kN) % 100000 // 10:04d}'
info = ['Höhenlinien 20 m, Zählhöhenlinien 100 m · Höhen in m über NHN',
        'Gitter (blau): UTM, Zone 32U, WGS 84 · Gitterquadrat 1 km',
        'Blattrand: geografisches Netz, Minuten schwarz-weiß, Striche alle 10″',
        f'Beispiel Gitterpunkt: Kirche Hohenscheid = {bsp}',
        'Druck in Originalgröße (100 %): Gitterquadrat = 2,0 cm',
        'Gelände, Orte und Namen frei erfunden – nur für Übungszwecke']
for k, s in enumerate(info):
    tx(L0, 32.0 - k * 3.5, s, fontsize=5.4, color='#a12' if k >= 4 else '#111')

# Nadeldiagramm
GAMMA = np.degrees(TH)                    # TN östlich von GN
DEKL, DEKL_ANN = 3.28, 0.14                # WMM für Blattmitte, 2026
NADEL = DEKL + GAMMA
nx0, ny0 = 90, 12
pg.plot([nx0, nx0], [ny0, ny0 + 27], color=C['gitter'], lw=0.7)
pg.text(nx0, ny0 + 28.5, 'GN', ha='center', fontsize=5.6, fontweight='bold', color=C['gitter'])
def ray(deg, L_, **kw):
    a_ = np.radians(deg); pg.plot([nx0, nx0 + L_ * np.sin(a_)], [ny0, ny0 + L_ * np.cos(a_)], **kw)
    return nx0 + L_ * np.sin(a_), ny0 + L_ * np.cos(a_)
xt, yt = ray(9, 26, color='#111', lw=0.7)
pg.plot(xt, yt + 0.6, marker='*', ms=5, color='#111')
xm, ym = ray(20, 25, color='#b3261e', lw=0.7)
pg.annotate('', xy=(xm, ym), xytext=(nx0 + 20 * np.sin(np.radians(20)), ny0 + 20 * np.cos(np.radians(20))),
            arrowprops=dict(arrowstyle='-|>', color='#b3261e', lw=0.7, mutation_scale=6))
pg.text(xm + 0.9, ym - 0.4, 'MN', fontsize=5.6, fontweight='bold', color='#b3261e', va='center')
pg.text(xt, yt + 2.6, 'TN', fontsize=5.6, fontweight='bold', ha='center')
strich = NADEL * 6400 / 360
NT = [('Nadeldiagramm für die Blattmitte, Stand 2026', dict(fontweight='bold')),
      (f'Missweisung {DEKL:.1f}° Ost'.replace('.', ','), {}),
      (f'Meridiankonvergenz {GAMMA:.1f}° (GN westlich von TN)'.replace('.', ','), {}),
      (f'Nadelabweichung {NADEL:.1f}° Ost = {strich:.0f} Strich'.replace('.', ','), dict(fontweight='bold', color='#b3261e')),
      (f'jährliche Änderung +{DEKL_ANN:.2f}° (nach Osten)'.replace('.', ','), {}),
      ('Winkel im Diagramm nicht maßstäblich', dict(style='italic', fontsize=4.8))]
for k, (s, kw) in enumerate(NT):
    tx(107, 40 - k * 3.7, s, **{'fontsize': 5.6, **kw})

# Legende
LX, LY = 166, 45.5
tx(LX, LY, 'Zeichenerklärung', fontsize=6.2, fontweight='bold')
lg = fig.add_axes([LX / PW, 4 / PH, 29 / PW, 39 / PH]); lg.set_xlim(0, 29); lg.set_ylim(0, 39); lg.axis('off')
rows = ['B', 'L', 'K', 'G', 'weg', 'bahn', 'tunnel', 'fluss', 'bach', 'wald', 'obst', 'ort', 'kirche', 'wka', 'turm', 'hsp']
TXT = dict(B='Bundesstraße', L='Landesstraße', K='Kreisstraße', G='Gemeindestraße', weg='Wirtschaftsweg', bahn='Eisenbahn',
           tunnel='Tunnel', fluss='Fluss', bach='Bach', wald='Wald', obst='Obstwiese', ort='Ortslage, Gebäude', kirche='Kirche',
           wka='Windkraftanlage', turm='Fernmeldeturm', hsp='Hochspannungsleitung')
for k, r in enumerate(rows):
    y = 37.6 - k * 2.38
    if r in STY:
        lg.plot([0.5, 5.5], [y, y], color='#2b2b2b', lw=STY[r][0], solid_capstyle='butt'); lg.plot([0.5, 5.5], [y, y], color=STY[r][2], lw=STY[r][1], solid_capstyle='butt')
    elif r == 'weg': lg.plot([0.5, 5.5], [y, y], color=C['weg'], lw=0.4)
    elif r == 'bahn': lg.plot([0.5, 5.5], [y, y], color='#111', lw=1.25); lg.plot([0.5, 5.5], [y, y], color='white', lw=0.55, ls=(0, (4, 4)))
    elif r == 'tunnel': lg.plot([0.5, 5.5], [y, y], color='#111', lw=0.6, ls=(0, (2.2, 1.4)))
    elif r == 'fluss': lg.plot([0.5, 5.5], [y, y], color=C['wasser'], lw=2.3); lg.plot([0.5, 5.5], [y, y], color=C['wasser_f'], lw=1.5)
    elif r == 'bach': lg.plot([0.5, 5.5], [y, y], color=C['wasser'], lw=0.6)
    elif r == 'wald': lg.add_patch(Rectangle((0.5, y - 0.8), 5, 1.6, facecolor=C['wald'], edgecolor=C['waldrand'], lw=0.3))
    elif r == 'obst':
        lg.add_patch(Rectangle((0.5, y - 0.8), 5, 1.6, facecolor='white', edgecolor='none'))
        lg.scatter([1.3, 2.6, 3.9, 5.0, 1.9, 3.2, 4.5], [y + 0.4, y + 0.4, y + 0.4, y + 0.4, y - 0.45, y - 0.45, y - 0.45], s=0.9, facecolors='none', edgecolors='#5f9a45', linewidths=0.3)
    elif r == 'ort':
        lg.add_patch(Rectangle((0.5, y - 0.8), 5, 1.6, facecolor=C['ort'])); lg.add_patch(Rectangle((1.4, y - 0.4), 1.0, 0.7, facecolor=C['geb'])); lg.add_patch(Rectangle((3.2, y - 0.35), 1.4, 0.6, facecolor=C['geb']))
    elif r == 'kirche':
        lg.add_patch(Circle((3, y), 0.55, facecolor='white', edgecolor='#111', lw=0.45)); lg.plot([3, 3], [y - 0.35, y + 0.35], color='#111', lw=0.45); lg.plot([2.75, 3.25], [y + 0.1, y + 0.1], color='#111', lw=0.45)
    elif r == 'wka':
        lg.add_patch(Circle((3, y - 0.2), 0.3, facecolor='white', edgecolor='#111', lw=0.4))
        for kk in range(3):
            a_ = np.radians(90 + 120 * kk); lg.plot([3, 3 + 1.1 * np.cos(a_)], [y - 0.2, y - 0.2 + 1.1 * np.sin(a_)], color='#111', lw=0.45)
    elif r == 'turm':
        lg.add_patch(Circle((3, y), 0.6, facecolor='white', edgecolor='#111', lw=0.5)); lg.add_patch(Circle((3, y), 0.2, facecolor='#111'))
    elif r == 'hsp':
        lg.plot([0.5, 5.5], [y, y], color='#222', lw=0.4); lg.plot([1.5, 4.5], [y, y], 'o', ms=1.6, mfc='white', mec='#222', mew=0.4)
    lg.text(7, y, TXT[r], fontsize=5.2, va='center')

fig.savefig(f'{OUT}.pdf', dpi=300)
fig.savefig(f'{OUT}.png', dpi=250)
print('fertig', FW, FH, 'Nadelabweichung', round(NADEL, 2), round(strich))
