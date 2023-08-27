from beet import Context, LootTable

from .handler import ConflictsHandler

def beet_default(ctx: Context):
    handler = ctx.inject(ConflictsHandler)
    ctx.data.merge_policy.extend_namespace(LootTable, handler)

    yield

    handler.process()
