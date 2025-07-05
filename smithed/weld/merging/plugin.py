from itertools import chain
from typing import cast
from beet import Context, JsonFileBase, Pack, TagFile
from beet.contrib import model_merging

from .handler import ConflictsHandler


def beet_default(ctx: Context):
    ctx.require(model_merging.beet_default)
    handler = ctx.inject(ConflictsHandler)

    packs = (cast(Pack, pack) for pack in chain(ctx.packs))
    for pack in packs:
        for (_, extension), file_type in pack.resolve_scope_map().items():
            if (
                extension == ".json"
                and issubclass(file_type, JsonFileBase)
                and not issubclass(file_type, TagFile)
            ):
                pack.merge_policy.extend_namespace(file_type, handler)


def process(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.process()
