import logging
from importlib import resources
from typing import TypeVar
from zipfile import ZipFile

from beet import (
    Context,
    DataPack,
    JsonFile,
    Mcmeta,
    PluginOptions,
    PngFile,
    ResourcePack,
    configurable,
)
from jinja2 import Template

from smithed.weld import merging, scripts
from .process import PackProcessor


DESCRIPTION = "Merged by Smithed Weld"

logger = logging.getLogger("weld")
MetaFileT = TypeVar("MetaFileT", bound=Mcmeta | PngFile)


FABRIC_MOD_TEMPLATE = Template(
    (resources.files("smithed") / "weld/resources/fabric.mod.json.j2").read_text()
)

DEFAULT_PACK_ICON = (
    resources.files("smithed") / "weld/resources/pack.png"
).read_bytes()


class WeldLoaderOptions(PluginOptions, arbitrary_types_allowed=True):
    """Options to configure how weld loads packs before merge time.

    packs - which packs (paths or ZipFile) to load
    """

    # TODO: change `str` to `PathLike`?
    packs: list[str] | list[ZipFile]


class WeldOptions(PluginOptions, arbitrary_types_allowed=True):
    """Options to configure how weld operates at merge time.

    scripts - determines whether weld scripts run after merging.
    """

    scripts: bool = True


def add_fabric_mod_json(ctx: Context, pack_names: list[str] | None = None):
    """Generates and adds a fabric mod json for producing value fabric jars.

    Note: Fabric jar is compromised of a renamed `.zip` -> `.jar` and a `fabric.mod.json`.
    """

    if pack_names is None:
        processor = ctx.inject(PackProcessor)
        pack_names = list(processor.packs.keys())

    content = FABRIC_MOD_TEMPLATE.render(
        pack_hash=hash("".join(pack_names)),
        pack_names=pack_names,
        mc_version=ctx.minecraft_version,
    )

    ctx.data.extra["fabric.mod.json"] = JsonFile(content)


@configurable(validator=WeldLoaderOptions)
def weld_loader(ctx: Context, opts: WeldLoaderOptions):
    """Loads packs into weld via the `PackProcessor` class."""

    processor = ctx.inject(PackProcessor)
    processor.load_packs(opts.packs)


def weld_handler(ctx: Context):
    """Loads the merging pre-processing pipeline."""

    ctx.require(merging.beet_default)


def weld_metadata(ctx: Context):
    """Attaches custom metadata to welded packs.

    TODO: make configurable
    """

    processor = ctx.inject(PackProcessor)

    if ctx.data:
        ctx.data.icon = PngFile(DEFAULT_PACK_ICON)
        ctx.data.mcmeta.data["pack"]["description"] = "A welded pack"
        ctx.data.mcmeta.data.setdefault("__smithed__", {})
        ctx.data.mcmeta.data["__smithed__"]["packs"] = [
            name for name, pack in processor.packs.items() if type(pack) is DataPack
        ]

    if ctx.assets:
        ctx.assets.icon = PngFile(DEFAULT_PACK_ICON)
        ctx.assets.mcmeta.data["pack"]["description"] = "A welded pack"
        ctx.assets.mcmeta.data.setdefault("__smithed__", {})
        ctx.assets.mcmeta.data["__smithed__"]["packs"] = [
            name for name, pack in processor.packs.items() if type(pack) is ResourcePack
        ]


@configurable(validator=WeldOptions)
def weld(ctx: Context, opt: WeldOptions):
    """Beet plugin that runs the main weld processes (merging + scripting)"""

    ctx.require(merging.process)

    if opt.scripts:
        ctx.require(scripts.beet_default)
