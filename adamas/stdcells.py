"""ADAMAS-PDK-0 standard-cell library (project P-2): layouts, LEF abstracts, and a timed Liberty file.

Cells are enhancement/depletion p-channel logic [liu2017], [meadconway1980]: every gate is a pull-up network of
enhancement transistors from the driver rail plus one depletion load to VSS (rails are negative in the laboratory,
positive in the abstract view). Row height 30 um, pitch 2 um (lambda = 1 um, chapter E2). Timing is computed from the
first-order model of adamas.digital [rabaey2003] with the ring-oscillator calibration of chapter E3 (the SPICE stage
delay is 0.68x the hand formula); it is a model, not a measurement, and experiment D-2 replaces it.

LEF/DEF conventions: [weste2011]. Liberty tables are 3 x 3 non-linear delay models indexed by input slew and load.
"""
from __future__ import annotations
from dataclasses import dataclass
from . import digital, pdk0
from .logic import Fet

ROW_HEIGHT_UM = 30.0
PITCH_UM = 2.0
SPICE_CALIBRATION = 2.2 / 3.3            # ngspice ring oscillator vs hand model, chapter E3
DRIVER = Fet(mu_cm2_vs=150, vth=1.5, w_um=16.0, l_um=2.0)
LOAD = Fet(mu_cm2_vs=150, vth=-2.0, w_um=2.0, l_um=2.0)

# name: (inputs, function, number of driver transistors in the pull-up, width in pitches)
CELLS = {
    "BUF": (["A"], "A", 2, 10), "INV": (["A"], "A'", 1, 7), "NAND2": (["A", "B"], "(A*B)'", 2, 10),
    "NOR2": (["A", "B"], "(A+B)'", 2, 10), "NOR3": (["A", "B", "C"], "(A+B+C)'", 3, 13), "DFF": (["D", "CLK"], None, 20, 40),
    "TIEHI": ([], "1", 1, 5), "TIELO": ([], "0", 1, 5), "FILL1": ([], None, 0, 1),
}
LOGIC_CELLS = [n for n in CELLS if n not in ("TIEHI", "TIELO", "FILL1")]
PIN_Y = (9.0, 19.0)                       # pins span three horizontal METAL2 tracks (y = 10, 14, 18)
TRACK_OFFSET, TRACK_PITCH = 2.0, 4.0      # both routing layers


def out_pin(name: str) -> str:
    return "Q" if name == "DFF" else "Y"


def geometry(name: str) -> dict:
    """Shapes shared by the GDS layout and the LEF abstract. All coordinates in um, origin lower left."""
    inputs, fn, n_drv, wp = CELLS[name]
    w = wp * PITCH_UM
    g = {"w": w, "rails": {"VDD": (0, ROW_HEIGHT_UM - 3, w, ROW_HEIGHT_UM), "VSS": (0, 0, w, 3)}, "pins": {}, "devices": [], "gates": []}
    if name == "FILL1":
        return g
    step = 12 if name == "DFF" else 11
    n_place = 6 if name == "DFF" else min(max(n_drv, 1), 3)
    x = 3.0
    if name not in ("TIEHI", "TIELO"):
        for _ in range(n_place):
            g["devices"].append((x, x + 3, x + 7, x + 10)); g["gates"].append((x + 4, 6, x + 6, 24)); x += step
    g["gates"].append((w - 5, 6, w - 3, 24))                                      # depletion load (the tie device)
    for i, pin in enumerate(inputs):
        c = 6 + 4 * i
        g["pins"][pin] = (c - 1, PIN_Y[0], c + 1, PIN_Y[1])
    c = w - 4 if name not in ("TIEHI", "TIELO") else 6
    g["pins"][out_pin(name)] = (c - 1, PIN_Y[0], c + 1, PIN_Y[1])
    return g


@dataclass(frozen=True)
class CellTiming:
    c_in_f: float
    delay_ns: list          # 3 x 3, by slew then load
    slew_ns: list


def _delay(gate: digital.EDGate, c_load_f: float, slew_in_ns: float) -> float:
    g = gate
    t_rise = c_load_f * g.vdd / 2 / g.i_load_a
    t_fall = c_load_f * g.vdd / 2 / (g.i_driver_a - g.i_load_a)
    return (0.5 * (t_rise + t_fall) * SPICE_CALIBRATION + 0.25 * slew_in_ns * 1e-9) * 1e9


def timing(name: str) -> CellTiming:
    inputs, fn, n_drv, _ = CELLS[name]
    c_in = digital.gate_capacitance_f(DRIVER)
    # series pull-up (NAND) is slower by the number of stacked drivers; NOR pull-ups are parallel
    series = n_drv if name.startswith("NAND") else 1
    drv = Fet(mu_cm2_vs=150, vth=1.5, w_um=DRIVER.w_um / series, l_um=2.0)
    gate = digital.EDGate(driver=drv, load=LOAD, vdd=10.0, fanout=0, c_wire_f=0.0)
    loads = [c_in, 3 * c_in, 10 * c_in]
    slews = [0.5, 2.0, 8.0]
    delay = [[_delay(gate, cl, s) for cl in loads] for s in slews]
    slew = [[0.8 * d for d in row] for row in delay]
    return CellTiming(c_in, delay, slew)


