"""
MDFlow command-line interface.
"""

import typer

from cli.analysis import app as analysis_app
from cli.prepare import app as prepare_app
from cli.simulation import app as simulation_app

app = typer.Typer(help="MDFlow: Molecular Dynamics Workflow Automation")

app.add_typer(
    prepare_app,
    name="prepare",
)

app.add_typer(
    simulation_app,
    name="simulation",
)

app.add_typer(
    analysis_app,
    name="analysis",
)


@app.command()
def version():
    """Show MDFlow version."""

    typer.echo("MDFlow v0.1.0")


if __name__ == "__main__":
    app()
