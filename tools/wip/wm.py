"""Wikimedia-Helfer: search <query...> | info <titles-file> | get <info.json> <idx...>"""
import json, sys, subprocess, time, re, urllib.parse
UA = 'JTACTrainer/1.0 (https://github.com/pschneider7-dev/JTAC)'
API = 'https://commons.wikimedia.org/w/api.php'
def api(params):
    data = urllib.parse.urlencode({**params, 'format': 'json'})
    for att in range(12):
        r = subprocess.run(['curl', '-sS', '-m', '40', '-A', UA, '-d', data, API], capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: print('wait', att, flush=True); time.sleep(60)
    raise SystemExit('API failed')
cmd = sys.argv[1]
if cmd == 'search':
    seen = []
    for q in sys.argv[2:]:
        d = api({'action': 'query', 'list': 'search', 'srsearch': q, 'srnamespace': 6, 'srlimit': 40})
        for x in d['query']['search']:
            if x['title'] not in seen and re.search(r'\.(jpe?g|png|webp)$', x['title'], re.I): seen.append(x['title'])
        time.sleep(1)
    print('\n'.join(seen))
elif cmd == 'info':
    titles = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    out = []
    for k in range(0, len(titles), 50):
        d = api({'action': 'query', 'titles': '|'.join(titles[k:k+50]), 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'iiurlwidth': 960})
        for p in d['query']['pages'].values():
            if 'imageinfo' not in p: continue
            ii = p['imageinfo'][0]; m = ii.get('extmetadata', {})
            g = lambda key: re.sub('<[^>]+>', '', m.get(key, {}).get('value', '') or '').strip()
            out.append({'t': p['title'], 'w': ii['width'], 'h': ii['height'], 'lic': g('LicenseShortName'), 'art': g('Artist')[:80],
                        'thumb': ii.get('thumburl', '').split('?')[0].replace('https://thumb.wikimedia.org/', 'https://upload.wikimedia.org/'),
                        'page': ii.get('descriptionurl')})
        time.sleep(1.5)
    json.dump(out, open(sys.argv[3], 'w'), ensure_ascii=False, indent=1)
    for n, o in enumerate(out): print(n, o['lic'][:16].ljust(16), ('%dx%d' % (o['w'], o['h'])).ljust(10), o['art'][:24].ljust(24), o['t'][5:90])
elif cmd == 'get':
    from PIL import Image
    info = json.load(open(sys.argv[2])); prefix = sys.argv[3]
    def ok(fn):
        try: Image.open(fn).verify(); return True
        except Exception: return False
    for n in map(int, sys.argv[4:]):
        fn = '%s-%02d.jpg' % (prefix, n)
        if ok(fn) if __import__('os').path.exists(fn) else False: continue
        for att in range(6):
            r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '-w', '%{http_code}', '-A', UA, '-o', fn, info[n]['thumb']], capture_output=True, text=True)
            if r.stdout == '200' and ok(fn): break
            time.sleep(30 * (att + 1))
        print(n, r.stdout, flush=True)
        time.sleep(12)
