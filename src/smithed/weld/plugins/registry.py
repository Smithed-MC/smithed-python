from typing import Any, Iterable

from beet import Context, DataPack, ResourcePack, TextFileBase
from beet.core.utils import FormatsRangeDict, normalize_string
from bolt.contrib.sandbox import Sandbox
from mecha import CompilationUnit, Mecha

from .resources import WeldPlugin, load_resources


def provide_compilation_units(
    pack: ResourcePack | DataPack,
    match: list[str] | None = None,
) -> Iterable[tuple[TextFileBase[Any], CompilationUnit]]:
    for resource_location in pack[WeldPlugin].match(*match or ["*"]):
        file_instance = pack[WeldPlugin][resource_location]

        overlay_name = f"generated_{normalize_string(resource_location)}"

        yield file_instance, CompilationUnit(
            resource_location=resource_location,
            pack=pack.overlays[overlay_name],
        )
        pack.overlays[overlay_name].supported_formats = FormatsRangeDict(
            min_inclusive=pack.pack_format,
            max_inclusive=pack.pack_format,
        )


def define_compilation_unit_providers(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.providers = [provide_compilation_units]


def beet_default(ctx: Context):
    sandbox = ctx.inject(Sandbox)
    sandbox.allowed_imports |= {"beet", "smithed"}

    ctx.require(define_compilation_unit_providers)
    ctx.require(load_resources)

    yield

    ctx.data[WeldPlugin].clear()
