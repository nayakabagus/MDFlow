from pathlib import Path

import pytest

from config.simulation import SimulationConfig
from exceptions import FileValidationError
from lib.runner import CommandResult
from lib.workflow import prepare_system, run_simulation


def _ok(*args, **kwargs) -> CommandResult:
    return CommandResult(
        command="gmx",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.0,
    )


def test_prepare_system_success(tmp_path: Path, monkeypatch):
    pdb = tmp_path / "protein.pdb"
    pdb.write_text("HEADER TEST")

    project = tmp_path / "project"

    monkeypatch.setattr("lib.workflow.pdb2gmx", _ok)
    monkeypatch.setattr("lib.workflow.editconf", _ok)
    monkeypatch.setattr("lib.workflow.solvate", _ok)
    monkeypatch.setattr("lib.workflow.grompp", _ok)
    monkeypatch.setattr("lib.workflow.genion", _ok)

    result = prepare_system(
        input_pdb=pdb,
        project_dir=project,
        config=SimulationConfig(),
    )

    assert result == project / "md" / "solv_ions.gro"


def test_prepare_system_default_config(tmp_path: Path, monkeypatch):
    pdb = tmp_path / "protein.pdb"
    pdb.write_text("HEADER TEST")

    project = tmp_path / "project"

    monkeypatch.setattr("lib.workflow.pdb2gmx", _ok)
    monkeypatch.setattr("lib.workflow.editconf", _ok)
    monkeypatch.setattr("lib.workflow.solvate", _ok)
    monkeypatch.setattr("lib.workflow.grompp", _ok)
    monkeypatch.setattr("lib.workflow.genion", _ok)

    result = prepare_system(
        input_pdb=pdb,
        project_dir=project,
    )

    assert result == project / "md" / "solv_ions.gro"


def test_prepare_system_missing_file():
    with pytest.raises(FileValidationError):
        prepare_system(
            input_pdb="missing.pdb",
            project_dir="project",
        )


def test_run_simulation_success(tmp_path: Path, monkeypatch):
    project = tmp_path / "project"
    md = project / "md"

    md.mkdir(parents=True)

    (md / "solv_ions.gro").write_text("")
    (md / "topol.top").write_text("")

    calls: list[str] = []

    def fake_grompp(*args, **kwargs):
        calls.append("grompp")
        return _ok()

    def fake_mdrun(*args, **kwargs):
        calls.append("mdrun")
        return _ok()

    monkeypatch.setattr(
        "lib.workflow.grompp",
        fake_grompp,
    )

    monkeypatch.setattr(
        "lib.workflow.mdrun",
        fake_mdrun,
    )

    result = run_simulation(
        project_dir=project,
    )

    assert result == md / "md.xtc"

    assert calls == [
        "grompp",
        "mdrun",
        "grompp",
        "mdrun",
        "grompp",
        "mdrun",
        "grompp",
        "mdrun",
    ]


def test_run_simulation_missing_preparation(tmp_path: Path):
    project = tmp_path / "project"

    project.mkdir()

    with pytest.raises(FileNotFoundError):
        run_simulation(project)
