"""ADF4351 wideband synthesizer (35 MHz to 4.4 GHz) register calculator for the A1 ODMR kit.

Pure Python with no imports, so this exact file also runs on a Raspberry Pi Pico under MicroPython. Register layout
follows the Analog Devices ADF4351 data sheet: six 32-bit registers written R5 first, R0 last; RF_out = f_PFD x
(INT + FRAC/MOD) / RF_divider with the VCO (2.2 to 4.4 GHz) in fundamental feedback. Defaults reproduce the widely used
evaluation-board values (R2 = 0x18004E42, R3 = 0x000004B3, R4 = 0x008C803C for divider 1, R5 = 0x00580005), which the
test suite checks. Check against the data sheet before changing charge-pump or loop-filter related bits.
"""

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def registers(f_out_mhz, ref_mhz=25.0, r_counter=1, step_khz=100, power=3, muxout=6):
    """Return (list of six register words R0..R5, dict of the settings actually used)."""
    if not 35.0 <= f_out_mhz <= 4400.0:
        raise ValueError("ADF4351 output range is 35 MHz to 4.4 GHz")
    pfd = ref_mhz / r_counter
    div_sel, div = 0, 1
    while f_out_mhz * div < 2200.0:           # choose the RF divider that puts the VCO in 2.2 to 4.4 GHz
        div *= 2; div_sel += 1
    vco = f_out_mhz * div
    mod = int(round(pfd * 1000 / step_khz))   # channel spacing sets the modulus
    mod = max(2, min(4095, mod))
    n = vco / pfd
    int_ = int(n); frac = int(round((n - int_) * mod))
    if frac == mod:
        int_ += 1; frac = 0
    g = _gcd(frac, mod) if frac else mod
    frac_r, mod_r = (frac // g, mod // g) if frac else (0, 2)
    prescaler = 1 if int_ >= 75 else 0        # 8/9 prescaler needs INT >= 75; 4/5 allows down to 23
    if int_ < (75 if prescaler else 23):
        raise ValueError("INT below the prescaler minimum; lower the PFD frequency")
    bscd = min(255, max(1, int(-(-pfd * 1000 // 125))))    # band-select clock at or below 125 kHz
    r0 = (int_ << 15) | (frac_r << 3) | 0
    r1 = (prescaler << 27) | (1 << 15) | (mod_r << 3) | 1
    r2 = (muxout << 26) | (r_counter << 14) | (7 << 9) | (1 << 6) | 2
    r3 = (150 << 3) | 3
    r4 = (1 << 23) | (div_sel << 20) | (bscd << 12) | (1 << 5) | (power << 3) | 4
    r5 = (1 << 22) | (3 << 19) | 5
    actual = pfd * (int_ + frac_r / mod_r) / div
    return [r0, r1, r2, r3, r4, r5], {"pfd_mhz": pfd, "int": int_, "frac": frac_r, "mod": mod_r, "divider": div,
                                       "prescaler": "8/9" if prescaler else "4/5", "vco_mhz": vco, "actual_mhz": actual, "bscd": bscd}


def write_order(regs):
    """The ADF4351 must be programmed R5, R4, R3, R2, R1, R0."""
    return [regs[5], regs[4], regs[3], regs[2], regs[1], regs[0]]
