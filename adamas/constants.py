"""Physical constants (CODATA 2018 values, SI units unless noted)."""
import math

H = 6.62607015e-34            # Planck constant, J s
HBAR = H / (2 * math.pi)      # reduced Planck constant, J s
KB = 1.380649e-23             # Boltzmann constant, J/K
KB_EV = 8.617333262e-5        # Boltzmann constant, eV/K
Q = 1.602176634e-19           # elementary charge, C
M0 = 9.1093837015e-31         # electron rest mass, kg
EPS0 = 8.8541878128e-12       # vacuum permittivity, F/m
MU0 = 1.25663706212e-6        # vacuum permeability, N/A^2
MU_B = 9.2740100783e-24       # Bohr magneton, J/T
G_E = 2.0028                  # NV ground-state electron g-factor [doherty2013]
GAMMA_E_HZ_PER_T = G_E * MU_B / H          # about 28.03 GHz/T [doherty2013]
GAMMA_E_MHZ_PER_G = GAMMA_E_HZ_PER_T * 1e-10  # about 2.803 MHz/G
