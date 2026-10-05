// Shared behavior: navigation, spotlight cards, number tickers, scroll reveals (GSAP ScrollTrigger when present,
// IntersectionObserver otherwise), reading-level toggles, copy buttons.
const BASE = document.documentElement.dataset.base || '.';
// Grouped navigation: [group, [[label, href, short description], ...]]. Labels double as boot(active) names.
export const NAV = [
  ['Learn', [['Course', 'course/index.html', 'Eight lessons with notebooks and graded checks'], ['Explorer', 'explorer.html', 'Every equation, nine live panels'],
    ['Gallery', 'gallery.html', 'All figures and animations'], ['Glossary', 'glossary.html', 'Every acronym, spelled out']]],
  ['Labs', [['Lattice', 'labs/lattice.html', 'Materials · crystal and NV center'], ['Heat', 'labs/heat.html', 'Materials · heat race'], ['Wafer', 'labs/wafer.html', 'Manufacturing · yield'],
    ['Fab', 'labs/fab.html', 'Manufacturing · process walkthrough'], ['Transistor', 'labs/transistor.html', 'Devices · I–V and ring oscillator'], ['Power', 'labs/power.html', 'Devices · EV inverter'],
    ['Chip', 'labs/cpu.html', 'Logic · program DIA-4'], ['Qubit', 'labs/qubit.html', 'Quantum · Bloch sphere'], ['Photon', 'labs/photon.html', 'Quantum · optical cycle'],
    ['Error correction', 'labs/qec.html', 'Quantum · break the code'], ['Machine', 'labs/machine.html', 'Architecture · size a computer'], ['Stack', 'labs/stack.html', 'Architecture · chip stack'],
    ['Globe', 'labs/globe.html', 'Landscape · who is building it']]],
  ['Build', [['Process', 'process.html', '19-step cleanroom traveler'], ['Experiments', 'experiments.html', 'Ten experiments, US$100 and up'], ['Data Lab', 'datalab.html', 'Fit your own measurements']]],
  ['Trust', [['Confidence', 'confidence.html', 'Validation matrix and uncertainty'], ['Preprint', 'paper/adamas.pdf', 'PDF, every number generated'],
    ['Talk', 'paper/talk.pdf', '12 slides'], ['Poster', 'paper/poster.pdf', 'A0 with QR code']]],
];
export const LINKS = [['Home', 'index.html'], ...NAV.flatMap(([, items]) => items.map(([t, h]) => [t, h]))];
const LOGO = '<svg viewBox="0 0 32 32"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6ff3ff"/><stop offset="1" stop-color="#9d7bff"/></linearGradient></defs><path d="M8 4h16l6 8-14 17L2 12z" fill="url(#lg)"/><path d="M8 4l4 8 4-8 4 8 4-8M2 12h28M12 12l4 17 4-17" stroke="#05070d" stroke-width="1.2" fill="none" opacity=".5"/></svg>';

export function mountNav(active) {
  const nav = document.createElement('nav'); nav.className = 'top'; nav.setAttribute('aria-label', 'Main');
  const group = NAV.find(([, items]) => items.some(([t]) => t === active));
  nav.innerHTML = `<a class="brand" href="${BASE}/index.html">${LOGO}ADAMAS</a>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <div class="links">` + NAV.map(([g, items]) => `<div class="dd${group && group[0] === g ? ' on' : ''}"><button class="ddb" aria-expanded="false">${g} <i>▾</i></button>
      <div class="ddm${items.length > 6 ? ' wide' : ''}">${items.map(([t, h, d]) => `<a href="${BASE}/${h}" class="${t === active ? 'on' : ''}"><b>${t === 'Chip' ? 'Diamond CPU' : t}</b><small>${d}</small></a>`).join('')}</div></div>`).join('') +
    `<button class="kbtn" id="openSearch" aria-label="Search">⌕ Search <kbd>Ctrl K</kbd></button><a class="gh" href="https://github.com/Normansrule/adamas-diamond-framework">★ GitHub</a></div>`;
  document.body.prepend(nav);
  const close = () => nav.querySelectorAll('.dd').forEach(d => { d.classList.remove('open'); d.querySelector('.ddb').setAttribute('aria-expanded', 'false'); });
  nav.querySelectorAll('.ddb').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); const d = b.parentElement, was = d.classList.contains('open'); close(); if (!was) { d.classList.add('open'); b.setAttribute('aria-expanded', 'true'); } }));
  document.addEventListener('click', close); addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  const burger = nav.querySelector('.burger'); burger.addEventListener('click', e => { e.stopPropagation(); const o = nav.classList.toggle('mobile'); burger.setAttribute('aria-expanded', String(o)); });
  nav.querySelector('#openSearch').addEventListener('click', e => { e.stopPropagation(); import('./search.js').then(m => m.open(BASE)); });
  addEventListener('keydown', e => { if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || ''))) { e.preventDefault(); import('./search.js').then(m => m.open(BASE)); } });
  const a = document.createElement('div'); a.className = 'aurora'; const g = document.createElement('div'); g.className = 'gridbg';
  document.body.prepend(g); document.body.prepend(a);
  mountFooter();
}

