// DIA-4: a 4-bit accumulator processor small enough for p-channel-only diamond logic.
// Scale reference: the Intel 4004 (2,300 p-channel transistors) [faggin1996].
// Instruction = {opcode[3:0], operand[3:0]}, fetched from an external read-only memory.
module dia4 (
    input  wire       clk,
    input  wire       rst,        // synchronous, active high
    input  wire [7:0] instr,      // from program memory at address pc
    output reg  [3:0] pc,
    output reg  [3:0] acc,
    output reg  [3:0] out_port,
    output reg        carry
);
    wire [3:0] op  = instr[7:4];
    wire [3:0] imm = instr[3:0];
    wire [4:0] sum  = {1'b0, acc} + {1'b0, imm};
    wire [4:0] diff = {1'b0, acc} - {1'b0, imm};
    always @(posedge clk) begin
        if (rst) begin
            pc <= 4'd0; acc <= 4'd0; out_port <= 4'd0; carry <= 1'b0;
        end else begin
            pc <= pc + 4'd1;
            case (op)
                4'h1: acc <= imm;                                   // LDI
                4'h2: begin acc <= sum[3:0];  carry <= sum[4];  end // ADD
                4'h3: begin acc <= diff[3:0]; carry <= diff[4]; end // SUB
                4'h4: acc <= acc & imm;                             // AND
                4'h5: acc <= acc | imm;                             // OR
                4'h6: acc <= acc ^ imm;                             // XOR
                4'h7: if (acc != 4'd0) pc <= imm;                   // JNZ
                4'h8: pc <= imm;                                    // JMP
                4'h9: out_port <= acc;                              // OUT
                default: ;                                          // NOP
            endcase
        end
    end
endmodule
