from pathlib import Path

from lib.gromacs import mdrun, version
from lib.runner import CommandResult


def test_gromacs_version():
    result = version()

    assert result.success is True
    assert result.return_code == 0
    assert "GROMACS" in result.stdout or "GROMACS" in result.stderr


def test_mdrun(mocker):
    expected = CommandResult(
        command="gmx mdrun -deffnm md -nt 8",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.01,
    )

    mocked = mocker.patch(
        "lib.gromacs.simulation.run_gmx",
        return_value=expected,
    )

    result = mdrun(
        deffnm="md",
        cwd=Path("/tmp/project"),
        nt=8,
    )

    mocked.assert_called_once_with(
        "mdrun",
        "-deffnm",
        "md",
        "-nt",
        "8",
        cwd=Path("/tmp/project"),
    )

    assert result is expected


def test_mdrun_default(mocker):
    expected = CommandResult(
        command="gmx mdrun -deffnm em",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.01,
    )

    mocked = mocker.patch(
        "lib.gromacs.simulation.run_gmx",
        return_value=expected,
    )

    result = mdrun("em")

    mocked.assert_called_once_with(
        "mdrun",
        "-deffnm",
        "em",
        cwd=None,
    )

    assert result is expected
