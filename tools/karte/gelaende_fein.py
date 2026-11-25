"""Gelände verfeinern: Talaue am Hauptfluss, 20-m-Raster, Abflussnetz (Bäche) als Linien."""
import sys
import heapq
import numpy as np
from numba import njit
from scipy import ndimage
from scipy.spatial import cKDTree

SRC, OUT = sys.argv[1], sys.argv[2]
d = np.load(SRC)
h40, xs40, ys40, river, lvl = d['h'], d['xs'], d['ys'], d['river'], d['lvl']
DX = 0.02
xs = np.arange(xs40[0], xs40[-1] + 1e-9, DX)
ys = np.arange(ys40[0], ys40[-1] + 1e-9, DX)
h = ndimage.map_coordinates(h40, np.meshgrid((ys - ys40[0]) / 0.04, (xs - xs40[0]) / 0.04, indexing='ij'), order=3, mode='nearest')
NY, NX = h.shape
X, Y = np.meshgrid(xs, ys)
pts = np.column_stack([X.ravel(), Y.ravel()])
rng = np.random.default_rng(3)

# Talaue: flacher Talboden, flussabwärts breiter
tree = cKDTree(river)
dist, idx = tree.query(pts)
dist = dist.reshape(h.shape); idx = idx.reshape(h.shape)
tt = idx / (len(river) - 1)
lv = lvl[idx]
wob = ndimage.gaussian_filter(rng.normal(size=h.shape), 25); wob /= wob.std()
TOWN, VIL = np.array([5.4, 6.08]), np.array([7.9, 1.95])
dtown = np.hypot(X - TOWN[0], Y - TOWN[1]); dvil = np.hypot(X - VIL[0], Y - VIL[1])
w = 0.06 + 0.10 * tt + 0.025 * wob + 0.2 * np.exp(-(dtown / 0.55) ** 2) + 0.1 * np.exp(-(dvil / 0.4) ** 2)
floor = lv + 1.0 + 1.5 * np.clip(dist / np.maximum(w, 0.02), 0, 1)
cone = lv + 2.5 + np.clip(dist - w, 0, None) * 700
h = np.minimum(h, np.maximum(floor, np.minimum(cone, h)))
h = np.where(dist < w, floor, np.minimum(h, cone))
h = ndimage.gaussian_filter(h, 0.8)
fine = ndimage.gaussian_filter(rng.normal(size=h.shape), 2.0); fine /= fine.std()
h = h + 0.8 * fine * np.clip(dist / 0.15, 0, 1)


@njit(cache=True)
def route(h, fixed, eps, dx):
    ny, nx = h.shape
    out = h.copy()
    closed = np.zeros((ny, nx), np.bool_)
    heap = [(np.float64(0.0), np.int64(0), np.int64(0))]
    heap.pop()
    for i in range(ny):
        for j in range(nx):
            if fixed[i, j]:
                closed[i, j] = True
                heapq.heappush(heap, (out[i, j], np.int64(i), np.int64(j)))
    while len(heap) > 0:
        z, i, j = heapq.heappop(heap)
        for di in range(-1, 2):
            for dj in range(-1, 2):
                a = i + di; b = j + dj
                if (di == 0 and dj == 0) or a < 0 or b < 0 or a >= ny or b >= nx or closed[a, b]:
                    continue
                closed[a, b] = True
                if out[a, b] < z + eps:
                    out[a, b] = z + eps
                heapq.heappush(heap, (out[a, b], np.int64(a), np.int64(b)))
    n = ny * nx
    recv = np.arange(n)
    s2 = dx * np.sqrt(2.0)
    for i in range(ny):
        for j in range(nx):
            if fixed[i, j]:
                continue
            best = 0.0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    a = i + di; b = j + dj
                    if (di == 0 and dj == 0) or a < 0 or b < 0 or a >= ny or b >= nx:
                        continue
                    dd = s2 if (di != 0 and dj != 0) else dx
                    s = (out[i, j] - out[a, b]) / dd
                    if s > best:
                        best = s; recv[i * nx + j] = a * nx + b
    order = np.argsort(out.ravel(), kind='mergesort')
    A = np.ones(n) * dx * dx
    for k in range(n - 1, -1, -1):
        c = order[k]
        if recv[c] != c:
            A[recv[c]] += A[c]
    return recv, A


fixed = np.zeros(h.shape, bool)
fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
ri = np.clip(np.round((river[:, 1] - ys[0]) / DX).astype(int), 0, NY - 1)
rj = np.clip(np.round((river[:, 0] - xs[0]) / DX).astype(int), 0, NX - 1)
fixed[ri, rj] = True
recv, A = route(h, fixed, 1e-5, DX * 1000)
A = A.reshape(h.shape) / 1e6
hfill = h.copy()
chm = (A > 3.0) & ~fixed
cp = np.column_stack([X[chm], Y[chm]]); ch_h = h[chm]; ch_a = A[chm]
ct = cKDTree(cp)
dd, ii = ct.query(pts)
dd = dd.reshape(h.shape); hc_ = ch_h[ii].reshape(h.shape); ac_ = ch_a[ii].reshape(h.shape)
wt = 0.02 + 0.018 * np.log(ac_ / 3.0) + 0.12 * np.exp(-(dtown / 0.6) ** 2) + 0.05 * np.exp(-(dvil / 0.4) ** 2)
floor_t = hc_ + 0.6 + 1.2 * np.clip(dd / wt, 0, 1)
cone_t = hc_ + 1.8 + np.clip(dd - wt, 0, None) * 650
h = np.where(dd < wt, np.minimum(h, floor_t), np.minimum(h, np.maximum(cone_t, np.minimum(h, cone_t))))
h = np.minimum(h, np.where(dd < wt + 0.2, np.maximum(cone_t, floor_t * (dd < wt)), h))
recv, A = route(h, fixed, 1e-5, DX * 1000)
A = A / 1e6                                            # km²
np.savez_compressed(OUT, h=h.astype(np.float32), xs=xs, ys=ys, A=A.reshape(h.shape).astype(np.float32), recv=recv.reshape(h.shape),
                    river=river, lvl=lvl, fixed=fixed)
inner = (X >= 0) & (X <= 9) & (Y >= 0) & (Y <= 11.2)
for thr in (0.15, 0.25, 0.4):
    ch = (A.reshape(h.shape) >= thr) & inner & ~fixed
    print(f'Schwelle {thr} km²: Gewässerdichte {ch.sum() * DX / (9 * 11.2):.2f} km/km²')
print('Höhen im Blatt', h[inner].min().round(), h[inner].max().round())
