"""Kartenobjekte erzeugen: Bäche, Straßen (Wegsuche mit Steigungskosten), Bahn, Orte, Gebäude, Wald, Sonderobjekte.
Ebene Koordinaten in km, Ursprung SW-Blattecke, x nach Osten (parallel zum unteren Blattrand), y nach geografisch Nord."""
import pickle
import heapq
import numpy as np
from numba import njit
from scipy import ndimage
from scipy.spatial import cKDTree, Voronoi
from scipy.interpolate import splprep, splev, RegularGridInterpolator

d = np.load('fein.npz')
h = d['h'].astype(float); xs, ys = d['xs'], d['ys']; A = d['A'].astype(float); recv = d['recv']; fixed = d['fixed']
river, lvl = d['river'], d['lvl']
FW, FH = 9.0236, 11.1204
DX = 0.02
NY, NX = h.shape
X, Y = np.meshgrid(xs, ys)
Hf = RegularGridInterpolator((ys, xs), h, bounds_error=False, fill_value=None)
def H(x, y): return Hf(np.column_stack([np.atleast_1d(y), np.atleast_1d(x)]))
rng = np.random.default_rng(42)
gy, gx = np.gradient(h, DX * 1000)
slope = np.hypot(gx, gy)
Sf = RegularGridInterpolator((ys, xs), ndimage.uniform_filter(slope, 3), bounds_error=False, fill_value=None)
def S(x, y): return Sf(np.column_stack([np.atleast_1d(y), np.atleast_1d(x)]))
rtree = cKDTree(river)
seg_r = np.r_[0, np.cumsum(np.hypot(*np.diff(river, axis=0).T))]
in_frame = lambda p, m=0.0: (p[:, 0] > -m) & (p[:, 0] < FW + m) & (p[:, 1] > -m) & (p[:, 1] < FH + m)


def chaikin(p, it=2):
    p = np.asarray(p, float)
    for _ in range(it):
        if len(p) < 3: return p
        q = 0.75 * p[:-1] + 0.25 * p[1:]; r = 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[0], np.column_stack([q, r]).reshape(-1, 2), p[-1]])
    return p


def resample(p, step):
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    if s[-1] == 0: return p[:1]
    n = max(2, int(s[-1] / step) + 1)
    u = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(u, s, p[:, 0]), np.interp(u, s, p[:, 1])])


def beside_river(y_or_x, side, off, axis='y'):
    """Punkt auf dem Talboden neben dem Fluss: erster Flusspunkt mit gegebenem y (oder x), seitlich versetzt."""
    k = int(np.argmin(np.abs(river[:, 1 if axis == 'y' else 0] - y_or_x)))
    t = river[min(k + 1, len(river) - 1)] - river[max(k - 1, 0)]; t /= np.hypot(*t)
    n = np.array([-t[1], t[0]])
    return river[k] + side * off * n


# ---------------- Bäche aus dem Abflussnetz ----------------
pts = np.column_stack([X.ravel(), Y.ravel()])
_dq, _iq = rtree.query(pts)
d_riv = _dq.reshape(h.shape)
floodplain = (h - lvl[_iq].reshape(h.shape) < 4.5) & (d_riv < 0.6)
Af, rv, fx = A.ravel(), recv.ravel(), fixed.ravel()
ch = (Af >= 0.15) & ~fx
src = np.where(ch)[0]
maxdon = np.zeros_like(Af)
np.maximum.at(maxdon, rv[src], Af[src])
has_don = np.zeros(NY * NX, bool); has_don[rv[src]] = True
heads = src[~has_don[src]]
streams = []
for hd in heads:
    c = hd; path = [c]
    while True:
        r = rv[c]
        if r == c: break
        path.append(r)
        if fx[r] or Af[c] < maxdon[r]: break
        c = r
    path = np.array(path)
    i, j = np.divmod(path, NX)
    fp = floodplain[i, j] & (d_riv[i, j] < 0.14)
    if fp.any():
        k = int(np.argmax(fp))
        if k == 0: continue
        path = path[:k + 1]; i, j = i[:k + 1], j[:k + 1]
        p = np.column_stack([xs[j], ys[i]])
        q = river[rtree.query(p[-1])[1]]
        p = np.vstack([p, p[-1] + 0.5 * (q - p[-1]), q])
        path = np.r_[path, path[-1], path[-1]]
    else:
        p = np.column_stack([xs[j], ys[i]])
    if not in_frame(p, 0.3).any() or len(p) < 4: continue
    keep = np.r_[0, np.arange(2, len(p) - 1, 2), len(p) - 1]
    ps = chaikin(p[keep], 3)
    a = Af[path]
    streams.append((ps, np.interp(np.linspace(0, 1, len(ps)), np.linspace(0, 1, len(a)), a)))
