"""
Wrapper for GROMACS simulation commands.
"""

from __future__ import annotations

from pathlib import Path

from lib.gromacs._core import run_gmx
from lib.runner import CommandResult


def mdrun(
    deffnm: str | Path,
    cwd: Path | None = None,
    nt: int | None = None,
) -> CommandResult:
    """
    Run GROMACS mdrun.

    Parameters
    ----------
    deffnm
        Base filename for simulation input/output.
    cwd
        Working directory.
    nt
        Number of CPU threads.
    """

    command: list[str] = [
        "mdrun",
        "-deffnm",
        str(deffnm),
    ]

    if nt is not None:
        command.extend(
            [
                "-nt",
                str(nt),
            ]
        )

    return run_gmx(
        *command,
        cwd=cwd,
    )
