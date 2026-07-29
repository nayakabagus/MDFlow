"""
Runner module for executing external commands.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from exceptions import GromacsError
from lib.logger import logger


@dataclass(slots=True)
class CommandResult:
    command: str
    success: bool
    return_code: int
    stdout: str
    stderr: str
    elapsed_time: float


def run_command(
    command: list[str],
    stdin: str | None = None,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Execute an external command.
    """

    logger.info(f"Running: {' '.join(command)}")

    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            cwd=cwd,
        )

    except FileNotFoundError as e:
        logger.error("Command not found.")

        raise GromacsError(
            command=" ".join(command),
            stderr=str(e),
        ) from e

    elapsed = time.time() - start_time

    if result.returncode != 0:
        logger.error("Command failed.")

        raise GromacsError(
            command=" ".join(command),
            return_code=result.returncode,
            stderr=result.stderr.strip(),
        )

    logger.success(f"Completed in {elapsed:.2f} s")

    return CommandResult(
        command=" ".join(command),
        success=True,
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        elapsed_time=elapsed,
    )
