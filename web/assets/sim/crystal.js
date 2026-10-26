// Crystal quality versus threading-dislocation density, mirroring adamas.power and adamas.nv (golden-checked).
// E_c(D): engineering fit from 7.7 MV/cm at 1e4 cm^-2 [volpe2010] to about 1.5 MV/cm at 2e7 [kwak2021] [weippert2022].
// Strain at the mean dislocation distance r = 1/(2 sqrt(D)): b / (2 pi r), b = 0.252 nm; T2* <= 1/(pi k_s eps),
// k_s = 10.9 GHz per unit strain [marshall2022]. Killer survival exp(-A f_k D) (f_k unmeasured).
export const BURGERS_NM = 0.252, SPIN_STRAIN_HZ = 10.9e9;
export const criticalField = D => { const d = Math.max(D, 1); return d <= 1e4 ? 7.7 : Math.max(1, 7.7 - 1.88 * Math.log10(d / 1e4)); };
export const strain = D => BURGERS_NM * 1e-9 / (2 * Math.PI * (1 / (2 * Math.sqrt(D)) * 1e-2));
export const t2star = D => 1e6 / (Math.PI * SPIN_STRAIN_HZ * strain(D));
export const killerSurvival = (areaMm2, D, fk) => Math.exp(-areaMm2 * 1e-2 * fk * D);
export const bfomRelative = D => (criticalField(D) / 10) ** 3;     // Baliga figure of merit relative to the 10 MV/cm value
export const SUBSTRATES = [['HPHT plate', 1e2], ['CVD on HPHT', 1e4], ['Heteroepitaxial wafer', 2e7]];
