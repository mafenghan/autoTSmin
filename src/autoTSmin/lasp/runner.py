from pathlib import Path
import subprocess
import time

class LASPRunner:
    def __init__(self, work_dir, slurm_script="gpu.slurm"):
        self.work_dir = Path(work_dir).resolve()
        self.slurm_script = slurm_script
        self.job_id = None
    def submit(self):
        """
        提交 LASP Slurm 作业。
        等价于在 work_dir 中执行：
            sbatch gpu.slurm
        返回：
            job_id
        """
        script = self.work_dir / self.slurm_script
        if not self.work_dir.exists():
            raise FileNotFoundError(
                f"Working directory does not exist: {self.work_dir}"
            )
        if not script.exists():
            raise FileNotFoundError(
                f"Slurm script does not exist: {script}"
            )
        result = subprocess.run(
            ["sbatch", self.slurm_script],
            cwd=self.work_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        # Slurm 正常返回：
        #
        # Submitted batch job 123456
        #
        output = result.stdout.strip()
        try:
            self.job_id = output.split()[-1]
        except Exception as e:
            raise RuntimeError(
                f"Cannot parse Slurm job ID from output: {output}"
            ) from e
        print(f"[LASP] Job submitted: {self.job_id}")
        return self.job_id

    def is_running(self):
        """
        判断当前 LASP Slurm 作业是否仍在运行。
        使用：
            squeue -j JOBID
        返回：
            True  -> 作业仍在运行/排队
            False -> 作业已经结束
        """
        if self.job_id is None:
            raise RuntimeError(
                "No job has been submitted."
            )
        result = subprocess.run(
            [
                "squeue",
                "-j",
                str(self.job_id),
                "-h",
            ],
            cwd=self.work_dir,
            capture_output=True,
            text=True,
        )
        # squeue:
        # 有结果 -> 作业还存在
        # 空结果 -> 作业已经结束
        return bool(result.stdout.strip())

    def wait(self, interval=10):
        """
        等待 Slurm 作业结束。
        interval:
            每隔多少秒检查一次。
        """
        if self.job_id is None:
            raise RuntimeError(
                "No job has been submitted."
            )
        print(
            f"[LASP] Waiting for job {self.job_id} ..."
        )
        while self.is_running():
            time.sleep(interval)
        print(
            f"[LASP] Job {self.job_id} finished."
        )
        return True

    def run(self, interval=10):
        """
        提交并等待 LASP 作业结束。
        """
        self.submit()
        self.wait(interval=interval)

    def check_result(self):
        """
        检查 LASP 是否正常结束。
        判断标准：
            lasp.out 文件中是否包含：
                LASP   job  ends
        返回：
            True  -> LASP 正常结束
            False -> LASP 未正常结束
        """
        lasp_out = self.work_dir / "lasp.out"
        if not lasp_out.exists():
            print(
                f"[LASP] Warning: lasp.out not found in {self.work_dir}"
            )
            return False
        with open(lasp_out, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "LASP   job  ends" in content:
            print(
                f"[LASP] Job completed successfully: {lasp_out}"
            )
            return True
        print(
            f"[LASP] Job did not finish normally: {lasp_out}"
        )
        return False

    def check_ts_result(self):
        """
        检查 LASP TS 搜索是否正常结束。
        判断标准：
            lasp.out 文件中是否包含：
                TS search finished
        返回：
            True  -> TS 搜索正常结束
            False -> TS 搜索未正常结束
        """
        lasp_out = self.work_dir / "lasp.out"
        if not lasp_out.exists():
            print(
                f"[LASP] Warning: lasp.out not found in {self.work_dir}"
            )
            return False
        with open(lasp_out, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "IS/TS/FS" in content:
            print(
                f"[LASP] TS search completed successfully: {lasp_out}"
            )
            return True
        print(
            f"[LASP] TS search did not finish normally: {lasp_out}"
        )
        return False

    