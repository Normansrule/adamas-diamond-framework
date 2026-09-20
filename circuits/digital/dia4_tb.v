`timescale 1ns/1ps
// Program: count down from 5, writing each value to the output port, then halt in a loop.
module dia4_tb;
    reg clk = 0, rst = 1;
    wire [3:0] pc, acc, out_port; wire carry;
    reg [7:0] rom [0:15];
    dia4 dut(.clk(clk), .rst(rst), .instr(rom[pc]), .pc(pc), .acc(acc), .out_port(out_port), .carry(carry));
    always #5 clk = ~clk;
    integer i;
    initial begin
        for (i = 0; i < 16; i = i + 1) rom[i] = 8'h00;
        rom[0] = 8'h15;   // LDI 5
        rom[1] = 8'h90;   // OUT
        rom[2] = 8'h31;   // SUB 1
        rom[3] = 8'h71;   // JNZ 1
        rom[4] = 8'h90;   // OUT (writes 0)
        rom[5] = 8'h85;   // JMP 5 (halt)
        #12 rst = 0;
        #400;
        if (out_port === 4'd0 && acc === 4'd0 && pc === 4'd5) $display("PASS: countdown finished, out=%0d", out_port);
        else $display("FAIL: pc=%0d acc=%0d out=%0d", pc, acc, out_port);
        $finish;
    end
    always @(out_port) if (!rst) $display("t=%0t out_port=%0d", $time, out_port);
endmodule
