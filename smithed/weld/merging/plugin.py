from beet import Context, LootTable, Texture

from .handler import ConflictsHandler, FancyPantsConflictsHandler


def beet_default(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    ctx.data.merge_policy.extend_namespace(LootTable, handler)
    ctx.assets.merge_policy.extend_namespace(Texture, FancyPantsConflictsHandler())


def process(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    handler.process()
