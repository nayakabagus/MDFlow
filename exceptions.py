"""
Custom exceptions used throughout MDFlow.
"""


class MDFlowError(Exception):
    """Base exception for MDFlow."""


class GromacsError(MDFlowError):
    """Raised when a GROMACS command fails."""

    def __init__(
        self,
        command: str,
        return_code: int | None = None,
        stderr: str = "",
    ):
        self.command = command
        self.return_code = return_code
        self.stderr = stderr

        message = f"GROMACS command failed: {command}"

        if return_code is not None:
            message += f"\nReturn code: {return_code}"

        if stderr:
            message += f"\n\n{stderr}"

        super().__init__(message)


class FileValidationError(MDFlowError):
    """Raised when an input file is invalid."""
