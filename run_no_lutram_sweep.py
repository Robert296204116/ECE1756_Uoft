#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_no_lutram_sweep.py
----------------------
Executes a parameter sweep for Part (e): Architecture with NO LUTRAM and 1 Block RAM type.

Workflow:
  * Iterates through defined (size_bits, max_width, lb_per_bram) combinations.
  * Builds architecture using build_arch_one_bram.
  * Generates mapping and runs the checker to get area stats.
"""

import subprocess
from ram_mapper_core import build_arch_one_bram, run_mapper


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
        print(f"[No LUTRAM] size={size_bits} bits, max_width={max_width}, "
              f"LBs/BRAM={lb_per_bram}")

        # 1. Construct architecture with specific BRAM parameters
        arch = build_arch_one_bram(size_bits, max_width, lb_per_bram)

        # 2. Run mapper
        lines = run_mapper(LOGICAL_RAMS, LOGIC_BLOCKS, arch)

        # 3. Write mapping to file
        out_name = f"mapping_noLUT_{size_bits}b_W{max_width}_R{lb_per_bram}.txt"
        with open(out_name, "w") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"  -> mapping written to {out_name}")

        # 4. Run checker
        cmd = [
            "./checker",
            "-t",
            "-b", str(size_bits), str(max_width), str(lb_per_bram), "1",
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