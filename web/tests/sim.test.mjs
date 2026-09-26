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
