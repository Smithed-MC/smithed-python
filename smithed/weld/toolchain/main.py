import logging
import sys
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Iterable, Literal, cast
from zipfile import Path as ZipPath
from zipfile import ZipFile

from beet import (
    Context,
    DeserializationError,
    Mcmeta,
    ProjectCache,
    ProjectConfig,
    run_beet,
    subproject,
)
from beet.core.utils import FileSystemPath, JsonDict

from smithed.weld import merging

from ..errors import InvalidMcmeta, WeldError
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
            "require": [
                "beet.contrib.auto_yaml",
                "beet.contrib.model_merging",
                "beet.contrib.unknown_files",
            ],
            pack_type: {"load": name},
            "pipeline": [
                # "smithed.weld.print_pack_name",
                "smithed.weld.inject_pack_stuff_into_smithed",
            ],
        }
    )


def inspect_zipfile(file: ZipFile) -> PackType:
    path = ZipPath(file)

    if (path / "data").is_dir():
        return PackType.DATA
    elif (path / "assets").is_dir():
        return PackType.ASSETS

    raise WeldError(f"Invalid. Pack '{path}' has neither assets nor data.")


def inspect(file: str | ZipFile | tuple[str | ZipFile]) -> PackType | Literal[False]:
    match file:
        case str(path) if path.endswith(".zip"):
            with ZipFile(path) as zip:
                return inspect_zipfile(zip)

        case str(path):
            if (path := Path(path)).is_dir():
                if (path / "data").is_dir():
                    return PackType.DATA
                elif (path / "assets").is_dir():
                    return PackType.ASSETS

                raise WeldError(
                    f"Invalid. Pack '{path}' has neither assets nor data. \n"
                )

        case ZipFile() as zip:
            return inspect_zipfile(zip)

        case (_, zip):
            return inspect_zipfile(zip)

    return False


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile] | Iterable[tuple[str, ZipFile]],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    cache: bool | ProjectCache = True,
    as_fabric_mod: bool = False,
):
    packs = cast(list[str] | list[ZipFile] | list[tuple[str, ZipFile]], list(packs))
    packs_with_types = zip(packs, (pack for pack in map(inspect, packs) if pack))

    with run_beet(config, directory=directory, cache=cache) as ctx:
        ctx.require(weld)
        load_packs(ctx, packs=list(packs_with_types))
        ctx.require(merging.process)
        if as_fabric_mod:
            ctx.require(partial(add_fabric_mod_json, packs=packs))
        yield ctx


def weld(ctx: Context):
    ctx.require(merging.beet_default)
    ctx.require("beet.contrib.model_merging")
    ctx.require("beet.contrib.unknown_files")


logger = logging.getLogger("weld")


def load_packs(
    ctx: Context, packs: Iterable[tuple[str | ZipFile | tuple[str, ZipFile], PackType]]
):
    for pack, pack_type in packs:
        try:
            match pack:
                case str(name):
                    logger.info(name)
                    ctx.require(subproject_config(pack_type, name))

                case (name, file):
                    with ZipFile("temp.zip", "w") as zip:
                        for info in file.infolist():
                            zip.writestr(info, file.read(info))
                    ctx.require(subproject_config(pack_type, "temp.zip"))
                    Path("temp.zip").unlink()

                case ZipFile() as file:
                    name = "temp"
                    with ZipFile("temp.zip", "w") as zip:
                        for info in file.infolist():
                            zip.writestr(info, file.read(info))
                    ctx.require(subproject_config(pack_type, "temp.zip"))
                    Path("temp.zip").unlink()
        except DeserializationError as err:
            if isinstance(err.file, Mcmeta):
                raise InvalidMcmeta(pack=name, contents=err.file.get_content()) from err  # type: ignore
            raise err
