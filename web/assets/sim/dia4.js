// Instruction-set emulator of the DIA-4 processor, cycle-exact against circuits/digital/dia4.v (checked by the test suite
// against Icarus Verilog on random programs). 4-bit accumulator, 4-bit PC, 16-byte ROM, 4-entry return stack.
export const OPS = { NOP: 0, LDI: 1, ADD: 2, SUB: 3, AND: 4, OR: 5, XOR: 6, JNZ: 7, JMP: 8, OUT: 9, CALL: 10, RET: 11 };
export const NAMES = Object.fromEntries(Object.entries(OPS).map(([k, v]) => [v, k]));

export function reset() { return { pc: 0, acc: 0, out: 0, carry: 0, sp: 0, stack: [0, 0, 0, 0], cycle: 0 }; }

export function step(s, rom) {
  const ins = rom[s.pc] & 0xff, op = ins >> 4, imm = ins & 15, n = { ...s, stack: s.stack.slice(), cycle: s.cycle + 1 };
  n.pc = (s.pc + 1) & 15;
  switch (op) {
    case 1: n.acc = imm; break;
    case 2: { const r = s.acc + imm; n.acc = r & 15; n.carry = (r >> 4) & 1; break; }
    case 3: { const r = (s.acc - imm) & 31; n.acc = r & 15; n.carry = (r >> 4) & 1; break; }
    case 4: n.acc = s.acc & imm; break;
    case 5: n.acc = s.acc | imm; break;
    case 6: n.acc = s.acc ^ imm; break;
    case 7: if (s.acc !== 0) n.pc = imm; break;
    case 8: n.pc = imm; break;
    case 9: n.out = s.acc; break;
    case 10: n.stack[s.sp] = (s.pc + 1) & 15; n.sp = (s.sp + 1) & 3; n.pc = imm; break;
    case 11: { const m = (s.sp - 1) & 3; n.pc = s.stack[m]; n.sp = m; break; }
    default: break;
  }
  return n;
}

export function assemble(src) {          // lines: "label:", "OP arg", "; comment"; arg may be a number or a label
  const lines = src.split('\n').map(l => l.replace(/;.*$/, '').trim()).filter(Boolean), labels = {}, body = [];
  for (const l of lines) { const m = l.match(/^(\w+):\s*(.*)$/); if (m) { labels[m[1]] = body.length; if (m[2]) body.push(m[2]); } else body.push(l); }
  if (body.length > 16) throw new Error('DIA-4 has 16 words of program memory');
  const rom = new Array(16).fill(0);
  body.forEach((l, i) => {
    const [opName, arg] = l.split(/\s+/), op = OPS[opName.toUpperCase()];
    if (op === undefined) throw new Error(`unknown instruction "${opName}" on line ${i + 1}`);
    let v = arg === undefined ? 0 : (arg in labels ? labels[arg] : parseInt(arg));
    if (Number.isNaN(v) || v < 0 || v > 15) throw new Error(`operand of "${l}" must be 0 to 15 or a label`);
    rom[i] = (op << 4) | v;
  });
  return rom;
}

export const PROGRAMS = {
  countdown: `; count 5..0 on the output port, then halt
LDI 5
loop: OUT
SUB 1
JNZ loop
OUT
halt: JMP halt`,
  subroutines: `; 2 + 2 * (3 + 1) = 10 using nested CALL/RET
LDI 2
CALL sub
CALL sub
OUT
halt: JMP halt
NOP
NOP
NOP
sub: ADD 3
CALL leaf
RET
NOP
leaf: ADD 1
RET`,
  fibonacci: `; Fibonacci mod 16 is out of reach for 1 register; instead: sum 1+2+...+5 = 15
LDI 0
ADD 1
ADD 2
ADD 3
ADD 4
ADD 5
OUT
halt: JMP halt`,
};
