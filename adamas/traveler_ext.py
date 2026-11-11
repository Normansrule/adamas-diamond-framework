"""Extension steps X07a to X27a: device-specific build steps that sit outside traveler T1 (adamas.traveler).

The Quantum Device Library (adamas.qdl) routes eleven devices through T1 plus one extra step each. Until v0.41.0 those
steps were shown as "missing". Here each is written as a step sheet with the same fields as a T1 step (purpose,
equipment, parameters with sources, checks, safety, failure modes, the silicon comparison), plus:
  label    the evidence for the step itself: demonstrated (done at room temperature in the cited work), cryogenic (the
           cited result needs cryogenic operation), or proposed (no fabricated device; the parameters are a proposal's
           assumptions);
  after    the T1 step it follows on the device's route;
  atlas    the Machine Atlas IDs it needs (adamas.atlas).
Numbers are read from the cited papers (abstract, arXiv text or the published PDF); a parameter the paper does not
give is written "not given in [key]; to source". Pass criteria marked ADAMAS are this repository's targets; the
others come from the cited paper. t_max_c is None where the source gives no process temperature. Safety notes
summarize hazards and do not replace your facility's training.
"""
from __future__ import annotations

KIM2019_SENS_UT = 32.1          # µT/√Hz, CMOS-integrated NV magnetometer [kim2019cmos]
KIM2019_TARGET_FACTOR = 2.0     # ADAMAS: a first copy passes within twice the published sensitivity

