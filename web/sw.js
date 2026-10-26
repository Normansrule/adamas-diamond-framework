// Service worker for the installable ADAMAS web app: works offline after the first visit.
// Everything from this site (pages, scripts, styles, data, images): network first, cached copy when offline, so a
// deploy never mixes new pages with old scripts. Version-pinned CDN libraries (three.js, GSAP, Plotly, fonts): cache first.
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
  const lib = /cdn\.jsdelivr\.net|cdn\.plot\.ly|fonts\.(googleapis|gstatic)\.com/.test(url.host);
  if (!same && !lib) return;                                            // leave GitHub API and other sites alone
  if (same) {   // everything from this site: network first, so HTML, scripts and data always match after a deploy
    e.respondWith(fetch(req).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); } return r; })
      .catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || (req.mode === 'navigate' ? caches.match('index.html') : Response.error()))));
    return;
  }
  // CDN libraries have version-pinned URLs, so a cached copy never goes stale: cache first
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(k => k.put(req, c)); } return r; })));
});
