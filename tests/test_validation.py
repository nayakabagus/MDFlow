from pathlib import Path

import pytest

from exceptions import FileValidationError
from lib.validation import validate_pdb_file


def test_validate_existing_pdb(tmp_path: Path):
    pdb = tmp_path / "protein.pdb"
    pdb.write_text("HEADER TEST")

    result = validate_pdb_file(str(pdb))

    assert result == pdb


def test_validate_missing_file():
    with pytest.raises(FileValidationError):
        validate_pdb_file("missing.pdb")


def test_validate_wrong_extension(tmp_path: Path):
    txt = tmp_path / "protein.txt"
    txt.write_text("test")

    with pytest.raises(FileValidationError):
        validate_pdb_file(str(txt))
