// Service Worker: macht das Spiel offline-fähig und installierbar
const CACHE = 'f1-rennen-1.47';
const APP = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './car.bin', './f2car.bin', './kart.bin', './textures/kart_body.jpg', './textures/kart_body_n.jpg', './textures/kart_wheel.jpg', './kartfahrer.bin', './textures/kart_fahrer.jpg', './textures/kart_stoff.jpg', './roadcar.bin', './menu.mp3',
  ...['asphalt_track', 'asphalt_pit_lane', 'sand_01', 'gravel_floor'].flatMap(t => ['diff', 'nor_gl'].map(m => './textures/' + t + '_' + m + '_1k.jpg')),
  ...['Grass004_Color', 'Grass004_NormalGL', 'LeafSet004_Color', 'LeafSet004_Opacity', 'LeafSet019_Color', 'LeafSet019_Opacity', 'Foliage001_Color', 'Foliage001_Opacity'].map(f => './textures/acg_' + f + '.jpg')];
const MBUSY = new Set();
const CDN = 'https://cdn.jsdelivr.net/npm/three@0.160.0/';
const LIBS = ['build/three.module.js', 'examples/jsm/postprocessing/EffectComposer.js', 'examples/jsm/postprocessing/RenderPass.js',
  'examples/jsm/postprocessing/UnrealBloomPass.js', 'examples/jsm/postprocessing/ShaderPass.js', 'examples/jsm/postprocessing/OutputPass.js',
  'examples/jsm/postprocessing/Pass.js', 'examples/jsm/postprocessing/MaskPass.js', 'examples/jsm/shaders/CopyShader.js',
  'examples/jsm/shaders/LuminosityHighPassShader.js', 'examples/jsm/shaders/OutputShader.js', 'examples/jsm/objects/Sky.js',
  'examples/jsm/postprocessing/GTAOPass.js', 'examples/jsm/shaders/GTAOShader.js', 'examples/jsm/shaders/PoissonDenoiseShader.js', 'examples/jsm/math/SimplexNoise.js'].map(p => CDN + p);

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(APP.map(u => new Request(u, { cache: 'reload' }))).then(() => Promise.all(LIBS.map(u => c.add(u).catch(() => {}))))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== 'fr-music' && k !== 'fr-logos').map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// Audio aus dem Cache: Safari/iOS fragt mit "Range" an und erwartet eine Teilantwort (206) – eine volle 200-Antwort spielt dort nicht
async function ranged(req, hit) {
  const rg = req.headers.get('range'), m = rg && /bytes=(\d*)-(\d*)/.exec(rg); if (!hit || !m || hit.status !== 200) return hit;
  const buf = await hit.clone().arrayBuffer(), n = buf.byteLength; let a = m[1] === '' ? Math.max(0, n - Number(m[2])) : Number(m[1]), b = m[1] === '' || m[2] === '' ? n - 1 : Math.min(n - 1, Number(m[2]));
  if (!(a <= b) || a >= n) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + n } });
  return new Response(buf.slice(a, b + 1), { status: 206, headers: { 'Content-Type': hit.headers.get('Content-Type') || 'audio/mpeg', 'Content-Range': 'bytes ' + a + '-' + b + '/' + n, 'Content-Length': String(b - a + 1), 'Accept-Ranges': 'bytes' } });
}
const LSEEN = new Set();   // Logos, bei denen in dieser Sitzung schon nach einer neuen Fassung gefragt wurde
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (/\/(qc|qc-reports)\//.test(new URL(req.url).pathname)) return;   // QC-Bot und seine Berichte nie zwischenspeichern
  if (new URL(req.url).hostname === 'api.github.com') { e.respondWith(fetch(req).catch(() => caches.match(req))); return; }   // Liste des Musik-Ordners immer frisch
  if (req.mode === 'navigate') { // Seite: zuerst Netz (Updates), sonst Cache
    e.respondWith(fetch(req.url, { cache: 'no-cache' }).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); } return r; })   // am Server nachfragen statt 10 Minuten alte Kopie zu nehmen
      .catch(() => caches.match('./index.html')));
    return;
  }
  if (/\/liveries\/(num\/)?[^/]+\.(png|json)$/i.test(new URL(req.url).pathname)) {   // Aufkleber (Ordner liveries/): immer zuerst am Server nachfragen – Bogen, Nummern und liveries.json gehören zusammen und müssen zum geladenen Spiel passen (ein alter Bogen zur neuen Grundfarbe zeigt ein Auto ohne Farbflächen); ohne Netz der letzte Stand
    const key = req.url.split('?')[0];
    e.respondWith(fetch(key, { cache: 'no-cache' }).then(r => { if (r.ok) { const cp = r.clone(); caches.open('fr-logos').then(c => c.put(key, cp)); } return r; }).catch(() => caches.open('fr-logos').then(c => c.match(key)).then(h => h || Response.error())));
    return;
  }
  if (/\/logos\/[^/]+\.png$/i.test(new URL(req.url).pathname)) {   // Logos (Ordner logos/): aus dem eigenen Dauer-Cache, ohne erneutes Laden. Je Sitzung fragt der Service Worker einmal im Hintergrund nach, ob sich die Datei geändert hat – neue, geänderte und gelöschte Dateien gelten ab dem nächsten Start
    const key = req.url.split('?')[0];
    e.respondWith(caches.open('fr-logos').then(c => c.match(key).then(hit => {
      if (hit && LSEEN.has(key)) return hit;
      const net = fetch(key, { cache: 'no-cache' }).then(r => { LSEEN.add(key); if (r.ok || r.status === 404) c.put(key, r.clone()); return r; });   // auch „gibt es nicht“ merken: sonst würde nach jedem fehlenden Logo neu gefragt
      if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
      return net;
    })));
    return;
  }
  if (/\/music\/[^/]+\.(mp3|ogg|m4a|aac|wav|opus)$|\/max\.mp3$/i.test(new URL(req.url).pathname)) { // Rennmusik (Ordner music/): eigener, dauerhafter Cache (bei Bedarf geladen)
    e.respondWith(caches.open('fr-music').then(c => c.match(req.url).then(hit => hit ? ranged(req, hit) : fetch(req).then(r => {
      if (!MBUSY.has(req.url)) { MBUSY.add(req.url); fetch(req.url).then(full => full.ok && full.status === 200 ? c.put(req.url, full) : 0).catch(() => {}).finally(() => MBUSY.delete(req.url)); }
      return r;
    }))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit ? (/\.mp3$/i.test(new URL(req.url).pathname) ? ranged(req, hit) : hit) : fetch(req).then(r => {
    if (r.ok && (req.url.startsWith(self.location.origin) || req.url.startsWith(CDN))) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return r;
  })));
});
