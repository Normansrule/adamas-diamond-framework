"""ADAMAS Explorer: one self-contained interactive web page (Plotly from a CDN, everything else inline) that lets anyone
move a slider and watch the framework's core equations respond. Every panel names its sources; the JavaScript
re-implements the same formulas as the Python package, and the test suite checks the two agree at spot values.

Panels: 1 material figures of merit [baliga1982] [baliga1989] [johnson1965] [keyes1972]; 2 on-resistance limit versus
breakdown voltage with measured diamond devices [baliga1982] [saha2021] [saha2022] [saha2023]; 3 dopant ionization
versus temperature [sze2006] [lagrange1998] [koizumi1997]; 4 NV magnetic-resonance spectrum [doherty2013]; 5 NV-NV
coupling and echoed-gate fidelity versus distance [dolde2013] [neumann2010natphys] [delange2010]; 6 converter loss
versus frequency [erickson2020] [baliga1989]; 7 size of a room-temperature quantum computer [gidney2021] [fowler2012].
"""
from __future__ import annotations
import json
from pathlib import Path
from . import materials, power

CSS = """
:root{--ink:#1d2733;--teal:#0fa3b1;--red:#e63946;--gold:#f4a261;--bg:#0b1320;--card:#ffffff}
*{box-sizing:border-box}body{margin:0;font-family:Helvetica,Arial,sans-serif;color:var(--ink);background:#f4f7f9}
header{background:linear-gradient(135deg,#0b1320,#12344a);color:#fff;padding:36px 24px}
header h1{margin:0;font-size:42px;letter-spacing:4px}header p{margin:8px 0 0;color:#9fe8f2;font-size:18px}
nav{display:flex;flex-wrap:wrap;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid #dde3e8;position:sticky;top:0;z-index:2}
nav a{text-decoration:none;color:var(--ink);background:#eef3f6;padding:6px 12px;border-radius:14px;font-size:14px}
main{max-width:1180px;margin:0 auto;padding:16px 24px 60px}
section{background:var(--card);border-radius:14px;padding:20px 22px;margin:22px 0;box-shadow:0 2px 12px rgba(0,0,0,.06)}
section h2{margin:0 0 4px;font-size:24px}.why{color:#4a5a6a;margin:0 0 12px;font-size:15px}
.controls{display:flex;flex-wrap:wrap;gap:16px;margin:8px 0 12px}
.controls label{font-size:14px;display:flex;flex-direction:column;gap:4px;min-width:200px}
input[type=range]{width:220px}select{padding:4px}
.plot{width:100%;height:420px}.src{font-size:12px;color:#5b6775;margin-top:8px}
.level{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}.level button{border:1px solid #cfd8de;background:#fff;border-radius:8px;padding:6px 10px;cursor:pointer}
.level button.on{background:var(--teal);color:#fff;border-color:var(--teal)}
.expl{display:none;padding:10px 12px;border-left:4px solid var(--teal);background:#f3fbfc;border-radius:6px;font-size:15px}.expl.on{display:block}
footer{text-align:center;color:#5b6775;font-size:13px;padding:24px}
"""


def _materials_json() -> str:
    out = {}
    for k, m in materials.MATERIALS.items():
        out[k] = {"eg": m.eg_ev, "ec": m.ec_mv_cm, "mun": m.mu_n, "mup": m.mu_p, "eps": m.eps_r, "vsat": m.vsat_cm_s, "kappa": m.kappa_w_cmk}
    return json.dumps(out)


def _measured_json() -> str:
    return json.dumps({k: {"bv": v["bv_v"], "ron": v["ron_mohm_cm2"]} for k, v in power.MEASURED_DIAMOND.items()})


