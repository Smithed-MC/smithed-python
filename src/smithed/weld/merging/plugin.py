from beet import Context, JsonFileBase, TagFile
from beet.contrib import model_merging

from smithed.weld.toolchain.process import Pack

from .handler import ConflictsHandler

def apply_merging[T: Pack](handler: ConflictsHandler, pack: T):
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
