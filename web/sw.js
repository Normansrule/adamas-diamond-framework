// Service worker for the installable ADAMAS web app: works offline after the first visit.
// Pages and data: network first (you always get the newest numbers when online), cached copy when offline.
// Scripts, styles, images, and the CDN libraries (three.js, GSAP, Plotly, fonts): cache first, refreshed in the background.
const VERSION = '__ADAMAS_VERSION__';
const CACHE = `adamas-${VERSION}`;
const CORE = ['./', 'index.html', 'action.html', 'experiments.html', 'download.html', 'assets/style.css', 'assets/site.js', 'assets/action_scenes.js',
  'assets/sim/action.js', 'assets/search.js', 'assets/glossary.js', 'assets/minis.js', 'data/site.json', 'data/search.json', 'data/glossary.json', 'data/findings.json',
  'manifest.webmanifest', 'assets/icons/icon-192.png', 'assets/icons/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(CORE.map(u => c.add(u).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('adamas-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url), same = url.origin === self.location.origin;
  const page = req.mode === 'navigate' || (same && (url.pathname.endsWith('.html') || url.pathname.endsWith('.json')));
  const lib = /cdn\.jsdelivr\.net|cdn\.plot\.ly|fonts\.(googleapis|gstatic)\.com/.test(url.host);
  if (!same && !lib) return;                                            // leave GitHub API and other sites alone
  if (page) {
    e.respondWith(fetch(req).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); } return r; })
      .catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); } return r; }).catch(() => hit);
    return hit || net;
  }));
});
