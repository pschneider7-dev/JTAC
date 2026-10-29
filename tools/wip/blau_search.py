import json, subprocess, time, urllib.parse, re, sys, os
UA = 'JTACTrainer/1.0 (https://github.com/pschneider7-dev/JTAC)'
Q = {
 'leo2': ['Leopard 2A6', 'Leopard 2A7', 'Leopard 2A4'], 'm1': ['M1A2 Abrams'], 'leclerc': ['Leclerc tank'], 'chall': ['Challenger 2 tank'],
 'puma': ['Puma IFV Schützenpanzer'], 'marder': ['Marder 1A3'], 'cv90': ['CV90 infantry fighting vehicle'], 'bradley': ['M2A3 Bradley'],
 'boxer': ['Boxer armoured vehicle'], 'stryker': ['Stryker ICV'], 'vbci': ['VBCI'], 'fuchs': ['Transportpanzer Fuchs'],
 'm113': ['M113 armored personnel carrier'], 'dingo': ['ATF Dingo 2'], 'fennek': ['Fennek reconnaissance'], 'jltv': ['Joint Light Tactical Vehicle', 'HMMWV M1151'],
 'pzh2000': ['Panzerhaubitze 2000'], 'm109': ['M109A6 Paladin', 'M109A7'], 'caesar': ['CAESAR self-propelled howitzer'],
 'himars': ['M142 HIMARS'], 'm270': ['M270 MLRS', 'MARS II Raketenwerfer'], 'griffon': ['VBMR Griffon'],
}
def api(params):
    data = urllib.parse.urlencode({**params, 'format': 'json'})
    for att in range(20):
        r = subprocess.run(['curl', '-sS', '-m', '40', '-A', UA, '-d', data, 'https://commons.wikimedia.org/w/api.php'], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(60)
    return None
for fid, qs in Q.items():
    fn = 'blau/%s.json' % fid
    if os.path.exists(fn): continue
    out = []
    for q in qs:
        d = api({'action': 'query', 'generator': 'search', 'gsrsearch': q, 'gsrnamespace': 6, 'gsrlimit': 40,
                 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'iiurlwidth': 960, 'iiextmetadatafilter': 'LicenseShortName|Artist'})
        if not d or 'query' not in d: continue
        for p in d['query']['pages'].values():
            ii = (p.get('imageinfo') or [{}])[0]; m = ii.get('extmetadata', {})
            lic = m.get('LicenseShortName', {}).get('value', '')
            if not re.search(r'\.(jpe?g|png)$', p['title'], re.I): continue
            out.append({'t': p['title'], 'w': ii.get('width'), 'h': ii.get('height'), 'lic': lic,
                        'art': re.sub('<[^>]+>', '', m.get('Artist', {}).get('value', ''))[:80],
                        'thumb': (ii.get('thumburl') or '').split('?')[0].replace('https://thumb.wikimedia.org/', 'https://upload.wikimedia.org/'),
                        'page': ii.get('descriptionurl')})
        time.sleep(20)
    json.dump(out, open(fn, 'w'), ensure_ascii=False, indent=1)
    print(fid, len(out), sum(1 for o in out if re.search(r'Public domain|CC0', o['lic'], re.I)), flush=True)
