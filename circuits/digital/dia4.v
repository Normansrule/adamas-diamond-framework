// DIA-4: a 4-bit accumulator processor small enough for p-channel-only diamond logic.
// v0.3: adds CALL/RET with a four-entry hardware return stack (project D-1), as the Intel 4004 had
// a three-entry one [faggin1996].
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
    reg  [3:0] stack [0:3];       // return addresses; not reset, always written before it is read
    reg  [1:0] sp;                // wraps silently on overflow, like the 4004's
    wire [1:0] sp_m1 = sp - 2'd1;
    always @(posedge clk) begin
        if (rst) begin
            pc <= 4'd0; acc <= 4'd0; out_port <= 4'd0; carry <= 1'b0; sp <= 2'd0;
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
                4'hA: begin stack[sp] <= pc + 4'd1; sp <= sp + 2'd1; pc <= imm; end   // CALL
                4'hB: begin pc <= stack[sp_m1]; sp <= sp_m1; end                    // RET
                default: ;                                          // NOP
            endcase
        end
    end
endmodule
