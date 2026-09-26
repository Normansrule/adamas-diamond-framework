// Who is building diamond electronics and quantum hardware, and where. Each entry cites the result it is known for;
// every key resolves in references/REFERENCES.md (the citation checker scans this file). Evidence labels as in
// chapter 10: P peer-reviewed, N news or trade press, V vendor statement. Coordinates are city-level.
export const SITES = [
  { name: 'Element Six & Orbray', place: 'Harwell, UK / Tokyo, Japan', lat: 51.57, lon: -1.31, kind: 'wafer', year: 2026, what: 'Reproducible 3-inch single-crystal diamond wafers; 4-inch in development', ev: 'N', refs: ['e6orbray2026'] },
  { name: 'Saga University & Orbray', place: 'Saga, Japan', lat: 33.24, lon: 130.29, kind: 'power', year: 2023, what: '2-inch heteroepitaxial wafers; 2608 V and 3659 V diamond MOSFETs', ev: 'P', refs: ['kim2021', 'saha2021', 'saha2023'] },
  { name: 'University of Augsburg', place: 'Augsburg, Germany', lat: 48.33, lon: 10.90, kind: 'wafer', year: 2017, what: '92 mm heteroepitaxial diamond on iridium', ev: 'P', refs: ['schreck2017'] },
  { name: 'AIST', place: 'Ikeda, Osaka, Japan', lat: 34.83, lon: 135.43, kind: 'wafer', year: 2014, what: 'Mosaic wafers cloned by ion-implant lift-off', ev: 'P', refs: ['yamada2014'] },
  { name: 'NIMS', place: 'Tsukuba, Japan', lat: 36.05, lon: 140.13, kind: 'logic', year: 2024, what: 'First n-channel diamond MOSFET; boron-nitride-gated transistors', ev: 'P', refs: ['liao2024', 'sasama2018'] },
  { name: 'Waseda University', place: 'Tokyo, Japan', lat: 35.71, lon: 139.72, kind: 'power', year: 2025, what: '400 °C hole-gas FETs; cascode diamond/SiC/GaN half-bridge', ev: 'P', refs: ['kawarada2014', 'kawai2025'] },
  { name: 'Kanazawa University', place: 'Kanazawa, Japan', lat: 36.54, lon: 136.71, kind: 'logic', year: 2016, what: 'First inversion-channel diamond MOSFET', ev: 'P', refs: ['matsumoto2016'] },
  { name: 'Ookuma Diamond Device', place: 'Fukushima, Japan', lat: 37.40, lon: 141.03, kind: 'power', year: 2026, what: 'Diamond semiconductor plant for radiation-hard electronics', ev: 'N', refs: ['ookuma2026'] },
  { name: 'University of Stuttgart', place: 'Stuttgart, Germany', lat: 48.78, lon: 9.10, kind: 'quantum', year: 2013, what: 'Room-temperature entanglement of two NV centers; error correction', ev: 'P', refs: ['dolde2013', 'waldherr2014', 'neumann2010natphys'] },
  { name: 'USTC', place: 'Hefei, China', lat: 31.84, lon: 117.26, kind: 'quantum', year: 2015, what: 'Fault-tolerant-threshold gates at room temperature', ev: 'P', refs: ['rong2015'] },
  { name: 'Kyoto University & AIST', place: 'Kyoto, Japan', lat: 35.03, lon: 135.78, kind: 'quantum', year: 2019, what: '2.4 ms room-temperature coherence in n-type diamond', ev: 'P', refs: ['herbschleb2019'] },
  { name: 'Hasselt University', place: 'Hasselt, Belgium', lat: 50.93, lon: 5.39, kind: 'quantum', year: 2019, what: 'Electrical (photocurrent) readout of single NV spins', ev: 'P', refs: ['siyushev2019'] },
  { name: 'Harvard University', place: 'Cambridge, MA, USA', lat: 42.377, lon: -71.117, kind: 'quantum', year: 2020, what: 'Second-long nuclear memory at 300 K; silicon-vacancy network nodes', ev: 'P', refs: ['maurer2012', 'bhaskar2020'] },
  { name: 'MIT', place: 'Cambridge, MA, USA', lat: 42.36, lon: -71.09, kind: 'quantum', year: 2024, what: 'Diamond qubit chiplets on foundry CMOS', ev: 'P', refs: ['li2024', 'wan2020'] },
  { name: 'QuTech, TU Delft', place: 'Delft, Netherlands', lat: 52.00, lon: 4.37, kind: 'quantum', year: 2021, what: '10-qubit register; three-node quantum network', ev: 'P', refs: ['bradley2019', 'pompili2021', 'hensen2015'] },
  { name: 'Quantum Brilliance at Pawsey', place: 'Perth, Australia', lat: -31.98, lon: 115.82, kind: 'industry', year: 2023, what: 'Room-temperature NV accelerator at a supercomputing center', ev: 'V', refs: ['qbpawsey2023'] },
  { name: 'Quantum Brilliance at ORNL', place: 'Oak Ridge, TN, USA', lat: 35.93, lon: -84.31, kind: 'industry', year: 2025, what: 'NV accelerators installed for hybrid computing', ev: 'V', refs: ['olcf2025'] },
  { name: 'SaxonQ', place: 'Leipzig, Germany', lat: 51.34, lon: 12.37, kind: 'industry', year: 2026, what: 'Portable diamond quantum computer (vendor claims)', ev: 'V', refs: ['saxonq2026'] },
  { name: 'Element Six / GaN-on-diamond', place: 'Santa Clara, CA, USA', lat: 37.35, lon: -121.95, kind: 'power', year: 2010, what: '4-inch GaN-on-diamond substrates for heat spreading', ev: 'P', refs: ['francis2010'] },
];
export const KINDS = { wafer: '#ffc46b', power: '#ff5d8f', logic: '#9d7bff', quantum: '#2de2e6', industry: '#48e5a3' };

export function toXYZ(lat, lon, r = 1) {           // y up, lon 0 at +z
  const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
  return [r * Math.cos(la) * Math.sin(lo), r * Math.sin(la), r * Math.cos(la) * Math.cos(lo)];
}

export function filter(sites, { kinds = null, upTo = 9999 } = {}) {
  return sites.filter(s => (!kinds || kinds.includes(s.kind)) && s.year <= upTo);
}
