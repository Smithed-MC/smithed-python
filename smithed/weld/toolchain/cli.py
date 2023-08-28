import logging
from collections.abc import Sequence
from glob import glob

import typer
from rich.logging import RichHandler
from rich.progress import Progress
from rich.rule import Rule

from smithed.theming import console, print

from .main import run_weld

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)


app = typer.Typer(
    help="🔧 Weld multiple data and resource packs into a single zip!",
)


@app.command()
def weld(packs: list[str]):
    """Weld data and resource packs together with all data and assets in one zip.

    See https://wiki.smithed.dev/weld more info!
    """

    print(Rule("[bold][accent] Weld [/bold][italic]by Smithed"))
    print()
    packs = list(expand_globs(packs))

    if len(packs) < 2:
        print("[error]:boom: Need at least one pack to weld")
        raise typer.Exit(-1)

    with Progress(console=console) as progress:
        progress.add_task("[bold][accent_light]Welding", total=None)

        with run_weld(packs) as ctx:
            ctx.data.save("tacos.zip")

    print()
    print(Rule("[success]✔️ Done"))


def expand_globs(packs: Sequence[str]):
    for pack in packs:
        yield from glob(pack)


if __name__ == "__main__":
    typer.run(weld)