def cell_layout(name: str) -> pdk0.Cell:
    """Placeable cell drawn from geometry(): rails and pins on METAL2, transistors as OHMIC/GATE/ENH."""
    g = geometry(name)
    c = pdk0.Cell(name)
    for rect in g["rails"].values():
        c.box("METAL2", *rect)
    for s0, s1, d0, d1 in g["devices"]:
        c.box("OHMIC", s0, 8, s1, 22); c.box("OHMIC", d0, 8, d1, 22); c.box("ENH", s1 + 1, 8, d0 - 1, 22)
    for rect in g["gates"]:
        c.box("GATE", *rect)
    for pin, rect in g["pins"].items():
        c.box("METAL2", *rect); c.text((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2, pin)
    return c


def write_tech_lef(path: str) -> None:
    """Technology LEF: units, site, two routing layers (GATE vertical, METAL2 horizontal), one cut layer, one via.
    Sheet resistances: 0.1 ohm/sq for the gate metal and 0.05 ohm/sq for gold (order-of-magnitude, chapter E2)."""
    L = ["VERSION 5.8 ;", 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', "", "UNITS", "  DATABASE MICRONS 1000 ;", "END UNITS", "",
         "MANUFACTURINGGRID 0.005 ;", "",
         "SITE core", "  CLASS CORE ;", "  SYMMETRY Y ;", f"  SIZE {PITCH_UM} BY {ROW_HEIGHT_UM} ;", "END core", "",
         "LAYER GATE", "  TYPE ROUTING ;", "  DIRECTION VERTICAL ;", f"  PITCH {TRACK_PITCH} ;", f"  OFFSET {TRACK_OFFSET} ;",
         "  WIDTH 2 ;", "  SPACING 2 ;", "  RESISTANCE RPERSQ 0.1 ;", "  CAPACITANCE CPERSQDIST 5e-05 ;", "END GATE", "",
         "LAYER CONT", "  TYPE CUT ;", "  SPACING 2 ;", "  WIDTH 1 ;", "  RESISTANCE 1 ;", "END CONT", "",
         "LAYER METAL2", "  TYPE ROUTING ;", "  DIRECTION HORIZONTAL ;", f"  PITCH {TRACK_PITCH} ;", f"  OFFSET {TRACK_OFFSET} ;",
         "  WIDTH 2 ;", "  SPACING 2 ;", "  RESISTANCE RPERSQ 0.05 ;", "  CAPACITANCE CPERSQDIST 5e-05 ;", "END METAL2", "",
         "VIA CONT_GATE_METAL2 DEFAULT", "  LAYER GATE ;", "    RECT -1 -1 1 1 ;", "  LAYER CONT ;", "    RECT -0.5 -0.5 0.5 0.5 ;",
         "  LAYER METAL2 ;", "    RECT -1 -1 1 1 ;", "END CONT_GATE_METAL2", "", "END LIBRARY", ""]
    open(path, "w").write("\n".join(L))


def write_lef(path: str) -> None:
    """Macro (cell) LEF. Obstructions cover only the transistor gate stripes, so vertical routing on GATE can cross cells."""
    L = ["VERSION 5.8 ;", 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', ""]
    r = lambda t: f"{t[0]:g} {t[1]:g} {t[2]:g} {t[3]:g}"                       # noqa: E731
    for name, (inputs, fn, n_drv, wp) in CELLS.items():
        g = geometry(name)
        L += [f"MACRO {name}", "  CLASS CORE ;" if name != "FILL1" else "  CLASS CORE SPACER ;", "  ORIGIN 0 0 ;",
              f"  FOREIGN {name} 0 0 ;", f"  SIZE {g['w']:g} BY {ROW_HEIGHT_UM:g} ;", "  SYMMETRY X Y ;", "  SITE core ;"]
        for pin, rect in g["pins"].items():
            direction = "OUTPUT" if pin == out_pin(name) else "INPUT"
            use = "CLOCK" if pin == "CLK" else "SIGNAL"
            L += [f"  PIN {pin}", f"    DIRECTION {direction} ;", f"    USE {use} ;", "    PORT", "      LAYER METAL2 ;",
                  f"        RECT {r(rect)} ;", "    END", f"  END {pin}"]
        for net, use in (("VDD", "POWER"), ("VSS", "GROUND")):
            L += [f"  PIN {net}", "    DIRECTION INOUT ;", f"    USE {use} ;", "    SHAPE ABUTMENT ;", "    PORT", "      LAYER METAL2 ;",
                  f"        RECT {r(g['rails'][net])} ;", "    END", f"  END {net}"]
        if g["gates"]:
            L += ["  OBS", "    LAYER GATE ;"] + [f"      RECT {r(t)} ;" for t in g["gates"]] + ["  END"]
        L += [f"END {name}", ""]
    L += ["END LIBRARY", ""]
    open(path, "w").write("\n".join(L))


def write_liberty(path: str) -> None:
    idx = "index_1(\"0.5, 2.0, 8.0\"); index_2(\"{0:.6g}, {1:.6g}, {2:.6g}\");"
    out = ["library(adamas_ed_timed) {", "  technology(cmos); delay_model : table_lookup;",
           "  time_unit : \"1ns\"; voltage_unit : \"1V\"; current_unit : \"1mA\"; capacitive_load_unit(1, ff);",
           "  pulling_resistance_unit : \"1kohm\"; leakage_power_unit : \"1uW\";",
           "  nom_voltage : 10; nom_temperature : 25; nom_process : 1;",
           "  operating_conditions(typ) { process : 1; voltage : 10; temperature : 25; } default_operating_conditions : typ;",
           "  default_input_pin_cap : 0.6; default_output_pin_cap : 0; default_fanout_load : 1; default_max_transition : 20;",
           "  slew_lower_threshold_pct_rise : 20; slew_upper_threshold_pct_rise : 80; slew_lower_threshold_pct_fall : 20; slew_upper_threshold_pct_fall : 80;",
           "  input_threshold_pct_rise : 50; input_threshold_pct_fall : 50; output_threshold_pct_rise : 50; output_threshold_pct_fall : 50;",
           "  lu_table_template(t33) { variable_1 : input_net_transition; variable_2 : total_output_net_capacitance; index_1(\"0.5, 2.0, 8.0\"); index_2(\"1, 3, 10\"); }"]
    for name in ("TIEHI", "TIELO", "FILL1"):
        fn = CELLS[name][1]
        out += [f"  cell({name}) {{", f"    area : {CELLS[name][3] * PITCH_UM * ROW_HEIGHT_UM / 60:.3g};"]
        if fn is not None:
            out += [f"    pin(Y) {{ direction : output; function : \"{fn}\"; }}"]
        else:
            out += ["    dont_use : true;"]
        out += ["  }"]
    for name in LOGIC_CELLS:
        inputs, fn, n_drv, wp = CELLS[name]
        t = timing(name)
        cin_ff = t.c_in_f * 1e15
        loads = [cin_ff, 3 * cin_ff, 10 * cin_ff]
        area = 2 + (n_drv if name != "DFF" else 20)
        out += [f"  cell({name}) {{", f"    area : {area};", f"    cell_leakage_power : {digital.EDGate().static_power_w() * 1e6:.3g};"]
        if name == "DFF":
            out += ["    ff(IQ, IQN) { clocked_on : \"CLK\"; next_state : \"D\"; }"]
        for pin in inputs:
            extra = " clock : true;" if pin == "CLK" else ""
            if name == "DFF" and pin == "D":
                out += [f"    pin(D) {{ direction : input; capacitance : {cin_ff:.4g};",
                        "      timing() { related_pin : \"CLK\"; timing_type : setup_rising; rise_constraint(scalar) { values(\"2.0\"); } fall_constraint(scalar) { values(\"2.0\"); } }",
                        "      timing() { related_pin : \"CLK\"; timing_type : hold_rising; rise_constraint(scalar) { values(\"0.5\"); } fall_constraint(scalar) { values(\"0.5\"); } } }"]
            else:
                out += [f"    pin({pin}) {{ direction : input; capacitance : {cin_ff:.4g};{extra} }}"]
        def table(rows):
            body = " \\\n".join('"' + ", ".join(f"{v:.4g}" for v in r) + '"' for r in rows)
            return f"index_1(\"0.5, 2.0, 8.0\"); index_2(\"{loads[0]:.4g}, {loads[1]:.4g}, {loads[2]:.4g}\"); values({body});"
        ypin = "Q" if name == "DFF" else "Y"
        func = "IQ" if name == "DFF" else fn
        out += [f"    pin({ypin}) {{ direction : output; function : \"{func}\"; max_capacitance : {10 * cin_ff:.4g};"]
        related = ["CLK"] if name == "DFF" else inputs
        for r in related:
            kind = " timing_type : rising_edge;" if name == "DFF" else ""
            out += [f"      timing() {{ related_pin : \"{r}\";{kind}",
                    f"        cell_rise(t33) {{ {table(t.delay_ns)} }}", f"        cell_fall(t33) {{ {table(t.delay_ns)} }}",
                    f"        rise_transition(t33) {{ {table(t.slew_ns)} }}", f"        fall_transition(t33) {{ {table(t.slew_ns)} }}", "      }"]
        out += ["    }"]
        out += ["  }"]
    out.append("}")
    open(path, "w").write("\n".join(out) + "\n")
