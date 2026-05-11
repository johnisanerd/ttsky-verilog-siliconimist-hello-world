![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Siliconimist Chip1

**Siliconimist Chip1** is our "hello world" of silicon: a one-digit 7-segment
seconds counter, built in Verilog and headed to a Tiny Tapeout shuttle.

I am  [The Siliconimist](https://siliconimist.com) - John Cole, learning how to design real chips out loud. The plan is simple: start from absolutely nothing, build the smallest interesting thing that can fit on a 1×1 Tiny Tapeout tile, get it manufactured, and write up everything we trip over along the way. We have no prior silicon experience, no special hardware, and no shortcuts - just the [Tiny Tapeout](https://tinytapeout.com) toolchain, a lot of curiosity, and a blog at [siliconimist.com](https://siliconimist.com) where we are documenting the journey lesson by lesson.

The chip itself does exactly one thing, and it does it once per second. A 50 MHz clock from the TT demo board gets divided down to a 1 Hz tick, a 4-bit counter advances 0 to 9 (and wraps back to 0) on every tick, and a combinational decoder turns the current digit into the seven segment-control bits that light up the display on the demo board. The reset button on the demo board snaps the counter back to 0. That's it. No inputs, no bidirectional pins, no clever tricks - just a digit that counts up. For the details on how it works and how to test it, see [docs/info.md](docs/info.md); for how to run the simulation locally, see [test/README.md](test/README.md).

Our journey started where most beginners start: in [Wokwi](https://wokwi.com/), wiring up the counter as a logic-level prototype to convince ourselves the idea was sound. From there we ported the design to Verilog, set up a [cocotb](https://docs.cocotb.org/en/stable/) testbench, and overrided the clock divider so a "second" of simulated time only takes 10 clock cycles. We then ran into the kind of small but real obstacle that every first project has - getting GTKWave to behave on Apple Silicon turned out to be more pain than it was worth, so we switched to [Surfer](https://surfer-project.org/) for waveform viewing and never looked back. 

Each of those steps, from Wokwi prototype to working RTL to picking a waveform viewer, is written up on [siliconimist.com](https://siliconimist.com).  I would say this is so the next person learning this has a slightly easier time than we did, but the documentation to get started is so good and the community is so helpful, I'll be honest, I'm not going to improve it.  At the end of the day, we wrote it up for your amusement, not really to learn anything.  

## What next?

Now we wait.  The shuttle will take a few months, so all we have are hopes, prayers, and the smart engineers at Tiny Tapeout to make it work.  Thoughts and prayers to the team at Tiny Tapeout and Skyworks to make it work.

Let's see if it works.

[![Siliconimist Chip1](./docs/TheSiliconimist.png)](https://siliconimist.com)