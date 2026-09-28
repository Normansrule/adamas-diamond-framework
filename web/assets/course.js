// Course pages: render the four-question check, grade it, and remember progress in this browser (localStorage).
const KEY = 'adamas-course-v1';
export function load() { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch { return {}; } }
export function save(p) { try { localStorage.setItem(KEY, JSON.stringify(p)); } catch { /* private mode: progress not saved */ } }

export function quiz(root, lessonId, questions) {
  const progress = load();
  root.innerHTML = questions.map((q, i) => `<div class="card" style="margin:12px 0" data-q="${i}"><b>${i + 1}. ${q.q}</b>
    <div style="display:grid;gap:6px;margin-top:10px">${q.o.map((o, k) => `<button class="btn small" data-k="${k}" style="justify-content:flex-start;text-align:left">${o}</button>`).join('')}</div>
    <p class="why" style="display:none;margin-top:10px"></p></div>`).join('') + `<div id="score" class="card" style="margin-top:12px"></div>`;
  const answered = {};
  root.querySelectorAll('[data-q]').forEach(card => {
    const i = +card.dataset.q, q = questions[i];
    card.querySelectorAll('button').forEach(b => b.onclick = () => {
      if (answered[i] !== undefined) return;
      const k = +b.dataset.k, ok = k === q.a; answered[i] = ok;
      card.querySelectorAll('button').forEach(x => { const kk = +x.dataset.k; x.style.borderColor = kk === q.a ? 'var(--green)' : kk === k ? 'var(--red)' : 'var(--line)'; x.style.opacity = kk === q.a || kk === k ? 1 : .55; });
      const w = card.querySelector('.why'); w.style.display = 'block'; w.innerHTML = `<b style="color:${ok ? 'var(--green)' : 'var(--red)'}">${ok ? 'Correct.' : 'Not quite.'}</b> ${q.why}`;
      const n = Object.keys(answered).length, right = Object.values(answered).filter(Boolean).length;
      root.querySelector('#score').innerHTML = n < questions.length ? `${right} of ${n} correct so far.` :
        `<b>${right} / ${questions.length}.</b> ${right === questions.length ? 'Lesson complete.' : 'Review the explanations, then retry by reloading the page.'}`;
      if (n === questions.length) { const p = load(); p[lessonId] = Math.max(p[lessonId] || 0, right / questions.length); save(p); }
    });
  });
  if (progress[lessonId] !== undefined) root.querySelector('#score').textContent = `Best score so far: ${Math.round(progress[lessonId] * 100)}%.`;
}

export function progressBar(el, ids) {
  const p = load(), done = ids.filter(i => (p[i] || 0) >= 0.75).length;
  el.innerHTML = `<div style="display:flex;justify-content:space-between;font-size:13px;color:var(--mute)"><span>Your progress (saved in this browser)</span><span>${done} of ${ids.length} lessons passed</span></div>
    <div style="height:10px;border-radius:6px;background:rgba(255,255,255,.06);margin-top:6px;overflow:hidden"><i style="display:block;height:100%;width:${100 * done / ids.length}%;background:var(--grad)"></i></div>`;
  ids.forEach(i => { const b = document.getElementById(`badge${i}`); if (b) b.textContent = p[i] !== undefined ? `${Math.round(p[i] * 100)}%` : 'not started'; });
}
