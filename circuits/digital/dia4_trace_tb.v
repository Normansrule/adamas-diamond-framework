`timescale 1ns/1ps
// Trace testbench: loads rom.hex, prints "pc acc out carry" after every clock for 40 cycles.
// Used by tests/test_web.py to check the JavaScript emulator (web/assets/sim/dia4.js) cycle by cycle.
module dia4_trace_tb;
    reg clk = 0, rst = 1;
    wire [3:0] pc, acc, out_port; wire carry;
    reg [7:0] rom [0:15];
    integer i;
    dia4 dut(.clk(clk), .rst(rst), .instr(rom[pc]), .pc(pc), .acc(acc), .out_port(out_port), .carry(carry));
    always #5 clk = ~clk;
    initial begin
        $readmemh("rom.hex", rom);
        #12 rst = 0;
        for (i = 0; i < 40; i = i + 1) begin
            @(posedge clk); #1 $display("%0d %0d %0d %0d", pc, acc, out_port, carry);
        end
        $finish;
    end
endmodule
