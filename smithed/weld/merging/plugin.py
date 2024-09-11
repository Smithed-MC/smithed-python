from beet import Context, LootTable
from beet.contrib import model_merging

from .handler import ConflictsHandler


def beet_default(ctx: Context):
    ctx.require(model_merging.beet_default)
    handler = ctx.inject(ConflictsHandler)
    ctx.data.merge_policy.extend_namespace(LootTable, handler)


def process(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.process()