print('Bäche', len(streams))
stream_pts = np.vstack([s[0] for s in streams])

# ---------------- Wegsuche ----------------
SUB = 2
x0i, x1i = np.searchsorted(xs, -0.8), np.searchsorted(xs, FW + 0.8)
y0i, y1i = np.searchsorted(ys, -0.8), np.searchsorted(ys, FH + 0.8)
hc = h[y0i:y1i:SUB, x0i:x1i:SUB].copy()
cx, cy = xs[x0i:x1i:SUB], ys[y0i:y1i:SUB]
CNY, CNX = hc.shape
cpts = np.column_stack([np.meshgrid(cx, cy)[0].ravel(), np.meshgrid(cx, cy)[1].ravel()])
river_c = (rtree.query(cpts)[0] < 0.07).reshape(hc.shape)
rail_c = np.zeros(hc.shape, bool)
lvl_c = lvl[rtree.query(cpts)[1]].reshape(hc.shape)
stream_c = (cKDTree(stream_pts).query(cpts)[0] < 0.03).reshape(hc.shape) & ~river_c
road_c = np.zeros(hc.shape, bool)
NB = np.array([(di, dj) for di in range(-2, 3) for dj in range(-2, 3) if (di, dj) != (0, 0) and np.gcd(abs(di), abs(dj)) == 1])


@njit(cache=True)
def dijkstra(hc, river, stream, road, rail, s, t, dx, a, gmax, pr, ps, disc, nb):
    ny, nx = hc.shape
    n = ny * nx
    dist = np.full(n, 1e18); prev = -np.ones(n, np.int64)
    dist[s] = 0.0
    heap = [(0.0, s)]
    while len(heap) > 0:
        du, u = heapq.heappop(heap)
        if u == t: break
        if du > dist[u]: continue
        ui = u // nx; uj = u % nx
        for k in range(nb.shape[0]):
            vi = ui + nb[k, 0]; vj = uj + nb[k, 1]
            if vi < 0 or vj < 0 or vi >= ny or vj >= nx: continue
            L = dx * np.sqrt(nb[k, 0] ** 2 + nb[k, 1] ** 2)
            g = abs(hc[vi, vj] - hc[ui, uj]) / (L * 1000.0)
            c = L * (1.0 + a * g * g)
            if g > gmax: c += L * (g - gmax) * 3000.0
            if river[vi, vj]:
                c += L * 25.0
                if not river[ui, uj]: c += pr
            if stream[vi, vj]:
                c += L * 2.0
                if not stream[ui, uj]: c += ps
            if rail[vi, vj]: c += L * 12.0
            if road[vi, vj] and road[ui, uj]: c *= disc
            v = vi * nx + vj
            if du + c < dist[v]:
                dist[v] = du + c; prev[v] = u
                heapq.heappush(heap, (du + c, v))
    path = [t]
    while path[-1] != s and prev[path[-1]] >= 0:
        path.append(prev[path[-1]])
    return np.array(path[::-1])


def cidx(p):
    return int(np.clip(round((p[1] - cy[0]) / (DX * SUB)), 0, CNY - 1)) * CNX + int(np.clip(round((p[0] - cx[0]) / (DX * SUB)), 0, CNX - 1))


