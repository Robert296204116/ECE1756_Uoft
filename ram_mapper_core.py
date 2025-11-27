#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ram_mapper_core.py
-------------------
ECE1756 Assignment 3 - RAM Mapper Core Library

Description:
  * Contains the core algorithms for RAM mapping and architecture definition.
  * Used by other scripts to run specific mapping tasks (default, sweeps, custom).
"""

import math
from typing import Dict, List, Tuple

# ------------------------- Mode Enumeration -------------------------

MODE_MAP: Dict[str, int] = {
    "SimpleDualPort": 0,
    "ROM": 1,
    "SinglePort": 2,
    "TrueDualPort": 3,
}

MODE_REVERSE: Dict[int, str] = {v: k for k, v in MODE_MAP.items()}


# ------------------------- Input Parsing -------------------------

def parse_logical_rams(path: str) -> List[dict]:
    """
    Parses the logical_rams.txt file.
    Format: <Circuit> <RamID> <Mode> <Depth> <Width>
    """
    items: List[dict] = []
    with open(path, "r") as f:
        lines = f.readlines()

    # Skip header lines
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            continue

        circuit_id = int(parts[0])
        ram_id = int(parts[1])
        mode_str = parts[2]
        depth = int(parts[3])
        width = int(parts[4])

        if mode_str not in MODE_MAP:
            continue

        mode_val = MODE_MAP[mode_str]

        item = {
            "Circuit": circuit_id,
            "RamID": ram_id,
            "Mode": mode_val,
            "ModeStr": mode_str,
            "Depth": depth,
            "Width": width,

            # Fields to be filled by the mapping algorithm
            "RAM_type": None,             # Physical RAM type ID
            "small_depthchoose": 0,       # Physical block depth D
            "small_widthchoose": 0,       # Physical block width W
            "small_depthnum": 0,          # Number of blocks in series (S)
            "small_widthnum": 0,          # Number of blocks in parallel (P)
        }
        items.append(item)

    return items


def parse_logic_block_count(path: str) -> Dict[int, int]:
    """
    Parses logic_block_count.txt.
    Maps Circuit ID to the number of logic blocks.
    """
    counts: Dict[int, int] = {}
    with open(path, "r") as f:
        lines = f.readlines()

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            cid = int(parts[0])
            lb = int(parts[1])
        except ValueError:
            continue
        counts[cid] = lb

    return counts


# ------------------------- Architecture Definitions -------------------------

def build_default_arch() -> List[dict]:
    """
    Constructs the default Stratix-IV-like architecture.
    
    Type 1: LUTRAM (640 bits)
    Type 2: 8k BRAM (8192 bits)
    Type 3: 128k BRAM (131072 bits)
    """
    arch: List[dict] = []

    # Type 1: LUTRAM (No TrueDualPort support)
    arch.append({
        "type_id": 1,
        "name": "LUTRAM",
        "capacity_bits": 640,
        "width_options": [10, 20],
        "width_options_tdp": [],
    })

    # Type 2: 8k BRAM
    arch.append({
        "type_id": 2,
        "name": "BRAM8K",
        "capacity_bits": 8192,
        "width_options": [1, 2, 4, 8, 16, 32],
        "width_options_tdp": [1, 2, 4, 8, 16],
    })

    # Type 3: 128k BRAM
    arch.append({
        "type_id": 3,
        "name": "BRAM128K",
        "capacity_bits": 131072,
        "width_options": [1, 2, 4, 8, 16, 32, 64, 128],
        "width_options_tdp": [1, 2, 4, 8, 16, 32, 64],
    })

    return arch


def build_arch_one_bram(size_bits, max_width, lbs_per_bram):
    """
    Constructs an architecture with a single Block RAM type (Part e).
    Width options are powers of 2 up to max_width.
    """
    # Calculate valid single-port widths
    width_options = []
    w = 1
    while w <= max_width and w <= size_bits:
        if size_bits % w == 0:
            width_options.append(w)
        w *= 2

    # TrueDualPort max width is half of the single-port max width
    tdp_max_width = max_width // 2
    width_options_tdp = [w for w in width_options if w <= tdp_max_width]

    arch = [
        {
            "type_id": 1,
            "phy_type": "Block RAM",
            "capacity_bits": size_bits,
            "max_width": max_width,
            "lb_per_bram": lbs_per_bram,
            "width_options": width_options,
            "width_options_tdp": width_options_tdp,
        }
    ]
    return arch


def build_arch_lutram_plus_bram(size_bits, max_width, lbs_per_bram):
    """
    Constructs an architecture with LUTRAM + one Block RAM type (Part f).
    """
    # Fixed LUTRAM resources
    lutram_capacity = 640
    lutram_entry = {
        "type_id": 1,
        "phy_type": "LUTRAM",
        "capacity_bits": lutram_capacity,
        "max_width": 20,
        "lb_per_bram": 1,
        "width_options": [10, 20],
        "width_options_tdp": [],  # LUTRAM does not support TrueDualPort
    }

    # Custom Block RAM resources
    width_options = []
    w = 1
    while w <= max_width and w <= size_bits:
        if size_bits % w == 0:
            width_options.append(w)
        w *= 2

    tdp_max_width = max_width // 2
    width_options_tdp = [w for w in width_options if w <= tdp_max_width]

    bram_entry = {
        "type_id": 2,
        "phy_type": "Block RAM",
        "capacity_bits": size_bits,
        "max_width": max_width,
        "lb_per_bram": lbs_per_bram,
        "width_options": width_options,
        "width_options_tdp": width_options_tdp,
    }

    arch = [lutram_entry, bram_entry]
    return arch


def build_arch_custom_example() -> List[dict]:
    """
    Constructs the custom architecture for Part (g).
    Includes LUTRAM, 8K BRAM, and 64K BRAM.
    """
    arch: List[dict] = []

    # Type 1: LUTRAM
    arch.append({
        "type_id": 1,
        "phy_type": "LUTRAM",
        "name": "LUTRAM",
        "capacity_bits": 640,
        "max_width": 20,
        "lb_per_bram": 1,
        "width_options": [10, 20],
        "width_options_tdp": [],
    })

    # Type 2: 8K BRAM
    arch.append({
        "type_id": 2,
        "phy_type": "Block RAM",
        "name": "BRAM8K",
        "capacity_bits": 8192,
        "max_width": 32,
        "lb_per_bram": 10,
        "width_options":      [1, 2, 4, 8, 16, 32],
        "width_options_tdp":  [1, 2, 4, 8, 16],
    })

    # Type 3: 64K BRAM
    arch.append({
        "type_id": 3,
        "phy_type": "Block RAM",
        "name": "BRAM64K",
        "capacity_bits": 65536,
        "max_width": 64,
        "lb_per_bram": 200,
        "width_options":      [1, 2, 4, 8, 16, 32, 64],
        "width_options_tdp":  [1, 2, 4, 8, 16, 32],
    })

    return arch

# ------------------------- Core Mapping Algorithm -------------------------

def map_rams_with_arch(items: List[dict],
                       arch: List[dict],
                       max_series: int = 16) -> None:
    """
    Selects the physical RAM implementation that minimizes bit waste for each logical RAM.
    
    Parameters:
      items: List of logical RAMs.
      arch: Architecture definition.
      max_series: Maximum allowable blocks in series (default 16).
    """
    for item in items:
        mode_str = item["ModeStr"]
        depth = item["Depth"]
        width = item["Width"]

        best_choice = None

        for ram in arch:
            type_id = ram["type_id"]
            capacity_bits = ram["capacity_bits"]

            # Select allowed width options based on mode
            if mode_str == "TrueDualPort":
                width_list = ram.get("width_options_tdp") or []
            else:
                width_list = ram.get("width_options") or []

            if not width_list:
                continue

            for phys_width in width_list:
                # Ensure capacity is divisible by width for integer depth
                if capacity_bits % phys_width != 0:
                    continue
                phys_depth = capacity_bits // phys_width

                # Calculate required blocks in Parallel (width) and Series (depth)
                width_num = math.ceil(width / phys_width)
                depth_num = math.ceil(depth / phys_depth)

                # Check constraint: Series depth should not exceed max limit
                if depth_num > max_series:
                    continue

                total_width = width_num * phys_width
                total_depth = depth_num * phys_depth
                total_bits = total_width * total_depth
                used_bits = depth * width
                waste_bits = total_bits - used_bits

                # Greedy selection: keep the configuration with minimum waste
                if best_choice is None or waste_bits < best_choice["waste_bits"]:
                    best_choice = {
                        "type_id": type_id,
                        "phys_width": phys_width,
                        "phys_depth": phys_depth,
                        "width_num": width_num,
                        "depth_num": depth_num,
                        "waste_bits": waste_bits,
                    }

        # Apply the best choice found
        if best_choice is None:
            # Fallback: default to the first architecture type if no valid mapping found
            ram0 = arch[0]
            type_id = ram0["type_id"]
            capacity_bits = ram0["capacity_bits"]
            width_list = ram0.get("width_options") or ram0.get("width_options_tdp") or [width]
            phys_width = min(width_list)
            if capacity_bits % phys_width == 0:
                phys_depth = capacity_bits // phys_width
            else:
                phys_depth = max(1, capacity_bits // phys_width)

            item["RAM_type"] = type_id
            item["small_depthchoose"] = phys_depth
            item["small_widthchoose"] = phys_width
            item["small_depthnum"] = 1
            item["small_widthnum"] = 1
        else:
            item["RAM_type"] = best_choice["type_id"]
            item["small_depthchoose"] = best_choice["phys_depth"]
            item["small_widthchoose"] = best_choice["phys_width"]
            item["small_depthnum"] = best_choice["depth_num"]
            item["small_widthnum"] = best_choice["width_num"]


# ------------------------- Overhead Calculation -------------------------

def compute_overhead_luts(items: List[dict]) -> Tuple[List[int], List[int], List[int]]:
    """
    Calculates overhead LUTs required for decoding and multiplexing.
    
    Rules:
      * Series R blocks requires R:1 decoder.
      * Reading requires W * R:1 MUX (implemented via 4:1 LUTs).
      * TrueDualPort doubles the overhead requirements.
    """
    overhead_list: List[int] = []
    decoder_list: List[int] = []
    mux_list: List[int] = []

    for item in items:
        dnum = item["small_depthnum"]  # Series count R
        width = item["Width"]          # Logical Width W
        mode_str = item["ModeStr"]

        if dnum is None or dnum <= 1:
            decoder = 0
            mux = 0
        else:
            # 1) Decoder logic
            if dnum == 2:
                decoder = 1
            else:
                decoder = dnum

            # 2) MUX logic (cascaded 4:1 LUTs)
            if dnum <= 4:
                mux = width
            else:
                mux_levels = dnum // 4 + 1
                mux = mux_levels * width

        if mode_str == "TrueDualPort":
            decoder *= 2
            mux *= 2

        overhead = decoder + mux
        overhead_list.append(overhead)
        decoder_list.append(decoder)
        mux_list.append(mux)

    return overhead_list, decoder_list, mux_list


# ------------------------- Output Generation -------------------------

def generate_mapping_lines(items: List[dict],
                           overhead_luts: List[int]) -> List[str]:
    """
    Generates the formatted text lines required by the checker.
    Format:
      <Circuit> <RamID> <AdditionalLUT>
      LW <logical_width> LD <logical_depth>
      ID <group_id> S <series> P <parallel>
      Type <type> Mode <mode_str> W <phys_width> D <phys_depth>
    """
    lines: List[str] = []
    next_group_id = 0

    for item, extra_luts in zip(items, overhead_luts):
        circuit = item["Circuit"]
        ramid = item["RamID"]
        logical_width = item["Width"]
        logical_depth = item["Depth"]
        mode_str = item["ModeStr"]
        ram_type = item["RAM_type"]
        phys_width = item["small_widthchoose"]
        phys_depth = item["small_depthchoose"]
        series = item["small_depthnum"]
        parallel = item["small_widthnum"]

        if series is None or series <= 0:
            series = 1
        if parallel is None or parallel <= 0:
            parallel = 1

        group_id = next_group_id
        next_group_id += 1

        line = (
            f"{circuit} {ramid} {extra_luts} "
            f"LW {logical_width} LD {logical_depth} "
            f"ID {group_id} S {series} P {parallel} "
            f"Type {ram_type} Mode {mode_str} "
            f"W {phys_width} D {phys_depth}"
        )
        lines.append(line)

    return lines


# ------------------------- Main Interface -------------------------

def run_mapper(logical_rams_path: str,
               logic_block_count_path: str,
               arch: List[dict],
               max_series: int = 16) -> List[str]:
    """
    Main entry point: processes inputs using the provided architecture and returns mapping lines.
    """
    items = parse_logical_rams(logical_rams_path)
    # Parse block count to verify file existence/format, though not strictly used in mapping
    _ = parse_logic_block_count(logic_block_count_path)

    map_rams_with_arch(items, arch, max_series=max_series)
    overhead_luts, _, _ = compute_overhead_luts(items)
    mapping_lines = generate_mapping_lines(items, overhead_luts)
    return mapping_lines


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        logical_rams_path = sys.argv[1]
        logic_block_count_path = sys.argv[2]
    else:
        logical_rams_path = "logical_rams.txt"
        logic_block_count_path = "logic_block_count.txt"

    arch = build_default_arch()
    lines = run_mapper(logical_rams_path, logic_block_count_path, arch)
    for l in lines:
        print(l)