export function mountFooter() {
  if (document.querySelector('footer.site')) return;
  const f = document.createElement('footer'); f.className = 'site';
  f.innerHTML = `<div class="wrap fgrid">${NAV.map(([g, items]) => `<div><b>${g}</b>${items.slice(0, 7).map(([t, h]) => `<a href="${BASE}/${h}">${t === 'Chip' ? 'Diamond CPU' : t}</a>`).join('')}</div>`).join('')}
    <div><b>Project</b><a href="https://github.com/Normansrule/adamas-diamond-framework">Source on GitHub</a><a href="https://github.com/Normansrule/adamas-diamond-framework/blob/main/CHANGELOG.md">Changelog</a>
    <a href="https://github.com/Normansrule/adamas-diamond-framework/blob/main/CITATION.cff">Cite this work</a><a href="https://github.com/Normansrule/adamas-diamond-framework/blob/main/references/REFERENCES.md">All references</a></div></div>
    <div class="wrap fnote">ADAMAS · MIT License · open research framework for diamond electronics and room-temperature quantum processors · every number is computed by the Python package and tested · press <kbd>Ctrl K</kbd> to search</div>`;
  document.body.appendChild(f);
}

export function spotlight() {
  document.addEventListener('pointermove', e => {
    for (const c of document.querySelectorAll('.card')) {
      const r = c.getBoundingClientRect(); c.style.setProperty('--mx', `${e.clientX - r.left}px`); c.style.setProperty('--my', `${e.clientY - r.top}px`);
    }
  });
}

export function ticker(el, to, { dur = 1600, fmt = x => Math.round(x).toLocaleString() } = {}) {
  const t0 = performance.now();
  const f = t => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 4); el.textContent = fmt(to * e); if (k < 1) requestAnimationFrame(f); };
  requestAnimationFrame(f);
}

export function reveal() {
  const els = [...document.querySelectorAll('.reveal')];
  if (window.gsap && window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);
    els.forEach(el => gsap.to(el, { opacity: 1, y: 0, duration: .9, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 85%' } }));
    return;
  }
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.style.transition = 'all .9s cubic-bezier(.2,.8,.2,1)'; e.target.style.opacity = 1; e.target.style.transform = 'none'; io.unobserve(e.target); } }), { threshold: .15 });
  els.forEach(el => io.observe(el));
}

export function onVisible(el, fn) {
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { fn(); io.disconnect(); } }), { threshold: .3 }); io.observe(el);
}

export function levels(root = document) {
  root.querySelectorAll('.levels').forEach(g => {
    const box = g.parentElement;
    g.querySelectorAll('button').forEach(b => b.onclick = () => {
      g.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
      box.querySelectorAll('.lvl').forEach(l => l.classList.toggle('on', l.dataset.l === b.dataset.l));
    });
    g.querySelector('button').click();
  });
}

export function copyButtons() {
  document.querySelectorAll('[data-copy]').forEach(b => b.onclick = async () => {
    const txt = document.getElementById(b.dataset.copy).innerText.replace(/^\$ /gm, '');
    try { await navigator.clipboard.writeText(txt); b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1400); } catch { b.textContent = 'Select and copy'; }
  });
}

export async function data(name = 'site.json') { const r = await fetch(`${BASE}/data/${name}`); return r.json(); }

export function scrollProgress() {
  const bar = document.createElement('div'); bar.className = 'scrollbar'; document.body.appendChild(bar);
  const f = () => { const h = document.documentElement, p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight); bar.style.transform = `scaleX(${p})`; };
  addEventListener('scroll', f, { passive: true }); f();
}

export function boot(active) { mountNav(active); spotlight(); levels(); copyButtons(); reveal(); scrollProgress(); document.body.classList.add('ready');
  import('./glossary.js').then(m => { m.glossary(BASE); setTimeout(() => m.glossary(BASE), 1200); }).catch(() => {}); }

// small canvas helpers shared by labs
export function fitCanvas(c, h) {
  const dpr = Math.min(2, window.devicePixelRatio || 1), w = c.clientWidth; c.width = w * dpr; c.height = (h || c.clientHeight) * dpr;
  const g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); return { g, w, h: h || c.clientHeight };
}
export function colormap(t) {          // 0..1 -> "inferno-like" rgb
  const s = [[0, 0, 4], [40, 11, 84], [101, 21, 110], [159, 42, 99], [212, 72, 66], [245, 125, 21], [250, 193, 39], [252, 255, 164]];
  const x = Math.max(0, Math.min(.9999, t)) * (s.length - 1), i = Math.floor(x), f = x - i, a = s[i], b = s[i + 1];
  return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
}
