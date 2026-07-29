"""
Validation utilities for MDFlow.
"""

from pathlib import Path

from exceptions import FileValidationError


def validate_pdb_file(file_path: str) -> Path:
    """
    Validate that the input file exists and is a PDB file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileValidationError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdb":
        raise FileValidationError("Input file must have a .pdb extension.")

    return path
