"""
Workflow module.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from config.simulation import SimulationConfig
from lib.gromacs.prepare import (
    editconf,
    genion,
    grompp,
    pdb2gmx,
    solvate,
)
from lib.gromacs.analysis import (
    distance,
    gyrate,
    hbond,
    rms,
    rmsf,
    sasa,
    trjconv,
)
from lib.gromacs.simulation import mdrun
from lib.layout import ProjectLayout
from lib.logger import logger
from lib.runner import CommandResult
from lib.validation import validate_pdb_file
from lib.gromacs.mmpbsa import run_mmpbsa
from lib.mmpbsa_input import MMPBSAInput


def _require_success(
    result: CommandResult,
) -> None:
    """
    Raise RuntimeError if a command failed.
    """

    if result.success:
        return

    message = f"Command failed:\n" f"{result.command}\n\n" f"{result.stderr.strip()}"

    raise RuntimeError(message)


def _validate_prepared_project(
    layout: ProjectLayout,
) -> None:
    """
    Validate that a project has completed system preparation.
    """

    required_files = [
        layout.ions,
        layout.topology,
    ]

    missing = [file for file in required_files if not file.exists()]

    if not missing:
        return

    files = "\n".join(f"- {file}" for file in missing)

    raise FileNotFoundError(
        "Simulation cannot start.\n\n"
        "Missing files:\n"
        f"{files}\n\n"
        "Run system preparation first."
    )


def _validate_simulation_project(
    layout: ProjectLayout,
) -> None:
    """
    Validate that a project has completed MD simulation.
    """

    required_files = [
        layout.md_tpr,
        layout.md_xtc,
    ]

    missing = [file for file in required_files if not file.exists()]

    if not missing:
        return

    files = "\n".join(f"- {file}" for file in missing)

    raise FileNotFoundError(
        "Analysis cannot start.\n\n"
        "Missing files:\n"
        f"{files}\n\n"
        "Run simulation first."
    )


def _validate_mmpbsa_project(
    layout: ProjectLayout,
) -> None:
    """
    Validate that a project is ready for MM-PBSA.
    """

    required_files = [
        layout.md_tpr,
        layout.md_fit_xtc,
        layout.topol_top,
        layout.index_ndx,
    ]

    missing = [file for file in required_files if not file.exists()]

    if not missing:
        return

    files = "\n".join(f"- {file}" for file in missing)

    raise FileNotFoundError(
        "MM-PBSA cannot start.\n\n"
        "Missing files:\n"
        f"{files}\n\n"
        "Run the previous workflow steps first."
    )


def _run_stage(
    *,
    stage: str,
    mdp: Path,
    structure: Path,
    topology: Path,
    output_tpr: Path,
    cwd: Path,
    reference: Path | None = None,
    checkpoint: Path | None = None,
    maxwarn: int = 0,
    nt: int | None = None,
) -> None:
    """
    Execute one simulation stage.
    """

    logger.info(f"Running {stage}...")

    _require_success(
        grompp(
            mdp=mdp,
            structure=structure,
            topology=topology,
            output_tpr=output_tpr,
            reference=reference,
            checkpoint=checkpoint,
            cwd=cwd,
            maxwarn=maxwarn,
        )
    )

    deffnm = output_tpr.with_suffix("")

    _require_success(
        mdrun(
            deffnm=deffnm,
            cwd=cwd,
            nt=nt,
        )
    )

    logger.success(f"{stage} completed.")


def prepare_system(
    input_pdb: str | Path,
    project_dir: str | Path,
    config: SimulationConfig | None = None,
) -> Path:
    """
    Prepare a molecular system.

    Returns
    -------
    Path
        Path to solv_ions.gro
    """

    config = config or SimulationConfig()

    pdb_file = validate_pdb_file(input_pdb)

    layout = ProjectLayout(Path(project_dir))

    layout.create()

    shutil.copy2(
        pdb_file,
        layout.input / "input.pdb",
    )

    logger.success(f"Validated : {pdb_file.name}")
    logger.info(f"Project    : {layout.root}")
    logger.info(f"Forcefield : {config.forcefield}")
    logger.info(f"Water      : {config.water_model}")
    logger.info(f"Box        : {config.box_type}")

    _require_success(
        pdb2gmx(
            input_pdb=layout.input / "input.pdb",
            output_gro=layout.processed,
            topology=layout.topology,
            forcefield=config.forcefield,
            water_model=config.water_model,
            cwd=layout.md,
        )
    )

    _require_success(
        editconf(
            input_gro=layout.processed,
            output_gro=layout.boxed,
            box_type=config.box_type,
            distance=config.box_distance,
            cwd=layout.md,
        )
    )

    _require_success(
        solvate(
            input_gro=layout.boxed,
            output_gro=layout.solvated,
            topology=layout.topology,
            cwd=layout.md,
        )
    )

    _require_success(
        grompp(
            mdp=config.ions_mdp,
            structure=layout.solvated,
            topology=layout.topology,
            output_tpr=layout.ions_tpr,
            cwd=layout.md,
        )
    )

    _require_success(
        genion(
            input_tpr=layout.ions_tpr,
            output_gro=layout.ions,
            topology=layout.topology,
            positive_ion=config.positive_ion,
            negative_ion=config.negative_ion,
            cwd=layout.md,
        )
    )

    logger.success("System preparation completed.")

    return layout.ions


def run_simulation(
    project_dir: str | Path,
    config: SimulationConfig | None = None,
    nt: int | None = None,
) -> Path:
    """
    Run the complete molecular dynamics simulation workflow.

    Parameters
    ----------
    project_dir
        MDFlow project directory.
    config
        Simulation configuration.
    nt
        Number of CPU threads passed to GROMACS.

    Returns
    -------
    Path
        Path to the production trajectory.
    """

    config = config or SimulationConfig()

    layout = ProjectLayout(Path(project_dir))

    _validate_prepared_project(layout)

    logger.info("Starting molecular dynamics simulation...")

    _run_stage(
        stage="Energy Minimization",
        mdp=config.em_mdp,
        structure=layout.ions,
        topology=layout.topology,
        output_tpr=layout.em_tpr,
        cwd=layout.md,
    )

    _run_stage(
        stage="NVT Equilibration",
        mdp=config.nvt_mdp,
        structure=layout.em_gro,
        topology=layout.topology,
        output_tpr=layout.nvt_tpr,
        reference=layout.em_gro,
        cwd=layout.md,
        nt=nt,
    )

    _run_stage(
        stage="NPT Equilibration",
        mdp=config.npt_mdp,
        structure=layout.nvt_gro,
        topology=layout.topology,
        output_tpr=layout.npt_tpr,
        reference=layout.nvt_gro,
        checkpoint=layout.nvt_cpt,
        cwd=layout.md,
        nt=nt,
    )

    _run_stage(
        stage="Production MD",
        mdp=config.md_mdp,
        structure=layout.npt_gro,
        topology=layout.topology,
        output_tpr=layout.md_tpr,
        checkpoint=layout.npt_cpt,
        cwd=layout.md,
        nt=nt,
    )

    logger.success("Simulation completed successfully.")

    return layout.md_xtc


def process_trajectory(
    project_dir: str | Path,
) -> Path:
    """
    Process the production trajectory for downstream analyses.

    Parameters
    ----------
    project_dir
        MDFlow project directory.

    Returns
    -------
    Path
        Path to the fitted trajectory.
    """

    layout = ProjectLayout(Path(project_dir))

    _validate_simulation_project(layout)

    logger.info("Processing trajectory...")

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_xtc,
            output=layout.md_nopbc_xtc,
            pbc="mol",
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_nopbc_xtc,
            output=layout.md_nojump_xtc,
            pbc="nojump",
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_nojump_xtc,
            output=layout.md_center_xtc,
            center=True,
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_center_xtc,
            output=layout.md_fit_xtc,
            fit="rot+trans",
            cwd=layout.md,
        )
    )

    logger.success("Trajectory processing completed.")

    return layout.md_fit_xtc


def run_analysis(
    project_dir: str | Path,
) -> None:
    """
    Run the default molecular dynamics analysis workflow.

    Parameters
    ----------
    project_dir
        MDFlow project directory.
    """

    layout = ProjectLayout(Path(project_dir))

    _validate_simulation_project(layout)

    logger.info("Running analysis...")

    _require_success(
        rms(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.rmsd_xvg,
            cwd=layout.md,
        )
    )

    _require_success(
        rmsf(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.rmsf_xvg,
            cwd=layout.md,
        )
    )

    _require_success(
        gyrate(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.rg_xvg,
            cwd=layout.md,
        )
    )

    _require_success(
        sasa(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.sasa_xvg,
            cwd=layout.md,
        )
    )

    _require_success(
        hbond(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.hbond_xvg,
            cwd=layout.md,
        )
    )

    _require_success(
        distance(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.com_xvg,
            selection='com of group "Protein" plus com of group "Protein"',
            cwd=layout.md,
        )
    )

    logger.success("Analysis completed.")


def run_mmpbsa_workflow(
    project_dir: str | Path,
) -> Path:
    """
    Run the MM-PBSA workflow.

    Parameters
    ----------
    project_dir
        MDFlow project directory.

    Returns
    -------
    Path
        Path to FINAL_RESULTS_MMPBSA.dat.
    """

    layout = ProjectLayout(Path(project_dir))

    _validate_mmpbsa_project(layout)

    logger.info("Preparing MM-PBSA input...")

    layout.mmpbsa.mkdir(
        parents=True,
        exist_ok=True,
    )

    MMPBSAInput().write(
        layout.mmpbsa_input,
    )

    logger.info("Running gmx_MMPBSA...")

    _require_success(
        run_mmpbsa(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            topology=layout.topol_top,
            index=layout.index_ndx,
            input_file=layout.mmpbsa_input,
            output=layout.mmpbsa_results,
            cwd=layout.mmpbsa,
        )
    )

    if not layout.mmpbsa_results.exists():
        raise FileNotFoundError(f"MM-PBSA output not found: {layout.mmpbsa_results}")

    logger.success("MM-PBSA completed.")

    return layout.mmpbsa_results
