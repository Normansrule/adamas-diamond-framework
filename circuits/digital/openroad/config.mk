# OpenROAD-flow-scripts configuration for DIA-4 on ADAMAS-PDK-0 (project P-2).
# Copy this directory to  <ORFS>/flow/designs/adamas/dia4/  and run  make DESIGN_CONFIG=designs/adamas/dia4/config.mk
# Platform files: the LEF and timed Liberty written by circuits/digital/place.py; no tech LEF beyond the one embedded.
export DESIGN_NAME = dia4
export PLATFORM    = adamas_pdk0
export VERILOG_FILES = $(DESIGN_HOME)/adamas/dia4/dia4.v
export SDC_FILE      = $(DESIGN_HOME)/adamas/dia4/constraint.sdc
export TECH_LEF      = $(DESIGN_HOME)/adamas/dia4/adamas_ed.lef
export SC_LEF        = $(DESIGN_HOME)/adamas/dia4/adamas_ed.lef
export LIB_FILES     = $(DESIGN_HOME)/adamas/dia4/adamas_ed_timed.lib
export PLACE_SITE    = core
export CORE_UTILIZATION = 55
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 20
export PLACE_DENSITY = 0.7
export MIN_ROUTING_LAYER = GATE
export MAX_ROUTING_LAYER = METAL2
export TIEHI_CELL_AND_PORT = BUF A
export TIELO_CELL_AND_PORT = INV A
export MIN_BUF_CELL_AND_PORTS = BUF A Y
export ABC_CLOCK_PERIOD_IN_PS = 400000
