import test from 'node:test';
import assert from 'node:assert/strict';
import * as bloch from '../assets/sim/bloch.js';
import * as heat from '../assets/sim/heat.js';
import * as cpu from '../assets/sim/dia4.js';
import * as sc from '../assets/sim/surface.js';
import * as phys from '../assets/sim/physics.js';

const P = { rabiMHz: 5, detuningMHz: 0, t2starUs: 0, t1Us: 0, n: 16 };
test('pi pulse flips the spin; 2 pi returns it', () => {
  const s = bloch.makeEnsemble(P); bloch.pulse(s, P, 'x', Math.PI); assert.ok(bloch.P_MINUS1(s) > 0.999);
  bloch.pulse(s, P, 'x', Math.PI); assert.ok(bloch.P_MINUS1(s) < 1e-3);
});
test('Ramsey dephases with T2*, echo refocuses static detunings', () => {
  const p = { ...P, t2starUs: 1, n: 400 };
  const ram = bloch.sweep(p, 'ramsey', [5])[0], ech = bloch.sweep(p, 'echo', [5])[0];
  assert.ok(Math.abs(ram - 0.5) < 0.08, `ramsey ${ram}`);   // fully dephased: 50/50
  assert.ok(ech < 0.02, `echo ${ech}`);                     // refocused: x-x-x echo returns the spin to ms = 0
});
test('diamond hot spot is kappa-ratio cooler than silicon at steady state', () => {
  const si = heat.steady(heat.create('Si', 24), 1000, 3000), di = heat.steady(heat.create('Diamond', 24), 1000, 3000);
  const r = heat.maxT(si) / heat.maxT(di); assert.ok(Math.abs(r / (22 / 1.5) - 1) < 0.01, `ratio ${r}`);
});
test('time stepping approaches the steady solution', () => {
  const a = heat.create('Diamond', 16), b = heat.steady(heat.create('Diamond', 16), 1000, 4000);
  heat.step(a, 1000, 0.05); assert.ok(Math.abs(heat.maxT(a) / heat.maxT(b) - 1) < 0.05);
});
test('DIA-4 programs give the same answers as the Verilog testbenches', () => {
  let s = cpu.reset(), rom = cpu.assemble(cpu.PROGRAMS.countdown), outs = [];
  for (let k = 0; k < 40; k++) { const n = cpu.step(s, rom); if (n.out !== s.out || k === 0) outs.push(n.out); s = n; }
  assert.equal(s.out, 0); assert.equal(s.pc, 5);
  s = cpu.reset(); rom = cpu.assemble(cpu.PROGRAMS.subroutines); for (let k = 0; k < 30; k++) s = cpu.step(s, rom);
  assert.equal(s.out, 10); assert.equal(s.pc, 4);
});
test('surface code: single error corrected, a full chain is a logical error', () => {
  const L = sc.layout(5), f = new Uint8Array(L.edges.length); f[7] = 1;
  const { corr } = sc.decode(L, sc.syndrome(L, f)); assert.equal(sc.logicalFlip(L, f, corr), 0);
  const g = new Uint8Array(L.edges.length); L.edges.forEach((e, i) => { if (e.kind === 'h' && e.r === 2) g[i] = 1; });
  assert.equal(sc.syndrome(L, g).reduce((a, b) => a + b, 0), 0);   // invisible to the checks
  assert.equal(sc.logicalFlip(L, g, new Uint8Array(L.edges.length)), 1);
});
test('NV lines split by 2 gamma B along an axis; lattice bonds are tetrahedral', () => {
  const a = phys.NV_AXES[0], ls = phys.lines(a.map(x => x * 1.0)).filter(l => l.axis === 0).map(l => l.f);
  assert.ok(Math.abs(ls[1] - ls[0] - 2 * 28.025) < 1e-6);
  const L = phys.diamondLattice(3); assert.ok(Math.abs(L.bond - 1.5445) < 1e-3);
  const deg = new Array(L.atoms.length).fill(0); L.bonds.forEach(([i, j]) => { deg[i]++; deg[j]++; });
  assert.ok(Math.max(...deg) === 4);
});
import * as world from '../assets/sim/world.js';
import * as paint from '../assets/sim/paint.js';
import * as stack from '../assets/sim/stack.js';

