// Shared behavior: navigation, spotlight cards, number tickers, scroll reveals (GSAP ScrollTrigger when present,
// IntersectionObserver otherwise), reading-level toggles, copy buttons.
const BASE = document.documentElement.dataset.base || '.';
const LINKS = [['Home', 'index.html'], ['Lattice', 'labs/lattice.html'], ['Qubit', 'labs/qubit.html'], ['Heat', 'labs/heat.html'], ['Transistor', 'labs/transistor.html'], ['Power', 'labs/power.html'],
  ['Chip', 'labs/cpu.html'], ['Error correction', 'labs/qec.html'], ['Fab', 'labs/fab.html'], ['Stack', 'labs/stack.html'], ['Machine', 'labs/machine.html'], ['Globe', 'labs/globe.html'], ['Explorer', 'explorer.html']];
const LOGO = '<svg viewBox="0 0 32 32"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6ff3ff"/><stop offset="1" stop-color="#9d7bff"/></linearGradient></defs><path d="M8 4h16l6 8-14 17L2 12z" fill="url(#lg)"/><path d="M8 4l4 8 4-8 4 8 4-8M2 12h28M12 12l4 17 4-17" stroke="#05070d" stroke-width="1.2" fill="none" opacity=".5"/></svg>';

export function mountNav(active) {
  const nav = document.createElement('nav'); nav.className = 'top';
  nav.innerHTML = `<a class="brand" href="${BASE}/index.html">${LOGO}ADAMAS</a><div class="links">` +
    LINKS.map(([t, h]) => `<a href="${BASE}/${h}" class="${t === active ? 'on' : ''}">${t}</a>`).join('') +
    `<a class="gh" href="https://github.com/Normansrule/adamas-diamond-framework">★ GitHub</a></div>`;
  document.body.prepend(nav);
  const a = document.createElement('div'); a.className = 'aurora'; const g = document.createElement('div'); g.className = 'gridbg';
  document.body.prepend(g); document.body.prepend(a);
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

export function boot(active) { mountNav(active); spotlight(); levels(); copyButtons(); reveal(); }

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