EXTENSIONS = [
 {"id": "X07a", "short": "p-i-n growth", "module": "M1", "title": "p-i-n doped growth (boron and phosphorus layers)", "t_max_c": None,
  "label": "demonstrated", "after": "S03", "devices": ["QDL-07"], "atlas": ["M01", "M23"],
  "why": "An NV center inside the intrinsic layer of a diamond p-i-n diode can be driven electrically: injected electrons and holes recombine at the defect, which then emits single photons at room temperature.",
  "equipment": ["MPCVD reactor with diborane and phosphine (or trimethylboron) doping lines", "SIMS for dopant profiles", "Ti/Pt/Au contacts (traveler S09 to S10)"],
  "params": [("Structure", "Single neutral NV center in the intrinsic layer of a p-i-n diode", "[mizuochi2012]"),
             ("Doping levels, layer thicknesses, growth temperature", "Not given in the abstract of [mizuochi2012]; to source from the full paper", "[mizuochi2012]")],
  "checks": [("Electroluminescence from a single center at room temperature", "", None, None, "[mizuochi2012]"),
             ("Diode rectifies (forward current, low reverse leakage)", "", None, None, "ADAMAS")],
  "safety": ["Phosphine and diborane are highly toxic and pyrophoric: gas cabinets, detectors and the facility's toxic-gas training are mandatory."],
  "failures": [("No n-type conduction", "Phosphorus not incorporated or compensated", "Check SIMS profile, growth orientation and nitrogen background")],
  "silicon": "Silicon p-n junctions are made by implantation or diffusion in minutes; diamond n-type doping is the hard part."},
 {"id": "X09a", "short": "Nanopillars", "module": "M2", "title": "Nanophotonic etch (nanopillars or waveguides)", "t_max_c": None,
  "label": "demonstrated", "after": "S07", "devices": ["QDL-09"], "atlas": ["M12", "M16", "M10"],
  "why": "A pillar or waveguide around an NV center guides its light out of the high-index diamond, so more photons reach the detector at lower laser power.",
  "equipment": ["Electron-beam lithography", "ICP-RIE with oxygen (and chlorine for angled etching)", "HF bath for mask removal", "Faraday cage for angled etching"],
  "params": [("Pillar size", "About 200 nm diameter, 2 µm long", "[babinec2010]"),
             ("Mask", "FOx-17 spin-on glass (negative e-beam resist) diluted 1:2 in MIBK; removed in HF", "[babinec2010] [hausmann2010]"),
             ("Pillar etch", "Oxygen ICP-RIE, 30 sccm O₂, 100 W bias, 10 mTorr, ICP 600 to 1000 W, about 10 min", "[babinec2010]"),
             ("Etch rate", "190 to 240 nm/min in single-crystal diamond", "[hausmann2010]"),
             ("Waveguides (angled etch)", "About 200 nm titanium mask; 50 sccm O₂ + 2 sccm Cl₂, 700 W ICP, 100 W RF, 10 mTorr; Faraday cage at about 45° gives about 35° sidewalls", "[burek2012]"),
             ("Clean", "Boiling nitric, perchloric and sulfuric acid (as traveler S02)", "[hausmann2010]")],
  "checks": [("Saturated count rate, pillar over unpatterned diamond", "×", 5.0, None, "ADAMAS (about ten-fold reported [babinec2010])"),
             ("g⁽²⁾(0) below 0.5 on the chosen pillar", "", None, None, "[babinec2010]")],
  "safety": ["HF: calcium gluconate gel at hand and HF-specific training.", "Chlorine is toxic and corrosive: interlocked gas cabinet.", "Hot tri-acid: face shield, acid hood."],
  "failures": [("Pillars taper or break", "Mask erodes or too much bias", "Thicker or harder mask (Al₂O₃ resists best [hausmann2010]), lower bias"),
               ("No NV in the pillar", "NV density too low for random placement", "Raise implant dose or align pillars to located NVs")],
  "silicon": "Silicon photonics etches waveguides at wafer scale with deep-UV lithography; diamond nanophotonics is still chip-scale."},
 {"id": "X10a", "short": "Spin chains", "module": "M2", "title": "Dark-spin chain placement", "t_max_c": None,
  "label": "proposed", "after": "S06", "devices": ["QDL-10"], "atlas": ["M20", "M21"],
  "why": "A chain of optically dark nitrogen spins between two NV registers carries quantum information over hundreds of nanometres without photons.",
  "equipment": ["Low-energy nitrogen implanter", "Aperture mask or scanning-probe implantation", "Vacuum anneal (traveler S07)"],
  "params": [("Chain spacing", "About 16 to 18 nm (16 nm for a 7-spin chain, 18.1 nm for an 18-spin chain in the proposal's examples)", "[yao2012]"),
             ("Chain length", "About 5 spins for 100 nm, about 20 for 500 nm", "[yao2012]"),
             ("Register spacing", "Plaquettes about 100 to 500 nm apart", "[yao2012]"),
             ("Placement process", "Implantation and anneal with about 40 % NV conversion assumed; operation at room temperature, with optional cooling to about 50 K", "[yao2012]"),
             ("State of the art", "No published process places nitrogen chains at this pitch", "ADAMAS")],
  "checks": [("Mean chain spacing", "nm", None, 20.0, "[yao2012]")],
  "safety": ["Ion implanters: radiation and high-voltage interlocks; facility training."],
  "failures": [("Gaps or doubled sites in the chain", "Poisson placement statistics", "Not solved: deterministic single-ion placement is open")],
  "silicon": "Silicon has no counterpart; single-dopant placement (phosphorus in silicon) is done by scanning-tunnelling lithography in research labs."},
 {"id": "X11a", "short": "Cavity", "module": "M2", "title": "Nanophotonic etch (cavity)", "t_max_c": None,
  "label": "cryogenic", "after": "S07", "devices": ["QDL-11"], "atlas": ["M12", "M16"],
  "why": "A small optical cavity speeds up the NV's zero-phonon emission; the published enhancement was measured below 10 K, where the line is narrow.",
  "equipment": ["Diamond membrane on SiO₂/Si", "Electron-beam lithography", "RIE for the SiN mask and oxygen RIE for thinning"],
  "params": [("Membrane", "5 µm single-crystal membrane on 2 µm SiO₂/Si, thinned by oxygen RIE to 280 nm", "[faraon2011]"),
             ("Mask", "500 nm SiN patterned by e-beam lithography", "[faraon2011]"),
             ("Cavity", "Microring 4.8 µm diameter, 700 nm wide", "[faraon2011]"),
             ("Monolithic alternative", "Angled-etch photonic-crystal nanobeam, 400 nm wide, 220 nm period (quality factor simulated only)", "[burek2012]")],
  "checks": [("Cavity quality factor", "", 3000.0, None, "ADAMAS (3800 and 4300 measured [faraon2011])"),
             ("Zero-phonon emission enhanced when the cavity is tuned onto the line (below 10 K)", "", None, None, "[faraon2011]")],
  "safety": ["Liquid helium: cryogenic burns and asphyxiation; oxygen monitors.", "HF for SiO₂ removal: as X09a."],
  "failures": [("Low quality factor", "Rough sidewalls or a thickness gradient", "Smoother mask, thinner uniform membrane")],
  "silicon": "Silicon microrings are a foundry product; the cavity enhancement of a diamond emitter needs cryogenic operation."},
 {"id": "X13a", "short": "Optomechanics", "module": "M2", "title": "Optomechanical resonator fabrication", "t_max_c": None,
  "label": "proposed", "after": "S07", "devices": ["QDL-13"], "atlas": ["M12", "M16"],
  "why": "The proposal couples an NV spin to a mechanical oscillator through a magnetic tip, and the oscillator to telecom light in a cavity, to build a room-temperature quantum repeater.",
  "equipment": ["SiN membrane oscillator with a magnetic tip", "High-finesse optical cavity"],
  "params": [("Oscillator", "SiN membrane inside the cavity; mechanical quality factor 3 × 10⁹ assumed in the proposal's calculations, against about 10⁹ for current membranes as the paper states", "[ji2022]"),
             ("Cavity", "Main design: about 60 cm long, finesse 12,000 (the paper also discusses a short, higher-finesse variant)", "[ji2022]"),
             ("Spin coupling", "Magnetic tip on the membrane, field gradient about 10⁷ T/m", "[ji2022]"),
             ("Fabrication", "No device fabricated; the diamond part follows T1; the membrane and tip are not specified", "[ji2022]")],
  "checks": [("Mechanical quality factor of the membrane", "", 3.0e9, None, "[ji2022] (assumed in the proposal)")],
  "safety": ["High-power lasers in the cavity: Class 3B or 4 controls."],
  "failures": [("Quality factor far below the assumption", "Clamping and gas damping", "Not solved: no fabricated device; measure the membrane's quality factor first")],
  "silicon": "Silicon nitride membranes are made in silicon foundries; the spin-mechanics interface is diamond-specific."},
 {"id": "X14a", "short": "Release", "module": "M2", "title": "Released diamond nanobeam", "t_max_c": 450,
  "label": "demonstrated", "after": "S07", "devices": ["QDL-14"], "atlas": ["M12", "M16"],
  "why": "A free-standing diamond cantilever with an NV inside lets the spin feel the beam's strain, so the beam's motion can drive or read the spin at room temperature.",
  "equipment": ["Diamond plate bonded to oxidized silicon (HSQ) or clamped between fused-quartz slides", "ICP-RIE (argon-chlorine thinning, oxygen patterning)", "Air anneal furnace"],
  "params": [("Starting plate", "CVD (100) plates 20 to 40 µm thick", "[tao2014]"),
             ("Thinning", "Argon-chlorine plasma RIE", "[tao2014]"),
             ("Release", "Backside etching; 106 of 108 cantilevers survived", "[tao2014]"),
             ("Size", "20 to 240 µm long, 8 to 16 µm wide, 80 to 800 nm thick [tao2014]; the strain-coupling device, made by its authors' own earlier process rather than this one, was 60 µm long, 15 µm wide, about 1 µm thick", "[tao2014] [ovartchaiyapong2014]"),
             ("NV creation", "¹⁴N implant 3 × 10⁹ cm⁻² at 40 keV; 800 °C vacuum anneal for 3 h (as traveler S06 and S07)", "[ovartchaiyapong2014]"),
             ("Surface", "Air anneal at 450 °C for oxygen termination raised the quality factor more than ten-fold", "[tao2014]"),
             ("Angled-etch alternative", "Nanobeams up to 85 µm long without a membrane", "[burek2012]")],
  "checks": [("Mechanical quality factor at room temperature in vacuum", "", 3.0e5, None, "[ovartchaiyapong2014]"),
             ("Beam survives release and is free over its length", "", None, None, "ADAMAS")],
  "safety": ["Chlorine plasma: toxic gas controls.", "HSQ bonding uses HF later for removal: HF training."],
  "failures": [("Low quality factor", "Surface loss", "Oxygen-terminate by the 450 °C air anneal [tao2014]"),
               ("Beam breaks on release", "Stress or rinse forces", "Critical-point drying; shorter beams")],
  "silicon": "Silicon MEMS release beams by etching a sacrificial oxide at wafer scale; diamond has no sacrificial layer, so it is thinned or undercut instead."},
 {"id": "X15a", "short": "Ferromagnet", "module": "M4", "title": "Ferromagnet strip deposition", "t_max_c": None,
  "label": "proposed", "cryogenic": True, "after": "S13", "devices": ["QDL-15"], "atlas": ["M13"],
  "why": "The proposal links two spin qubits about a micrometre apart through the magnons of a ferromagnet placed just above them.",
  "equipment": ["Deposition of a ferromagnetic film (not specified)", "E-beam lithography and lift-off"],
  "params": [("Material", "Not specified in the model; yttrium iron garnet is named as an example", "[trifunovic2013]"),
             ("Geometry", "Worked estimate: a disc 20 nm thick, 50 nm radius, with qubits 25 nm below it; qubits about 1 µm apart", "[trifunovic2013]"),
             ("Operating temperature", "0.1 K in the proposal (cryogenic)", "[trifunovic2013]"),
             ("Deposition process", "Not given in [trifunovic2013]; to source. It follows gold, so it must stay below 500 °C (traveler rule 1)", "ADAMAS")],
  "checks": [("Process temperature after gold", "°C", None, 500.0, "ADAMAS (traveler rule 1)")],
  "safety": ["Evaporation and sputtering: high voltage and vacuum hazards; facility training."],
  "failures": [("No coupling", "Film too far from the NV, or magnon gap wrong", "Not solved: no fabricated device")],
  "silicon": "Magnetic tunnel junctions (MRAM) are deposited on silicon wafers in production; a magnon bus for spin qubits is a proposal."},
 {"id": "X17a", "short": "Scanning tip", "module": "M2", "title": "Pillar tip etch and cantilever mount", "t_max_c": None,
  "label": "demonstrated", "after": "S07", "devices": ["QDL-17"], "atlas": ["M12", "M16", "M21", "M24"],
  "why": "An NV center near the end of a diamond pillar, scanned over a sample like an AFM tip, images magnetic fields with nanometre resolution at room temperature.",
  "equipment": ["Electronic-grade plate", "ICP-RIE (argon-chlorine and oxygen) for back-thinning and pillars", "Electron-beam lithography", "Focused ion beam with tungsten deposition", "Tuning-fork AFM head"],
  "params": [("Plate", "Electronic grade, 50 µm thick, back-thinned to about 3 µm by RIE (argon-chlorine and oxygen)", "[maletinsky2012]"),
             ("NV creation", "Nitrogen implant 6 keV, 3 × 10¹¹ cm⁻², 800 °C for 2 h; NVs about 10 nm deep (as traveler S06 and S07)", "[maletinsky2012]"),
             ("Pillars", "About 200 nm diameter, about 1 µm long, by e-beam lithography and RIE", "[maletinsky2012]"),
             ("Mount", "A diamond platform fused to a quartz tip of a tuning-fork AFM by tungsten deposition, then cut free with a focused ion beam", "[maletinsky2012]")],
  "checks": [("Photon count rate from the tip NV", "counts/s", 1.0e5, None, "ADAMAS (above 3 × 10⁵ reported, with excitation as low as 20 µW [maletinsky2012])"),
             ("Echo coherence time T₂ of the tip NV", "µs", 10.0, None, "ADAMAS (33 µs reported [maletinsky2012])")],
  "safety": ["Chlorine plasma: toxic gas controls.", "532 nm laser: Class 3B or 4 controls."],
  "failures": [("Tip NV too deep or too shallow", "Implant energy", "Adjust energy; shallow NVs lose coherence")],
  "silicon": "Silicon AFM tips are made in batch on wafers; a single-spin tip is diamond-specific."},
 {"id": "X20a", "short": "Nanodiamonds", "module": "M2", "title": "Nanodiamond milling and surface treatment", "t_max_c": None,
  "label": "demonstrated", "after": "S07", "devices": ["QDL-20"], "atlas": ["M31"],
  "why": "Nanodiamonds with many NV centers go where a plate cannot, such as inside a living cell, and read out temperature optically.",
  "equipment": ["Commercial NV nanodiamonds", "Confocal ODMR setup"],
  "params": [("Material", "Single-crystal nanodiamonds with about 500 NV centers each, bought from a supplier", "[kucsko2013]"),
             ("Size", "Not stated in [kucsko2013]; the 200 nm figure there is the spatial resolution", "[kucsko2013]"),
             ("Milling and surface treatment", "Not described in [kucsko2013]; buy them; to source a milling process", "[kucsko2013]")],
  "checks": [("Temperature accuracy of one nanodiamond", "mK", None, 100.0, "ADAMAS (44 ± 10 mK reported [kucsko2013])")],
  "safety": ["Nanoparticle powders: avoid inhalation; handle in suspension.", "Biological samples: the institution's biosafety rules."],
  "failures": [("Broad ODMR lines", "Strain and surface spins in small particles", "Larger particles or surface treatment")],
  "silicon": "Silicon has no counterpart; quantum-dot nanoparticles are the nearest optical probes."},
 {"id": "X25a", "short": "Maser cavity", "module": "M5", "title": "Cavity assembly (sapphire or dielectric resonator)", "t_max_c": None,
  "label": "demonstrated", "after": "S07", "devices": ["QDL-25"], "atlas": ["M38", "M41"],
  "why": "Optically pumped NV centers in a high-quality microwave resonator amplify microwaves: a continuous-wave maser at room temperature.",
  "equipment": ["Hollow single-crystal sapphire resonator in a copper cavity", "Electromagnet or permanent magnet near 0.43 T", "532 nm continuous-wave laser of hundreds of mW"],
  "params": [("Resonator", "Sapphire ring 10 mm outer, 5.1 mm inner diameter, 6.5 mm tall; TE01δ mode at 9.22 GHz; quality factor 55,000 unloaded, 30,000 loaded", "[breeze2018]"),
             ("Diamond", "CVD type IIa, 1 ppm nitrogen, 2.1 × 2.1 × 2.6 mm³, electron-irradiated and annealed (energy, dose and anneal not given in the arXiv text); 0.072 ppm NV⁻", "[breeze2018]"),
             ("Field", "About 429.8 mT along an NV axis", "[breeze2018]"),
             ("Pump", "532 nm continuous wave, 400 mW; threshold predicted at about 210 mW; heats the sample by about 35 °C", "[breeze2018]")],
  "checks": [("Loaded resonator quality factor", "", 30000.0, None, "[breeze2018]"),
             ("Maser threshold pump power", "mW", None, 400.0, "ADAMAS (threshold predicted at about 210 mW [breeze2018])")],
  "safety": ["Class 4 laser (hundreds of mW): interlocked enclosure and laser training.", "Strong magnet: pacemakers, tools and pinch hazards."],
  "failures": [("No maser oscillation", "Loaded quality factor or NV density too low", "Re-seat the diamond, raise NV density, check field alignment")],
  "silicon": "Silicon has no room-temperature maser; microwave amplifiers use transistors."},
 {"id": "X27a", "short": "CMOS die", "module": "M5", "title": "CMOS die from a multi-project wafer (MPW) shuttle", "t_max_c": None,
  "label": "demonstrated", "after": "S19", "devices": ["QDL-27"], "atlas": ["M00", "M29"],
  "why": "A CMOS chip under the diamond delivers the microwaves, filters out the green pump and detects the red light, shrinking the sensor to one die.",
  "equipment": ["CMOS design tools (open or commercial)", "MPW shuttle (prices in the Machines and Facilities Atlas)", "Microscope for pick-and-place"],
  "params": [("Process and die", "TSMC 65 nm LP; inductor, filter and photodiode stacked in a 200 × 200 µm footprint; a 0.8 × 0.5 mm² die appears in the public-access copy, not in the arXiv text (to confirm)", "[kim2019cmos]"),
             ("On-chip parts", "Three-turn microwave loop in Metal 9; grating filter in Metal 8 absorbing about 95 % of the green; photodiode 0.23 A/W", "[kim2019cmos]"),
             ("Diamond", "CVD, electron-irradiated 1 × 10¹⁸ cm⁻² at 1 MeV and annealed 2 h at 850 °C; about 0.01 ppm NV", "[kim2019cmos]"),
             ("Attach", "Diamond transferred onto the die; pick-and-place with immersion oil appears in the public-access copy, not in the arXiv text (to confirm)", "[kim2019cmos]"),
             ("Operation", "532 nm, 500 mW; 6.27 mT bias", "[kim2019cmos]")],
  "checks": [("ODMR seen on the on-chip photodiode", "", None, None, "[kim2019cmos]"),
             ("Attach temperature, after gold", "°C", None, 500.0, "ADAMAS (traveler rule 1)"),
             ("Magnetic sensitivity", "µT/√Hz", None, KIM2019_TARGET_FACTOR * KIM2019_SENS_UT, "ADAMAS (twice the 32.1 reported [kim2019cmos])")],
  "safety": ["Class 4 laser at 500 mW: interlocked enclosure and laser training."],
  "failures": [("Pump light swamps the photodiode", "Filter layer mis-drawn or the diamond overhangs it", "Check the metal grating in layout review; align the diamond")],
  "silicon": "This step is silicon: the control and readout die is an ordinary CMOS chip."},
]
BY_ID = {x["id"]: x for x in EXTENSIONS}
LABELS = ("demonstrated", "cryogenic", "proposed")


