"""
Tests for trajectory processing workflow.
"""

from pathlib import Path
from unittest.mock import MagicMock, call, patch

from lib.layout import ProjectLayout
from lib.runner import CommandResult
from lib.workflow import process_trajectory


def _success() -> CommandResult:
    return CommandResult(
        command="gmx trjconv",
        success=True,
        return_code=0,
        stdout="",
        stderr="",
        elapsed_time=0.1,
    )


@patch("lib.workflow.trjconv")
def test_process_trajectory(
    mock_trjconv: MagicMock,
    tmp_path: Path,
) -> None:
    """
    process_trajectory should execute the standard four-step
    trajectory processing workflow.
    """

    mock_trjconv.return_value = _success()

    project = tmp_path / "project"

    layout = ProjectLayout(project)
    layout.create()

    layout.md_tpr.touch()
    layout.md_xtc.touch()

    output = process_trajectory(project)

    assert output == layout.md_fit_xtc

    assert mock_trjconv.call_count == 4

    mock_trjconv.assert_has_calls(
        [
            call(
                structure=layout.md_tpr,
                trajectory=layout.md_xtc,
                output=layout.md_nopbc_xtc,
                input_groups=["System"],
                pbc="mol",
                cwd=layout.md,
            ),
            call(
                structure=layout.md_tpr,
                trajectory=layout.md_nopbc_xtc,
                output=layout.md_nojump_xtc,
                input_groups=["System"],
                pbc="nojump",
                cwd=layout.md,
            ),
            call(
                structure=layout.md_tpr,
                trajectory=layout.md_nojump_xtc,
                output=layout.md_center_xtc,
                input_groups=["Protein", "System"],
                center=True,
                cwd=layout.md,
            ),
            call(
                structure=layout.md_tpr,
                trajectory=layout.md_center_xtc,
                output=layout.md_fit_xtc,
                input_groups=["Backbone", "System"],
                fit="rot+trans",
                cwd=layout.md,
            ),
        ]
    )