JS = r"""
const EPS0=8.8541878128e-14, Q=1.602176634e-19, KB=8.617333262e-5, H=4.135667696e-15, C_MHZ_NM3=52.07;
const COL={Si:'#7a8793','4H-SiC':'#e0a030',GaN:'#8a62d6',Ga2O3:'#d65f5f',Diamond:'#0fa3b1'};
const NAME={Si:'Silicon','4H-SiC':'Silicon carbide',GaN:'Gallium nitride',Ga2O3:'Gallium oxide',Diamond:'Diamond'};
const L={margin:{t:30,r:20,b:50,l:60},paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{family:'Helvetica,Arial',size:13}};
function $(id){return document.getElementById(id)}
function v(id){return parseFloat($(id).value)}
// --- level toggles (explanations at three reading levels) ---
document.querySelectorAll('.level').forEach(g=>{g.querySelectorAll('button').forEach(b=>b.onclick=()=>{
 g.querySelectorAll('button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
 const sec=g.parentElement;sec.querySelectorAll('.expl').forEach(e=>e.classList.toggle('on',e.dataset.level===b.dataset.level));});});
document.querySelectorAll('.level button[data-level="kid"]').forEach(b=>b.click());
// --- 1 figures of merit ---
function fom(m,carrier){const mu=carrier==='p'?m.mup:m.mun,eps=m.eps*EPS0,ec=m.ec*1e6;
 return {BFOM:eps*mu*ec**3,BHFFOM:mu*ec*ec,JFOM:(ec*m.vsat/(2*Math.PI))**2,KFOM:m.kappa*Math.sqrt(3e10*m.vsat/(4*Math.PI*eps))}}
function drawFOM(){const carrier=$('fomCarrier').value;const si=fom(MAT.Si,'n');const names=['BFOM','BHFFOM','JFOM','KFOM'];
 const tr=Object.keys(MAT).map(k=>{const f=fom(MAT[k],k==='Diamond'?carrier:'n');return {type:'bar',name:NAME[k],x:names,y:names.map(n=>Math.max(f[n]/si[n],1e-2)),marker:{color:COL[k]}}});
 Plotly.react('fomPlot',tr,{...L,barmode:'group',yaxis:{type:'log',title:'Relative to silicon (log)'},title:'Figures of merit'});}
// --- 2 Ron vs BV ---
function ron(m,bv,carrier){const mu=carrier==='p'?m.mup:m.mun;return 4*bv*bv/(m.eps*EPS0*mu*(m.ec*1e6)**3)*1e3}
function drawRon(){const bv=[];for(let e=2;e<=4.7;e+=0.05)bv.push(10**e);
 const tr=Object.keys(MAT).map(k=>({x:bv,y:bv.map(b=>ron(MAT[k],b,k==='Diamond'?'p':'n')),name:NAME[k]+' limit',line:{color:COL[k],width:3}}));
 tr.push({x:Object.values(MEAS).map(d=>d.bv),y:Object.values(MEAS).map(d=>d.ron),mode:'markers+text',text:Object.keys(MEAS),textposition:'top right',marker:{symbol:'star',size:16,color:'#e63946',line:{color:'#1d2733',width:1}},name:'measured diamond MOSFETs'});
 const t=v('ronT');const k=(t/300)**2.4;tr.push({x:bv,y:bv.map(b=>ron(MAT['4H-SiC'],b,'n')*k),name:`SiC at ${t} K`,line:{color:COL['4H-SiC'],dash:'dot'}});
 Plotly.react('ronPlot',tr,{...L,xaxis:{type:'log',title:'Breakdown voltage (V)'},yaxis:{type:'log',title:'Specific on-resistance (mΩ·cm²)'},title:'On-resistance limit lines'});}
// --- 3 ionization ---
function nv(T,mstar){return 2*(2*Math.PI*mstar*9.109e-31*1.380649e-23*T/(6.626e-34)**2)**1.5*1e-6}
function ionized(ea,na,T,g=4,mstar=0.8){const rhs=nv(T,mstar)/g*Math.exp(-(ea/(KB*T)));let lo=0,hi=na;for(let i=0;i<80;i++){const p=(lo+hi)/2;(p*p/(na-p)>rhs)?hi=p:lo=p;}return (lo+hi)/2/na}
function drawIon(){const na=10**v('ionN');const T=[];for(let t=250;t<=900;t+=5)T.push(t);
 const dop=[['Si:B',0.045,'#7a8793','solid'],['C:B',0.37,'#0fa3b1','solid'],['C:P',0.57,'#0fa3b1','dash'],['C:N',1.7,'#e63946','dot']];
 const tr=dop.map(([n,ea,c,d])=>({x:T,y:T.map(t=>Math.max(ionized(ea,na,t),1e-14)),name:`${n} (${ea} eV)`,line:{color:c,dash:d,width:3}}));
 Plotly.react('ionPlot',tr,{...L,yaxis:{type:'log',title:'Ionized fraction',range:[-13,0.3]},xaxis:{title:'Temperature (K)'},title:`Dopant ionization at ${na.toExponential(0)} cm⁻³`});
 $('ionText').textContent=`At 300 K and this doping, silicon:boron is ${(100*ionized(0.045,na,300)).toFixed(0)}% active; diamond:boron is ${(100*ionized(0.37,na,300)).toFixed(2)}%.`;}
// --- 4 ODMR ---
function drawODMR(){const B=v('odmrB'),th=v('odmrTh')*Math.PI/180,lw=v('odmrLw');const D=2870,g=28.03;const f=[];for(let x=2600;x<=3140;x+=0.5)f.push(x);
 const axes=[[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]].map(a=>a.map(x=>x/Math.sqrt(3)));const b=[B*Math.sin(th),0,B*Math.cos(th)];
 let y=f.map(()=>1);axes.forEach(a=>{const bp=b[0]*a[0]+b[1]*a[1]+b[2]*a[2];const bt2=B*B-bp*bp;
  // second-order perpendicular shift (D - term) keeps the lines honest at large angles [doherty2013]
  [-1,1].forEach(s=>{const f0=D+s*g*bp+ (3*g*g*bt2)/(2*D);f.forEach((x,i)=>{y[i]-=0.075/4*lw*lw/((x-f0)**2+lw*lw)/0.075*0.075});});});
 Plotly.react('odmrPlot',[{x:f,y:y,line:{color:'#0fa3b1',width:2}}],{...L,xaxis:{title:'Microwave frequency (MHz)'},yaxis:{title:'Red fluorescence (normalized)'},title:`Four NV orientations in a ${B.toFixed(1)} mT field at ${v('odmrTh')}° from [111]`});}
// --- 5 coupling & gate ---
function drawGate(){const t2=v('gT2'),dq=$('gDQ').checked?4:1,q=v('gQ');const r=[];for(let x=6;x<=50;x+=0.5)r.push(x);
 const nu=r.map(x=>C_MHZ_NM3/x**3*1e3*dq);const tg=nu.map(n=>1e3/(2*n));const F=tg.map(t=>{const w=Math.exp(-((t/t2)**3));return q*q*(1+w)**2/4+(1-q*q)/4});
 Plotly.react('gatePlot',[{x:r,y:nu,name:'coupling (kHz)',yaxis:'y',line:{color:'#0fa3b1',width:3}},{x:r,y:F,name:'echoed-gate fidelity',yaxis:'y2',line:{color:'#e63946',width:3}},
  {x:[25],y:[0.67],yaxis:'y2',mode:'markers+text',text:['dolde2013: 0.67'],textposition:'bottom right',marker:{symbol:'star',size:16,color:'#f4a261',line:{color:'#1d2733',width:1}},name:'measured'}],
  {...L,xaxis:{title:'NV–NV distance (nm)'},yaxis:{type:'log',title:'Coupling (kHz)'},yaxis2:{title:'Fidelity',overlaying:'y',side:'right',range:[0.2,1.02]},legend:{x:0.55,y:0.15},title:'Two qubits: how close, how good?'});}
// --- 6 converter ---
function coss(m,bv){return m.eps*EPS0*m.ec*1e6/(2*bv)}
function drawConv(){const app={ev:[1200,800,300],dc:[650,400,20],grid:[10000,6500,100]}[$('convApp').value];const [bv,vop,I]=app;const f=[];for(let e=3;e<=6.5;e+=0.05)f.push(10**e);
 const loss=(rsp,c)=>f.map(fr=>2*I*vop*Math.sqrt(fr*rsp*1e-3*c/2));
 const tr=['Si','4H-SiC','GaN','Diamond'].map(k=>({x:f,y:loss(ron(MAT[k],bv,k==='Diamond'?'p':'n'),coss(MAT[k],bv)),name:NAME[k]+' (ideal)',line:{color:COL[k],width:3}}));
 const m=MEAS.saha2022;tr.push({x:f,y:loss(m.ron*(bv/m.bv)**2,coss(MAT.Diamond,bv)),name:'diamond, measured 2022 device',line:{color:'#e63946',dash:'dash',width:3}});
 Plotly.react('convPlot',tr,{...L,xaxis:{type:'log',title:'Switching frequency (Hz)'},yaxis:{type:'log',title:'Loss per switch (W)'},title:`${bv} V devices, ${vop} V bus, ${I} A: area-optimized switch loss`});}
// --- 7 quantum sizing ---
function drawQ(){const cyc=10**v('qCycle');const y=v('qYield')/100;const pitch=v('qPitch');const W={'RSA-2048 (2021)':[20e6,8],'RSA-2048 (2025)':[1e6,168],'FeMoco chemistry':[1e6,96],'100 logical qubits':[57700,1]};
 const rows=Object.entries(W).map(([n,[qb,h]])=>{const cells=Math.ceil(qb/4);const side=Math.sqrt(cells*pitch*pitch/0.6/y)*1e-3;return `<tr><td>${n}</td><td>${qb.toExponential(1)}</td><td>${(h*cyc/1e-6).toExponential(2)} h (${(h*cyc/1e-6/8760).toFixed(2)} years)</td><td>${side.toFixed(1)} mm</td></tr>`});
 $('qTable').innerHTML=`<tr><th>Workload</th><th>Physical qubits</th><th>Wall-clock time</th><th>Die side at ${pitch} µm pitch, ${(y*100).toFixed(0)}% yield</th></tr>`+rows.join('');}
['fomCarrier'].forEach(i=>$(i).onchange=drawFOM);['ronT'].forEach(i=>$(i).oninput=drawRon);$('ionN').oninput=drawIon;
['odmrB','odmrTh','odmrLw'].forEach(i=>$(i).oninput=drawODMR);['gT2','gQ'].forEach(i=>$(i).oninput=drawGate);$('gDQ').onchange=drawGate;
$('convApp').onchange=drawConv;['qCycle','qYield','qPitch'].forEach(i=>$(i).oninput=drawQ);
drawFOM();drawRon();drawIon();drawODMR();drawGate();drawConv();drawQ();
"""


