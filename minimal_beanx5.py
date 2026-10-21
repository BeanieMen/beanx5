from migen import *
from litex.gen import *
from litex.build.generic_platform import *
from litex.build.gowin.platform import GowinPlatform
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

_io = [
    ("clk", 0, Pins("E2"), IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("L6"), IOStandard("LVCMOS33")),
    ("serial", 0,
        Subsignal("tx", Pins("C3")),
        Subsignal("rx", Pins("C4")),
        IOStandard("LVCMOS33")
    ),
]
class Platform(GowinPlatform):
    default_clk_name   = "clk"
    default_clk_period = 1e9 / 27e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(self, "GW5A-LV25MG121", _io, toolchain=toolchain)

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=27e6, **kwargs):
        platform = Platform()
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
                         cpu_type="vexriscv", cpu_variant="standard",
                         integrated_rom_size=0x8000,
                         integrated_sram_size=0x8000,
                         **kwargs)
        self.crg = CRG(platform.request("clk"), ~platform.request("cpu_reset"))