test('world: coordinates on the unit sphere, filters work', () => {
  for (const s of world.SITES) { const p = world.toXYZ(s.lat, s.lon); assert.ok(Math.abs(Math.hypot(...p) - 1) < 1e-9); assert.ok(s.refs.length > 0 && s.kind in world.KINDS); }
  assert.ok(world.filter(world.SITES, { kinds: ['quantum'] }).every(s => s.kind === 'quantum'));
  assert.ok(world.filter(world.SITES, { upTo: 2015 }).every(s => s.year <= 2015));
});
test('paint: heat spreads about alpha-ratio faster in the diamond half and is conserved away from the edges', () => {
  const g = paint.create(160, 80); paint.deposit(g, 40, 40, 1, 2); paint.deposit(g, 120, 40, 1, 2);
  const s0 = paint.spread(g, 'Si'), d0 = paint.spread(g, 'Diamond'); paint.step(g, 40);
  const rs = (paint.spread(g, 'Diamond') - d0) / (paint.spread(g, 'Si') - s0);
  assert.ok(Math.abs(rs / (paint.ALPHA.Diamond / paint.ALPHA.Si) - 1) < 0.1, `ratio ${rs}`);
});
test('stack: five ordered layers that separate when exploded', () => {
  assert.equal(stack.LAYERS.length, 5);
  const z = stack.LAYERS.map(l => stack.explodedZ(l, 1)); assert.ok(z.every((v, i) => i === 0 || v > z[i - 1]));
});
import { isLand } from '../assets/sim/landmask.js';
test('land mask: known land and ocean points', () => {
  for (const [la, lo] of [[48.8, 2.3], [35.7, 139.7], [-25, 134], [40, -100], [0, 20]]) assert.equal(isLand(la, lo), 1, `${la},${lo}`);
  for (const [la, lo] of [[0, -30], [-40, -120], [30, 160], [-30, 75]]) assert.equal(isLand(la, lo), 0, `${la},${lo}`);
});
import * as F from '../assets/sim/fet.js';
import * as CV from '../assets/sim/converter.js';
test('FET: square law and E/D inverter behave', () => {
  const d = F.fet({ w: 200, vth: 1.5 }), l = F.fet({ w: 25, vth: -2 });
  assert.ok(Math.abs(d.current(5, 20) - d.k * 3.5 ** 2 / 2) < 1e-12);
  const { vin, vout } = F.vtc(d, l, 10); assert.ok(vout[0] > 9.9 && vout[vout.length - 1] < 0.6);
  const nm = F.noiseMargins(vin, vout); assert.ok(nm.nml > 0.5 && nm.nmh > 0.5, JSON.stringify(nm));
});
test('ring oscillator period is within 40% of the ngspice deck (22.4 ns, circuits/spice/ring_oscillator.cir)', () => {
  const r = F.ring(F.fet({ w: 16, l: 2, vth: 1.5 }), F.fet({ w: 2, l: 2, vth: -2 }), { tEnd: 300e-9 });
  assert.ok(Math.abs(r.period / 22.4e-9 - 1) < 0.4, `period ${r.period}`);
});
test('converter closed form equals the area optimum', () => {
  const o = CV.optimum(20, 1e-9, 800, 300, 2e4); assert.ok(Math.abs(o.pCond - o.pSw) / o.pSw < 1e-9 && Math.abs(o.pCond + o.pSw - o.pTotal) / o.pTotal < 1e-9);
});
import * as PH from '../assets/sim/photophys.js';
import * as Y from '../assets/sim/yield.js';
test('photophysics: ms=0 brighter; contrast near the Python value 0.445; populations conserved', () => {
  const c = PH.contrast(1, 0.3); assert.ok(Math.abs(c - 0.445) < 0.01, `contrast ${c}`);
  const e = PH.evolve(1, '1', 2); assert.ok(Math.abs(e.pops.at(-1).reduce((a, b) => a + b) - 1) < 1e-9);
  const tr = PH.trajectory(1, '0', 5, (() => { let s = 1; return () => (s = (s * 16807) % 2147483647) / 2147483647; })()); assert.ok(tr.length > 20);
});
test('wafer: Monte Carlo yield matches Poisson within sampling error', () => {
  let good = 0, total = 0; const rng = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  for (let k = 0; k < 40; k++) { const L = Y.layout(76, 5); const area = Math.PI * L.r ** 2 / 100; Y.drop(L, Math.round(area * 2), rng); good += L.dies.filter(d => !d.bad).length; total += L.dies.length; }
  assert.ok(Math.abs(good / total - Y.poisson(25, 2)) < 0.04, `${good / total} vs ${Y.poisson(25, 2)}`);
  assert.equal(Y.diesPerWafer(300, 100), 640);
});
import * as FIT from '../assets/sim/fit.js';
import fs from 'node:fs';
const ex = n => FIT.parseCSV(fs.readFileSync(new URL(`../../docs/data/examples/${n}.csv`, import.meta.url), 'utf8'));
test('fit.js recovers the parameters of the example datasets', () => {
  let d = ex('rabi'), r = FIT.fit('rabi', d.x, d.y); assert.ok(Math.abs(r.p[1] - 5) < 0.05, `rabi ${r.p[1]}`);
  d = ex('echo'); r = FIT.fit('echo', d.x, d.y); assert.ok(Math.abs(r.p[1] - 300) < 30, `T2 ${r.p[1]}`);
  d = ex('arrhenius'); r = FIT.fit('arrhenius', d.x, d.y); assert.ok(Math.abs(r.ea - 0.37) < 0.02, `Ea ${r.ea}`);
  d = ex('g2'); r = FIT.fit('g2', d.x, d.y); assert.ok(r.p[0] < 0.3);
  d = ex('odmr_zero_field'); r = FIT.fit('odmr', d.x, d.y); assert.equal((r.p.length - 1) / 3, 1); assert.ok(Math.abs(r.p[2] - 2870) < 0.5);
  d = ex('odmr_with_magnet'); r = FIT.fit('odmr', d.x, d.y); assert.ok((r.p.length - 1) / 3 >= 4, `lines ${(r.p.length - 1) / 3}`);
  assert.ok(r.hist.length > 2);
});
import * as UN from '../assets/sim/uncertainty.js';
test('uncertainty: power ratio baseline 6.67 and permittivity-free; LHS covers every stratum', () => {
  const P = { 'Diamond critical field': [10, 5, 10, 'lin'], 'Diamond hole mobility': [3800, 1000, 3800, 'log'], 'SiC critical field': [3, 2.5, 3.5, 'lin'], 'SiC electron mobility': [950, 700, 1000, 'lin'] };
  assert.ok(Math.abs(UN.powerRatio(UN.baseline(P)) - 6.667) < 0.01);
  const s = UN.lhs(P, 100), f = s.map(x => x['Diamond critical field']);
  for (let k = 0; k < 100; k++) assert.equal(f.filter(v => v >= 5 + 0.05 * k && v < 5 + 0.05 * (k + 1)).length, 1);
});
import { search, score } from '../assets/search.js';
test('search palette ranks title matches first and tolerates partial words', () => {
  const items = [{ title: 'Qubit Lab', kind: 'lab', text: 'Bloch sphere' }, { title: 'Heat Race', kind: 'lab', text: 'qubit cooling is not the point' }, { title: 'XZZX: XZZX surface code', kind: 'term', text: 'biased noise' }];
  assert.equal(search(items, 'qubit')[0].title, 'Qubit Lab');
  assert.equal(search(items, 'xzz')[0].kind, 'term');
  assert.equal(search(items, 'zzzzzz').length, 0);
  assert.ok(score(items[0], 'qub lab') > 0);
});