def _section(sid, title, why, controls, plot_id, kid, student, expert, src, extra=""):
    return f"""
<section id="{sid}"><h2>{title}</h2><p class="why">{why}</p>
<div class="level"><button data-level="kid">I am 10</button><button data-level="student">Student</button><button data-level="expert">Researcher</button></div>
<div class="expl" data-level="kid">{kid}</div><div class="expl" data-level="student">{student}</div><div class="expl" data-level="expert">{expert}</div>
<div class="controls">{controls}</div>{f'<div id="{plot_id}" class="plot"></div>' if plot_id else ''}{extra}
<p class="src">Sources: {src}</p></section>"""


def build_html() -> str:
    s = []
    s.append(_section("fom", "1 · Why diamond? Four scorecards", "Engineers rank semiconductors with figures of merit. Move the switch to see diamond scored with holes (what can be built today) or electrons.",
        '<label>Diamond carrier <select id="fomCarrier"><option value="p">holes (boron doped, today)</option><option value="n">electrons (future n-type)</option></select></label>',
        "fomPlot",
        "Each bar says how many times better than silicon a material is at one job. Diamond's bars are the tallest, sometimes by tens of thousands.",
        "BFOM = εμE<sub>c</sub>³ scores conduction loss in a power switch; BHFFOM = μE<sub>c</sub>² switching loss; JFOM the power–frequency product; KFOM the heat-limited switching density. The log axis hides how extreme diamond's 10 MV/cm breakdown field is: it enters cubed.",
        "Values are room-temperature single-crystal numbers with diamond mobilities at the ultrapure upper bound; the figures assume full dopant ionization, which fails in diamond (panel 3), so read them as ceilings and pair them with panel 2's measured points.",
        "[baliga1982] [baliga1989] [johnson1965] [keyes1972] [sze2006] [isberg2002] [wort2008]"))
    s.append(_section("ron", "2 · Power switches: the limit lines and where real diamond sits", "Lower is better. The stars are real diamond transistors; the gap to the teal line is the room left to improve.",
        '<label>Show silicon carbide at temperature (K) <input type="range" id="ronT" min="300" max="600" step="10" value="300"></label>',
        "ronPlot",
        "Every line is the best a material could ever do. The stars are what people have actually built with diamond. They already beat silicon's best-possible line.",
        "R<sub>on,sp</sub> = 4BV²/(εμE<sub>c</sub>³) for a one-sided drift region. The measured 2022 device beats ideal silicon by about 90× and trails ideal SiC; a vertical diamond device at 1% of its own limit would match GaN.",
        "Measured points are lateral hydrogen-terminated NO₂-doped MOSFETs on heteroepitaxial wafers; the 3659 V device's R<sub>on</sub> is derived from its reported Baliga figure of merit. SiC's T<sup>2.4</sup> mobility law is applied to its limit line; diamond's bulk-doped R<sub>on</sub> falls with temperature instead (chapter E9).",
        "[baliga1982] [donato2020] [saha2021] [saha2022] [saha2023] [kimoto2014]"))
    s.append(_section("ion", "3 · The catch: diamond's dopants are deep", "Boron in silicon gives up its hole easily. Boron in diamond holds on. Slide the doping level.",
        '<label>Doping density, 10<sup>x</sup> cm⁻³ <input type="range" id="ionN" min="15" max="20" step="0.25" value="17"></label><span id="ionText" style="align-self:center;font-size:14px"></span>',
        "ionPlot",
        "Adding impurity atoms is how you make a semiconductor conduct. In diamond most of those atoms just sit there at room temperature. Heat wakes them up.",
        "Charge neutrality with a single acceptor level E<sub>A</sub>: p(p+N<sub>D</sub>)/(N<sub>A</sub>−N<sub>D</sub>−p) = (N<sub>V</sub>/g)e<sup>−E<sub>A</sub>/kT</sup>. Boron at 0.37 eV and phosphorus at 0.57 eV are 8 to 13 kT deep at 300 K.",
        "Effective mass 0.8 m<sub>0</sub>, degeneracy 4, no compensation. Above about 3×10<sup>20</sup> cm⁻³ the boron band merges with the valence band and the model no longer applies (metallic conduction, superconductivity). Surface transfer doping sidesteps activation entirely (chapter 3).",
        "[sze2006] [lagrange1998] [koizumi1997] [farrer1969] [ekimov2004] [maier2000]"))
    s.append(_section("odmr", "4 · The qubit's fingerprint: optically detected magnetic resonance", "Shine green light, sweep microwaves, watch the red glow dip. The dips move with the magnetic field, which is why a diamond chip is also a compass.",
        '<label>Magnetic field (mT) <input type="range" id="odmrB" min="0" max="8" step="0.1" value="3"></label><label>Field angle from [111] (°) <input type="range" id="odmrTh" min="0" max="90" step="1" value="35"></label><label>Line width (MHz) <input type="range" id="odmrLw" min="0.3" max="6" step="0.1" value="1.5"></label>',
        "odmrPlot",
        "The NV center glows red. When a microwave hits exactly its note (2.87 GHz), the glow dims a little. A magnet splits that note into two, and the crystal has four kinds of NV pointing different ways, so you can see up to eight dips.",
        "H/h = D(S<sub>z</sub>² − 2/3) + γ<sub>e</sub><b>B</b>·<b>S</b> with D = 2.870 GHz and γ<sub>e</sub> = 28 MHz/mT. Each of the four ⟨111⟩ orientations sees a different projection B<sub>∥</sub>, giving lines at D ± γ<sub>e</sub>B<sub>∥</sub>.",
        "Second-order perpendicular shift 3γ²B<sub>⊥</sub>²/(2D) included; hyperfine structure (2.16 MHz for ¹⁴N) omitted at these line widths. Contrast fixed at 7.5% per orientation for an ensemble. The Python package includes the hyperfine term.",
        "[gruber1997] [doherty2013] [rondin2014] [barry2020]"))
    s.append(_section("gate", "5 · Two qubits talking: distance, coherence, and the real bottleneck", "Magnetic coupling fades as 1/r³. Slide coherence and preparation probability and see which one actually limits the gate.",
        '<label>Echo T₂ (µs) <input type="range" id="gT2" min="20" max="3000" step="10" value="600"></label><label>Preparation probability q <input type="range" id="gQ" min="0.5" max="1" step="0.01" value="1"></label><label>Double-quantum encoding (4× coupling) <input type="checkbox" id="gDQ"></label>',
        "gatePlot",
        "Two qubits feel each other through magnetism, but only when very close. The surprise: even with perfect memory, the gate fails if the qubit was not set up right at the start (that is the q slider).",
        "ν = 52 MHz·nm³/r³; gate time 1/(2ν); with a spin echo the coherence factor is w = exp(−(t/T₂)³) and the Bell fidelity is q²(1+w)²/4 + (1−q²)/4.",
        "With the published pair's parameters (25 nm, 19.7 kHz double-quantum coupling, T₂ 150 and 514 µs) the coherence-limited fidelity is 0.998; the measured 0.67 corresponds to q ≈ 0.75, the NV⁻ charge fraction under green light. See chapter E5, sections E5.1b and E5.1c.",
        "[neumann2010natphys] [dolde2013] [dolde2014] [delange2010] [aslam2013]"))
    s.append(_section("conv", "6 · A real converter: diamond against silicon carbide and gallium nitride", "Pick an application. Loss per switch at the optimum die area scales as √(R·C·f).",
        '<label>Application <select id="convApp"><option value="ev">EV traction inverter (800 V, 300 A)</option><option value="dc">Data-center supply (400 V, 20 A)</option><option value="grid">Medium-voltage grid (6.5 kV, 100 A)</option></select></label>',
        "convPlot",
        "A power switch wastes energy two ways: resistance while on, and charging its own capacitance every time it flips. The best material wastes the least of both.",
        "P<sub>min</sub> = 2IV√(fR<sub>on,sp</sub>C<sub>oss,sp</sub>/2) with C<sub>oss,sp</sub> ≈ εE<sub>c</sub>/(2BV). Gate charge, reverse recovery, and GaN dynamic R<sub>on</sub> are not modeled.",
        "Hard-switched half-bridge, duty 0.5, area-optimized per switch. The measured diamond curve scales the 2022 device's R<sub>on,sp</sub> as BV² to the chosen voltage class. Ideal diamond is a ceiling; today's device beats ideal silicon and trails ideal SiC. Chapter E9.",
        "[erickson2020] [kassakian2023] [baliga1989] [huang2004] [shenai2018] [reimers2019] [saha2022]"))
    s.append(_section("qsize", "7 · How big is a room-temperature quantum computer?", "Slide the error-correction cycle time (set by readout) and the cell yield.",
        '<label>Cycle time, 10<sup>x</sup> s <input type="range" id="qCycle" min="-7" max="-1" step="0.25" value="-3"></label><label>Working-cell yield (%) <input type="range" id="qYield" min="1" max="100" step="1" value="50"></label><label>Cell pitch (µm) <input type="range" id="qPitch" min="0.5" max="5" step="0.1" value="1"></label>',
        None,
        "Even a giant quantum computer would fit on a fingernail of diamond. The problem is speed: reading a diamond qubit takes about a thousand times longer than a superconducting one, so big jobs take years instead of hours.",
        "Physical qubits from published surface-code estimates; 4 qubits per NV cell; time scales linearly with the cycle. Area is never the constraint; readout time and yield are.",
        "Wall-clock times assume the published qubit counts at 10⁻³ physical error and a 1 µs reference cycle. Electrical readout (proposed, 100 µs) would bring a year down to a month. Chapter E10.",
        "[gidney2021] [gidney2025] [babbush2018] [fowler2012] [google2025] [neumann2010science] [hopper2018]",
        extra='<table id="qTable" style="width:100%;border-collapse:collapse;font-size:14px"></table><style>#qTable td,#qTable th{border-bottom:1px solid #e3e8ec;padding:6px;text-align:left}</style>'))
    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in [("fom", "Scorecards"), ("ron", "Power switches"), ("ion", "Doping"), ("odmr", "NV fingerprint"), ("gate", "Two qubits"), ("conv", "Converter"), ("qsize", "Machine size")])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ADAMAS Explorer</title><style>{CSS}</style><script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script></head><body>
<header><h1>ADAMAS</h1><p>Explorer: the diamond-wafer framework's equations, live. Pick your reading level in each panel.</p></header>
<nav>{nav}<a href="https://github.com/Normansrule/adamas-diamond-framework">Repository</a><a href="../README.md">Chapters</a></nav>
<main>{''.join(s)}</main>
<footer>Every formula here is the same one in the Python package (tests check them at spot values). Bibliography keys resolve in references/REFERENCES.md.</footer>
<script>const MAT={_materials_json()};const MEAS={_measured_json()};{JS}</script></body></html>"""


def write(path: str | Path) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_html(), encoding="utf-8")
    return path