def route(pts, a=200.0, gmax=0.11, pr=3.0, ps=0.25, disc=0.55, smooth=2):
    out = []
    for p, q in zip(pts[:-1], pts[1:]):
        path = dijkstra(hc, river_c, stream_c, road_c, rail_c, cidx(p), cidx(q), DX * SUB, a, gmax, pr, ps, disc, NB)
        i, j = np.divmod(path, CNX)
        seg = np.column_stack([cx[j], cy[i]])
        seg[0], seg[-1] = p, q
        out.append(seg if not out else seg[1:])
    pth = np.vstack(out)
    if len(pth) > 8:
        k = 5
        sm = np.array([ndimage.uniform_filter1d(pth[:, c], k, mode='nearest') for c in range(2)]).T
        sm[0], sm[-1] = pth[0], pth[-1]
        pth = sm
    pth = chaikin(pth, smooth + 1)
    for pp in resample(pth, 0.02):
        road_c.flat[cidx(pp)] = True
    return pth


V = {  # Ortsmittelpunkte
    'Ilsenau': beside_river(5.45, 1, 0.09, axis='x'),
    'Niederilsen': np.array([7.95, 1.95]),
    'Hohenscheid': np.array([2.8, 2.4]),
    'Lindenweiler': np.array([0.95, 1.05]),
    'Elmenhausen': np.array([8.15, 4.35]),
    'Wolfsrath': np.array([7.95, 9.0]),
    'Gräfenrath': np.array([0.4, 7.0]),
    'Buchholz': np.array([8.6, 10.55]),
    'Heidehof': np.array([4.3, 1.3]),
}
# Niederilsen auf den Talboden
V['Niederilsen'] = river[np.argmin(np.hypot(*(river - V['Niederilsen']).T))] + np.array([-0.06, 0.09])

top_in = beside_river(FH + 0.5, 1, 0.1)
roads = []
def add(cls, name, pts, **kw):
    p = route([np.asarray(q, float) for q in pts], **kw); roads.append(dict(cls=cls, name=name, p=p)); return p

# Bundesstraße im Haupttal
B = add('B', 'B 422', [top_in, V['Ilsenau'], V['Niederilsen'], beside_river(-0.6, 1, 0.1)], a=120, gmax=0.06, pr=1.5, ps=0.05)
# ---------------- Bahn im Haupttal (Tunnel durch Mäanderhälse) ----------------
@njit(cache=True)
def rail_dijkstra(hc, lvlc, river, block, s, t, dx, nb, tf):
    ny, nx = hc.shape
    n = ny * nx
    dist = np.full(n, 1e18); prev = -np.ones(n, np.int64)
    dist[s] = 0.0
    heap = [(0.0, s)]
    while len(heap) > 0:
        du, u = heapq.heappop(heap)
        if u == t: break
        if du > dist[u]: continue
        ui = u // nx; uj = u % nx
        for k in range(nb.shape[0]):
            vi = ui + nb[k, 0]; vj = uj + nb[k, 1]
            if vi < 0 or vj < 0 or vi >= ny or vj >= nx: continue
            L = dx * np.sqrt(nb[k, 0] ** 2 + nb[k, 1] ** 2)
            over = hc[vi, vj] - (lvlc[vi, vj] + 7.0)
            c = L
            if over > 14.0: c = L * tf
            elif over > 4.0: c = L * (1.0 + (over - 4.0) * 0.6)
            if block[vi, vj]: c += L * 12.0
            if river[vi, vj]:
                c += L * 20.0
                if not river[ui, uj]: c += 0.25
            v = vi * nx + vj
            if du + c < dist[v]:
                dist[v] = du + c; prev[v] = u
                heapq.heappush(heap, (du + c, v))
    path = [t]
    while path[-1] != s and prev[path[-1]] >= 0:
        path.append(prev[path[-1]])
    return np.array(path[::-1])

r_start, r_end = beside_river(FH + 0.7, -1, 0.11), beside_river(-0.7, -1, 0.11)
rp = rail_dijkstra(hc, lvl_c, (rtree.query(cpts)[0] < 0.055).reshape(hc.shape), ndimage.binary_dilation(road_c, iterations=1), cidx(r_start), cidx(r_end), DX * SUB, NB, 2.4)
i_, j_ = np.divmod(rp, CNX)
rail = np.column_stack([cx[j_], cy[i_]])
for _ in range(3):
    rail = np.array([ndimage.uniform_filter1d(rail[:, c], 9, mode='nearest') for c in range(2)]).T
