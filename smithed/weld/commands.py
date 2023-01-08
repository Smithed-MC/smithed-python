import json
import time
from argparse import ArgumentParser
from ensurepip import bootstrap
from glob import glob
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import click
import mecha
from beet import Context, Project, ProjectConfig, run_beet
from beet.core.utils import FileSystemPath
from beet.toolchain.cli import beet, message_fence
from beet.toolchain.commands import build

pass_project = click.make_pass_decorator(Project)  # type: ignore


@beet.command()
@pass_project
@click.pass_context
@click.argument("packs", nargs=-1)
@click.option("-l", "--link", metavar="WORLD", help="Link the project to a world")
def weld(
    ctx: click.Context,
    project: Project,
    packs: tuple[str],
    link: str | None,
):
    """Weld data and resource packs together with all data and assets in one zip.

    See https://wiki.smithed.dev/weld more info!
    """

    packs = tuple(expand_globs(packs))

    if len(packs) < 2:
        click.echo(click.style("Need at least one pack to weld", fg="red"))
        return -1

    with message_fence(f"Welding packs:\n - " + "\n - ".join(packs)):
        config = bootstrap_config(packs)

        if Path("beet.yaml").exists():
            config["extend"] = "beet.yaml"  # TODO: JANK

        with NamedTemporaryFile("w+", suffix=".json") as fp:
            json.dump(config, fp, indent=2)
            fp.read()  # still avoids bugs
            project.config_path = fp.name
            return ctx.invoke(build, link=link)


def expand_globs(packs: tuple[str]):
    for pack in packs:
        yield from glob(pack)


# weld_command = beet.command()(weld)
# weld_alias = click.command()(weld)
