from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ProjectLayout:
    """
    Standard directory layout for one simulation project.

    Example
    -------
    project/
    ├── input/
    ├── md/
    ├── analysis/
    └── mmpbsa/
    """

    root: Path

    @property
    def input(self) -> Path:
        return self.root / "input"

    @property
    def md(self) -> Path:
        return self.root / "md"

    @property
    def analysis(self) -> Path:
        return self.root / "analysis"

    @property
    def trajectory(self) -> Path:
        return self.analysis / "trajectory"

    @property
    def rmsd(self) -> Path:
        return self.analysis / "rmsd"

    @property
    def rmsf(self) -> Path:
        return self.analysis / "rmsf"

    @property
    def rg(self) -> Path:
        return self.analysis / "rg"

    @property
    def sasa(self) -> Path:
        return self.analysis / "sasa"

    @property
    def hbond(self) -> Path:
        return self.analysis / "hbond"

    @property
    def com(self) -> Path:
        return self.analysis / "com"

    @property
    def system(self) -> Path:
        return self.analysis / "system"

    @property
    def mmpbsa(self) -> Path:
        return self.root / "mmpbsa"

    @property
    def processed(self) -> Path:
        return self.md / "processed.gro"

    @property
    def boxed(self) -> Path:
        return self.md / "boxed.gro"

    @property
    def solvated(self) -> Path:
        return self.md / "solv.gro"

    @property
    def ions(self) -> Path:
        return self.md / "solv_ions.gro"

    @property
    def ions_tpr(self) -> Path:
        return self.md / "ions.tpr"

    @property
    def topology(self) -> Path:
        return self.md / "topol.top"

    @property
    def em_tpr(self) -> Path:
        return self.md / "em.tpr"

    @property
    def em_gro(self) -> Path:
        return self.md / "em.gro"

    @property
    def em_cpt(self) -> Path:
        return self.md / "em.cpt"

    @property
    def nvt_tpr(self) -> Path:
        return self.md / "nvt.tpr"

    @property
    def nvt_gro(self) -> Path:
        return self.md / "nvt.gro"

    @property
    def nvt_cpt(self) -> Path:
        return self.md / "nvt.cpt"

    @property
    def npt_tpr(self) -> Path:
        return self.md / "npt.tpr"

    @property
    def npt_gro(self) -> Path:
        return self.md / "npt.gro"

    @property
    def npt_cpt(self) -> Path:
        return self.md / "npt.cpt"

    @property
    def md_tpr(self) -> Path:
        return self.md / "md.tpr"

    @property
    def md_xtc(self) -> Path:
        return self.md / "md.xtc"

    def create(self) -> None:
        """
        Create all required directories.
        """

        for directory in (
            self.input,
            self.md,
            self.analysis,
            self.trajectory,
            self.rmsd,
            self.rmsf,
            self.rg,
            self.sasa,
            self.hbond,
            self.com,
            self.system,
            self.mmpbsa,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def md_nopbc_xtc(self) -> Path:
        return self.trajectory / "md_noPBC.xtc"

    @property
    def md_nojump_xtc(self) -> Path:
        return self.trajectory / "md_nojump.xtc"

    @property
    def md_center_xtc(self) -> Path:
        return self.trajectory / "md_center.xtc"

    @property
    def md_fit_xtc(self) -> Path:
        return self.trajectory / "md_fit.xtc"

    @property
    def rmsd_xvg(self) -> Path:
        return self.rmsd / "rmsd.xvg"

    @property
    def rmsf_xvg(self) -> Path:
        return self.rmsf / "rmsf.xvg"

    @property
    def rg_xvg(self) -> Path:
        return self.rg / "rg.xvg"

    @property
    def sasa_xvg(self) -> Path:
        return self.sasa / "sasa.xvg"

    @property
    def hbond_xvg(self) -> Path:
        return self.hbond / "hbond.xvg"

    @property
    def com_xvg(self) -> Path:
        return self.com / "com_distance.xvg"

    @property
    def energy_xvg(self) -> Path:
        return self.system / "energy.xvg"
