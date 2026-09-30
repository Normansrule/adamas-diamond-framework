# ADAMAS A1 ODMR kit firmware for a Raspberry Pi Pico (MicroPython).
# Copy adf4351.py, odmr_sweep.py (from adamas/hw/) and this file to the Pico:  see hardware/a1_odmr/README.md
# Serial protocol (USB):  host sends  "SWEEP 2800 2940 0.5 64\n"  (start MHz, stop MHz, step MHz, averages)
#                          Pico replies with lines "frequency_MHz,adc_volts" and a final "END".
import sys
import time
from machine import ADC, Pin, SPI
from odmr_sweep import sweep

spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
le = Pin(17, Pin.OUT, value=1)          # ADF4351 latch enable
ce = Pin(20, Pin.OUT, value=1)          # ADF4351 chip enable
adc = ADC(26)                           # GP26 = ADC0 <- transimpedance amplifier output (0 to 3.3 V)
led = Pin(25, Pin.OUT)


def program(words):
    for w in words:
        le.value(0)
        spi.write(bytes([(w >> 24) & 0xFF, (w >> 16) & 0xFF, (w >> 8) & 0xFF, w & 0xFF]))
        le.value(1)


def read_adc():
    return adc.read_u16() * 3.3 / 65535


def emit(line):
    sys.stdout.write(line + "\n")


while True:
    cmd = sys.stdin.readline().strip().split()
    if len(cmd) == 5 and cmd[0] == "SWEEP":
        led.value(1)
        sweep(program, read_adc, float(cmd[1]), float(cmd[2]), float(cmd[3]), int(cmd[4]), emit, settle=lambda: time.sleep_ms(2))
        led.value(0)
    elif cmd and cmd[0] == "PING":
        emit("ADAMAS-A1 OK")
