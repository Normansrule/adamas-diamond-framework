// ADAMAS desktop: the website, bundled with its libraries, served from inside the app over a private app:// scheme
// (so ES modules, fetch of data/*.json, and the import map behave exactly as on the web), in a sandboxed window.
const { app, BrowserWindow, Menu, protocol, shell } = require('electron');
const path = require('node:path');
const fs = require('node:fs');

const SITE = path.join(__dirname, 'site');
const HOME = 'app://adamas/index.html';
const REPO = 'https://github.com/Normansrule/adamas-diamond-framework';
// Pages may only load code from inside the app; the one network call is the release check on the download page.
const CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; " +
  "connect-src 'self' https://api.github.com; worker-src 'self' blob:; frame-src 'none'; object-src 'none'; base-uri 'self'";
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.woff': 'font/woff', '.pdf': 'application/pdf',
  '.csv': 'text/csv', '.txt': 'text/plain', '.mp4': 'video/mp4', '.webmanifest': 'application/manifest+json', '.ipynb': 'application/json', '.wasm': 'application/wasm' };

protocol.registerSchemesAsPrivileged([{ scheme: 'app', privileges: { standard: true, secure: true, supportFetchAPI: true, corsEnabled: true, stream: true } }]);

function resolve(url) {                     // app://adamas/<path> -> file inside SITE, refusing anything that escapes it
  const u = new URL(url); let rel = decodeURIComponent(u.pathname);
  if (rel.endsWith('/')) rel += 'index.html';
  const file = path.normalize(path.join(SITE, rel));
  return file.startsWith(SITE + path.sep) || file === SITE ? file : null;
}

function serve() {
  protocol.handle('app', async req => {
    const file = resolve(req.url);
    if (!file) return new Response('Forbidden', { status: 403 });
    try {
      const body = await fs.promises.readFile(file);
      const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream', headers = { 'content-type': type, 'cache-control': 'no-cache' };
      if (type === 'text/html') headers['content-security-policy'] = CSP;
      return new Response(body, { status: 200, headers });
    } catch { return new Response('Not found', { status: 404 }); }
  });
}

function external(url) { return /^https?:/i.test(url) ? (shell.openExternal(url), true) : false; }

function createWindow(page = HOME) {
  const win = new BrowserWindow({
    width: 1440, height: 920, minWidth: 900, minHeight: 600, backgroundColor: '#05070d', title: 'ADAMAS', show: false, autoHideMenuBar: true,
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, sandbox: true, nodeIntegration: false, spellcheck: false,
      additionalArguments: [`--adamas-version=${app.getVersion()}`] },
  });
  win.once('ready-to-show', () => win.show());
  win.webContents.setWindowOpenHandler(({ url }) => { if (url.startsWith('app://')) { createWindow(url); return { action: 'deny' }; } external(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (!url.startsWith('app://')) { e.preventDefault(); external(url); } });
  win.loadURL(page);
  return win;
}

