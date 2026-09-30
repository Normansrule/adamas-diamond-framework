"""Frequency sweep logic for the A1 kit, shared by the Pico firmware and the tests (pure Python)."""
try:
    from adamas.hw.adf4351 import registers, write_order
except ImportError:                          # on the Pico both files sit in the root directory
    from adf4351 import registers, write_order


def frange(start, stop, step):
    n = int(round((stop - start) / step)) + 1
    return [start + k * step for k in range(n)]


def sweep(program, read_adc, start_mhz, stop_mhz, step_mhz, averages, emit, settle=lambda: None, ref_mhz=25.0):
    """For each frequency: program the synthesizer (list of 32-bit words, R5 first), wait, average the detector,
    and emit 'frequency,value'. `program`, `read_adc`, `settle` and `emit` are supplied by the hardware or the tests."""
    for f in frange(start_mhz, stop_mhz, step_mhz):
        regs, info = registers(f, ref_mhz=ref_mhz)
        program(write_order(regs))
        settle()
        total = 0
        for _ in range(averages):
            total += read_adc()
        emit("%.3f,%.6f" % (info["actual_mhz"], total / averages))
    emit("END")
