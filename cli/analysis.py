"""
Analysis commands.
"""

import typer

app = typer.Typer()


@app.command()
def rmsd():
    """Calculate RMSD."""

    typer.echo("Calculating RMSD...")


@app.command()
def rmsf():
    """Calculate RMSF."""

    typer.echo("Calculating RMSF...")