function menu() {
  const go = (label, p, accel) => ({ label, accelerator: accel, click: (_, w) => (w || BrowserWindow.getFocusedWindow() || createWindow()).loadURL(`app://adamas/${p}`) });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' }] : []),
    { label: 'File', submenu: [{ label: 'New window', accelerator: 'CmdOrCtrl+N', click: () => createWindow() }, { type: 'separator' }, process.platform === 'darwin' ? { role: 'close' } : { role: 'quit' }] },
    { label: 'Go', submenu: [go('Home', 'index.html', 'CmdOrCtrl+H'), go('Equations in Action', 'action.html', 'CmdOrCtrl+E'), go('Experiments', 'experiments.html', 'CmdOrCtrl+X'),
      go('Process traveler', 'process.html'), go('Course', 'course/index.html', 'CmdOrCtrl+L'), go('Explorer', 'explorer.html'), go('Gallery', 'gallery.html'), go('Glossary', 'glossary.html'),
      { type: 'separator' }, go('Qubit Lab', 'labs/qubit.html'), go('Lattice Lab', 'labs/lattice.html'), go('Heat Race', 'labs/heat.html'), go('Machine Builder', 'labs/machine.html'), go('Break the Code', 'labs/qec.html'),
      { type: 'separator' }, { label: 'Back', accelerator: 'Alt+Left', click: (_, w) => w && w.webContents.navigationHistory.canGoBack() && w.webContents.navigationHistory.goBack() },
      { label: 'Forward', accelerator: 'Alt+Right', click: (_, w) => w && w.webContents.navigationHistory.canGoForward() && w.webContents.navigationHistory.goForward() }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'toggleDevTools' }, { type: 'separator' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { type: 'separator' }, { role: 'togglefullscreen' }] },
    { label: 'Help', submenu: [{ label: 'Website', click: () => shell.openExternal('https://normansrule.github.io/adamas-diamond-framework/') },
      { label: 'Source code and releases', click: () => shell.openExternal(REPO) }, { label: 'Report a problem', click: () => shell.openExternal(`${REPO}/issues/new`) },
      { label: `About ADAMAS ${app.getVersion()}`, click: () => shell.openExternal(`${REPO}/blob/main/CHANGELOG.md`) }] },
  ]));
}

if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => { const w = BrowserWindow.getAllWindows()[0]; if (w) { if (w.isMinimized()) w.restore(); w.focus(); } });
  app.whenReady().then(() => {
    serve(); menu(); if (process.argv.includes('--check')) return;
    createWindow(process.env.ADAMAS_PAGE ? `app://adamas/${process.env.ADAMAS_PAGE}` : HOME);
    app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
  });
  app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
}

// Self-test used by CI and `npm run check`: open every page in a hidden window, fail on any script error.
async function check() {
  const pages = [];
  const walk = d => { for (const f of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, f.name); if (f.isDirectory()) { if (f.name !== 'vendor') walk(p); } else if (f.name.endsWith('.html')) pages.push(path.relative(SITE, p).split(path.sep).join('/')); } };
  walk(SITE);
  const win = new BrowserWindow({ show: false, width: 1400, height: 900, webPreferences: { preload: path.join(__dirname, 'preload.js'), sandbox: true, contextIsolation: true, additionalArguments: [`--adamas-version=${app.getVersion()}`] } });
  const errors = []; let page = '';
  win.webContents.on('console-message', e => { const lvl = e.level, msg = e.message || ''; if ((lvl === 'error' || lvl === 3) && !/fonts\.g|ERR_INTERNET|api\.github/.test(msg)) errors.push(`${page}: ${msg}`); });
  win.webContents.on('render-process-gone', (_, d) => errors.push(`${page}: renderer gone ${d.reason}`));
  for (page of pages) {
    await win.loadURL(`app://adamas/${page}`).catch(e => errors.push(`${page}: ${e.message}`));
    await new Promise(r => setTimeout(r, 900));
    const bad = await win.webContents.executeJavaScript('document.body ? document.body.innerText.length : 0').catch(() => 0);
    if (!bad) errors.push(`${page}: empty page`);
  }
  if (process.argv.includes('--shots')) for (const p of ['index.html', 'action.html', 'experiments.html', 'download.html']) {
    await win.loadURL(`app://adamas/${p}`); await new Promise(r => setTimeout(r, 2500));
    const dir = path.join(process.cwd(), 'dist'); fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, `shot-${p.replace('.html', '')}.png`), (await win.webContents.capturePage()).toPNG());
  }
  console.log(JSON.stringify({ pages: pages.length, errors: [...new Set(errors)].slice(0, 40) }, null, 1));
  app.exit(errors.length ? 1 : 0);
}
if (process.argv.includes('--check')) for (const [k, v] of [['use-gl', 'angle'], ['use-angle', 'swiftshader'], ['enable-unsafe-swiftshader', '']]) app.commandLine.appendSwitch(k, v);  // software WebGL on headless CI
if (process.argv.includes('--check')) app.whenReady().then(check).catch(e => { console.error(e); app.exit(2); });
