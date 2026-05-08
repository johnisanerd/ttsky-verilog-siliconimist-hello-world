// Copyright (c) 2026 - The Siliconimist
// SPDX-License-Identifier: Apache-2.0
//
// One-digit 7-segment seconds counter for the Tiny Tapeout demo board.
// Displays a single digit 0–9, advancing once per second from a 50 MHz clock.
//
// Architecture:
//   clk (50 MHz) → [clock divider] → tick (1 Hz) → [digit counter 0–9]
//                                                  → [7-segment encoder] → uo_out[6:0]
//
// 7-Segment Display Pinout (uo_out → segment):
//
//          AAA
//         F   B
//         F   B
//          GGG
//         E   C
//         E   C
//          DDD   DP
//
//   uo_out[0] = A  (top)
//   uo_out[1] = B  (top right)
//   uo_out[2] = C  (bottom right)
//   uo_out[3] = D  (bottom)
//   uo_out[4] = E  (bottom left)
//   uo_out[5] = F  (top left)
//   uo_out[6] = G  (middle)
//   uo_out[7] = DP (decimal point, always off)

`default_nettype none

module tt_um_the_siliconimist_chip1 #(
    parameter CLK_DIV = 50_000_000  // override to a small value in simulation
) (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Bidirectional pins are unused — drive outputs low and set all as inputs.
  assign uio_out = 0;
  assign uio_oe  = 0;

  // --- Stage 1: Clock divider ---
  //
  // The TT demo board runs at 50 MHz (CLK_DIV = 50_000_000).
  // We need a 1 Hz signal to advance the display once per second.
  //
  // clk_div counts 0, 1, 2, ... CLK_DIV-1, then resets to 0.
  // tick is a combinational wire that goes HIGH for exactly one clock cycle:
  // the cycle where clk_div reaches its terminal count (CLK_DIV-1).
  //
  // tick is a wire (not a reg) so that it and the digit counter both
  // update on the SAME posedge. If tick were registered, digit would
  // lag one cycle behind every tick, causing the display to advance
  // one clock late.
  //
  // CLK_DIV is a parameter so simulations can override it to a small
  // value (e.g. 10) via the Makefile, making tests run in nanoseconds
  // rather than waiting a full simulated second.
  reg  [25:0] clk_div;
  wire        tick = (clk_div == CLK_DIV - 1);

  always @(posedge clk) begin
    if (!rst_n)    clk_div <= 0;
    else if (tick) clk_div <= 0;
    else           clk_div <= clk_div + 1;
  end

  // --- Stage 2: Second counter ---
  //
  // Counts 0–9 and wraps back to 0 after 9. Advances by 1 on each tick
  // (once per second in hardware). Reset returns it to 0 immediately.
  //
  // 4 bits are sufficient: 9 = 4'b1001. Values 10–15 are unreachable
  // because the wrap condition catches the count at 9.
  reg [3:0] digit;

  always @(posedge clk) begin
    if (!rst_n)
      digit <= 0;
    else if (tick)
      digit <= (digit == 9) ? 0 : digit + 1;
  end

  // --- Stage 3: 7-segment encoder ---
  //
  // Converts the 4-bit digit (0–9) to the 7 segment control bits.
  // This is purely combinational (always @(*)).
  //
  // Bit ordering matches the TT demo board pinout (see header):
  //   seg[0]=A, seg[1]=B, seg[2]=C, seg[3]=D,
  //   seg[4]=E, seg[5]=F, seg[6]=G
  // A HIGH bit lights the corresponding segment.
  reg [6:0] seg;

  always @(*) begin
    case (digit)
      4'd0: seg = 7'b0111111; // A B C D E F   (all but middle)
      4'd1: seg = 7'b0000110; // B C
      4'd2: seg = 7'b1011011; // A B D E G
      4'd3: seg = 7'b1001111; // A B C D G
      4'd4: seg = 7'b1100110; // B C F G
      4'd5: seg = 7'b1101101; // A C D F G
      4'd6: seg = 7'b1111101; // A C D E F G
      4'd7: seg = 7'b0000111; // A B C
      4'd8: seg = 7'b1111111; // all segments
      4'd9: seg = 7'b1101111; // A B C D F G
      default: seg = 7'b0000000; // blank (unreachable for 0–9)
    endcase
  end

  // Concatenate decimal point (off) with the 7 segment bits.
  // uo_out[7] = DP (off), uo_out[6:0] = G F E D C B A
  assign uo_out = {1'b0, seg};

  // Tie off all unused inputs to avoid synthesis warnings.
  wire _unused = &{ena, ui_in, uio_in, 1'b0};

endmodule