rail = resample(chaikin(rail, 2), 0.01)
rail_h = H(rail[:, 0], rail[:, 1])
track = ndimage.uniform_filter1d(lvl[rtree.query(rail)[1]] + 7, 151, mode='nearest')
tunnel = rail_h > track + 16
tunnel = ndimage.binary_closing(tunnel, iterations=6)
tl, tn = ndimage.label(tunnel)
for k in range(1, tn + 1):
    if (tl == k).sum() < 12: tunnel[tl == k] = False
print('Tunnelanteil', tunnel.mean().round(2))
rail_tree = cKDTree(rail)
rail_c[:] = (rail_tree.query(cpts)[0] < 0.055).reshape(hc.shape)

# Landesstraßen
add('L', 'L 181', [V['Ilsenau'], (FW + 0.6, 6.9)], a=150, gmax=0.08, ps=0.05)
add('L', 'L 182', [V['Ilsenau'], V['Hohenscheid'], V['Lindenweiler'], (-0.6, 0.45)], a=200, gmax=0.09)
add('L', 'L 183', [V['Niederilsen'], V['Elmenhausen'], (FW + 0.6, 5.2)], a=220, gmax=0.10)
# Kreisstraßen
add('K', 'K 12', [V['Hohenscheid'], V['Niederilsen']], a=220, gmax=0.11)
add('K', 'K 13', [V['Ilsenau'] + np.array([0.05, 0.08]), V['Wolfsrath'], V['Buchholz'], (FW + 0.6, 10.9)], a=220, gmax=0.11)
add('K', 'K 14', [np.array([5.02, 9.3]), (7.2, 10.35), (FW + 0.6, 11.4)], a=160, gmax=0.09, ps=0.05)
add('K', 'K 15', [V['Gräfenrath'], (3.62, 7.3)], a=220, gmax=0.11)
add('K', 'K 16', [V['Gräfenrath'], (-0.6, 7.6)], a=220, gmax=0.11)
# Gemeindestraßen
add('G', '', [V['Lindenweiler'], (1.15, -0.6)], a=220)
add('G', '', [V['Hohenscheid'], V['Heidehof'], (4.9, -0.6)], a=220)
add('G', '', [V['Wolfsrath'], (7.2, 10.35)], a=220)
add('G', '', [V['Elmenhausen'], (FW + 0.6, 3.6)], a=220)

# ---------------- Wald ----------------
sl_s = ndimage.uniform_filter(slope, 4)
steep = sl_s > 0.17
gx_, gy_ = np.meshgrid(np.arange(-1.5, FW + 1.5, 0.26), np.arange(-1.5, FH + 1.5, 0.26))
seeds = np.column_stack([gx_.ravel(), gy_.ravel()]) + rng.uniform(-0.1, 0.1, (gx_.size, 2))
lab = cKDTree(seeds).query(pts)[1]
cnt = np.bincount(lab, minlength=len(seeds)).clip(1)
frac_steep = np.bincount(lab, steep.ravel(), minlength=len(seeds)) / cnt
mean_h = np.bincount(lab, h.ravel(), minlength=len(seeds)) / cnt
pn = rng.random(len(seeds))
parcel_f = (pn < 0.14) | (frac_steep > 0.3) | (mean_h > 540)
forest = parcel_f[lab].reshape(h.shape) | steep
excl = floodplain.copy()
for nm, c in V.items():
    r = {'Ilsenau': 0.45, 'Niederilsen': 0.3, 'Buchholz': 0.28, 'Heidehof': 0.2}.get(nm, 0.5)
    excl |= np.hypot(X - c[0], Y - c[1]) < r
forest &= ~excl
forest = ndimage.binary_opening(forest, iterations=2)
lbl, n = ndimage.label(forest)
sizes = ndimage.sum(forest, lbl, range(1, n + 1))
forest = np.isin(lbl, 1 + np.where(sizes > 120)[0])
holes = ndimage.binary_fill_holes(forest) & ~forest
lbl, n = ndimage.label(holes)
sizes = ndimage.sum(holes, lbl, range(1, n + 1))
forest |= np.isin(lbl, 1 + np.where(sizes < 60)[0])

