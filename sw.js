// Service Worker: macht das Spiel offline-fähig und installierbar
const CACHE = 'f1-rennen-v28';
const APP = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './car.bin', './roadcar.bin', './menu.mp3'];
const MBUSY = new Set();
const CDN = 'https://cdn.jsdelivr.net/npm/three@0.160.0/';
const LIBS = ['build/three.module.js', 'examples/jsm/postprocessing/EffectComposer.js', 'examples/jsm/postprocessing/RenderPass.js',
  'examples/jsm/postprocessing/UnrealBloomPass.js', 'examples/jsm/postprocessing/ShaderPass.js', 'examples/jsm/postprocessing/OutputPass.js',
  'examples/jsm/postprocessing/Pass.js', 'examples/jsm/postprocessing/MaskPass.js', 'examples/jsm/shaders/CopyShader.js',
  'examples/jsm/shaders/LuminosityHighPassShader.js', 'examples/jsm/shaders/OutputShader.js', 'examples/jsm/objects/Sky.js',
  'examples/jsm/postprocessing/GTAOPass.js', 'examples/jsm/shaders/GTAOShader.js', 'examples/jsm/shaders/PoissonDenoiseShader.js', 'examples/jsm/math/SimplexNoise.js'].map(p => CDN + p);

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(APP).then(() => Promise.all(LIBS.map(u => c.add(u).catch(() => {}))))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== 'fr-music').map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (req.mode === 'navigate') { // Seite: zuerst Netz (Updates), sonst Cache
    e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  if (/\/(all-night|back-to-life|headphonk|blast|okay-energy|glorious|max)\.mp3$/i.test(new URL(req.url).pathname)) { // Rennmusik: eigener, dauerhafter Cache (bei Bedarf geladen)
    e.respondWith(caches.open('fr-music').then(c => c.match(req.url).then(hit => hit || fetch(req).then(r => {
      if (!MBUSY.has(req.url)) { MBUSY.add(req.url); fetch(req.url).then(full => full.ok && full.status === 200 ? c.put(req.url, full) : 0).catch(() => {}).finally(() => MBUSY.delete(req.url)); }
      return r;
    }))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r.ok && (req.url.startsWith(self.location.origin) || req.url.startsWith(CDN))) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return r;
  })));
});
