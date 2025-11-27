#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_default.py
--------------
Runs the RAM mapper using the default Stratix-IV-like architecture.

Usage:
    python3 run_default.py > ram_mapping.txt
    ./checker -d logical_rams.txt logic_block_count.txt ram_mapping.txt
"""

import sys
from ram_mapper_core import build_default_arch, run_mapper


def main():
    # 1. Determine input file paths
    if len(sys.argv) >= 3:
        logical_rams_path = sys.argv[1]
        logic_block_count_path = sys.argv[2]
    else:
        logical_rams_path = "logical_rams.txt"
        logic_block_count_path = "logic_block_count.txt"

    # 2. Build the default architecture
    arch = build_default_arch()

    # 3. Execute the mapper logic
    lines = run_mapper(logical_rams_path, logic_block_count_path, arch)

    # 4. Output results to stdout
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()