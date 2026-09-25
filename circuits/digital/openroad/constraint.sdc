# DIA-4 timing constraints: 2.5 MHz target clock (chapter E3 estimate at 2 um gates).
create_clock -name clk -period 400 [get_ports clk]
set_input_delay  40 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 40 -clock clk [all_outputs]
set_load 2.0 [all_outputs]
