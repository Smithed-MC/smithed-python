# ruff: noqa: F821
from typing import cast
from beet import Function, ItemModel, LootTable, Model, Context

ctx: Context = cast(Context, ctx)  # type: ignore
commands = []

for table in sorted(ctx.data.loot_tables):
    namespace, path = table.split(":", 1)
    if path.startswith("items/"):
        item = path[6:]
        model = f"{namespace}:item/{item}"
        item_model = f"{namespace}:{item}"

        if model not in ctx.assets.models:
            ctx(
                model,
                Model(
                    {
                        "parent": "minecraft:item/generated",
                        "textures": {"layer0": "minecraft:item/paper"},
                    }
                ),
            )

        if item_model not in ctx.assets.item_models:
            ctx(
                item_model,
                ItemModel({"model": {"type": "minecraft:model", "model": model}}),
            )

        preview = f"catalog:preview/{namespace}/{item}"
        ctx(
            preview,
            LootTable(
                {
                    "type": "minecraft:generic",
                    "pools": [
                        {
                            "rolls": 1,
                            "entries": [
                                {
                                    "type": "minecraft:item",
                                    "name": "minecraft:paper",
                                    "functions": [
                                        {
                                            "function": "minecraft:set_components",
                                            "components": {
                                                "minecraft:item_model": item_model
                                            },
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ),
        )
        commands.append(f"loot give @s loot {preview}")

ctx("catalog:give_textured", Function(commands))
