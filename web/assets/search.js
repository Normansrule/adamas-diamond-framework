// Command palette: Ctrl+K or "/" anywhere. Searches pages, labs, glossary terms, figures, experiments, process steps,
// and lessons from data/search.json (built by adamas.site). Arrow keys move, Enter opens, Esc closes.
let idx = null, box = null, sel = 0, hits = [];
const norm = s => s.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
export function score(item, q) {
  const t = norm(item.title), d = norm(item.text || ''), words = norm(q).split(/\s+/).filter(Boolean); if (!words.length) return 0;
  let s = 0;
  for (const w of words) { if (t.startsWith(w)) s += 6; else if (t.includes(w)) s += 4; else if (d.includes(w)) s += 1.5; else { let i = 0; for (const ch of t) if (ch === w[i]) i++; if (i === w.length) s += 1; else return 0; } }
  return s + (item.kind === 'page' ? 0.5 : 0);
}
export function search(items, q, n = 12) { return items.map(it => [score(it, q), it]).filter(([s]) => s > 0).sort((a, b) => b[0] - a[0]).slice(0, n).map(([, it]) => it); }
export async function open(base = '.') {
  if (!idx) { try { idx = await (await fetch(`${base}/data/search.json`)).json(); } catch { idx = []; } }
  if (!box) {
    box = document.createElement('div'); box.className = 'palette'; box.innerHTML = `<div class="pbox" role="dialog" aria-label="Search"><input id="pq" placeholder="Search labs, terms, figures, experiments, steps…" autocomplete="off"><div id="pres"></div><div class="phelp">↑ ↓ to move · Enter to open · Esc to close</div></div>`;
    document.body.appendChild(box);
    box.addEventListener('click', e => { if (e.target === box) close(); });
    const inp = box.querySelector('#pq');
    inp.addEventListener('input', () => { sel = 0; render(base); });
    inp.addEventListener('keydown', e => { if (e.key === 'ArrowDown') { sel = Math.min(hits.length - 1, sel + 1); render(base, false); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { sel = Math.max(0, sel - 1); render(base, false); e.preventDefault(); } else if (e.key === 'Enter' && hits[sel]) location.href = `${base}/${hits[sel].href}`; else if (e.key === 'Escape') close(); });
  }
  box.classList.add('on'); const inp = box.querySelector('#pq'); inp.value = ''; sel = 0; render(base); setTimeout(() => inp.focus(), 10);
}
function close() { box?.classList.remove('on'); }
const ICON = { page: '◆', lab: '⚗', term: 'Aa', figure: '▦', experiment: '🔬', step: '⚙', lesson: '🎓' };
function render(base, recompute = true) {
  const q = box.querySelector('#pq').value;
  if (recompute) hits = q ? search(idx, q) : idx.filter(i => i.kind === 'page' || i.kind === 'lab').slice(0, 10);
  box.querySelector('#pres').innerHTML = hits.length ? hits.map((h, i) => `<a href="${base}/${h.href}" class="${i === sel ? 'sel' : ''}"><span class="pk">${ICON[h.kind] || '·'}</span><span><b>${h.title}</b><small>${h.kind} · ${(h.text || '').slice(0, 110)}</small></span></a>`).join('')
    : '<p style="color:var(--mute);padding:14px">No matches. Try "qubit", "XZZX", "yield", or "ALD".</p>';
}
