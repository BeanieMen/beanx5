# beanx5 

an fpga dev board built around the Gowin Arora V GW5A-25 with an an onboard RISC-V SoC, HDMI, and USB-C

---

## What is this?

beanx5 is a minimalist FPGA dev board powered by the Gowin GW5A-LV25MG121 (23K LUTs). I used Sipeed Tang Primer 25K as a base for components and because the parts work togther as evidenced by it. i didnt like the modular system so i wanted a single board with all of em in under 100$ (hopefully)

---

## Features

- **Gowin GW5A-LV25MG121 FPGA**: 23,040 LUT4 logic cells, DSP blocks, and high-speed PLLs in an 11x11 BGA package.
- **Onboard RISC-V Softcore**: Ships with a working [LiteX](https://github.com/enjoy-digital/litex) SoC running a 32-bit **VexRiscv** CPU at 27 MHz with 32 KB ROM / 32 KB SRAM. 
(note: in the future it is gonna be my own softcore not vexriscv)

- **Direct HDMI/DVI Out**: Differential TMDS pairs wired directly to the FPGA banks for 720p/1080p video generation.
- **USB-C Interface**: Power delivery, UART serial console, and JTAG debugging via a single USB-C cable.
- **MicroSD Card Storage**: Full push-pull slot for loading bitstreams, boot ROMs, or data logging over SPI/SDIO.

---

## Repository Tour

```
beanx5/
├── hardware/
│   ├── datasheets/    # UG985 Pinout table (GW5A-LV25MG121N) in CSV
│   └── pcb/           # KiCad 10 schematic, PCB, and symbol libraries
├── litex/
│   └── minimal_beanx5.py  # LiteX SoC generator targeting the board
├── scripts/
│   └── csv_to_kicad_sym.py # Tool to generate KiCad symbols from pin tables
└── bom.csv            # SMT parts list + JLCPCB assembly cost estimates
```

---


### Prerequisites
- Python 3.10+
- Gowin EDA toolchain (`gw_sh` in your `$PATH`)
- RISC-V GCC toolchain (`riscv64-unknown-elf-gcc` or `riscv64-elf-gcc`)

### 1. Clone & Set Up LiteX
```bash
git clone https://github.com/BeanieMen/beanx5.git
cd beanx5
```

### run litex builder
Run the litex builder to generate the verilog, compile the BIOS and other stuff

```bash
python3 litex/minimal_beanx5.py --build
```

The resulting bitstream will be located at:
```
build/beanx5/gateware/minimal_beanx5.fs
```

---

## scripts for convenience

If you update the pinout CSV:
```bash
python3 scripts/csv_to_kicad_sym.py \
  --csv hardware/datasheets/GW5A-LV25MG121N_KiCad_PinTable_Format.csv \
  --symbol GW5A-LV25MG121N \
  --output hardware/pcb/symbol-table.kicad_sym
```

---

## Built With

- [Gowin Semiconductor](https://www.gowinsemi.com/) (GW5A-25 FPGA)
- [LiteX](https://github.com/enjoy-digital/litex) & [Migen](https://github.com/m-labs/migen)
- [VexRiscv](https://github.com/SpinalHDL/VexRiscv)
- [KiCad](https://www.kicad.org/) (v10.0)
