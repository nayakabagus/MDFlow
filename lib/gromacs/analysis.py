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
    group: str = "Backbone",
) -> CommandResult:
    """
    Calculate RMSF.
    """

    return run_gmx(
        "rmsf",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-o",
        str(output),
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
    selection: str = "System",
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

    return run_gmx(
        *command,
        cwd=cwd,
        stdin=f"{selection}\n",
    )


def hbond(
    structure: Path,
    trajectory: Path,
    output: Path,
    cwd: Path | None = None,
    donor_group: str = "Protein",
    acceptor_group: str = "Protein",
) -> CommandResult:
    """
    Calculate hydrogen bonds.
    """

    return run_gmx(
        "hbond",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-num",
        str(output),
        cwd=cwd,
        stdin=f"{donor_group}\n{acceptor_group}\n",
    )


def distance(
    structure: Path,
    trajectory: Path,
    output: Path,
    selection: str,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Calculate center-of-mass distance.
    """

    return run_gmx(
        "distance",
        "-s",
        str(structure),
        "-f",
        str(trajectory),
        "-oall",
        str(output),
        "-select",
        selection,
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
