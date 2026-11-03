// Record the equation-in-the-loop panel of the Lattice Lab while the field rises, frame by frame, for the README GIF.
// Usage: node tools/record_loop.mjs <built-site-url> <frame-dir>   (needs Playwright; make loop-gif does all of it)
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base = 'http://localhost:8000', dir = '/tmp/loop-frames'] = process.argv;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader'] });
const pg = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
await pg.goto(`${base}/labs/lattice.html`, { waitUntil: 'networkidle' }); await pg.waitForSelector('#loop .eql-eq .v[data-k="B"]');
await pg.evaluate(() => { document.querySelector('#b').value = 5; document.querySelector('#b').dispatchEvent(new Event('input')); });
const panel = pg.locator('#loop'), sym = pg.locator('#loop .eql-eq .v[data-k="B"]').first();
await sym.focus(); await pg.waitForTimeout(300);
let k = 0;
for (let i = 0; i < 46; i++) { await pg.keyboard.press('ArrowUp'); await pg.waitForTimeout(70); await panel.screenshot({ path: `${dir}/f${String(k++).padStart(3, '0')}.png` }); }
await pg.evaluate(() => { const t = document.querySelector('#th'); t.value = 80; t.dispatchEvent(new Event('input')); });   // tilt the field: θ to [111] grows
for (let i = 0; i < 10; i++) { await pg.waitForTimeout(80); await panel.screenshot({ path: `${dir}/f${String(k++).padStart(3, '0')}.png` }); }
await b.close(); console.log(k, 'frames');
