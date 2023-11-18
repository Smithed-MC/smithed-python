from typing import Annotated, Optional

import typer

cli = typer.Typer(
    help="All smithed functionality at the tip of your fingers!",
    add_completion=False,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="markdown",
)


# Decided to include the flavortext as standard
@cli.command(
    epilog="Made with :heart: by [Smithed](https://beta.smithed.dev)",
    no_args_is_help=True,
)
def smithed(
):
    """
    Access the smithed API directly from the command line!
    """
    print(f"Welcome to smithed!")

if __name__ == "__main__":
    typer.run(smithed)