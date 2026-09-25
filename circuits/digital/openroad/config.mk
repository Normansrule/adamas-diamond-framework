# OpenROAD-flow-scripts configuration for DIA-4 on ADAMAS-PDK-0 (project P-2).
# Copy this directory to  <ORFS>/flow/designs/adamas/dia4/  and run  make DESIGN_CONFIG=designs/adamas/dia4/config.mk
# Platform files (LEF, Liberty) live in platform/config.mk -> <ORFS>/flow/platforms/adamas_pdk0/.
export DESIGN_NAME = dia4
export PLATFORM    = adamas_pdk0
export VERILOG_FILES = $(DESIGN_HOME)/adamas/dia4/dia4.v
export SDC_FILE      = $(DESIGN_HOME)/adamas/dia4/constraint.sdc
export CORE_UTILIZATION = 55
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 20
export PLACE_DENSITY = 0.7
export ABC_CLOCK_PERIOD_IN_PS = 400000
