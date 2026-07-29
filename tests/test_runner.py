import pytest

from exceptions import GromacsError
from lib.runner import run_command


def test_run_command_success():
    result = run_command(["python", "--version"])

    assert result.success is True
    assert result.return_code == 0
    assert "Python" in result.stdout or "Python" in result.stderr


def test_run_command_failure():
    with pytest.raises(GromacsError) as exc_info:
        run_command(["false"])

    error = exc_info.value

    assert error.return_code == 1
    assert error.command == "false"
