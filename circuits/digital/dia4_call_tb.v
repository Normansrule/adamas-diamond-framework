`timescale 1ns/1ps
// Nested subroutine test: main calls SUB twice; SUB adds 3 and calls LEAF, which adds 1.  2 + 2*(3+1) = 10.
module dia4_call_tb;
    reg clk = 0, rst = 1;
    wire [3:0] pc, acc, out_port; wire carry;
    reg [7:0] rom [0:15];
    dia4 dut(.clk(clk), .rst(rst), .instr(rom[pc]), .pc(pc), .acc(acc), .out_port(out_port), .carry(carry));
    always #5 clk = ~clk;
    integer i;
    initial begin
        for (i = 0; i < 16; i = i + 1) rom[i] = 8'h00;
        rom[0]  = 8'h12;   // LDI 2
        rom[1]  = 8'hA8;   // CALL SUB
        rom[2]  = 8'hA8;   // CALL SUB
        rom[3]  = 8'h90;   // OUT
        rom[4]  = 8'h84;   // JMP 4 (halt)
        rom[8]  = 8'h23;   // SUB:  ADD 3
        rom[9]  = 8'hAC;   //       CALL LEAF
        rom[10] = 8'hB0;   //       RET
        rom[12] = 8'h21;   // LEAF: ADD 1
        rom[13] = 8'hB0;   //       RET
        #12 rst = 0;
        #300;
        if (out_port === 4'd10 && pc === 4'd4) $display("PASS: nested CALL/RET, out=%0d", out_port);
        else $display("FAIL: pc=%0d acc=%0d out=%0d", pc, acc, out_port);
        $finish;
    end
endmodule
