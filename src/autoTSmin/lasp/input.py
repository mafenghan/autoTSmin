from pathlib import Path

class LASPInput:
    """
    LASP.in 文件修改器

    主要负责：
    1. 修改 SSW.SSWsteps
    2. 添加/删除 potential 中的 bond
    3. 添加/删除 bond_by_atom 模块
    """
    def __init__(self, filename):
        self.filename = Path(filename)
        if not self.filename.exists():
            raise FileNotFoundError(f"LASP input file not found: {self.filename}")
        with open(self.filename, "r", encoding="utf-8") as f:
            self.lines = f.readlines()

    def save(self):
        """保存修改后的 lasp.in"""
        with open(self.filename, "w", encoding="utf-8") as f:
            f.writelines(self.lines)

    def set_run_type(self, run_type):
        """
        设置 LASP 的 Run_type。
        例如：
            set_run_type(2)
        将：
            Run_type                  2
        修改为：
            Run_type                  2
        """
        run_type = int(run_type)
        for i, line in enumerate(self.lines):
            stripped = line.strip()

            if stripped.startswith("Run_type"):
                prefix = line[:line.index("Run_type")]

                self.lines[i] = (
                    f"{prefix}Run_type    {run_type}\n"
                )
                return
        # 如果原文件不存在 Run_type，则添加
        self.lines.append(
            f"Run_type    {run_type}\n"
        )

    def set_ssw_steps(self, steps):
        steps = int(steps)
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped.startswith("SSW.SSWsteps"):
                # 保留原来的格式
                prefix = line[:line.index("SSW.SSWsteps")]
                self.lines[i] = (
                    f"{prefix}SSW.SSWsteps    {steps}\n"
                )
                return
        # 如果原文件不存在，则追加
        self.lines.append(f"SSW.SSWsteps    {steps}\n")

    def add_bond_potential(self):
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("potential"):
                parts = stripped.split()
                # 防止重复添加
                if "bond" not in parts[1:]:
                    parts.append("bond")
                # 保持统一格式
                self.lines[i] = (
                    f"potential                 {' '.join(parts[1:])}\n"
                )
                return
        raise ValueError(
            "Cannot find 'potential' line in LASP input file."
        )

    def remove_bond_potential(self):
        """
        从 potential 行中删除 bond。
        例如：
            potential                 gpunn gpud3 bond
        修改为：
            potential                 gpunn gpud3
        """
        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("potential"):
                parts = stripped.split()
                # 删除 bond
                parts = [
                    part for part in parts[1:]
                    if part.lower() != "bond"
                ]
                self.lines[i] = (
                    f"potential                 {' '.join(parts)}\n"
                )
                return
        raise ValueError(
            "Cannot find 'potential' line in LASP input file."
        )

    def set_bond_by_atom(
        self,
        atom_i,
        atom_j,
        bond_length=1.0,
        bond_strength=10.0
    ):
        """
        添加或修改：
        %block bond_by_atom
        atom_i atom_j bond_strength bond_length 
        %endblock bond_by_atom
        例如：
        %block bond_by_atom
        145 146 10.0 1.0
        %endblock bond_by_atom
        """
        atom_i = int(atom_i)
        atom_j = int(atom_j)
        bond_length = float(bond_length)
        bond_strength = float(bond_strength)
        new_block = [
            "%block bond_by_atom\n",
            f"{atom_i} {atom_j} {bond_strength} {bond_length}\n",
            "%endblock bond_by_atom\n",
        ]
        start = None
        end = None
        # 查找已有 bond_by_atom 模块
        for i, line in enumerate(self.lines):
            if line.strip().lower() == "%block bond_by_atom":
                start = i
            elif (
                start is not None
                and line.strip().lower() == "%endblock bond_by_atom"
            ):
                end = i
                break
        # ======================================================
        # 已经存在 → 替换
        # ======================================================
        if start is not None and end is not None:
            self.lines[start:end + 1] = new_block
            return
        # ======================================================
        # 不存在 → 添加
        # ======================================================
        # 通常放到文件最后
        if self.lines and not self.lines[-1].endswith("\n"):
            self.lines[-1] += "\n"
        self.lines.append("\n")
        self.lines.extend(new_block)

    def set_fixatom(
        self,
        atom_i,
        atom_j,
    ):
        """
        添加或修改：
        %block fixatom
        1 1 xyz
        atom_i atom_i xyz
        atom_j atom_j xyz
        %endblock fixatom
        例如：
        """
        atom_i = int(atom_i)
        atom_j = int(atom_j)
        new_block = [
            "%block fixatom\n",
            f"1 1 xyz\n",
            f"{atom_i} {atom_i} xyz\n",
            f"{atom_j} {atom_j} xyz\n",
            "%endblock fixatom\n",
        ]
        start = None
        end = None
        # 查找已有 fixatom 模块
        for i, line in enumerate(self.lines):
            if line.strip().lower() == "%block fixatom":
                start = i
            elif (
                start is not None
                and line.strip().lower() == "%endblock fixatom"
            ):
                end = i
                break
        # ======================================================
        # 已经存在 → 替换
        # ======================================================
        if start is not None and end is not None:
            self.lines[start:end + 1] = new_block
            return
        # ======================================================
        # 不存在 → 添加
        # ======================================================
        # 通常放到文件最后
        if self.lines and not self.lines[-1].endswith("\n"):
            self.lines[-1] += "\n"
        self.lines.append("\n")
        self.lines.extend(new_block)

    def remove_bond_by_atom(self):
        """
        删除整个：
        %block bond_by_atom
        ...
        %endblock bond_by_atom
        """
        while True:
            start = None
            end = None
            for i, line in enumerate(self.lines):
                if line.strip().lower() == "%block bond_by_atom":
                    start = i
                elif (
                    start is not None
                    and line.strip().lower() == "%endblock bond_by_atom"
                ):
                    end = i
                    break
            # 没找到
            if start is None or end is None:
                return
            # 删除整个 block
            del self.lines[start:end + 1]

    def set_sswoutput(self, status = True):
        for i, line in enumerate(self.lines):
            stripped = line.strip()

            if stripped.startswith("SSW.output"):
                prefix = line[:line.index("SSW.output")]

                self.lines[i] = (
                    f"{prefix}SSW.output    {status}\n"
                )
                return
        # 如果原文件不存在 SSW.output，则添加
        self.lines.append(
            f"SSW.output    {status}\n"
        )

