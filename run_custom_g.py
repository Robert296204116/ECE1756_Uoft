#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_custom_g.py
---------------
Executes the recommended Custom RAM Architecture for Part (g).

Requires:
  1. Modifying build_arch_custom_example() in ram_mapper_core.py with the proposed architecture.
  2. Setting CHECKER_CMD below to match the proposed architecture parameters.
"""

import subprocess
from ram_mapper_core import build_arch_custom_example, run_mapper

LOGICAL_RAMS = "logical_rams.txt"
LOGIC_BLOCKS = "logic_block_count.txt"

# Checker command corresponding to the custom architecture
# Example: Type1 LUTRAM, Type2 8K, Type3 64K
CHECKER_CMD = [
    "./checker",
    "-t",
    "-l", "1", "1",                      # Type 1: LUTRAM, ratio 1:1
    "-b", "8192", "32", "10", "1",       # Type 2: 8K BRAM
    "-b", "65536", "64", "200", "1",     # Type 3: 64K BRAM
    LOGICAL_RAMS,
    LOGIC_BLOCKS,
    "mapping_custom_g.txt",
]


def main():
    # 1. Construct the custom architecture
    arch = build_arch_custom_example()

    # 2. Run mapper
    lines = run_mapper(LOGICAL_RAMS, LOGIC_BLOCKS, arch)

    # 3. Write mapping to file
    out_name = "mapping_custom_g.txt"
    with open(out_name, "w") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"  -> Custom mapping written to {out_name}")

    # 4. Run checker
    print("  -> Running command:", " ".join(CHECKER_CMD))
    result = subprocess.run(CHECKER_CMD, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print("[checker stderr]")
        print(result.stderr)


if __name__ == "__main__":
    main()