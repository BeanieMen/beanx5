from migen import *
from litex.gen import *
from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder
import argparse


_io = [
    ("clk", 0, Pins("E2"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("L6"), IOStandard("LVCMOS33")),
    ("serial", 0,
        Subsignal("tx", Pins("C3")),
        Subsignal("rx", Pins("B3")),
        IOStandard("LVCMOS33")
    ),
]

class Platform(GowinPlatform):
    default_clk_name = "clk"
    default_clk_period = 1e9 / 27e6

    def __init__(self, toolchain="gowin"):
        super().__init__(
            "GW5A-LV25MG121NC1/I0",
            _io,
            toolchain=toolchain,
            devicename="GW5A-25A",
        )

        # use the sspi (e2) as gpio after boot
        self.toolchain.options["use_sspi_as_gpio"] = 1
        self.toolchain.options["use_cpu_as_gpio"] = 1


class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=27e6, **kwargs):
        platform = Platform()

        super().__init__(
            platform,
            clk_freq=int(sys_clk_freq),
            cpu_type="vexriscv",
            cpu_variant="standard",
            integrated_rom_size=0x8000,
            integrated_sram_size=0x8000,
            **kwargs
        )

        self.crg = CRG(
            platform.request("clk"),
            ~platform.request("cpu_reset")
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--output-dir", default="build/beanx5")
    parser.add_argument("--sys-clk-freq", type=float, default=27e6)
    args = parser.parse_args()

    soc = BaseSoC(sys_clk_freq=args.sys_clk_freq)

    builder = Builder(
        soc,
        output_dir=args.output_dir
    )

    if args.build:
        builder.build()
    else:
        print("SoC initialized. Use --build to build the FPGA design.")


if __name__ == "__main__":
    main()