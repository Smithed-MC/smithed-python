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

from smithed.weld import merging
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


class WeldOptions(PluginOptions, arbitrary_types_allowed=True):
    packs: list[str] | list[ZipFile]


def add_fabric_mod_json(ctx: Context, pack_names: list[str] | None = None):
    if pack_names is None:
        processor = ctx.inject(PackProcessor)
        pack_names = list(set(pack.name for pack in processor.packs))

    content = FABRIC_MOD_TEMPLATE.render(
        pack_hash=hash("".join(pack_names)),
        pack_names=pack_names,
        mc_version=ctx.minecraft_version,
    )

    ctx.data.extra["fabric.mod.json"] = JsonFile(content)


@configurable(validator=WeldOptions)
def weld_loader(ctx: Context, opts: WeldOptions):
    processor = ctx.inject(PackProcessor)
    processor.load_packs(opts.packs)


def weld_handler(ctx: Context):
    ctx.require(merging.beet_default)


def weld_metadata(ctx: Context):
    processor = ctx.inject(PackProcessor)

    if ctx.data:
        ctx.data.icon = PngFile(DEFAULT_PACK_ICON)
        ctx.data.mcmeta.data["pack"]["description"] = "A welded pack"
        ctx.data.mcmeta.data.setdefault("__smithed__", {})
        ctx.data.mcmeta.data["__smithed__"]["packs"] = [
            name for pack, name in processor.packs if type(pack) is DataPack
        ]

    if ctx.assets:
        ctx.assets.icon = PngFile(DEFAULT_PACK_ICON)
        ctx.assets.mcmeta.data["pack"]["description"] = "A welded pack"
        ctx.assets.mcmeta.data.setdefault("__smithed__", {})
        ctx.assets.mcmeta.data["__smithed__"]["packs"] = [
            name for pack, name in processor.packs if type(pack) is ResourcePack
        ]


def weld(ctx: Context):
    ctx.require(merging.process)
