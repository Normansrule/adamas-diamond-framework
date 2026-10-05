// Headless smoke test: load each built page in jsdom (stubbed canvas and WebGL), run its module script, click controls,
// and fail on any uncaught error. Usage: node tests/smoke.mjs <site_dir> <page> [id*n,id,...]   (see tests/smoke_all.mjs)
import { JSDOM } from 'jsdom';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import os from 'node:os';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const [,, siteDir, page, actions] = process.argv;
const file = path.join(siteDir, page), html = fs.readFileSync(file, 'utf8');
const dom = new JSDOM(html, { url: `http://localhost/${page}`, pretendToBeVisual: true });
const W = dom.window;
const ctx = new Proxy({}, { get: (t, k) => k === 'createImageData' ? (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }) :
  k === 'createLinearGradient' || k === 'createRadialGradient' ? () => ({ addColorStop() {} }) : k in t ? t[k] : () => {}, set: (t, k, v) => (t[k] = v, true) });
W.HTMLCanvasElement.prototype.getContext = () => ctx;
Object.defineProperty(W.HTMLElement.prototype, 'clientWidth', { get: () => 800 });
Object.defineProperty(W.HTMLElement.prototype, 'clientHeight', { get: () => 420 });
W.URL.createObjectURL = () => 'blob:x'; W.HTMLAnchorElement.prototype.click = function () {};
W.IntersectionObserver = class { constructor(cb) { this.cb = cb; } observe(el) { this.cb([{ isIntersecting: true, target: el }]); } unobserve() {} disconnect() {} };
let frames = 0; W.requestAnimationFrame = cb => (frames++ < 40 ? setTimeout(() => cb(performance.now()), 1) : 0);
for (const k of ['window', 'document', 'navigator', 'HTMLElement', 'IntersectionObserver', 'requestAnimationFrame', 'getComputedStyle', 'NodeFilter'])
  Object.defineProperty(globalThis, k, { value: k === 'window' ? W : W[k], configurable: true, writable: true });
globalThis.addEventListener = W.addEventListener.bind(W); globalThis.devicePixelRatio = 1; W.SVGElement.prototype.getTotalLength = () => 1000;
globalThis.fetch = async u => { const p = path.join(siteDir, page.includes('/') ? 'labs' : '', u); return { json: async () => JSON.parse(fs.readFileSync(p, 'utf8')) }; };
const errors = []; process.on('unhandledRejection', e => errors.push(String(e && e.stack || e)));
const src = [...html.matchAll(/<script type="module">([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n')
  .replace(/from '(\.\.\/|\.\/)assets\/([^']+)'/g, (_, d, f) => `from '${pathToFileURL(path.join(siteDir, 'assets', f)).href}'`)
  .replace(/import\('(\.\.\/|\.\/)assets\/([^']+)'\)/g, (_, d, f) => `import('${pathToFileURL(path.join(siteDir, 'assets', f)).href}')`)
  .replace(/import\('three'\)/g, `import('${pathToFileURL(path.join(HERE, 'three-stub.mjs')).href}')`)
  .replace(/import\('three\/addons\/([^']+)'\)/g, (_, f) => `import('${pathToFileURL(path.join(HERE, '..', 'node_modules', 'three', 'examples', 'jsm', f)).href}')`);
const tmp = path.join(os.tmpdir(), 'adamas_' + page.replace(/\W/g, '_') + '.mjs'); fs.writeFileSync(tmp, src);
try { await import(pathToFileURL(tmp).href); } catch (e) { errors.push(String(e.stack || e)); }
await new Promise(r => setTimeout(r, 200));
const $ = id => W.document.getElementById(id);
const extra = {};
for (const a of (actions || '').split(',').filter(Boolean)) {
  if (a === 'xzzx') { W.document.querySelector('#model button[data-x="xzzx_biased"]')?.click(); continue; }
  if (a === 'search') { W.document.getElementById('openSearch').click(); await new Promise(r => setTimeout(r, 200)); const q = W.document.getElementById('pq'); q.value = 'xzzx'; q.dispatchEvent(new W.Event('input')); await new Promise(r => setTimeout(r, 50)); extra.palette = W.document.getElementById('pres').textContent.slice(0, 160); continue; }
  if (a === 'loadex') { const k = W.document.getElementById('kind'); const f = path.join(siteDir, 'data', 'examples', 'rabi.csv'); W.document.getElementById('paste').value = fs.readFileSync(f, 'utf8'); k.value = 'rabi'; W.document.getElementById('go').click(); continue; }
  if (a === 'step1') { W.document.querySelector('#steps li')?.click(); continue; }
  if (a === 'tierC') { W.document.querySelector('#tiers button[data-t="C"]')?.click(); continue; }
  if (a === 'quizall') { W.document.querySelectorAll('[data-q] button[data-k="1"]').forEach(b => b.click()); continue; } const [id, n] = a.split('*'); for (let i = 0; i < (+n || 1); i++) $(id).click(); await new Promise(r => setTimeout(r, 60)); }
await new Promise(r => setTimeout(r, 300));
if (errors.length) { console.error(JSON.stringify({ page, errors })); process.exit(1); }
console.log(JSON.stringify({ page, errors, gl: W.document.querySelectorAll('abbr.gl').length, probe: Object.assign(Object.fromEntries(['evpi', 'fcards', 'vsum', 'kpis', 'notes', 'plotNote', 'xsHud', 'prog', 'kC', 'kN', 'score', 'progress', 'chipHud', 'kpis', 'barHud', 'kNM', 'kP', 'kT', 'hud', 'n0', 'refHead', 'kRatio', 'kTime', 'verdict', 'regs', 'dTitle', 'stepHud', 'chipHud', 'err', 'mcHud'].filter(i => $(i)).map(i => [i, $(i).textContent.slice(0, 140)])), extra) }));
process.exit(0);
