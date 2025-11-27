# ECE1756 Assignment 3 – RAM Mapper (Python)

This README explains how to run my RAM mapper implementation for **ECE1756 Assignment 3** on the UG Linux systems, and how to reproduce all experiments:

- Fixed Stratix-IV-like architecture (part d)
- “No LUTRAM” single-BRAM sweep (part e)
- “With LUTRAM” + single-BRAM sweep (part f)
- Custom architecture with up to 3 RAM types (part g)

---

## 1. Files in This Directory

Source code:

- `ram_mapper_core.py`  
  Core implementation of the RAM mapping tool:
  - Parses `logical_rams.txt` and `logic_block_count.txt`
  - Defines architecture builders:
    - `build_default_arch()` – Stratix-IV-like architecture (LUTRAM + 8K BRAM + 128K BRAM)
    - `build_arch_one_bram(size_bits, max_width, lbs_per_bram)` – single-BRAM, no-LUTRAM architecture (part e)
    - `build_arch_lutram_plus_bram(size_bits, max_width, lbs_per_bram)` – LUTRAM + single-BRAM architecture (part f)
    - `build_arch_custom_example()` – custom architecture with LUTRAM + two BRAM types (part g)
  - Implements the mapping algorithm (`run_mapper`, etc.) and prints mappings in the **basic** checker format.

- `run_default.py`  
  Entry point for **part (d)** (fixed Stratix-IV-like architecture).  
  Generates `ram_mapping_default.txt`.

- `run_no_lutram_sweep.py`  
  Entry point for **part (e)** (architectures **without LUTRAM**).  
  Explores multiple single-BRAM architectures; produces `run_nolut.txt`.

- `run_with_lutram_sweep.py`  
  Entry point for **part (f)** (architectures **with LUTRAM**).  
  Explores LUTRAM + single-BRAM; produces `run_withlut.txt`.

- `run_custom_g.py`  
  Entry point for **part (g)** (custom architecture).  
  Produces `mapping_custom_g.txt` and `run_custom.txt`.

Benchmark & checker files:

- `logical_rams.txt`  
- `logic_block_count.txt`  
- `checker`

Output files (examples):

- `ram_mapping_default.txt`
- `run_default.txt`, `run_nolut.txt`, `run_withlut.txt`, `run_custom.txt`
- `mapping_noLUT_*.txt`, `mapping_LUT+BRAM_*.txt`, `mapping_custom_g.txt`

---

## 2. UG Linux Setup

```bash
ssh <utorid>@ugXX.eecg.utoronto.ca
module load python/3
python3 --version
```

All scripts run directly with `python3`.

---

## 3. Part (d): Fixed Stratix-IV-like Architecture

### 3.1 Generate mapping file

```bash
python3 run_default.py > ram_mapping_default.txt
```

### 3.2 Run checker and generate Table 1

```bash
./checker -d logical_rams.txt logic_block_count.txt ram_mapping_default.txt -t > run_default.txt
```

This prints:

- per-circuit LUT/BRAM usage
- LB tiles required
- total FPGA area
- geometric average FPGA area

### 3.3 Measure CPU runtime (required in report)

```bash
/usr/bin/time -f "CPU runtime: %e seconds" \
  python3 run_default.py > /dev/null 2> run_default_time.txt
```

Record the number in `run_default_time.txt`.

---

## 4. Part (e): NO LUTRAM – Single BRAM Sweep

Candidates are defined inside `run_no_lutram_sweep.py`:

```python
CANDIDATES = [
    ( 1*1024, 16, 10),
    ( 2*1024, 16, 10),
    ( 4*1024, 32, 10),
    ( 8*1024, 32, 10),
    (16*1024, 32, 10),
    (32*1024, 64, 10),
    (64*1024, 64, 10),
    (128*1024,128,10),
]
```

Run:

```bash
python3 run_no_lutram_sweep.py > run_nolut.txt
```

Each candidate produces:

- mapping file: `mapping_noLUT_<...>.txt`
- checker output appended to `run_nolut.txt`

Use the geometric average area for each size to fill **Table 2**.

---

## 5. Part (f): WITH LUTRAM – LUTRAM + Single BRAM Sweep

Candidates are inside `run_with_lutram_sweep.py`:

```python
CANDIDATES = [
    ( 1*1024, 16, 10),
    ( 2*1024, 16, 10),
    ( 4*1024, 32, 10),
    ( 8*1024, 32, 10),
    (16*1024, 32, 10),
    (32*1024, 64, 10),
    (64*1024, 64, 10),
    (128*1024,128,10),
]
```

Run:

```bash
python3 run_with_lutram_sweep.py > run_withlut.txt
```

Each candidate produces:

- mapping file: `mapping_LUT+BRAM_<...>.txt`
- checker output appended to `run_withlut.txt`

Use geometric average area for Table 3.

---

## 6. Part (g): Custom Architecture

The custom design is inside `build_arch_custom_example()` (in `ram_mapper_core.py`), e.g.:

- LUTRAM: 640 bits, max width 20, 50% logic blocks
- BRAM8K: 8192 bits, max width 32, LBs/BRAM=10
- BRAM64K: 65536 bits, max width 64, LBs/BRAM=200

Run:

```bash
python3 run_custom_g.py > run_custom.txt
```

Checker command (embedded in script):

```bash
./checker -t \
  -l 1 1 \
  -b 8192  32 10 1 \
  -b 65536 64 200 1 \
  logical_rams.txt logic_block_count.txt mapping_custom_g.txt
```

Use the last line `Geometric Average Area` in your Part (g) analysis.

---

## 7. Summary of All Commands

```bash
# Part (d)
python3 run_default.py > ram_mapping_default.txt
./checker -d logical_rams.txt logic_block_count.txt ram_mapping_default.txt -t > run_default.txt
/usr/bin/time -f "CPU runtime: %e" python3 run_default.py > /dev/null 2> run_default_time.txt

# Part (e)
python3 run_no_lutram_sweep.py > run_nolut.txt

# Part (f)
python3 run_with_lutram_sweep.py > run_withlut.txt

# Part (g)
python3 run_custom_g.py > run_custom.txt
```

This reproduces all results needed for **Tables 1–3** and **custom-architecture comparison**.
