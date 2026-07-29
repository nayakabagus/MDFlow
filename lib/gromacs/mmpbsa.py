from __future__ import annotations

from pathlib import Path

from lib.runner import CommandResult, run_command


def run_mmpbsa(
    *,
    structure: Path,
    trajectory: Path,
    topology: Path,
    index: Path,
    input_file: Path,
    output: Path,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Execute gmx_MMPBSA.
    """

    return run_command(
        [
            "gmx_MMPBSA",
            "-O",
            "-i",
            str(input_file),
            "-cs",
            str(structure),
            "-ct",
            str(trajectory),
            "-cp",
            str(topology),
            "-ci",
            str(index),
            "-o",
            str(output),
        ],
        cwd=cwd,
    )
