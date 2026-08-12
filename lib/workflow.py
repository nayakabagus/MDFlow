"""
Workflow module.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from config.simulation import SimulationConfig
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
from lib.gromacs.mmpbsa import run_mmpbsa
from lib.gromacs.prepare import (
    editconf,
    genion,
    grompp,
    pdb2gmx,
    solvate,
    write_index,
)
from lib.gromacs.simulation import mdrun
from lib.layout import ProjectLayout
from lib.logger import logger
from lib.mmpbsa_input import MMPBSAInput
from lib.resources import ResourceManager
from lib.runner import CommandResult
from lib.validation import validate_pdb_file


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
        layout.topology,
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

    ResourceManager.install_templates(
        layout,
        config.forcefield,
    )

    config.template_dir = layout.md

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
            maxwarn=1,
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

    config.template_dir = layout.md

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


def _count_topology_atoms(
    topology_file: Path,
) -> int:
    """
    Count atoms defined in a GROMACS topology include file.
    """

    text = topology_file.read_text(encoding="utf-8")

    inside_atoms = False
    count = 0

    for line in text.splitlines():
        stripped = line.strip()

        if stripped == "[ atoms ]":
            inside_atoms = True
            continue

        if inside_atoms and stripped.startswith("["):
            break

        if inside_atoms:
            if not stripped or stripped.startswith(";"):
                continue

            fields = stripped.split()

            if fields and fields[0].isdigit():
                count += 1

    return count


def _get_component_ranges(
    layout: ProjectLayout,
    config: SimulationConfig,
) -> tuple[str, str]:
    """
    Determine global atom ranges for receptor and peptide components
    using the molecule order defined in topol.top.
    """

    topology = layout.md / "topol.top"

    if not topology.exists():
        raise FileNotFoundError(f"Topology not found: {topology}")

    receptor_ranges: list[str] = []
    peptide_ranges: list[str] = []

    current_atom = 1

    inside_molecules = False

    for line in topology.read_text(encoding="utf-8").splitlines():

        stripped = line.strip()

        if stripped == "[ molecules ]":
            inside_molecules = True
            continue

        if not inside_molecules:
            continue

        if not stripped or stripped.startswith(";"):
            continue

        if stripped.startswith("["):
            break

        fields = stripped.split()

        if len(fields) < 2:
            continue

        molecule_name = fields[0]

        try:
            molecule_count = int(fields[1])
        except ValueError:
            continue

        if not molecule_name.startswith("Protein_chain_"):
            continue

        chain_id = molecule_name.removeprefix("Protein_chain_")

        chain_file = layout.md / f"topol_Protein_chain_{chain_id}.itp"

        if not chain_file.exists():
            raise FileNotFoundError(f"Chain topology not found: {chain_file}")

        atoms_per_molecule = _count_topology_atoms(chain_file)

        total_atoms = atoms_per_molecule * molecule_count

        start = current_atom
        end = current_atom + total_atoms - 1

        atom_range = f"{start}-{end}"

        if chain_id in config.receptor_chains:
            receptor_ranges.append(atom_range)

        if chain_id in config.peptide_chains:
            peptide_ranges.append(atom_range)

        current_atom = end + 1

    if not receptor_ranges:
        raise ValueError("No receptor chains found in topol.top.")

    if not peptide_ranges:
        raise ValueError("No peptide chains found in topol.top.")

    return (
        " | ".join(receptor_ranges),
        " | ".join(peptide_ranges),
    )


def create_index(
    project_dir: str | Path,
    config: SimulationConfig,
) -> Path:
    """
    Create receptor, peptide, and complex index groups.
    """

    layout = ProjectLayout(Path(project_dir))

    _validate_simulation_project(layout)

    receptor_range, peptide_range = _get_component_ranges(
        layout,
        config,
    )

    def parse_ranges(
        value: str,
    ) -> list[tuple[int, int]]:
        ranges: list[tuple[int, int]] = []

        for part in value.split("|"):
            start, end = part.strip().split("-")
            ranges.append((int(start), int(end)))

        return ranges

    receptor_ranges = parse_ranges(
        receptor_range,
    )

    peptide_ranges = parse_ranges(
        peptide_range,
    )

    logger.info("Creating custom index...")

    _require_success(
        write_index(
            output=layout.index_ndx,
            receptor_ranges=receptor_ranges,
            peptide_ranges=peptide_ranges,
        )
    )

    logger.success("Custom index created.")

    return layout.index_ndx


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
            input_groups=["System"],
            pbc="mol",
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_nopbc_xtc,
            output=layout.md_nojump_xtc,
            input_groups=["System"],
            pbc="nojump",
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_nojump_xtc,
            output=layout.md_center_xtc,
            input_groups=["Protein", "System"],
            center=True,
            cwd=layout.md,
        )
    )

    _require_success(
        trjconv(
            structure=layout.md_tpr,
            trajectory=layout.md_center_xtc,
            output=layout.md_fit_xtc,
            input_groups=["Backbone", "System"],
            fit="rot+trans",
            cwd=layout.md,
        )
    )

    logger.success("Trajectory processing completed.")

    return layout.md_fit_xtc


def run_analysis(
    project_dir: str | Path,
    config: SimulationConfig,
) -> None:
    """
    Run the default molecular dynamics analysis workflow.
    """

    layout = ProjectLayout(Path(project_dir))

    _validate_simulation_project(layout)

    logger.info("Running analysis...")

    create_index(
        project_dir,
        config,
    )

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
            donor_group="Receptor",
            acceptor_group="Peptide",
            index=layout.index_ndx,
        )
    )

    _require_success(
        distance(
            structure=layout.md_tpr,
            trajectory=layout.md_fit_xtc,
            output=layout.com_xvg,
            selection='com of group "Receptor" plus com of group "Peptide"',
            cwd=layout.md,
            index=layout.index_ndx,
        )
    )

    _require_success(
        energy(
            energy_file=layout.md_edr,
            output=layout.temperature_xvg,
            terms=["Temperature"],
            cwd=layout.md,
        )
    )

    _require_success(
        energy(
            energy_file=layout.md_edr,
            output=layout.pressure_xvg,
            terms=["Pressure"],
            cwd=layout.md,
        )
    )

    _require_success(
        energy(
            energy_file=layout.md_edr,
            output=layout.density_xvg,
            terms=["Density"],
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
            topology=layout.topology,
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
