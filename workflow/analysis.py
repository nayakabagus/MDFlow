from __future__ import annotations

from pathlib import Path

from lib.gromacs.analysis import (
    distance,
    energy,
    gyrate,
    hbond,
    rms,
    rmsf,
    sasa,
    trjconv,
)


def _require_success(result) -> None:
    if not result.success:
        raise RuntimeError(result.stderr or result.stdout)


def run_analysis(project_dir: Path) -> None:
    """
    Complete MD analysis workflow.

    Parameters
    ----------
    project_dir
        Project directory containing simulation results.
    """

    simulation = project_dir / "02_Simulation"
    analysis = project_dir / "03_Analysis"

    trajectory_dir = analysis / "Trajectory"
    rmsd_dir = analysis / "RMSD"
    rmsf_dir = analysis / "RMSF"
    rg_dir = analysis / "Rg"
    sasa_dir = analysis / "SASA"
    hbond_dir = analysis / "HBond"
    com_dir = analysis / "COM"
    system_dir = analysis / "System"

    for directory in (
        trajectory_dir,
        rmsd_dir,
        rmsf_dir,
        rg_dir,
        sasa_dir,
        hbond_dir,
        com_dir,
        system_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    tpr = simulation / "md.tpr"
    xtc = simulation / "md.xtc"
    edr = simulation / "md.edr"

    nopbc = trajectory_dir / "md_noPBC.xtc"
    nojump = trajectory_dir / "md_nojump.xtc"
    center = trajectory_dir / "md_center.xtc"
    fit = trajectory_dir / "md_fit.xtc"

    _require_success(
        trjconv(
            structure=tpr,
            trajectory=xtc,
            output=nopbc,
            selection="System",
            pbc="mol",
        )
    )

    _require_success(
        trjconv(
            structure=tpr,
            trajectory=nopbc,
            output=nojump,
            selection="System",
            pbc="nojump",
        )
    )

    _require_success(
        trjconv(
            structure=tpr,
            trajectory=nojump,
            output=center,
            selection="System",
            center=True,
        )
    )

    _require_success(
        trjconv(
            structure=tpr,
            trajectory=center,
            output=fit,
            selection="Backbone",
            fit="rot+trans",
        )
    )

    _require_success(
        rms(
            structure=tpr,
            trajectory=fit,
            output=rmsd_dir / "rmsd.xvg",
        )
    )

    _require_success(
        rmsf(
            structure=tpr,
            trajectory=fit,
            output=rmsf_dir / "rmsf.xvg",
        )
    )

    _require_success(
        gyrate(
            structure=tpr,
            trajectory=fit,
            output=rg_dir / "rg.xvg",
        )
    )

    _require_success(
        sasa(
            structure=tpr,
            trajectory=fit,
            output=sasa_dir / "sasa.xvg",
        )
    )

    _require_success(
        hbond(
            structure=tpr,
            trajectory=fit,
            output=hbond_dir / "hbond.xvg",
        )
    )

    _require_success(
        distance(
            structure=tpr,
            trajectory=fit,
            output=com_dir / "com_distance.xvg",
            selection="com of group Protein plus com of group Protein",
        )
    )

    for term, filename in (
        (["Temperature"], "temperature.xvg"),
        (["Pressure"], "pressure.xvg"),
        (["Density"], "density.xvg"),
    ):
        _require_success(
            energy(
                energy_file=edr,
                output=system_dir / filename,
                terms=term,
            )
        )
