from pathlib import Path
from .config import AutoTSminConfig
from .lasp.input import LASPInput
from .lasp.runner import LASPRunner
from .structure.arc import get_lowest_energy_structure, check_bond_relation, write_arc
from .utils.filesystem import copy_file, cat_file

class AutoTSmin:
    def __init__(self, config: AutoTSminConfig):
        self.config = config
        self.work_dir = Path(config.work_dir)
        self.runner = LASPRunner(self.work_dir, slurm_script=self.config.gpu_slurm)
        self.lasp_input = LASPInput(config.lasp_input)
        self.cycle = 0

    def run_lasp(self, waiting_time: int = 10):
        self.runner.run(interval = waiting_time)

    def prepare_fs_ssw_search(self, file: Path = None, run_type: int = 5):
        copy_file(file, self.work_dir / "input.arc")
        self.lasp_input.remove_fixatom()
        self.lasp_input.set_fixatom([1])
        self.lasp_input.add_bond_potential()
        self.lasp_input.set_run_type(run_type)
        self.lasp_input.set_bond_by_atom(
            self.config.atom_i, self.config.atom_j,
            self.config.bond_length, self.config.bond_strength
        )
        self.lasp_input.set_ssw_steps(self.config.fs_search_ssw_steps)
        self.lasp_input.save()

    def prepare_optimization(self, run_type: int = 5):
        best_structure = get_lowest_energy_structure(self.config.all_arc)
        write_arc(best_structure.arc, best_structure.abc, self.work_dir / "input.arc", sort=False)
        self.lasp_input.remove_fixatom()
        self.lasp_input.set_fixatom([1])
        self.lasp_input.remove_bond_potential()
        self.lasp_input.remove_bond_by_atom()
        self.lasp_input.set_ssw_steps(1)
        self.lasp_input.set_run_type(run_type)
        self.lasp_input.set_sswoutput(False)
        self.lasp_input.save()

    def prepare_desw(self, file1: Path = None, file2: Path = None):
        cat_file(file1, file2, self.work_dir / "uncm.arc")
        self.lasp_input.remove_fixatom()
        self.lasp_input.set_fixatom([1])
        self.lasp_input.set_run_type(2)
        self.lasp_input.set_ssw_steps(1)
        self.lasp_input.set_sswoutput(True)
        self.lasp_input.save()

    def prepare_ts_ssw_search(self, file: Path = None, run_type: int = 5):
        copy_file(file, self.work_dir / "input.arc")
        self.lasp_input.set_run_type(run_type)
        self.lasp_input.set_ssw_steps(self.config.ts_search_ssw_steps)
        self.lasp_input.remove_fixatom()
        self.lasp_input.set_fixatom([1,self.config.atom_i, self.config.atom_j])
        self.lasp_input.save()

    def prepare_ts_extrapolation_optimization(self, file: Path = None, is_or_fs: str = 'is', run_type: int = 5):
        copy_file(file, self.work_dir / "input.arc")
        self.lasp_input.remove_fixatom()
        self.lasp_input.set_fixatom([1])
        self.lasp_input.set_run_type(run_type)
        self.lasp_input.set_ssw_steps(1)
        self.lasp_input.set_sswoutput(False)
        self.lasp_input.add_bond_potential()
        if is_or_fs == "is":
            self.lasp_input.set_bond_by_atom(
                self.config.atom_i, self.config.atom_j,
                2.1, self.config.bond_strength
            )
        elif is_or_fs == "fs":
            self.lasp_input.set_bond_by_atom(
                self.config.atom_i, self.config.atom_j,
                self.config.bond_length, self.config.bond_strength
            )
        self.lasp_input.save()

    def check_final_structure(self, file1: Path = None, file2: Path = None):
        is_bonded, _ = check_bond_relation(file1, file2, self.config.atom_i - 1 , self.config.atom_j - 1)
        return is_bonded

    def run_find_fs(self, run_type: int = 5):
        print("\n========== RUN FS ssw search ==========")
        self.prepare_fs_ssw_search(self.config.is_file, run_type)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_result():
            print("[LASP] FS Search failed. No new bonding relation found. Check the lasp.out for details.")
            return False
        print("\n========== RUN FS optimization ==========")
        self.prepare_optimization(run_type)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_result():
            print("[LASP] FS Structure Optimization failed. Check the lasp.out for details.")
            return False
        copy_file(self.work_dir / "all.arc", self.config.fs_file)
        return self.check_final_structure(self.config.is_file, self.config.fs_file)

    def run_desw(self):
        print(f"\n========== Run DESW ==========")
        self.prepare_desw(self.config.is_file, self.config.fs_file)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_ts_result():
            print("[LASP] DESW failed. Check the lasp.out for details.")
            return False
        copy_file(self.work_dir / "TSstr.arc", self.config.ts_file)
        return True

    def run_tsmin(self, run_type: int = 5):
        if not self.run_desw():
            return False
        print(f"\n========== Run TS SSW search ==========")
        self.prepare_ts_ssw_search(self.config.ts_file, run_type)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_result():
            print("[LASP] TS Structure SSW search failed. Check the lasp.out for details.")
            return False
        best_structure = get_lowest_energy_structure(self.config.all_arc)
        write_arc(best_structure.arc, best_structure.abc, self.config.ts_file, sort=False)
        return True

    def run_ts_extrapolation(self, is_or_fs: str, run_type: int = 5):
        print(f"\n========== Run TS extrapolation to {is_or_fs} ==========")
        self.prepare_ts_extrapolation_optimization(self.config.ts_file, is_or_fs, run_type)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_result():
            print("[LASP] TSmin Extrapolation Optimization failed. Check the lasp.out for details.")
            return False
        print(f"\n========== Run {is_or_fs} optimization ==========")
        self.prepare_optimization(run_type)
        self.run_lasp(self.config.waiting_time)
        if not self.runner.check_result():
            print("[LASP] TSmin Extrapolation Optimization failed. Check the lasp.out for details.")
            return False
        if is_or_fs == "is":
            copy_file(self.work_dir / "all.arc", self.config.is_file)
        elif is_or_fs == "fs":
            copy_file(self.work_dir / "all.arc", self.config.fs_file)
        return True

    def run(self, run_type: int = 5):
        print("========== Start TSmin workflow ==================")
        # find FS structure
        for cycle in range(1, self.config.max_cycles + 1):
            self.cycle = cycle
            print(f"\n========== Cycle {self.cycle} ==========")
            # FS search
            fs_status = self.run_find_fs(run_type=run_type)
            if not fs_status:
                print("\nNo FS structure found. Restarting search...")
                continue
            print("\nFS structure found!")
            # TS search
            ts_status = self.run_tsmin(run_type=run_type)
            if not ts_status:
                print("\nNo TSmin structure found. Restarting search...")
                continue
            print("\nTSmin Finnished!")
            # TSmin 外推优化产生IS结构和FS结构
            is_status = self.run_ts_extrapolation("is", run_type=run_type)
            fs_status = self.run_ts_extrapolation("fs", run_type=run_type)
            if not is_status or not fs_status:                
                print("\nTSmin extrapolation optimization failed. Restarting search...")
                continue
            print("\nTSmin extrapolation optimization success!")
            # check bonding relation
            check_status = self.check_final_structure(self.config.is_file, self.config.fs_file)
            if not check_status:
                print("\nNo new bonding relation found. Restarting search...")
                continue
            print("\nNew bonding relation found!")
            ts_status = self.run_desw()
            if not ts_status:
                print("\nDESW failed. Restarting search...")
                continue
            print(f"\nDESW success! Please check the IS/TS/FS structure in {self.config.is_file}/{self.config.ts_file}/{self.config.fs_file}.")
            return True
        print("\nMaximum cycles reached.")
        return False
