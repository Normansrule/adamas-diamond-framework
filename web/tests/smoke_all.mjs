// Run the headless smoke test on every page of a built site. Usage: node tests/smoke_all.mjs ../site
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)), site = path.resolve(process.argv[2] || '../site');
const PAGES = [['index.html', ''], ['labs/qubit.html', 'run'], ['labs/lattice.html', ''], ['labs/heat.html', ''], ['labs/cpu.html', 'stepB*6'],
  ['labs/qec.html', 'noise,dec,mc'], ['labs/fab.html', 'next*3'], ['labs/globe.html', 'play'], ['labs/stack.html', ''], ['labs/transistor.html', ''], ['labs/power.html', ''], ['labs/machine.html', ''], ['labs/photon.html', 'go,many'], ['labs/wafer.html', 'rain'], ['gallery.html', ''], ['course/index.html', ''], ['course/lesson-1.html', 'quizall'], ['course/lesson-6.html', '']];
let fail = 0;
for (const [p, a] of PAGES) {
  try { console.log(execFileSync(process.execPath, [path.join(HERE, 'smoke.mjs'), site, p, a], { encoding: 'utf8' }).trim()); }
  catch (e) { fail++; console.error(`FAIL ${p}\n${e.stderr || e.message}`); }
}
process.exit(fail ? 1 : 0);
