import logging
from contextlib import contextmanager
from functools import partial
from typing import Iterable
from zipfile import ZipFile

from beet import (
    ProjectCache,
    ProjectConfig,
    run_beet,
)
from beet.core.utils import FileSystemPath, JsonDict


from .plugins import add_fabric_mod_json, weld, weld_handler, weld_loader, weld_metadata


DESCRIPTION = "Merged by Smithed Weld"

logger = logging.getLogger("weld")


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    cache: bool | ProjectCache = True,
    as_fabric_mod: bool = False,
):
    """Runs the beet toolchain alongside the weld machinery programmatically."""

    with run_beet(config, directory=directory, cache=cache) as ctx:
        ctx.require(weld_handler)
        ctx.require(weld_metadata)
        ctx.require(partial(weld_loader, packs=list(packs)))
        ctx.require(weld)

        if as_fabric_mod:
            ctx.require(add_fabric_mod_json)

        yield ctx
