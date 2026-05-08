# SPDX-FileCopyrightText: © 2026 The Siliconimist
# SPDX-License-Identifier: Apache-2.0
"""Cocotb tests for the one-digit 7-segment seconds counter.

In RTL simulation, tb.v overrides CLK_DIV from 50_000_000 to 10 so each
simulated "second" takes 10 clock cycles. In gate-level simulation the
parameter has been baked into the synthesized netlist and cannot be
overridden, so the slow tests are skipped (waiting 50M cycles per tick
would take many minutes per test).

Timing note:
    Cocotb's ClockCycles trigger fires on the rising edge BEFORE the
    always @(posedge clk) non-blocking assignments commit. Any wait
    that is followed by a register read therefore uses CLK_DIV + 1
    so that the read lands one cycle after the register has updated.
"""

import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

# True when running against the synthesized gate-level netlist. Set by
# `make GATES=yes`; the Makefile exports the variable for us.
GATES: bool = os.environ.get("GATES") == "yes"

# Number of clock cycles per simulated "second". Must match the override
# of the CLK_DIV parameter in tb.v.
CLK_DIV = 10

# Clock period for the 100 MHz simulation clock.
CLK_PERIOD_NS = 10

# Expected uo_out values for each digit. Bit 7 (decimal point) is always
# off; bits 6:0 are segments G, F, E, D, C, B, A (high = lit).
SEG: dict[int, int] = {
    0: 0b00111111,
    1: 0b00000110,
    2: 0b01011011,
    3: 0b01001111,
    4: 0b01100110,
    5: 0b01101101,
    6: 0b01111101,
    7: 0b00000111,
    8: 0b01111111,
    9: 0b01101111,
}


async def start_and_reset(dut: cocotb.handle.HierarchyObject) -> None:
    """Start the clock, drive inputs to a known state, and pulse reset.

    Leaves the DUT out of reset, with all inputs at 0 and ena high.
    """
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1


@cocotb.test()
async def test_reset_shows_zero(dut: cocotb.handle.HierarchyObject) -> None:
    """After reset, the display must show digit 0."""
    await start_and_reset(dut)
    actual = int(dut.uo_out.value)
    assert actual == SEG[0], (
        f"Expected {SEG[0]:#010b} (digit 0), got {actual:#010b}"
    )


# cocotb.test() # is the default test, so we can skip it if GATES is True
@cocotb.test(skip=GATES)
async def test_counts_0_to_9(dut: cocotb.handle.HierarchyObject) -> None:
    """The display must advance one digit per simulated second, 0 → 9.

    Skipped in gate-level mode because CLK_DIV is fixed at 50_000_000.
    """
    await start_and_reset(dut)

    for expected_digit in range(1, 10):
        await ClockCycles(dut.clk, CLK_DIV + 1)
        actual = int(dut.uo_out.value)
        assert actual == SEG[expected_digit], (
            f"Expected digit {expected_digit} = {SEG[expected_digit]:#010b}, "
            f"got {actual:#010b}"
        )


@cocotb.test(skip=GATES)
async def test_wraps_9_to_0(dut: cocotb.handle.HierarchyObject) -> None:
    """After 10 ticks, the digit must wrap from 9 back to 0.

    Skipped in gate-level mode because CLK_DIV is fixed at 50_000_000.
    """
    await start_and_reset(dut)

    await ClockCycles(dut.clk, CLK_DIV * 10 + 1)
    actual = int(dut.uo_out.value)
    assert actual == SEG[0], (
        f"Expected wrap to digit 0 = {SEG[0]:#010b}, got {actual:#010b}"
    )


@cocotb.test(skip=GATES)
async def test_reset_mid_count(dut: cocotb.handle.HierarchyObject) -> None:
    """Asserting reset mid-count must immediately return the digit to 0.

    Skipped in gate-level mode because CLK_DIV is fixed at 50_000_000.
    """
    await start_and_reset(dut)

    # Advance to digit 4 by waiting four "seconds".
    await ClockCycles(dut.clk, CLK_DIV * 4 + 1)
    assert int(dut.uo_out.value) == SEG[4], (
        f"Setup failed: expected digit 4, got {int(dut.uo_out.value):#010b}"
    )

    # Assert reset and confirm the display goes to 0 while reset is held.
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    assert int(dut.uo_out.value) == SEG[0], (
        f"During reset: expected digit 0, got {int(dut.uo_out.value):#010b}"
    )

    # Release reset and confirm counting resumes from 0 → 1.
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, CLK_DIV + 1)
    assert int(dut.uo_out.value) == SEG[1], (
        f"After reset release: expected digit 1, got {int(dut.uo_out.value):#010b}"
    )


@cocotb.test(skip=GATES)
async def test_segment_encoding(dut: cocotb.handle.HierarchyObject) -> None:
    """Each digit 0–9 must produce the correct 7-segment pattern.

    Catches lookup-table bugs: a counter could pass test_counts_0_to_9
    while still showing the wrong glyph if a single bit in SEG is wrong.

    Skipped in gate-level mode because CLK_DIV is fixed at 50_000_000.
    """
    await start_and_reset(dut)

    for digit in range(10):
        actual = int(dut.uo_out.value)
        expected = SEG[digit]
        assert actual == expected, (
            f"Digit {digit}: expected segments {expected:#010b}, "
            f"got {actual:#010b}"
        )
        await ClockCycles(dut.clk, CLK_DIV + 1)
