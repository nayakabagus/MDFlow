"""
Tests for analysis workflow.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from config.simulation import SimulationConfig
from lib.layout import ProjectLayout
from lib.runner import CommandResult
from lib.workflow import run_analysis
from main import app


def _success() -> CommandResult:
    return CommandResult(
        command="gmx",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.1,
    )


@patch("lib.workflow.create_index")
@patch("lib.workflow.energy")
@patch("lib.workflow.distance")
@patch("lib.workflow.hbond")
@patch("lib.workflow.sasa")
@patch("lib.workflow.gyrate")
@patch("lib.workflow.rmsf")
@patch("lib.workflow.rms")
def test_run_analysis(
    mock_rms: MagicMock,
    mock_rmsf: MagicMock,
    mock_rg: MagicMock,
    mock_sasa: MagicMock,
    mock_hbond: MagicMock,
    mock_distance: MagicMock,
    mock_energy: MagicMock,
    mock_create_index: MagicMock,
    tmp_path: Path,
) -> None:
    """
    run_analysis should execute the default analysis workflow.
    """

    for mock in (
        mock_rms,
        mock_rmsf,
        mock_rg,
        mock_sasa,
        mock_hbond,
        mock_distance,
        mock_energy,
    ):
        mock.return_value = _success()

    project = tmp_path / "project"

    layout = ProjectLayout(project)
    layout.create()

    layout.md_tpr.touch()
    layout.md_xtc.touch()
    layout.md_fit_xtc.touch()
    layout.md_edr.touch()

    config = SimulationConfig()

    run_analysis(
        project,
        config,
    )

    mock_create_index.assert_called_once_with(
        project,
        config,
    )

    assert mock_rms.called
    assert mock_rmsf.called
    assert mock_rg.called
    assert mock_sasa.called
    assert mock_hbond.called

    mock_hbond.assert_called_once_with(
        structure=layout.md_tpr,
        trajectory=layout.md_fit_xtc,
        output=layout.hbond_xvg,
        cwd=layout.md,
        donor_group="Receptor",
        acceptor_group="Peptide",
        index=layout.index_ndx,
    )

    assert mock_distance.called
    assert mock_energy.call_count == 3


def test_analysis_run_command(tmp_path: Path) -> None:
    """analysis run should process the trajectory and run analysis."""

    runner = CliRunner()
    project = tmp_path / "project"
    project.mkdir()

    with patch("cli.analysis.process_trajectory") as mock_process, patch(
        "cli.analysis.run_analysis"
    ) as mock_analysis:
        result = runner.invoke(
            app,
            ["analysis", "run", str(project)],
        )

    assert result.exit_code == 0

    mock_process.assert_called_once_with(project)

    mock_analysis.assert_called_once()

    analysis_project = mock_analysis.call_args.args[0]
    config = mock_analysis.call_args.args[1]

    assert analysis_project == project
    assert isinstance(config, SimulationConfig)
