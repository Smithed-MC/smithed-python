from beet import Context, LootTable

from .handler import ConflictsHandler


def beet_default(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    ctx.data.merge_policy.extend_namespace(LootTable, handler)


def process(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.process()
