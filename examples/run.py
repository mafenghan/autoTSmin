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
)

AutoTSmin(config).run()
