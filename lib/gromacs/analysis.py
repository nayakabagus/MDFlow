"""
Wrapper for GROMACS analysis commands.
"""

from __future__ import annotations

from pathlib import Path

from lib.gromacs._core import run_gmx
from lib.runner import CommandResult


def rms(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    reference_group: str = "Backbone",
    fit_group: str = "Backbone",
) -> CommandResult:
    """
    Calculate RMSD.
    """

    return run_gmx(
        "rms",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
        cwd=cwd,
        stdin=f"{reference_group}\n{fit_group}\n",
    )


def rmsf(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    group: str = "C-alpha",
) -> CommandResult:
    """
    Calculate per-residue RMSF using C-alpha atoms.
    """

    return run_gmx(
        "rmsf",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
        "-res",
        cwd=cwd,
        stdin=f"{group}\n",
    )


def gyrate(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    group: str = "Protein",
) -> CommandResult:
    """
    Calculate radius of gyration.
    """

    return run_gmx(
        "gyrate",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
        cwd=cwd,
        stdin=f"{group}\n",
    )


def sasa(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    group: str = "Protein",
) -> CommandResult:
    """
    Calculate solvent accessible surface area.
    """

    return run_gmx(
        "sasa",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
        cwd=cwd,
        stdin=f"{group}\n",
    )


def trjconv(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    input_groups: list[str] | None = None,
    pbc: str | None = None,
    center: bool = False,
    fit: str | None = None,
) -> CommandResult:
    """
    Process trajectory using gmx trjconv.
    """

    command = [
        "trjconv",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
    ]

    if pbc is not None:
        command.extend(["-pbc", pbc])

    if center:
        command.append("-center")

    if fit is not None:
        command.extend(["-fit", fit])

    if input_groups is None:
        input_groups = ["System"]

    return run_gmx(
        *command,
        cwd=cwd,
        stdin="\n".join(input_groups) + "\n",
    )


def hbond(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    donor_group: str = "Protein",
    acceptor_group: str = "Protein",
    index: Path | None = None,
) -> CommandResult:
    """
    Calculate hydrogen bonds between two selected groups.
    """

    command = [
        "hbond",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-num",
        str(output),
    ]

    if index is not None:
        command.extend(
            [
                "-n",
                str(index),
            ]
        )

    return run_gmx(
        *command,
        cwd=cwd,
        stdin=f"{donor_group}\n{acceptor_group}\n",
    )


def distance(
    structure: Path,
    trajectory: Path,
    output: Path,
    selection: str,
    cwd: Path | None = None,
    index: Path | None = None,
) -> CommandResult:
    """
    Calculate center-of-mass distance.
    """

    command = [
        "distance",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-oall",
        str(output),
    ]

    if index is not None:
        command.extend(
            [
                "-n",
                str(index),
            ]
        )

    command.extend(
        [
            "-select",
            selection,
        ]
    )

    return run_gmx(
        *command,
        cwd=cwd,
    )


def energy(
    energy_file: Path,
    output: Path,
    terms: list[str],
    cwd: Path | None = None,
) -> CommandResult:
    """
    Extract energy terms.
    """

    stdin = "\n".join(terms) + "\n"

    return run_gmx(
        "energy",
        "-f",
        str(energy_file),
        "-o",
        str(output),
        cwd=cwd,
        stdin=stdin,
    )
