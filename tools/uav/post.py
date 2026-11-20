import json, math, random, os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
S = json.load(open('raw/shots.json')); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
PRI = {('t72', 'A'): ['turm', 'gun', 'rear', 'stow'], ('t72', 'B'): ['era', 'sight', 'turm', 'gun'], ('t72', 'B3'): ['sight', 'era', 'turm', 'gun'],
       ('t72', 'B3M'): ['hslat', 'sight', 'era', 'turm', 'gun'], ('t90m', None): ['bustle', 'wedge', 'pano', 'gun', 'hslat'],
       ('btr', '80'): ['turm', 'waffe', 'rad', 'motor'], ('btr', '82A'): ['waffe', 'turm', 'rad', 'motor'], ('btr', '82AT'): ['waffe', 'turm', 'rad', 'motor'],
       ('bmp', '1'): ['turm', 'waffe', 'motor', 'bug'], ('bmp', '1AM'): ['turm', 'waffe', 'motor', 'bug'], ('bmp', '2'): ['turm', 'waffe', 'lfk', 'motor'],
       ('bmp', '2M'): ['lfk', 'turm', 'waffe', 'motor'], ('bmp3', '3'): ['waffe', 'mk', 'turm', 'motor'], ('brdm', 'BRDM'): ['rad', 'turm', 'kabine', 'motor']}
HOT = {'t72': 'exh', 't90m': 'exh', 'btr': 'motor', 'bmp': 'motor', 'bmp3': 'motor', 'brdm': 'motor'}
rng = np.random.default_rng(7); meta = []
for k, s in enumerate(S):
    im = Image.open(s['file']).convert('RGB').resize((720, 540), Image.LANCZOS)
    far = s['r'] > 30
    if s['ir']:
        im = ImageOps.autocontrast(im.convert('L'), cutoff=1)
        if far: im = im.resize((360, 270), Image.BILINEAR).resize((720, 540), Image.BILINEAR)
        im = im.filter(ImageFilter.GaussianBlur(0.8)); a = np.asarray(im).astype(float) + rng.normal(0, 7, (540, 720))
        im = Image.fromarray(np.clip(a, 0, 255).astype('uint8')).convert('RGB')
    else:
        im = ImageEnhance.Color(im).enhance(0.8); im = ImageEnhance.Contrast(im).enhance(0.95)
        if far: im = im.resize((420, 315), Image.BILINEAR).resize((720, 540), Image.BILINEAR)
        im = im.filter(ImageFilter.GaussianBlur(0.55)); a = np.asarray(im).astype(float) + rng.normal(0, 5, (540, 720, 1))
        yy, xx = np.mgrid[0:540, 0:720]; v = 1 - 0.18 * (((xx - 360) / 360) ** 2 + ((yy - 270) / 270) ** 2)
        im = Image.fromarray(np.clip(a * v[..., None], 0, 255).astype('uint8'))
    fn = f'uav-{k}.webp'; im.save(os.path.join(OUT, fn), 'WEBP', quality=74, method=6)
    by = {p['id']: p for p in s['pins'] if not p['occ'] and 5 < p['x'] < 95 and 5 < p['y'] < 95}
    order = PRI[(s['page'], s['hash'])][:]
    if s['ir']: order = [HOT[s['page']]] + order
    pins = []
    for fid in order:
        p = by.get(fid)
        if not p or any(math.hypot(p['x'] - q[0], p['y'] - q[1]) < 7 for q in pins): continue
        t = p['n'] + (' – ' + p['s'] if p.get('s') else '')
        if s['ir'] and fid == HOT[s['page']]: t = p['n'] + ' – im Wärmebild der hellste Bereich'
        pins.append([round(p['x']), round(p['y']), t])
        if len(pins) == 3: break
    meta.append({'src': 'img/' + fn, 'fam': s['fam'], 'v': s['v'], 'el': round(s['el']), 'ir': s['ir'], 'ar': 1.3333, 'pins': pins})
json.dump(meta, open(os.path.join(OUT, 'uav.json'), 'w'), ensure_ascii=False)
print(len(meta), 'Bilder', sum(len(m['pins']) == 0 for m in meta), 'ohne Pins', round(sum(os.path.getsize(os.path.join(OUT, f'uav-{k}.webp')) for k in range(len(meta))) / 1e6, 2), 'MB')