def badge(x: dict) -> str:
    """The evidence label, with "cryogenic" added to a proposal that assumes cryogenic operation."""
    return x["label"] + (" · cryogenic" if x.get("cryogenic") else "")


def to_markdown() -> str:
    """The extension section of docs/process/TRAVELER.md."""
    L = ["## Extension steps (device-specific, outside T1)", "",
         "Eleven devices in the Quantum Device Library add one step to T1. Each is written below with its evidence label: "
         "**demonstrated** (done at room temperature in the cited work), **cryogenic** (the cited result needs cryogenic "
         "operation) or **proposed** (no fabricated device; marked proposed · cryogenic when the proposal assumes cold operation). A parameter the source does not give is marked *to source*.", "",
         "| Step | Title | After | Devices | Label |", "|---|---|---|---|---|"]
    L += [f"| {x['id']} | {x['title']} | {x['after']} | {', '.join(x['devices'])} | {badge(x)} |" for x in EXTENSIONS]
    L.append("")
    for x in EXTENSIONS:
        t = f"peak temperature {x['t_max_c']} °C" if x["t_max_c"] is not None else "peak temperature not given by the source"
        L += [f"### {x['id']} · {x['title']}", "", f"*Evidence: **{badge(x)}** · after {x['after']} · devices {', '.join(x['devices'])} · {t} · Atlas {', '.join(x['atlas'])}*", "",
              f"**Why.** {x['why']}", "", "**Equipment.** " + "; ".join(x["equipment"]) + ".", "",
              "| Parameter | Value | Source |", "|---|---|---|"]
        L += [f"| {a} | {b} | {c} |" for a, b, c in x["params"]]
        L += ["", "| Check | Pass criterion | Source |", "|---|---|---|"]
        for name, unit, lo, hi, src in x["checks"]:
            crit = "pass / fail" if lo is None and hi is None else (f"≥ {lo:g} {unit}" if hi is None else f"≤ {hi:g} {unit}" if lo is None else f"{lo:g} to {hi:g} {unit}")
            L.append(f"| {name} | {crit.strip()} | {src} |")
        L += ["", "**Safety.** " + " ".join(x["safety"]), "", "| Symptom | Likely cause | Action |", "|---|---|---|"]
        L += [f"| {a} | {b} | {c} |" for a, b, c in x["failures"]]
        L += ["", f"**Silicon, for comparison.** {x['silicon']}", ""]
    return "\n".join(L)
