"""
Prepare commands.
"""

from pathlib import Path

import typer

from exceptions import MDFlowError
from lib.workflow import prepare_system

app = typer.Typer()


@app.callback(invoke_without_command=True)
def prepare(
    ctx: typer.Context,
    input_pdb: str = typer.Argument(..., help="Input PDB file."),
    project: str = typer.Argument(..., help="Project directory."),
):
    """
    Prepare a molecular system.
    """

    if ctx.invoked_subcommand is not None:
        return

    try:
        result: Path = prepare_system(
            input_pdb=input_pdb,
            project_dir=project,
        )

        typer.secho(
            f"✔ Preparation completed: {result}",
            fg=typer.colors.GREEN,
        )

    except MDFlowError as e:
        typer.secho(
            str(e),
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
