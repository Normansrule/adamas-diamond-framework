# The ADAMAS app: desktop, installable web app, and `adamas app`

The website is the app. Three ways to run it, all built from the same `adamas.site` output, so every number matches the
package, the preprint, and the tests.

| Way | For | How |
|---|---|---|
| Desktop app | Anyone, offline | Download from the [latest release](https://github.com/Normansrule/adamas-diamond-framework/releases/latest) or the [download page](https://normansrule.github.io/adamas-diamond-framework/download.html) |
| Installable web app | Phones, Chromebooks, quick installs | Open the website, use the browser's install icon or "Add to Home Screen" |
| `adamas app` | Developers working on the code | `pip install -e ".[app]"` then `adamas app` (add `--page action.html` to open a page directly) |

## Downloads

| File | System | Notes |
|---|---|---|
| `ADAMAS-Setup-x64.exe` | Windows 10 and 11 | Per-user installer, lets you choose the folder. Not code-signed yet: SmartScreen asks once, choose **More info → Run anyway** |
| `ADAMAS-Portable-x64.exe` | Windows | Runs without installing |
| `ADAMAS-mac-arm64.dmg`, `ADAMAS-mac-x64.dmg` | macOS 12+ (Apple silicon, Intel) | Ad-hoc signed, not notarized: right-click, **Open**. If macOS says the app is damaged: `xattr -cr /Applications/ADAMAS.app` |
| `ADAMAS-linux-x86_64.AppImage` | Any Linux | `chmod +x` then run; Ubuntu 24.04 and newer need `sudo apt install libfuse2t64` |
| `ADAMAS-linux-amd64.deb` | Debian, Ubuntu | `sudo apt install ./ADAMAS-linux-amd64.deb`, then start ADAMAS from the app menu |
| `SHA256SUMS.txt` | All | `sha256sum -c SHA256SUMS.txt --ignore-missing` |

From WSL2, download the Windows installer and run it from Windows; it is a normal Windows app.

## How the desktop app is built

```
python -m adamas.site desktop/site --offline     # the website, with three.js, GSAP, Plotly, and fonts copied in
python -m adamas.icons desktop/build/icon.png    # the icon, drawn from the logo
cd desktop && npm ci && npx electron-builder      # Electron package for the current system
```

- **Offline libraries.** `--offline` copies three.js, GSAP, Plotly, and the Inter and JetBrains Mono fonts from
  `web/node_modules` (run `cd web && npm ci` once) into `vendor/` and rewrites every CDN reference, so nothing is
  fetched at run time. The one network call left is the optional release check on the download page.
- **Private scheme.** `desktop/main.js` serves the site over `app://adamas/`, a privileged standard scheme, so ES
  modules, `fetch()` of the data files, and import maps work exactly as on the web. Paths cannot escape the bundled
  folder. Pages get a strict Content-Security-Policy, run sandboxed with context isolation, and open external links in
  your browser.
- **Self-test.** `npx electron . --check` opens every page in a hidden window and fails on any script error (WebGL runs
  in software, so it works on a headless server). The `desktop` workflow runs it on every pull request that touches the
  site or the app, and before packaging every release.
- **Release.** Publishing a GitHub release triggers `.github/workflows/desktop.yml`: one job builds the offline site,
  then Windows, macOS, and Linux runners package it, and a final job uploads the installers and `SHA256SUMS.txt` to the
  release. File names are fixed, so `releases/latest/download/<file>` links always work.

Local Linux build on Ubuntu (WSL2 works too):

```bash
cd ~/projects/adamas-diamond-framework
(cd web && npm ci)
python -m adamas.site desktop/site --offline && python -m adamas.icons desktop/build/icon.png 1024
cd desktop && npm ci
xvfb-run -a npx electron . --check --no-sandbox          # every page, no script errors (sudo apt install xvfb)
npx electron-builder --linux AppImage --x64 --publish never
ls dist/                                                 # ADAMAS-linux-x86_64.AppImage
```

Windows installers need a Windows machine (or the workflow) because the installer builder runs Windows tools.

## The installable web app

Every page links `manifest.webmanifest` and registers `sw.js`, a service worker that keeps working offline after the
first visit: pages and data come from the network when you are online (so numbers stay fresh) and from the cache when
you are not; scripts, images, and the CDN libraries are served from the cache and refreshed in the background. The cache
name carries the package version, so a new release replaces the old cache.

## `adamas app`

Builds the site once into `site/` (rebuilt automatically when the package version changes, or with `--rebuild`),
serves it on `127.0.0.1` on a free port, and opens it in a native window if `pywebview` is installed, otherwise in your
browser. With `web/node_modules` present it uses the offline libraries; `--online` uses the CDNs instead.
