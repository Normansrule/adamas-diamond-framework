// Equation in the loop: a live panel that shows the equation governing a lab, with every symbol clickable, the numbers
// substituted as the lab runs, unit and assumption checks that turn amber when the state leaves the equation's validity
// range, and an inspector with the local sensitivity and the output plotted against the selected symbol.
// Metadata comes from adamas.loop (data/site.json, key "loops"); arithmetic from loop_models.js (golden-tested).
import { MODELS } from './loop_models.js';

const fmt = (x, d = 3) => {
  if (!Number.isFinite(x)) return x > 0 ? '∞' : '–';
  const a = Math.abs(x); if (a < 1e-12) return (0).toFixed(d);
  if (a !== 0 && (a >= 1e5 || a < 1e-3)) { const e = Math.floor(Math.log10(a)); return `${(x / 10 ** e).toFixed(2)}×10${sup(e)}`; }
  return x.toFixed(d);
};
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
const sup = e => String(e).split('').map(c => SUP[c] ?? c).join('');
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const HUES = ['gold', 'teal', 'green', 'violet', 'red'];
const sym = t => esc(t).replace(/_([A-Za-z0-9]+|\{[^}]+\})/g, (_, x) => `<sub>${x.replace(/[{}]/g, '')}</sub>`);   // R_on -> R<sub>on</sub>

