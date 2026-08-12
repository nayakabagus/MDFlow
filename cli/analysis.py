"""
Analysis commands.
"""

from pathlib import Path

import typer

from config.simulation import SimulationConfig
from lib.workflow import process_trajectory, run_analysis

app = typer.Typer()


@app.command()
def run(
    project: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="MDFlow project directory.",
    ),
):
    """Process trajectory and run the default MD analysis."""

    try:
        process_trajectory(project)
        run_analysis(project, SimulationConfig())
    except Exception as exc:
        typer.secho(
            str(exc),
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.secho(
        f"Analysis completed successfully.\nProject: {project}",
        fg=typer.colors.GREEN,
    )
