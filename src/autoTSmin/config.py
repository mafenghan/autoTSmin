from dataclasses import dataclass
from os import wait
from pathlib import Path

@dataclass
class AutoTSminConfig:
    is_file: Path
    fs_file: Path
    ts_file: Path
    atom_i: int
    atom_j: int
    work_dir: Path
    bond_length: float = 1.0
    bond_strength: float = 10.0
    fs_search_ssw_steps: int = 5
    ts_search_ssw_steps: int = 5
    waiting_time: int = 10
    max_cycles: int = 10
    lasp_input: Path = Path("lasp.in")
    all_arc: Path = Path("all.arc")
    gpu_slurm: Path = Path("gpu.slurm")

    def __post_init__(self):
        self.is_file = Path(self.is_file)
        self.fs_file = Path(self.fs_file)
        self.ts_file = Path(self.ts_file)
        self.work_dir = Path(self.work_dir)
        self.lasp_input = self.work_dir / self.lasp_input
        self.all_arc = self.work_dir / self.all_arc
        self.gpu_slurm = self.work_dir / self.gpu_slurm
