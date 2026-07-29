"""
Simulation commands.
"""

from pathlib import Path

import typer

from lib.workflow import run_simulation

app = typer.Typer(
    help="Run molecular dynamics simulation.",
)


@app.command()
def run(
    project: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="MDFlow project directory.",
    ),
    nt: int | None = typer.Option(
        None,
        "--nt",
        help="Number of CPU threads.",
    ),
):
    """
    Run the complete molecular dynamics workflow.
    """

    try:
        trajectory = run_simulation(
            project_dir=project,
            nt=nt,
        )
    except Exception as exc:
        typer.secho(
            str(exc),
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.secho(
        f"Simulation completed successfully.\nTrajectory: {trajectory}",
        fg=typer.colors.GREEN,
    )
