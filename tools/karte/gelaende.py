"""Fiktives Mittelgebirgsgelände (Hunsrück-Typ) per Landschaftsentwicklung:
Phase 1: flache, reife Hochfläche mit Muldentälern und einem harten Quarzitrücken.
Phase 2: Vorfluter (Hauptfluss) wird tiefer gelegt -> Kerbtäler schneiden sich rückschreitend ein.
Stream-Power-Gesetz implizit (Braun & Willett 2013) + Hangdiffusion. Koordinaten in km, Ursprung linke untere Blattecke."""
import sys
import heapq
import numpy as np
from numba import njit
from scipy import ndimage
from scipy.interpolate import splprep, splev

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
FW, FH = 9.0, 12.05            # Blattrahmen (km)
MARG = 2.5
DX = 0.04                       # 40 m
X0, Y0 = -MARG, -MARG
NX = int(round((FW + 2 * MARG) / DX)) + 1
NY = int(round((FH + 2 * MARG) / DX)) + 1
xs = X0 + np.arange(NX) * DX
ys = Y0 + np.arange(NY) * DX
X, Y = np.meshgrid(xs, ys)
rng = np.random.default_rng(7)


def fractal(beta, seed, lo_cut=0.0):
    r = np.random.default_rng(seed)
    kx, ky = np.meshgrid(np.fft.fftfreq(NX), np.fft.fftfreq(NY))
    k = np.hypot(kx, ky); k[0, 0] = 1
    spec = (r.normal(size=(NY, NX)) + 1j * r.normal(size=(NY, NX))) / k ** (beta / 2)
    spec[0, 0] = 0
    if lo_cut: spec *= np.exp(-(k / lo_cut) ** 2)
    f = np.real(np.fft.ifft2(spec))
    return (f - f.mean()) / f.std()


@njit(cache=True)
def pflood(h, fixed, eps):
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
    return out


@njit(cache=True)
def step(h, fixed, K, dt, m, dx, D):
    ny, nx = h.shape
    hf = pflood(h, fixed, 1e-4)
    n = ny * nx
    recv = np.arange(n)
    dist = np.ones(n) * dx
    s2 = dx * np.sqrt(2.0)
    for i in range(ny):
        for j in range(nx):
            c = i * nx + j
            if fixed[i, j]:
                continue
            best = 0.0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    a = i + di; b = j + dj
                    if (di == 0 and dj == 0) or a < 0 or b < 0 or a >= ny or b >= nx:
                        continue
                    d = s2 if (di != 0 and dj != 0) else dx
                    s = (hf[i, j] - hf[a, b]) / d
                    if s > best:
                        best = s; recv[c] = a * nx + b; dist[c] = d
    flat = hf.ravel().copy()
    order = np.argsort(flat, kind='mergesort')
    A = np.ones(n) * dx * dx
    for k in range(n - 1, -1, -1):
        c = order[k]
        if recv[c] != c:
            A[recv[c]] += A[c]
    Kf = K.ravel()
    fx = fixed.ravel()
    for k in range(n):
        c = order[k]
        r = recv[c]
        if fx[c] or r == c:
            continue
        F = Kf[c] * dt * A[c] ** m / dist[c]
        flat[c] = (flat[c] + F * flat[r]) / (1.0 + F)
    h2 = flat.reshape((ny, nx))
    # Hangdiffusion
    out = h2.copy()
    a = D * dt / (dx * dx)
    for i in range(1, ny - 1):
        for j in range(1, nx - 1):
            if not fixed[i, j]:
                out[i, j] = h2[i, j] + a * (h2[i + 1, j] + h2[i - 1, j] + h2[i, j + 1] + h2[i, j - 1] - 4 * h2[i, j])
    return out, A.reshape((ny, nx)), recv.reshape((ny, nx))


def smooth_path(ctrl, n, s=0.0):
    ctrl = np.asarray(ctrl, float)
    tck, _ = splprep([ctrl[:, 0], ctrl[:, 1]], s=s, k=3)
    return np.column_stack(splev(np.linspace(0, 1, n), tck))


# --- Hauptfluss (Vorfluter), eingesenkte Mäander ---
ctrl = [(1.2, 15.0), (2.0, 13.2), (1.5, 11.6), (1.9, 10.3), (3.1, 9.9), (4.2, 10.3), (4.9, 9.3), (4.2, 8.0),
        (3.6, 6.8), (4.5, 5.9), (5.9, 6.2), (6.6, 5.1), (6.0, 3.8), (6.3, 2.5), (7.6, 2.1), (8.6, 1.0), (9.6, -0.6), (11.6, -3.0)]
river = smooth_path(ctrl, 4000, s=0.0)
seg = np.r_[0, np.cumsum(np.hypot(*np.diff(river, axis=0).T))]
t = seg / seg[-1]
ri = np.clip(np.round((river[:, 1] - Y0) / DX).astype(int), 0, NY - 1)
rj = np.clip(np.round((river[:, 0] - X0) / DX).astype(int), 0, NX - 1)

fixed = np.zeros((NY, NX), bool)
fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True

# --- Ausgangsfläche: Hochfläche, nach NW ansteigend, Quarzitrücken SW-NO ---
v = -(X - 2.4) * np.sin(np.radians(60)) + (Y - 8.9) * np.cos(np.radians(60))   # Abstand quer zur Streichrichtung 60°
band = np.exp(-((v + 0.35 * fractal(3.4, 22)) / 0.85) ** 2)
ridge = band * np.clip(0.75 + 0.35 * fractal(3.0, 23), 0.2, 1.3)
h0 = 440 + 14 * (Y / FH) - 10 * (X / FW) + 12 * fractal(3.0, 1) + 3 * fractal(2.2, 2) + 150 * ridge
K = 2.0e-5 * (1 + 0.25 * fractal(3.0, 5)) * (1 - 0.7 * band)
K = np.clip(K, 3e-6, None)

h = h0.copy()
# Phase 1: Vorfluter hoch -> reife Muldentäler
fixed1 = fixed.copy(); fixed1[ri, rj] = True
lvl1 = 430 - 25 * t
h[ri, rj] = lvl1
h[fixed] += 250                      # Rand ist keine Vorflut: alles entwässert zum Hauptfluss
h[ri, rj] = lvl1
U = 1e-4
for it in range(160):
    h[~fixed1] += U * 2e4
    h, A, recv = step(h, fixed1, K, 2e4, 0.45, DX * 1000, 0.02)
    h[ri, rj] = lvl1
p1 = h.copy()
# Phase 2: Vorfluter tiefer -> Einschneiden
lvl2 = 300 - 45 * t
h[ri, rj] = lvl2
NSTEP = int(sys.argv[2]) if len(sys.argv) > 2 else 25
D2 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
for it in range(NSTEP):
    h, A, recv = step(h, fixed1, K * 1.0, 1e4, 0.45, DX * 1000, D2)
    h[ri, rj] = lvl2
np.savez_compressed(f'{OUT}/gelaende.npz', h=h, p1=p1, A=A, xs=xs, ys=ys, river=river, lvl=lvl2, ri=ri, rj=rj)
inner = (X >= 0) & (X <= FW) & (Y >= 0) & (Y <= FH)
print('Höhen im Blatt', h[inner].min().round(), h[inner].max().round(), 'Phase1', p1[inner].min().round(), p1[inner].max().round())