# ---------------- Wege: Feld-, Wald- und Fußwege als zusammenhängendes Netz ----------------
tracks = []
def track(pts, kind='feld', **kw):
    p = route([np.asarray(q, float) for q in pts], **{'a': 60.0, 'gmax': 0.16, 'pr': 6.0, 'ps': 0.15, 'disc': 0.45, 'smooth': 2, **kw})
    tracks.append((kind, p)); return p
def ok_target(p, smax=0.14):
    return -0.4 < p[0] < FW + 0.4 and -0.4 < p[1] < FH + 0.4 and S(*p)[0] < smax and rtree.query(p)[0] > 0.15
def net_point(p):
    ii, jj = np.nonzero(road_c)
    q = np.column_stack([cx[jj], cy[ii]])
    return q[np.argmin(np.hypot(*(q - p).T))]
for name, n in (('Hohenscheid', 12), ('Lindenweiler', 10), ('Elmenhausen', 10), ('Wolfsrath', 10), ('Gräfenrath', 9),
                ('Buchholz', 6), ('Heidehof', 6), ('Niederilsen', 3), ('Ilsenau', 4)):
    c = V[name]; got = 0
    for _ in range(80):
        if got >= n: break
        ang = rng.uniform(0, 2 * np.pi); r = rng.uniform(0.5, 2.0)
        p = c + r * np.array([np.cos(ang), np.sin(ang)])
        if not ok_target(p): continue
        track([c, p]); got += 1
inner = (X > 0.15) & (X < FW - 0.15) & (Y > 0.15) & (Y < FH - 0.15)
fcells = np.argwhere(forest & inner & (sl_s < 0.3))
for _ in range(34):
    i, j = fcells[rng.integers(len(fcells))]
    p = np.array([xs[j], ys[i]])
    q = net_point(p)
    if np.hypot(*(p - q)) < 0.25: continue
    track([q, p], 'forst')
    for _ in range(10):
        ang = rng.uniform(0, 2 * np.pi); p2 = p + rng.uniform(0.6, 1.4) * np.array([np.cos(ang), np.sin(ang)])
        ii_, jj_ = int(round((p2[1] - ys[0]) / DX)), int(round((p2[0] - xs[0]) / DX))
        if 0 <= ii_ < NY and 0 <= jj_ < NX and forest[ii_, jj_] and ok_target(p2, 0.3):
            track([p, p2], 'forst'); break

# ---------------- Fernmeldeturm, Windpark, Höhenpunkte ----------------
hm = np.where(inner, h, 0)
ti = np.unravel_index(np.argmax(hm), h.shape)
tower = np.array([xs[ti[1]], ys[ti[0]]])
wka = []
cand = np.argwhere(inner & (h > 545) & (X < 2.6) & (Y > 2.8) & (Y < 7.2))
cand = sorted(cand, key=lambda c: -h[c[0], c[1]])
for c in cand:
    p = np.array([xs[c[1]], ys[c[0]]])
    if np.hypot(*(p - tower)) < 0.4 or any(np.hypot(*(p - q)) < 0.42 for q in wka): continue
    wka.append(p)
    if len(wka) >= 7: break
for p in [tower] + wka:
    track([p, net_point(p)], 'forst', smooth=1)
track([V['Gräfenrath'], tower, V['Lindenweiler']], 'fuss', a=25.0, gmax=0.35, disc=0.8)
track([V['Ilsenau'] + np.array([0.2, 0.15]), (6.9, 8.2), V['Wolfsrath']], 'fuss', a=25.0, gmax=0.35, disc=0.8)
mx = ndimage.maximum_filter(h, size=31)
pk = np.argwhere((h == mx) & inner & (h > 400))
pk = sorted(pk, key=lambda c: -h[c[0], c[1]])
peaks = []
for c in pk:
    p = np.array([xs[c[1]], ys[c[0]]])
    if np.hypot(*(p - tower)) < 0.5 or any(np.hypot(*(p - q[:2])) < 1.1 for q in peaks): continue
    peaks.append(np.r_[p, h[c[0], c[1]]])
    if len(peaks) >= 14: break

