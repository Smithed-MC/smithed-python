from json import JSONDecodeError
import logging
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Iterable
from zipfile import Path as ZipPath
from zipfile import ZipFile

from beet import (
    Context,
    DataPack,
    DeserializationError,
    Generator,
    ItemModifier,
    JsonFileBase,
    Mcmeta,
    PackQuery,
    ProjectCache,
    ProjectConfig,
    ResourcePack,
    run_beet,
)
from beet.core.utils import FileSystemPath, JsonDict
from beet.contrib.unknown_files import UnknownAsset, UnknownData
from beet.contrib.model_merging import model_merging
from beet.contrib.auto_yaml import use_auto_yaml

from .plugins import weld, weld_handler, add_fabric_mod_json

from ..errors import InvalidMcmeta, WeldError

DESCRIPTION = "Merged by Smithed Weld"

logger = logging.getLogger("weld")


def get_pack_type(path: ZipPath | Path) -> DataPack | ResourcePack:
    if (path / "data").is_dir():
        pack = DataPack()
        pack.extend_namespace += [UnknownData]

    elif (path / "assets").is_dir():
        pack = ResourcePack()
        pack.extend_namespace += [UnknownAsset]
        model_merging(pack)

    else:
        raise WeldError(f"Invalid. Pack '{path}' has neither assets nor data.")

    use_auto_yaml(pack)

    return pack


def create_pack(
    file: str | ZipFile, gen: Generator
) -> tuple[DataPack | ResourcePack, str]:
    """Creates a DataPack or ResourcePack given a file (either ZipFile or str).

    1. Determine type of file and it's name to figure out how to load it.
    2. Peek inside to figure out if it's a data or resource pack.
    3. Create an empty pack and load some default plugin behavior:
       - `beet.contrib.unknown_files`
       - `beet.contrib.model_merging`
       - `beet.contrib.use_auto_yaml`
    4. Load the actual file into the empty pack object.
    5. Inject smithed specific information to some resource files within.
    6. Return the pack and it's name as a tuple.

    This process of loading the pack data in it's own object is isolated:
    - We need to load the pack data isolated so if there's an error within, we can
       surface it properly so it can be handled by the outer app. This allows us to
       skip the pack or just highlight the broken pack in a weld process.
    - File names, `pack.mcmeta`s, and the specific file tree gets lots when merged into
       a larger pack. While resource files themselves get conflict handled via our
       merger, the pack "metainfo" is useful enough for us to tabulate within itself.
    - Specific errors from invalid mcmeta and json files is useful to surface before the
       actual merging process.
    """

    match file:
        case ZipFile() as f:
            name = f.filename or "<unknown>"
            name = f"{name}.zip"
            pack = get_pack_type(ZipPath(f))

        case str() as p:
            name = p
            pack = get_pack_type(Path(p))

    try:
        logger.info(f"Loading pack: {name}")
        pack.load(file)

    except DeserializationError as err:
        if isinstance(err.file, Mcmeta):
            raise InvalidMcmeta(pack=name, contents=err.file.get_content()) from err  # type: ignore
        raise err

    inject_smithed_into_pack_resources(gen, pack)

    return pack, name


def load_pack(ctx: Context, pack: DataPack | ResourcePack):
    """Loads a DataPack or ResourcePack into a context by merging it."""

    match pack:
        case DataPack() as dp:
            ctx.data.merge(dp)
        case ResourcePack() as rp:
            ctx.assets.merge(rp)


def inject_smithed_into_pack_resources(gen: Generator, pack: DataPack | ResourcePack):
    """Inject some metadata into resource files to be used in later welding."""

    id = pack.mcmeta.data.get("id", gen.format("missing_{incr}"))
    override = pack.mcmeta.data.get("__smithed__", {}).get("override", False)

    for resource in PackQuery([pack]).distinct(match="*", extend=JsonFileBase):  # type: ignore
        try:
            resource_data: dict[str, Any] | list[Any] = resource.data
        except JSONDecodeError as e:
            logging.exception(
                f"Resource {resource.snake_name} has invalid json at {e.lineno}:{e.colno} (line:col).\n"
                f"{e}"
            )
            logging.warning("Skipping..")
            continue

        # `ItemModifier` is the only resource that *can* be a list.
        # TODO: what to do with custom resources that are lists..
        if isinstance(resource_data, list):
            if isinstance(resource, ItemModifier):
                resource_data = {"function": "sequence", "functions": resource_data}
            else:
                continue

        # TODO: Maybe rethink how this works. This injects the id and override state rather than
        #  inheriting it from the pack (when conflicts get handled). This can be redone when there's
        #  a global pack cache that tracks the pack, pack.png, mcmeta, and namespaces / paths to be
        #  available as apart of weld plugins.
        if override:
            resource_data.setdefault("__smithed__", {})

        smithed = resource_data.get("__smithed__", False)
        if smithed is not False:
            if isinstance(smithed, list):
                for item in smithed:  # type: ignore
                    item["id"] = id
                    if override:
                        smithed["override"] = override  # type: ignore
            elif isinstance(smithed, dict):
                smithed["id"] = id
                if override:
                    smithed["override"] = override


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    cache: bool | ProjectCache = True,
    as_fabric_mod: bool = False,
):
    """Runs the beet toolchain alongside the weld machinery programmatically.

    TODO: deprecate this for a proper python interface.
    """

    with run_beet(config, directory=directory, cache=cache) as ctx:
        loaded_packs = list(create_pack(pack, ctx.generate) for pack in packs)
        ctx.require(weld_handler)

        for pack, _ in loaded_packs:
            load_pack(ctx, pack)

        ctx.require(weld)
        if as_fabric_mod:
            ctx.require(
                partial(
                    add_fabric_mod_json, pack_names=[name for _, name in loaded_packs]
                )
            )
        yield ctx
