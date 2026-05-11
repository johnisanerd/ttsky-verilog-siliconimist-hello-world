# Testbench for the Siliconimist Chip1 project

This is the testbench for the Siliconimist Chip1 project — our "hello world" of
Verilog. It follows the first Wokwi project we built to get started and drives
the on-chip clock counter forward so we can confirm it advances one digit per
simulated "second" and wraps from 9 back to 0.

The DUT (`src/project.v`, module `tt_um_the_siliconimist_chip1`) is a one-digit
7-segment seconds counter:

- A clock divider turns the 50 MHz board clock into a 1 Hz `tick`.
- A 4-bit digit counter advances 0 → 9 on each tick and wraps to 0.
- A combinational decoder maps the digit to the 7-segment output bits on `uo_out`.

In RTL simulation `tb.v` overrides `CLK_DIV` from `50_000_000` down to `10` so
each simulated second only takes 10 clock cycles. In gate-level simulation the
parameter is baked into the netlist, so the slow tests are skipped.

The testbench uses [cocotb](https://docs.cocotb.org/en/stable/) to drive the DUT
and check the outputs. For more background on testing TT projects, see the
[Tiny Tapeout testing guide](https://tinytapeout.com/hdl/testing/). For a
write-up of what we learned building this, see
[siliconimist.com](https://siliconimist.com).

## Setting up

1. Edit [Makefile](Makefile) if you need to point `PROJECT_SOURCES` at
   different Verilog files. For this project it is already set to `project.v`.
2. Edit [tb.v](tb.v) if you rename the top module. For this project it
   instantiates `tt_um_the_siliconimist_chip1`.

## How to run

To run the RTL simulation:

```sh
make clean && make -B
```

I NEVER FIGURED THIS OUT --> To run gate-level simulation, first harden your project and copy
`../runs/wokwi/results/final/verilog/gl/{your_module_name}.v` to
`gate_level_netlist.v`.

Then run:

```sh
make clean && make -B GATES=yes
```

We run `make clean` before each build because stale artifacts in `sim_build/`
have bitten us — running clean first guarantees the simulator is rebuilt from
the current sources every time.

If you wish to save the waveform in VCD format instead of FST format, edit
`tb.v` to use `$dumpfile("tb.vcd");` and then run:

```sh
make clean && make -B FST=
```

This will generate `tb.vcd` instead of `tb.fst`.

## How to view the waveform file

Using Surfer:

```sh
surfer tb.fst
```

We started out on GTKWave but ran into enough trouble getting it working on
Apple Silicon that we switched to [Surfer](https://surfer-project.org/). Some of
that analysis — and what we tried before giving up on GTKWave — is written up on
[siliconimist.com](https://siliconimist.com).
