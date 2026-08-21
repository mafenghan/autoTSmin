# autoTSmin

Automated Transition-State and Final-State Search Using LASP

## Overview

autoTSmin is an automated computational workflow for searching
reaction final states and transition-state candidates based on
LASP stochastic surface walking (SSW).

The workflow starts from an initial structure and a pair of atoms
whose bond formation or breaking is of interest.

## Workflow

IS structure
    ↓
Bond-constrained SSW
    ↓
Stable structure
    ↓
Unconstrained optimization
    ↓
Bond connectivity analysis
    ↓
FS structure
    ↓
DESW search
    ↓
TS structure
    ↓
Bond-constrained SSW
    ↓
Stable TS structure
    ↓
extrapolation optimization
    ↓
get new IS and FS structures
    ↓
Bond connectivity analysis
    ↓
DESW search
    ↓
TS final structure

## Features

- Automated LASP input generation
- Automatic bond constraint generation
- Slurm job submission
- Automatic job monitoring
- Lowest-energy structure extraction
- Bond connectivity analysis
- Automatic reaction-state classification
- Iterative TS/FS searching
- Automatic TSmin extrapolation optimization

## Requirements

- Python >= 3.10
- LASP(need lasp.in, NN potential, and gpu.slurm)
- NumPy
- Pandas

## Installation

```bash
git clone https://github.com/mafenghan/autoTSmin.git

cd autoTSmin

pip install -e .


## Usage

```python
from pathlib import Path
from autoTSmin import AutoTSmin
from autoTSmin.config import AutoTSminConfig

config = AutoTSminConfig(
    is_file=Path("IS.arc"),
    fs_file=Path("FS.arc"),
    ts_file=Path("TS.arc"),
    atom_i=145,
    atom_j=146,
    work_dir=Path("."),
    bond_length=1.0,
    bond_strength=10.0,
    fs_search_ssw_steps=5,
    ts_search_ssw_steps=5,
    max_cycles=100,
    gpu_slurm=Path("gpu.slurm"),
)

AutoTSmin(config).run()
```
