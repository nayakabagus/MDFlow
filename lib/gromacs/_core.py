from __future__ import annotations

from pathlib import Path

from lib.runner import CommandResult, run_command


def run_gmx(
    *args: str,
    stdin: str | None = None,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Run a GROMACS command.
    """
    return run_command(
        ["gmx", *args],
        stdin=stdin,
        cwd=cwd,
    )


def version() -> CommandResult:
    """
    Return GROMACS version information.
    """
    return run_gmx("--version")
