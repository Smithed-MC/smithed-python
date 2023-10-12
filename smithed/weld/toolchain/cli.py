import logging
import shutil
from collections.abc import Sequence
from glob import glob
from pathlib import Path
from time import perf_counter
from typing import Annotated, Optional

import typer
from beet import ProjectCache
from rich.logging import RichHandler
from rich.panel import Panel

from smithed.theming import console, print
from smithed.utils import error_handler, path_str

from .main import run_weld

cli = typer.Typer(
    help="🔧 Weld multiple data and resource packs into a single zip!",
    add_completion=False,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="markdown",
)

logger = logging.getLogger("weld")
OUTPUT_DIR, OUTPUT = "output", "welded-pack.zip"


def version_callback(value: bool):
    if not value:
        return
    from smithed import weld

    print("weld", style="secondary", end=" ")
    print(f"v{weld.__version__}", highlight=False, style="accent_light")
    raise typer.Exit()


@cli.command(
    epilog="Made with :heart: by [Smithed](https://beta.smithed.dev)",
    no_args_is_help=True,
)
def weld(
    packs: Annotated[list[str], typer.Argument(help="A series of packs to weld")],
    dir: Annotated[Path, typer.Option(help="Output directory")] = Path(OUTPUT_DIR),
    name: Annotated[Path, typer.Option(help="Output file name")] = Path(OUTPUT),
    log: Annotated[str, typer.Option(help="Log level")] = "INFO",
    clear_cache: Annotated[bool, typer.Option(help="Clear cache")] = False,
    dev: Annotated[bool, typer.Option(help="Enable dev mode")] = False,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    """Weld data and resource packs together with all data and assets in one zip.

    See the [docs](https://wiki.smithed.dev/weld) more info!
    """

    setup_logger(dev, log.upper())

    packs = list(expand_globs(packs))
    if len(packs) < 1:
        raise typer.BadParameter("Need at least one pack to weld")

    weld_config_dir = Path(typer.get_app_dir("smithed")) / "weld"
    cache = weld_config_dir / "beet_cache"

    if clear_cache:
        shutil.rmtree(cache)

    print(
        Panel(
            "[bold][accent] Weld [/bold]by Smithed ",
            border_style="accent_light",
        ),
    )

    success = False

    logger.debug("Using cache: '%s'", path_str(cache))
    logger.info("Packs: %s", ", ".join(f"'{pack}'" for pack in packs))

    t0 = perf_counter()
    with (
        error_handler(should_exit=True),
        run_weld(packs, cache=ProjectCache(cache, cache)) as ctx,
    ):
        logger.info(
            "[success]Saving[/success], might take a while.",
            extra={"markup": True},
        )
        ctx.data.save(path=dir / name, zipped=name.suffix == ".zip", overwrite=True)
        success = True
    t1 = perf_counter()

    if success:
        print()
        print(
            Panel(
                f"[success][bold]✔️[/bold] Welded [bold]{len(packs)}[/bold] packs"
                f" in [bold]{t1-t0:.3f}s[/bold]"
                f"\n[success]Output: [bold]{path_str((dir / name).resolve())}[/bold]",
                border_style="accent_light",
            )
        )
    else:
        print()
        print(Panel("[error]:boom: Failed to weld packs", border_style="error"))
        raise typer.Abort()


def setup_logger(dev: bool, log_level: str):
    if dev:
        log_level = "DEBUG"

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=False, show_path=dev)],
    )


def expand_globs(packs: Sequence[str]):
    for pack in packs:
        yield from glob(pack)


if __name__ == "__main__":
    typer.run(weld)