export function mountLoop(host, meta, opts = {}) {
  const model = MODELS[opts.id || meta.id];
  if (!model) throw new Error(`no model for panel ${opts.id || meta.id}`);
  const keys = Object.keys(meta.vars), hue = Object.fromEntries(keys.map((k, i) => [k, HUES[i % HUES.length]]));
  const S = { ...model.defaults, ...(opts.state || {}) };
  let sel = opts.select || keys.find(k => !meta.vars[k].derived) || keys[0], pending = false, lastSpoken = 0, rendered = false;
  host.classList.add('eql');
  host.innerHTML = `
    <div class="eql-h"><h2>In the loop</h2><span class="eql-title">${esc(meta.title)}</span><span class="eql-state" data-state="live">live</span></div>
    <div class="eql-eq" role="group" aria-label="Governing equation; select a symbol to inspect it">${meta.html}</div>
    <div class="eql-sub" aria-hidden="true"></div>
    <div class="eql-res"><span class="eql-rs">${sym(meta.result.sym)}</span><span class="eql-eqs">=</span><b class="eql-rv"></b><span class="eql-ru">${esc(meta.result.unit || '')}</span><small>${esc(meta.result.name)}</small></div>
    <ul class="eql-chips" aria-label="Units and assumptions"></ul>
    ${opts.controls?.length ? '<div class="eql-ctl"></div>' : ''}
    <div class="eql-insp"></div>
    <p class="eql-src">Reference implementation <code>${esc(meta.python)}</code>, tested against this panel. Derivation: <a href="https://github.com/Normansrule/adamas-diamond-framework/blob/main/${esc(meta.derivation[1])}" target="_blank" rel="noopener">${esc(meta.derivation[0])}</a> · ${meta.refs.map(r => `[${esc(r)}]`).join(' ')}</p>
    <p class="sr-only" aria-live="polite" data-k="speak"></p>`;
  const q = s => host.querySelector(s), eqEl = q('.eql-eq');
  // symbols: colour by variable, keyboard nudging, selection
  eqEl.querySelectorAll('.v').forEach(b => {
    const k = b.dataset.k, v = meta.vars[k]; if (!v) return;
    b.dataset.hue = hue[k]; b.setAttribute('aria-label', `${v.name}${v.unit ? `, ${v.unit}` : ''}: inspect${v.derived ? '' : '; arrow keys change it'}`);
    b.onclick = () => select(k);
    b.onkeydown = e => { if (v.derived || !['ArrowUp', 'ArrowDown', 'ArrowRight', 'ArrowLeft'].includes(e.key)) return; e.preventDefault();
      const up = e.key === 'ArrowUp' || e.key === 'ArrowRight', st = v.step ?? (v.log ? 10 ** (Math.log10(v.max / v.min) / 50) : (v.max - v.min) / 50);
      const nv = v.log && !v.step ? S[k] * (up ? st : 1 / st) : S[k] + (up ? st : -st); set({ [k]: Math.min(v.max, Math.max(v.min, nv)) }, true); select(k); };
  });
  // optional sliders for the variables the lab does not own
  const ctl = q('.eql-ctl');
  if (ctl) {
    ctl.innerHTML = opts.controls.map(k => { const v = meta.vars[k], lg = !!v.log, val = lg ? Math.log10(S[k]) : S[k];
      return `<label class="eql-c" data-hue="${hue[k]}"><span class="eql-cs">${sym(v.sym)}</span><input type="range" data-k="${k}" min="${lg ? Math.log10(v.min) : v.min}" max="${lg ? Math.log10(v.max) : v.max}" step="${v.step ?? (lg ? 0.01 : (v.max - v.min) / 400)}" value="${val}" aria-label="${esc(v.name)}"><output></output></label>`; }).join('');
    ctl.querySelectorAll('input').forEach(i => i.oninput = () => { const k = i.dataset.k, v = meta.vars[k]; set({ [k]: v.log ? 10 ** +i.value : +i.value }, true); select(k); });
  }
  function derived() { return model.derive ? model.derive(S) : {}; }
  function value(st = S) { return model.f(st); }
  function sens(k) {
    const v = meta.vars[k]; if (v.derived) return null;
    const x = S[k], h = v.log ? x * 1e-3 : Math.max(1e-6, (v.max - v.min) * 1e-4), a = value({ ...S, [k]: x - h }), b = value({ ...S, [k]: x + h });
    const d = (b - a) / (2 * h), out = v.log ? d * x * Math.LN10 : d; return Math.abs(out) < 1e-9 ? 0 : out;     // log variables: change per decade
  }
  function chips() {
    const u = meta.units.map(t => `<li class="eql-chip ok"><i aria-hidden="true"></i><b class="eql-st">units</b>${esc(t)}</li>`);
    // state is spelled out in words (holds, outside, assumed), not carried by colour alone (WCAG 1.4.1)
    const a = meta.assumptions.map(as => { const r = model.checks[as.id](S), st = r.assumed ? 'assumed' : r.ok ? 'ok' : 'warn', word = r.assumed ? 'assumed' : r.ok ? 'holds' : 'outside';
      return `<li class="eql-chip ${st}"><i aria-hidden="true"></i><b class="eql-st">${word}</b>${esc(as.text)}${r.note ? `<span>${esc(r.note)}</span>` : ''}</li>`; });
    q('.eql-chips').innerHTML = u.concat(a).join('');
  }
  function inspector() {
    const v = meta.vars[sel], d = derived(), labSet = v.derived && !(sel in d), x = v.derived && !labSet ? d[sel] : S[sel], s = sens(sel);
    q('.eql-insp').innerHTML = `<div class="eql-ib"><b data-hue="${hue[sel]}">${sym(v.sym)}</b><span>${fmt(x, v.digits ?? 3)} ${esc(v.unit || '')}</span></div><dl>
      <dt>Quantity</dt><dd>${esc(v.name)}</dd>
      ${v.derived ? `<dt>Status</dt><dd>${labSet ? 'set by the lab from its own controls; not adjustable here' : 'computed from the other symbols'}</dd>` : `<dt>Range</dt><dd>${fmt(v.min, v.digits ?? 2)} to ${fmt(v.max, v.digits ?? 2)} ${esc(v.unit || '')}</dd>
      <dt>${v.log ? `∂${sym(meta.result.sym)} per decade of ${sym(v.sym)}` : `∂${sym(meta.result.sym)}/∂${sym(v.sym)}`}</dt><dd>${fmt(s, 4)}${v.log || !v.unit ? '' : ` per ${esc(v.unit)}`}</dd>`}
      <dt>Where it comes from</dt><dd class="eql-why">${esc(v.src)}</dd></dl>${v.derived ? '' : `<canvas class="eql-spark" aria-label="${esc(meta.result.sym)} against ${esc(v.name)}" role="img"></canvas>`}`;
    if (!v.derived) spark();
  }
  function spark() {
    const c = q('.eql-spark'); if (!c) return; const dpr = Math.min(2, devicePixelRatio || 1), w = c.clientWidth || 300, h = c.clientHeight || 80;
    c.width = w * dpr; c.height = h * dpr; const g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const css = getComputedStyle(host), col = name => css.getPropertyValue(name).trim() || '#9ab';
    const v = meta.vars[sel], N = model.sweepSamples || 120, lo = v.log ? Math.log10(v.min) : v.min, hi = v.log ? Math.log10(v.max) : v.max;
    const xs = [...Array(N)].map((_, i) => lo + (hi - lo) * i / (N - 1)), ys = xs.map(u => value({ ...S, [sel]: v.log ? 10 ** u : u }));
    const fin = ys.filter(Number.isFinite), ymin = Math.min(...fin), ymax = Math.max(...fin), span = ymax - ymin || 1;
    const X = u => 6 + (w - 12) * (u - lo) / (hi - lo), Y = y => h - 14 - (h - 24) * (y - ymin) / span;
    g.strokeStyle = col('--line'); g.lineWidth = 1; g.beginPath(); g.moveTo(6, h - 14); g.lineTo(w - 6, h - 14); g.stroke();
    g.strokeStyle = col(`--${hue[sel]}`); g.lineWidth = 1.8; g.beginPath(); let started = false;
    xs.forEach((u, i) => { if (!Number.isFinite(ys[i])) { started = false; return; } started ? g.lineTo(X(u), Y(ys[i])) : g.moveTo(X(u), Y(ys[i])); started = true; }); g.stroke();
    const cu = v.log ? Math.log10(S[sel]) : S[sel], cy = value(S);
    g.fillStyle = col('--ink'); g.beginPath(); g.arc(X(cu), Y(cy), 3.5, 0, 7); g.fill();
    g.fillStyle = col('--mute'); g.font = '11px "JetBrains Mono", monospace'; g.textAlign = 'left'; g.fillText(`${fmt(v.min, 2)}`, 6, h - 2); g.textAlign = 'right'; g.fillText(`${fmt(v.max, 2)} ${v.unit || ''}`, w - 6, h - 2);
    g.textAlign = 'right'; g.fillText(`${meta.result.sym} ${fmt(ymax, 3)}`, w - 6, 10);
  }
  function render() {
    pending = false; const y = value();
    q('.eql-sub').innerHTML = model.sub(S);
    q('.eql-rv').textContent = fmt(y, meta.result.digits ?? 3);
    eqEl.querySelectorAll('.v').forEach(b => { const on = b.dataset.k === sel; b.classList.toggle('sel', on); b.setAttribute('aria-pressed', String(on)); });
    if (ctl) ctl.querySelectorAll('input').forEach(i => { const k = i.dataset.k, v = meta.vars[k]; if (document.activeElement !== i) i.value = v.log ? Math.log10(S[k]) : S[k]; i.setAttribute('aria-valuetext', `${fmt(S[k], v.digits ?? 2)} ${v.unit || ''}`); i.nextElementSibling.textContent = `${fmt(S[k], v.digits ?? 2)} ${v.unit || ''}`; });
    chips(); inspector();
    if (rendered) { clearTimeout(lastSpoken); lastSpoken = setTimeout(() => { q('[data-k="speak"]').textContent = `${meta.result.name}: ${meta.result.sym} = ${fmt(value(), meta.result.digits ?? 3)} ${meta.result.unit || ''}`; }, 700); } rendered = true;
  }
  function schedule() { if (!pending) { pending = true; requestAnimationFrame(render); } }
  function set(partial, fromPanel = false) {
    Object.assign(S, partial); schedule();
    if (fromPanel && opts.onChange) opts.onChange({ ...S }, Object.keys(partial));
  }
  function select(k) { if (!meta.vars[k]) return; sel = k; schedule(); }
  function freeze(on) { const st = q('.eql-state'); st.dataset.state = on ? 'frozen' : 'live'; st.textContent = on ? 'frozen' : 'live'; }
  render();
  return { set, select, freeze, state: S, value, el: host };
}

// Convenience for lab pages: fetch the registry from data/site.json and mount by id.
export async function loop(host, id, opts = {}) {
  const { data } = await import('./site.js');
  const D = await data(), meta = (D.loops || {})[id];
  if (!meta) { host.hidden = true; return null; }
  return mountLoop(host, { ...meta, id }, { ...opts, id });
}
