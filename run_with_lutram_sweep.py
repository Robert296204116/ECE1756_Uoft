#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_with_lutram_sweep.py
------------------------
Executes a parameter sweep for Part (f): Architecture WITH LUTRAM (Type 1) + 1 Block RAM type (Type 2).

Workflow:
  * Iterates through defined (size_bits, max_width, lb_per_bram) combinations for the BRAM.
  * LUTRAM is fixed (640 bits, 64x10/32x20).
  * Calls checker with flags for both LUTRAM and BRAM.
"""

import subprocess
from ram_mapper_core import build_arch_lutram_plus_bram, run_mapper


# Test Configurations: (size_bits, max_width, lb_per_bram)
CANDIDATES = [
    # (size_bits, max_width, lb_per_bram)
    # (8 * 1024,   32, 10),
    # (16 * 1024,  32, 10),
    # (32 * 1024,  64, 10),
    # (64 * 1024,  64, 10),
    # (128 * 1024, 128, 10),

    # #1k, 2k
    # (1 * 1024, 8, 10),
    # (1 * 1024, 16, 10),
    # (2 * 1024, 8, 10),
    # (2 * 1024, 16, 10),

    # #4k, 8k, 16k
    # (4 * 1024, 16, 10),
    # (4 * 1024, 32, 10),
    # (8 * 1024, 16, 10),
    # (8 * 1024, 32, 10),
    # (16 * 1024, 32, 10),

    # # 32k, 64k, 128k
    # (32 * 1024, 32, 10),
    # (32 * 1024, 64, 10),
    # (64 * 1024, 64, 10),
    # (128 * 1024, 64, 10),
    # (128 * 1024, 128, 10),

    # 4k
    (4 * 1024, 16, 5),
    (4 * 1024, 16, 10),
    (4 * 1024, 16, 20),

    # 8k
    (8 * 1024, 32, 5),
    (8 * 1024, 32, 10),
    (8 * 1024, 32, 20),

    # 16k
    (16 * 1024, 32, 5),
    (16 * 1024, 32, 10),
    (16 * 1024, 32, 20),

    # 32k
    (32 * 1024, 64, 10),
    (32 * 1024, 64, 20),
]


LOGICAL_RAMS = "logical_rams.txt"
LOGIC_BLOCKS = "logic_block_count.txt"


def main():
    for size_bits, max_width, lb_per_bram in CANDIDATES:
        print("=" * 80)
        print(f"[With LUTRAM] size={size_bits} bits, max_width={max_width}, "
              f"LBs/BRAM={lb_per_bram}")

        # 1. Construct architecture (Type 1 = LUTRAM, Type 2 = BRAM)
        arch = build_arch_lutram_plus_bram(size_bits, max_width, lb_per_bram)

        # 2. Run mapper
        lines = run_mapper(LOGICAL_RAMS, LOGIC_BLOCKS, arch)

        # 3. Write mapping to file
        out_name = f"mapping_LUT+BRAM_{size_bits}b_W{max_width}_R{lb_per_bram}.txt"
        with open(out_name, "w") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"  -> mapping written to {out_name}")

        # 4. Run checker
        cmd = [
            "./checker",
            "-t",
            "-l", "1", "1",  # Type 1: LUTRAM, ratio 1:1
            "-b", str(size_bits), str(max_width), str(lb_per_bram), "1",  # Type 2: BRAM
            LOGICAL_RAMS,
            LOGIC_BLOCKS,
            out_name,

        ]
        print("  -> Running command:", " ".join(cmd))
        result = subprocess.run(cmd, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print("[checker stderr]")
            print(result.stderr)


if __name__ == "__main__":
    main()