/* Service Worker: hält alle Dateien für die Offline-Nutzung vor.
   VERSION und PRECACHE trägt tools/build.py beim Veröffentlichen ein. Ohne Build
   (lokale Entwicklung) bleibt die Liste leer, dann wird nur bei Bedarf zwischengespeichert. */
const VERSION = 'dev';
const PRECACHE = [];

const CACHE = 'jtac';
const NAV_TIMEOUT = 3000;
const PARALLEL = 6;

const scope = self.registration.scope;
const abs = path => new URL(path, scope).href;
const META = abs('__precache.json');
const isCore = path => !path.includes('/img/');

async function readMeta(cache) {
  const res = await cache.match(META);
  try { return res ? await res.json() : {}; } catch (e) { return {}; }
}

// Lädt nur Dateien, deren Inhalt sich seit dem letzten Stand geändert hat.
async function precache() {
  const cache = await caches.open(CACHE);
  const old = await readMeta(cache);
  const next = {};
  const queue = PRECACHE.slice();
  let coreMissing = false;
  async function worker() {
    for (let item; (item = queue.shift());) {
      const [path, hash] = item;
      const url = abs(path);
      if (old[path] === hash && await cache.match(url)) { next[path] = hash; continue; }
      try {
        const res = await fetch(url, {cache: 'no-cache'});
        if (!res.ok || res.redirected) throw new Error(res.status);
        await cache.put(url, res);
        next[path] = hash;
      } catch (e) {
        if (isCore(path)) coreMissing = true;
      }
    }
  }
  await Promise.all(Array.from({length: PARALLEL}, worker));
  await cache.put(META, new Response(JSON.stringify(next), {headers: {'content-type': 'application/json'}}));
  // Fehlen Seiten oder Skripte, Installation später wiederholen; fehlende Bilder lädt der Abruf nach.
  if (coreMissing) throw new Error('Offline-Daten unvollständig');
}

self.addEventListener('install', event => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== CACHE) await caches.delete(key);
    if (PRECACHE.length) {
      const keep = new Set(PRECACHE.map(([path]) => abs(path)).concat(META));
      const cache = await caches.open(CACHE);
      for (const req of await cache.keys()) if (!keep.has(req.url)) await cache.delete(req);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET' || !req.url.startsWith(scope)) return;
  event.respondWith(req.mode === 'navigate' ? page(req) : asset(req));
});

// Seiten: aus dem Netz, wenn es schnell antwortet – sonst der gespeicherte Stand.
async function page(req) {
  const cache = await caches.open(CACHE);
  const url = new URL(req.url);
  const key = url.origin + url.pathname.replace(/index\.html$/, '');
  let fresh;
  try { fresh = new Request(req, {cache: 'no-cache'}); } catch (e) { fresh = req; }
  const net = fetch(fresh).then(res => {
    if (res.ok && !res.redirected) cache.put(key, res.clone());
    return res;
  });
  const quick = await Promise.race([
    net.catch(() => null),
    new Promise(resolve => setTimeout(resolve, NAV_TIMEOUT, null)),
  ]);
  if (quick && quick.ok) return quick;
  const saved = await cache.match(key);
  if (saved) return saved;
  if (quick) return quick;
  try { return await net; } catch (e) { return (await cache.match(abs('./'))) || Response.error(); }
}

// Bilder, Schriften, Skripte: aus dem Speicher, sonst aus dem Netz und dann speichern.
async function asset(req) {
  const cache = await caches.open(CACHE);
  const saved = await cache.match(req, {ignoreSearch: true});
  if (saved) return saved;
  const res = await fetch(req);
  if (res.ok && res.type === 'basic') cache.put(req, res.clone());
  return res;
}

// Die Übersicht fragt den Offline-Stand ab.
self.addEventListener('message', event => {
  if (event.data !== 'status' || !event.ports[0]) return;
  event.waitUntil((async () => {
    const meta = await readMeta(await caches.open(CACHE));
    const cached = PRECACHE.filter(([path, hash]) => meta[path] === hash).length;
    event.ports[0].postMessage({version: VERSION, total: PRECACHE.length, cached});
  })());
});
