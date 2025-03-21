from typing import Any, Iterable, cast
from logging import Logger

from beet import Context, DataPack, ResourcePack, TextFileBase
from beet.core.utils import FormatsRangeDict, normalize_string
from bolt.contrib.sandbox import Sandbox
from mecha import CompilationUnit, Mecha
import mecha

from .resources import ResourceDefinition, WeldScript, load_resources

logger = Logger(__name__)


def provide_compilation_units(
    pack: ResourcePack | DataPack,
    match: list[str] | None = None,
) -> Iterable[tuple[TextFileBase[Any], CompilationUnit]]:
    for resource_location in pack[WeldScript].match(*match or ["*"]):
        file_instance = pack[WeldScript][resource_location]
        namespace, *_ = resource_location.split(":")
        overlay_name = f"weld_generated_{normalize_string(namespace)}"

        yield cast(TextFileBase[Any], file_instance), CompilationUnit(
            resource_location=resource_location,
            pack=pack.overlays[overlay_name],
        )
        pack.overlays[overlay_name].supported_formats = FormatsRangeDict(
            min_inclusive=pack.pack_format,
            max_inclusive=pack.pack_format,
        )


def define_compilation_unit_providers(ctx: Context):
    """Replace all default providers with only weld script providers"""
    mc = ctx.inject(Mecha)
    mc.providers = [provide_compilation_units]


def beet_default(ctx: Context):
    sandbox = ctx.inject(Sandbox)
    sandbox.allowed_imports |= {"beet", "smithed"}

    ctx.require(define_compilation_unit_providers)
    ctx.require(load_resources)

    # This mecha will *not* process every file bc we replaced all the providers
    ctx.require(mecha.beet_default)


def clear_plugins(ctx: Context):
    for pack in [
        ctx.data,
        *ctx.data.overlays.values(),
        ctx.assets,
        *ctx.assets.overlays.values(),
    ]:
        for resource in [WeldScript, ResourceDefinition]:
            pack[resource].clear()
