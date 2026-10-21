#!/usr/bin/env python3
"""
csv_to_kicad_sym.py

A general-purpose tool to generate or update KiCad (.kicad_sym) symbols from pinout CSV files.

Supported CSV column headers (case-insensitive):
  - Number (or Pin, Pin Number)
  - Name (or Pin Name)
  - Electrical Type (or Type)
  - Unit (optional, defaults to 1)

Usage:
  python3 scripts/csv_to_kicad_sym.py --csv <path_to_csv> --symbol <symbol_name> --output <path_to_kicad_sym>
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List

# KiCad electrical type mapping
TYPE_MAP = {
    'input': 'input',
    'output': 'output',
    'bidirectional': 'bidirectional',
    'tri_state': 'tri_state',
    'passive': 'passive',
    'power input': 'power_in',
    'power output': 'power_out',
    'power_in': 'power_in',
    'power_out': 'power_out',
    'open collector': 'open_collector',
    'open emitter': 'open_emitter',
    'free': 'no_connect',
    'no connect': 'no_connect',
    'no_connect': 'no_connect',
    'unspecified': 'unspecified',
}

def normalize_field_names(fieldnames: List[str]) -> Dict[str, str]:
    mapping = {}
    for f in fieldnames:
        clean = f.strip().lower().replace('_', ' ')
        if clean in ('number', 'pin', 'pin number', 'num'):
            mapping['number'] = f
        elif clean in ('name', 'pin name', 'signal'):
            mapping['name'] = f
        elif clean in ('electrical type', 'type', 'pin type'):
            mapping['type'] = f
        elif clean in ('unit', 'sub unit', 'gate'):
            mapping['unit'] = f
    return mapping

def generate_symbol_sexp(
    symbol_name: str,
    pins: List[Dict[str, str]],
    reference_prefix: str = "U",
    pin_pitch: float = 2.54,
    pin_length: float = 5.08,
    box_half_width: float = 40.64,
) -> str:
    # Organize pins by unit
    units: Dict[str, List[Dict[str, str]]] = {}
    for p in pins:
        unit = str(p.get('unit', '1')).strip() or '1'
        units.setdefault(unit, []).append(p)

    sorted_units = sorted(units.keys(), key=lambda u: int(u) if u.isdigit() else u)

    lines = [
        '(kicad_symbol_lib',
        '\t(version 20251024)',
        '\t(generator "csv_to_kicad_sym")',
        '\t(generator_version "10.0")',
        f'\t(symbol "{symbol_name}"',
        '\t\t(exclude_from_sim no)',
        '\t\t(in_bom yes)',
        '\t\t(on_board yes)',
        '\t\t(in_pos_files yes)',
        '\t\t(duplicate_pin_numbers_are_jumpers no)',
        f'\t\t(property "Reference" "{reference_prefix}" (at 0 0 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))',
        f'\t\t(property "Value" "{symbol_name}" (at 0 -2.54 0) (show_name no) (do_not_autoplace no) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))',
        f'\t\t(property "Description" "{symbol_name}" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes) (effects (font (size 1.27 1.27))))',
    ]

    for unit in sorted_units:
        unit_pins = units[unit]
        n_pins = len(unit_pins)
        box_half_h = round(((n_pins + 1) * pin_pitch) / 2.0, 2)
        top_y = box_half_h
        bottom_y = -box_half_h
        left_x = -box_half_width
        right_x = box_half_width

        lines.append(f'\t\t(symbol "{symbol_name}_{unit}_1"')
        lines.append('\t\t\t(rectangle')
        lines.append(f'\t\t\t\t(start {left_x} {top_y})')
        lines.append(f'\t\t\t\t(end {right_x} {bottom_y})')
        lines.append('\t\t\t\t(stroke (width 0.254) (type default))')
        lines.append('\t\t\t\t(fill (type background))')
        lines.append('\t\t\t)')

        start_y = top_y - pin_pitch
        for i, p in enumerate(unit_pins):
            py = round(start_y - i * pin_pitch, 2)
            px = left_x - pin_length
            raw_type = p.get('type', 'bidirectional').strip().lower()
            ptype = TYPE_MAP.get(raw_type, 'bidirectional')
            pnum = p.get('number', str(i + 1))
            pname = p.get('name', f'Pin_{pnum}')

            lines.append(f'\t\t\t(pin {ptype} line (at {px} {py} 0) (length {pin_length})')
            lines.append(f'\t\t\t\t(name "{pname}" (effects (font (size 1.27 1.27))))')
            lines.append(f'\t\t\t\t(number "{pnum}" (effects (font (size 1.27 1.27))))')
            lines.append('\t\t\t)')

        lines.append('\t\t)')

    lines.append('\t\t(embedded_fonts no)')
    lines.append('\t)')
    lines.append(')')
    return '\n'.join(lines) + '\n'

def main():
    parser = argparse.ArgumentParser(description="Convert pinout CSV to KiCad .kicad_sym symbol")
    parser.add_argument("--csv", required=True, help="Path to pinout CSV file")
    parser.add_argument("--symbol", required=True, help="Symbol name (e.g. GW5A-LV25MG121N)")
    parser.add_argument("--output", required=True, help="Output .kicad_sym path")
    parser.add_argument("--prefix", default="U", help="Reference prefix (default: U)")

    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"Error: CSV file not found: {csv_path}")

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit(f"Error: CSV has no headers: {csv_path}")

        field_map = normalize_field_names(reader.fieldnames)
        if 'number' not in field_map or 'name' not in field_map:
            sys.exit(f"Error: CSV must contain pin Number and Name columns. Found: {reader.fieldnames}")

        parsed_pins = []
        for row in reader:
            parsed_pins.append({
                'number': row[field_map['number']],
                'name': row[field_map['name']],
                'type': row.get(field_map.get('type', ''), 'bidirectional'),
                'unit': row.get(field_map.get('unit', ''), '1'),
            })

    sym_content = generate_symbol_sexp(
        symbol_name=args.symbol,
        pins=parsed_pins,
        reference_prefix=args.prefix,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, mode='w', encoding='utf-8') as f:
        f.write(sym_content)

    print(f"Successfully generated {len(parsed_pins)} pins into {out_path} for symbol '{args.symbol}'.")

if __name__ == '__main__':
    main()