# Hochspannungsleitung 110 kV
pl_ctrl = np.array([(-0.3, 9.45), (2.25, 7.95), (4.55, 6.45), (6.95, 4.25), (FW + 0.3, 3.35)])
masts = [pl_ctrl[0]]
for p, q in zip(pl_ctrl[:-1], pl_ctrl[1:]):
    L = np.hypot(*(q - p)); n = max(1, int(round(L / 0.33)))
    for k in range(1, n + 1): masts.append(p + (q - p) * k / n)
masts = np.array(masts)

# ---------------- Orte: Gassen und Gebäude ----------------
road_pts = np.vstack([resample(r['p'], 0.005) for r in roads])
road_tree = cKDTree(road_pts)
buildings, specials, bpos = [], {}, []
grid = {}
def free(c, rr):
    k0, k1 = int(c[0] // 0.02), int(c[1] // 0.02)
    for a_ in range(k0 - 1, k0 + 2):
        for b_ in range(k1 - 1, k1 + 2):
            for q in grid.get((a_, b_), ()):
                if np.hypot(c[0] - q[0], c[1] - q[1]) < rr: return False
    return True
def put(c, ang, l, w, kind='haus'):
    cs, sn = np.cos(ang), np.sin(ang)
    poly = (np.array([[-l, -w], [l, -w], [l, w], [-l, w]]) / 2) @ np.array([[cs, sn], [-sn, cs]]) + c
    buildings.append((kind, poly)); bpos.append(c)
    grid.setdefault((int(c[0] // 0.02), int(c[1] // 0.02)), []).append(c)

SETS = {'Ilsenau': (0.85, 12, 1.0, 0.32), 'Niederilsen': (0.42, 4, 0.9, 0.24), 'Hohenscheid': (0.45, 7, 0.95, 0.18),
        'Lindenweiler': (0.38, 5, 0.9, 0.18), 'Elmenhausen': (0.42, 6, 0.9, 0.2), 'Wolfsrath': (0.4, 6, 0.9, 0.18),
        'Gräfenrath': (0.36, 5, 0.9, 0.18), 'Buchholz': (0.2, 2, 0.8, 0.2), 'Heidehof': (0.07, 0, 0.9, 0.2)}

def lanes_for(c, R, n, smax):
    out = []
    near = road_pts[np.hypot(*(road_pts - c).T) < R * 0.6]
    for _ in range(n * 15):
        if len(out) >= n or len(near) < 3: break
        k = rng.integers(1, len(near) - 1); p = near[k]
        t_ = road_pts[road_tree.query(p, k=3)[1][-1]] - p
        t_ = t_ / (np.hypot(*t_) + 1e-12)
        ang = np.arctan2(t_[1], t_[0]) + rng.choice([-1, 1]) * np.pi / 2 + rng.uniform(-0.6, 0.6)
        L = rng.uniform(0.1, 0.28); bend = rng.uniform(-0.7, 0.7)
        tt = np.linspace(0, 1, 14)
        seg = np.column_stack([p[0] + L * tt * np.cos(ang + bend * tt), p[1] + L * tt * np.sin(ang + bend * tt)])
        if (S(seg[:, 0], seg[:, 1]) > smax + 0.03).any() or rtree.query(seg)[0].min() < 0.06: continue
        if np.hypot(*(seg[-1] - c)) > R * 1.1 or road_tree.query(seg[3:])[0].min() < 0.03: continue
        if rail_tree.query(seg)[0].min() < 0.03: continue
        if out and cKDTree(np.vstack(out)).query(seg[2:])[0].min() < 0.035: continue
        out.append(seg)
    return out

# Ilsenau: Straßen parallel zum Fluss in der Aue und Hangstraßen auf Höhenlinien
c = V['Ilsenau']
town_lanes = []
for off in (-0.2, -0.11, 0.11, 0.2):
    k_ = np.arange(len(river))
    t_ = np.gradient(river, axis=0); t_ /= np.hypot(*t_.T)[:, None]
    p = river + off * np.column_stack([-t_[:, 1], t_[:, 0]])
    ok = (np.hypot(*(p - c).T) < 0.75)
    hp = H(p[:, 0], p[:, 1]) - lvl
    ok &= (hp < 5) & (road_tree.query(p)[0] > 0.035) & (rail_tree.query(p)[0] > 0.035)
    lab_, n_ = ndimage.label(ok)
    for k in range(1, n_ + 1):
        seg = p[lab_ == k]
        if np.hypot(*np.diff(seg, axis=0).T).sum() > 0.12: town_lanes.append(resample(seg, 0.02))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig_ = plt.figure(); ax_ = fig_.add_subplot()
base = float(H(*c)[0])
for dz in (16, 30, 46):
    cs = ax_.contour(X, Y, ndimage.gaussian_filter(h, 2), levels=[base + dz])
    for path in cs.allsegs[0]:
        ok = (np.hypot(*(path - c).T) < 0.7) & (S(path[:, 0], path[:, 1]) < 0.34) & (road_tree.query(path)[0] > 0.03)
        lab_, n_ = ndimage.label(ok)
        for k in range(1, n_ + 1):
            seg = path[lab_ == k]
            if np.hypot(*np.diff(seg, axis=0).T).sum() > 0.15: town_lanes.append(resample(seg, 0.02))
plt.close(fig_)

lane_list = []
for name, (R, nl, dens, smax) in SETS.items():
    c = V[name]
    lanes = lanes_for(c, R, nl, smax)
    if name == 'Ilsenau': lanes += town_lanes
    lane_list += lanes
    lane_tree = cKDTree(np.vstack(lane_list)) if lane_list else None
    streets = [(r['p'], 0.009) for r in roads] + [(ln, 0.006) for ln in lanes]
    for st, hw in streets:
        st = resample(st, 0.0105)
        if len(st) < 3: continue
        for k in range(1, len(st) - 1):
            p = st[k]; dc = np.hypot(*(p - c))
            if dc > R: continue
            prob = dens * np.clip(1.25 - (dc / R) ** 2, 0, 1)
            tvec = st[k + 1] - st[k - 1]; tvec /= np.hypot(*tvec) + 1e-12
            nvec = np.array([-tvec[1], tvec[0]])
            for side in (-1, 1):
                if rng.random() > prob: continue
                l, w = rng.uniform(0.015, 0.027), rng.uniform(0.011, 0.016)
                if name == 'Ilsenau' and dc < 0.35: l *= rng.uniform(1.0, 1.6)
                bc = p + side * (hw + w / 2 + rng.uniform(0.002, 0.006)) * nvec
                ang = np.arctan2(tvec[1], tvec[0]) + (np.pi / 2 if rng.random() < 0.3 else 0)
                if S(*bc)[0] > smax + 0.06 or rtree.query(bc)[0] < 0.04 or rail_tree.query(bc)[0] < 0.025: continue
                if road_tree.query(bc)[0] < 0.0095 + w / 2: continue
                if lane_tree is not None and lane_tree.query(bc)[0] < 0.0065 + w / 2: continue
                if not free(bc, 0.019): continue
                put(bc, ang, l, w)
                if name != 'Ilsenau' and rng.random() < 0.35:      # Hakenhof: Scheune quer dahinter
                    bc2 = bc + side * nvec * (w / 2 + 0.009) + tvec * rng.choice([-1, 1]) * l * 0.3
                    if road_tree.query(bc2)[0] > 0.016 and free(bc2, 0.012) and S(*bc2)[0] < smax + 0.06:
                        put(bc2, ang + np.pi / 2, rng.uniform(0.014, 0.024), 0.0095, 'scheune')
    if bpos and name not in ('Heidehof', 'Buchholz'):
        dd = np.hypot(*(np.array(bpos) - c).T); k = int(np.argmin(dd))
        if dd[k] < 0.2: specials.setdefault('kirche', []).append(bpos[k])
    print(f'{name}: {sum(1 for q in bpos if np.hypot(*(q - c)) < R + 0.05)} Gebäude')
k = int(np.argmin(np.hypot(*(rail - V['Ilsenau']).T)))
specials['bahnhof'] = [(rail[k], rail[min(k + 3, len(rail) - 1)] - rail[max(k - 3, 0)])]
print('Gebäude', len(buildings))

# Ortslage
bm = np.zeros(h.shape, bool)
bp = np.array(bpos)
bi = np.clip(np.round((bp[:, 1] - ys[0]) / DX).astype(int), 0, NY - 1)
bj = np.clip(np.round((bp[:, 0] - xs[0]) / DX).astype(int), 0, NX - 1)
bm[bi, bj] = True
ort = ndimage.binary_dilation(bm, iterations=2)
ort = ndimage.binary_closing(ort, iterations=3)
ort = ndimage.binary_fill_holes(ort) & (d_riv > 0.02)
forest &= ~ndimage.binary_dilation(ort, iterations=1)

# Sonderflächen: Friedhöfe, Sportplätze, Obstwiesen, Weinberg
for name in ('Hohenscheid', 'Wolfsrath', 'Elmenhausen', 'Lindenweiler', 'Gräfenrath', 'Ilsenau'):
    c = V[name]; R = SETS[name][0]
    for _ in range(80):
        a_ = rng.uniform(0, 2 * np.pi); rr = R * rng.uniform(0.75, 1.05)
        p = c + rr * np.array([np.cos(a_), np.sin(a_)])
        if S(*p)[0] < 0.12 and road_tree.query(p)[0] > 0.03 and free(p, 0.04) and rtree.query(p)[0] > 0.1:
            specials.setdefault('friedhof', []).append((p, a_)); break
for name in ('Hohenscheid', 'Ilsenau', 'Elmenhausen'):
    c = V[name]; R = SETS[name][0]
    for _ in range(300):
        a_ = rng.uniform(0, 2 * np.pi); rr = R * rng.uniform(0.7, 1.4)
        p = c + rr * np.array([np.cos(a_), np.sin(a_)])
        corners = p + np.array([[-0.055, -0.035], [0.055, -0.035], [0.055, 0.035], [-0.055, 0.035]])
        hh = H(corners[:, 0], corners[:, 1])
        if hh.max() - hh.min() < 3.5 and road_tree.query(p)[0] < 0.08 and road_tree.query(corners)[0].min() > 0.02 and free(p, 0.07) and rtree.query(corners)[0].min() > 0.03 and cKDTree(stream_pts).query(corners)[0].min() > 0.03:
            specials.setdefault('sportplatz', []).append(p); break
orchard = np.zeros(h.shape, bool)
for name in ('Hohenscheid', 'Lindenweiler', 'Elmenhausen', 'Wolfsrath', 'Gräfenrath', 'Niederilsen'):
    c = V[name]; R = SETS[name][0]
    ring = (np.hypot(X - c[0], Y - c[1]) < R + 0.3) & ~ort & ~forest & (sl_s < 0.2)
    plab = lab.reshape(h.shape)
    ids = np.unique(plab[ring])
    sel = ids[rng.random(len(ids)) < 0.3]
    orchard |= ring & np.isin(plab, sel)
vine = (X > 6.8) & (X < 8.2) & (Y > 2.0) & (Y < 2.9) & (gy > 0.12) & (sl_s > 0.15) & (h < 400) & ~ort
vine = ndimage.binary_opening(vine, iterations=2)
forest &= ~vine
orchard &= ~vine

pickle.dump(dict(streams=streams, roads=roads, rail=rail, tunnel=tunnel, forest=forest, ort=ort, orchard=orchard, vine=vine,
                 buildings=buildings, specials=specials, tower=tower, wka=wka, peaks=peaks, masts=masts, tracks=tracks,
                 V=V, lanes=lane_list, floodplain=floodplain), open('merkmale.pkl', 'wb'))
print('Turm', tower.round(2), H(*tower).round(), 'WKA', len(wka), 'Gipfel', len(peaks), 'Wege', len(tracks))
