const { chromium } = require('playwright'); const fs = require('fs');
// gen_sprites.js <outdir>  – Draufsicht (Tag/Wärmebild) und Seitenansicht (mit/ohne Turm) je Version
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const JOBS = [['t72','A'],['t72','B'],['t72','B3'],['t72','B3M'],['t90m',null],['btr','80'],['btr','82A'],['btr','82AT'],['bmp','1'],['bmp','1AM'],['bmp','2'],['bmp','2M'],['bmp3','3'],['brdm','BRDM'],['brdm','SA9']];
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const meta = [];
  for (const [page, hash] of JOBS) {
    const p = await b.newPage({ viewport: { width: 1000, height: 800 } });
    await p.goto(`http://localhost:8790/manoever/3d/${page}.html${hash ? '#' + hash : ''}`);
    await p.waitForFunction(() => window.__uav, null, { timeout: 60000 }); await p.waitForTimeout(1200);
    const key = `${page}-${hash || 'x'}`; const rec = { page, hash, key };
    for (const [name, o, mode] of [['top', { az: 0, el: 89.9, r: 22 }, 'orig'], ['topir', { az: 0, el: 89.9, r: 22 }, 'wbg'],
                                   ['side', { az: 90, el: 1, r: 30, w: 1200, h: 600 }, 'orig'], ['sidehull', { az: 90, el: 1, r: 30, w: 1200, h: 600, noTurret: true }, 'orig']]) {
      const r = await p.evaluate(([o, mode]) => { __uav.mode(mode); __uav.setGround('grass', 1); return __uav.sprite(o); }, [o, mode]);
      fs.writeFileSync(`${out}/${key}-${name}.png`, Buffer.from(r.url.split(',')[1], 'base64'));
      rec[name] = { center: r.center, bow: r.bow, hullLen: r.hullLen, hullW: r.hullW };
    }
    meta.push(rec); process.stdout.write(key + ' '); await p.close();
  }
  fs.writeFileSync(`${out}/sprites.json`, JSON.stringify(meta, null, 1)); console.log('\nfertig', meta.length); await b.close();
})();
