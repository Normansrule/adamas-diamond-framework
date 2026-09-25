# ORFS platform definition for ADAMAS-PDK-0. Copy this directory to  <ORFS>/flow/platforms/adamas_pdk0/  together with
# adamas_ed.lef and adamas_ed_timed.lib (written by circuits/digital/place.py).
export PLATFORM = adamas_pdk0
export PROCESS = 2000
export TECH_LEF = $(PLATFORM_DIR)/adamas_ed.lef
export SC_LEF   = $(PLATFORM_DIR)/adamas_ed.lef
export LIB_FILES = $(PLATFORM_DIR)/adamas_ed_timed.lib
export PLACE_SITE = core
export MIN_ROUTING_LAYER = GATE
export MAX_ROUTING_LAYER = METAL2
export IO_PLACER_H = METAL2
export IO_PLACER_V = GATE
export TIEHI_CELL_AND_PORT = BUF A
export TIELO_CELL_AND_PORT = INV A
export MIN_BUF_CELL_AND_PORTS = BUF A Y
export ABC_DRIVER_CELL = BUF
export ABC_LOAD_IN_FF = 1
export FILL_CELLS =
export TAPCELL_TCL =
export MACRO_PLACE_HALO = 10 10
export PLACE_PINS_ARGS = -min_distance 4
export CELL_PAD_IN_SITES_GLOBAL_PLACEMENT = 0
export CELL_PAD_IN_SITES_DETAIL_PLACEMENT = 0
