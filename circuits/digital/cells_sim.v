// Behavioral models of the ADAMAS cells, for gate-level simulation of the synthesized netlist.
module BUF(input A, output Y);            assign Y = A;          endmodule
module INV(input A, output Y);            assign Y = ~A;         endmodule
module NAND2(input A, input B, output Y); assign Y = ~(A & B);   endmodule
module NOR2(input A, input B, output Y);  assign Y = ~(A | B);   endmodule
module NOR3(input A, input B, input C, output Y); assign Y = ~(A | B | C); endmodule
module DFF(input CLK, input D, output reg Q); always @(posedge CLK) Q <= D; endmodule
