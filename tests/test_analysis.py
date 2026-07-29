"""
Tests for analysis workflow.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from lib.layout import ProjectLayout
from lib.runner import CommandResult
from lib.workflow import run_analysis


def _success() -> CommandResult:
    return CommandResult(
        command="gmx",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.1,
    )


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
    ):
        mock.return_value = _success()

    project = tmp_path / "project"

    layout = ProjectLayout(project)
    layout.create()

    layout.md_tpr.touch()
    layout.md_xtc.touch()
    layout.md_fit_xtc.touch()

    run_analysis(project)

    assert mock_rms.called
    assert mock_rmsf.called
    assert mock_rg.called
    assert mock_sasa.called
    assert mock_hbond.called
    assert mock_distance.called
