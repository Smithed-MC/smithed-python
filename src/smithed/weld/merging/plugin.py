from typing import TypeVar
from beet import Context, DataPack, JsonFileBase, ResourcePack, TagFile
from beet.contrib import model_merging

from .handler import ConflictsHandler

T = TypeVar("T", DataPack, ResourcePack)


def apply_merging(handler: ConflictsHandler, pack: T):
    for (_, extension), file_type in pack.resolve_scope_map().items():
        if (
            extension == ".json"
            and issubclass(file_type, JsonFileBase)
            and not issubclass(file_type, TagFile)
        ):
            pack.merge_policy.extend_namespace(file_type, handler)


def beet_default(ctx: Context):
    ctx.require(model_merging.beet_default)
    handler = ctx.inject(ConflictsHandler)

    for pack in ctx.packs:
        apply_merging(handler, pack)  # type: ignore


def process(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.process()
