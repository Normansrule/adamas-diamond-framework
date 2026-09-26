// The five-layer reference stack of chapter 9 (a proposal of this repository), as data for the 3-D exploded view.
export const LAYERS = [
  { id: 'cmos', name: 'Silicon CMOS', z: 0, h: 0.5, color: '#8b98a5', what: 'Microwave synthesis, amplifiers, converters, pulse sequencer, and the error-correction decoder. Billions of cheap, low-power transistors: keep silicon for what silicon does best.', refs: ['kim2019cmos', 'ibrahim2021', 'irds2023'] },
  { id: 'bond', name: 'Bond interface', z: 1, h: 0.18, color: '#ffc46b', what: 'Micro-bumps or direct bonding. It is also the heat path: microwave drive dissipates milliwatts per site, and diamond spreads it before it detunes the qubits (−74 kHz/K).', refs: ['li2024', 'acosta2010'] },
  { id: 'device', name: 'Diamond device layer', z: 2, h: 0.35, color: '#9d7bff', what: 'Photocurrent electrodes, microwave striplines, and p-channel hole-gas transistors that multiplex picoampere readout next to the qubits. p-channel-only logic is enough here.', refs: ['siyushev2019', 'liu2017', 'bourgeois2015'] },
  { id: 'quantum', name: 'Quantum layer', z: 3, h: 0.22, color: '#2de2e6', what: 'Carbon-12 enriched, oxygen-terminated epilayer with aligned NV clusters: an electron plus nuclear-spin memories per cell, linked across 10 to 25 nm.', refs: ['balasubramanian2009', 'michl2014', 'dolde2013', 'hauf2011'] },
  { id: 'optics', name: 'Optical delivery', z: 4, h: 0.12, color: '#ff5d8f', what: 'Green light for initialization, by flood illumination or grating couplers. Readout is electrical, so no microscope objective is needed.', refs: ['wan2020', 'mouradian2015'] },
];
export function explodedZ(layer, t) { return layer.z * (0.6 + 1.6 * t); }   // t: 0 assembled, 1 exploded
