from __future__ import annotations

from pathlib import Path

from lib.gromacs._core import run_gmx
from lib.runner import CommandResult


def pdb2gmx(
    input_pdb: Path,
    output_gro: Path,
    topology: Path,
    forcefield: str,
    water_model: str,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Generate topology and processed structure.
    """
    return run_gmx(
        "pdb2gmx",
        "-f",
        str(input_pdb),
        "-o",
        str(output_gro),
        "-p",
        str(topology),
        "-ff",
        forcefield,
        "-water",
        water_model,
        cwd=cwd,
    )


def editconf(
    input_gro: Path,
    output_gro: Path,
    box_type: str,
    distance: float,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Define simulation box.
    """
    return run_gmx(
        "editconf",
        "-f",
        str(input_gro),
        "-o",
        str(output_gro),
        "-bt",
        box_type,
        "-d",
        str(distance),
        cwd=cwd,
    )


def solvate(
    input_gro: Path,
    output_gro: Path,
    topology: Path,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Solvate the system.
    """
    return run_gmx(
        "solvate",
        "-cp",
        str(input_gro),
        "-o",
        str(output_gro),
        "-p",
        str(topology),
        cwd=cwd,
    )


def grompp(
    mdp: Path,
    structure: Path,
    topology: Path,
    output_tpr: Path,
    reference: Path | None = None,
    checkpoint: Path | None = None,
    cwd: Path | None = None,
    maxwarn: int = 0,
) -> CommandResult:
    """
    Preprocess GROMACS input files.
    """

    args = [
        "grompp",
        "-f",
        str(mdp),
        "-c",
        str(structure),
        "-p",
        str(topology),
        "-o",
        str(output_tpr),
    ]

    if reference is not None:
        args.extend(
            [
                "-r",
                str(reference),
            ]
        )

    if checkpoint is not None:
        args.extend(
            [
                "-t",
                str(checkpoint),
            ]
        )

    if maxwarn > 0:
        args.extend(
            [
                "-maxwarn",
                str(maxwarn),
            ]
        )

    return run_gmx(
        *args,
        cwd=cwd,
    )


def genion(
    input_tpr: Path,
    output_gro: Path,
    topology: Path,
    positive_ion: str,
    negative_ion: str,
    cwd: Path | None = None,
    solvent_group: str = "SOL",
) -> CommandResult:
    """
    Replace solvent molecules with ions.
    """
    return run_gmx(
        "genion",
        "-s",
        str(input_tpr),
        "-o",
        str(output_gro),
        "-p",
        str(topology),
        "-pname",
        positive_ion,
        "-nname",
        negative_ion,
        "-neutral",
        cwd=cwd,
        stdin=f"{solvent_group}\n",
    )


def make_ndx(
    structure: Path,
    output: Path,
    commands: str,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Create a custom GROMACS index file.
    """

    return run_gmx(
        "make_ndx",
        "-f",
        str(structure),
        "-o",
        str(output),
        cwd=cwd,
        stdin=commands,
    )


def write_index(
    output: Path,
    receptor_ranges: list[tuple[int, int]],
    peptide_ranges: list[tuple[int, int]],
) -> CommandResult:
    """
    Write a GROMACS index file for receptor, peptide, and complex groups.
    """

    def _format_atoms(
        ranges: list[tuple[int, int]],
    ) -> str:
        atoms: list[int] = []

        for start, end in ranges:
            atoms.extend(range(start, end + 1))

        lines: list[str] = []

        for i in range(0, len(atoms), 15):
            lines.append(" ".join(str(atom) for atom in atoms[i : i + 15]))

        return "\n".join(lines)

    receptor_atoms = _format_atoms(receptor_ranges)
    peptide_atoms = _format_atoms(peptide_ranges)

    complex_ranges = [
        (start, end)
        for ranges in (
            receptor_ranges,
            peptide_ranges,
        )
        for start, end in ranges
    ]

    complex_atoms = _format_atoms(complex_ranges)

    content = (
        "[ Receptor ]\n"
        f"{receptor_atoms}\n\n"
        "[ Peptide ]\n"
        f"{peptide_atoms}\n\n"
        "[ Complex ]\n"
        f"{complex_atoms}\n"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        content,
        encoding="utf-8",
    )

    return CommandResult(
        command="write_index",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.0,
    )
