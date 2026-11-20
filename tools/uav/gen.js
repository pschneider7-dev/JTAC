const { chromium } = require('playwright'); const fs = require('fs');
// gen.js <config.json> <outdir>
const [cfgPath, out] = process.argv.slice(2); const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const res = [];
  for (const job of cfg) {
    const p = await b.newPage({ viewport: { width: 1000, height: 800 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(`http://localhost:8790/manoever/3d/${job.page}.html${job.hash ? '#' + job.hash : ''}`);
    await p.waitForFunction(() => window.__uav, null, { timeout: 60000 }); await p.waitForTimeout(1200);
    for (const s of job.shots) {
      const r = await p.evaluate(s => { __uav.mode(s.ir ? 'wbg' : 'orig'); __uav.setGround(s.ir ? 'therm' : s.ground, s.seed); return __uav.shot(s); }, s);
      const fn = `${out}/${s.name}.png`; fs.writeFileSync(fn, Buffer.from(r.url.split(',')[1], 'base64'));
      res.push({ ...s, page: job.page, hash: job.hash, fam: job.fam, v: job.v, file: fn, pins: r.pins });
      process.stdout.write(s.name + ' ');
    }
    if (errs.length) console.log('\nFehler', job.page, errs.slice(0, 2));
    await p.close();
  }
  fs.writeFileSync(`${out}/shots.json`, JSON.stringify(res));
  console.log('\nfertig', res.length);
  await b.close();
})();
