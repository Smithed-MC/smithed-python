import sys
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Iterable, cast
from zipfile import Path as ZPath
from zipfile import ZipFile

from beet import Context, ProjectCache, ProjectConfig, run_beet, subproject
from beet.core.utils import FileSystemPath, JsonDict

from ..errors import WeldError
from .helper_plugins import add_fabric_mod_json

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

DESCRIPTION = "Merged by Smithed Weld"


class PackType(StrEnum):
    DATA = "data_pack"
    ASSETS = "resource_pack"


def subproject_config(pack_type: PackType, name: str = ""):
    return subproject(
        {
            "require": ["beet.contrib.auto_yaml"],
            pack_type: {"load": name},
            "pipeline": ["weld.print_pack_name", "weld.inject_pack_id_into_smithed"],
        }
    )


def inspect_zipfile(file: ZipFile) -> PackType:
    path = ZPath(file)

    if (path / "data").is_dir():
        return PackType.DATA
    elif (path / "assets").is_dir():
        return PackType.ASSETS

    raise WeldError("Invalid. Pack has neither assets nor data.")


def inspect(file: str | ZipFile) -> PackType:
    match file:
        case str(path) if path.endswith(".zip"):
            with ZipFile(path) as zip:
                return inspect_zipfile(zip)

        case str(path):
            if (Path(path) / "data").is_dir():
                return PackType.DATA
            elif (Path(path) / "assets").is_dir():
                return PackType.ASSETS

            raise WeldError(f"Invalid. Pack {path} has neither assets nor data. \n")

        case ZipFile() as zip:
            return inspect_zipfile(zip)

    assert False


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    cache: bool | ProjectCache = True,
    as_fabric_mod: bool = False,
):
    packs = cast(list[str] | list[ZipFile], list(packs))
    packs_with_types = zip(packs, map(inspect, packs))

    with run_beet(config, directory=directory, cache=cache) as ctx:
        ctx.require(weld)
        ctx.require(partial(load_packs, packs=list(packs_with_types)))
        ctx.require("weld.merging.process")
        if as_fabric_mod:
            ctx.require(partial(add_fabric_mod_json, packs=packs))
        yield ctx


def weld(ctx: Context):
    ctx.require("weld.merging")
    ctx.require("beet.contrib.model_merging")
    ctx.require("beet.contrib.unknown_files")

    # yield

    # ctx.require("weld.merging.process")


def load_packs(ctx: Context, packs: Iterable[tuple[str | ZipFile, PackType]]):
    for pack, pack_type in packs:
        match pack:
            case str(name):
                ctx.require(subproject_config(pack_type, name))
            case ZipFile() as file:
                match pack_type:
                    case PackType.DATA:
                        ctx.data.load(file)
                    case PackType.ASSETS:
                        ctx.assets.load(file)
