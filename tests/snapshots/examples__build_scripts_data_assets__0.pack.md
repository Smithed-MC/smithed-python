# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "",
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ]
  },
  "id": "weapons",
  "overlays": {
    "entries": [
      {
        "directory": "weld_generated",
        "min_format": [
          121,
          0
        ],
        "max_format": [
          121,
          0
        ]
      }
    ]
  }
}
```

### weapons

`@loot_table weapons:items/ruby_sword`

```json
{
  "type": "minecraft:generic",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:diamond_sword",
          "functions": [
            {
              "function": "minecraft:set_components",
              "components": {
                "minecraft:item_model": "weapons:ruby_sword"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

`@loot_table weapons:items/untextured`

```json
{
  "type": "minecraft:generic",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:iron_sword"
        }
      ]
    }
  ]
}
```

## Overlay `weld_generated`

`@overlay weld_generated`

### catalog

`@loot_table catalog:preview/weapons/ruby_sword`

```json
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
                "minecraft:item_model": "weapons:ruby_sword"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

`@loot_table catalog:preview/weapons/untextured`

```json
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
                "minecraft:item_model": "weapons:untextured"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

`@function catalog:give_textured`

```mcfunction
loot give @s loot catalog:preview/weapons/ruby_sword
loot give @s loot catalog:preview/weapons/untextured
```

`@endoverlay`

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "",
    "min_format": [
      97,
      1
    ],
    "max_format": [
      97,
      1
    ]
  },
  "id": "weapons_art",
  "overlays": {
    "entries": [
      {
        "directory": "weld_generated",
        "min_format": [
          97,
          1
        ],
        "max_format": [
          97,
          1
        ]
      }
    ]
  }
}
```

### catalog

`@resource_pack assets/catalog/weld/script/main.bolt`

```
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
```

### other

`@model other:item/untextured`

```json
{
  "parent": "minecraft:item/handheld",
  "textures": {
    "layer0": "minecraft:item/iron_sword"
  }
}
```

### weapons

`@item_model weapons:ruby_sword`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "weapons:item/ruby_sword"
  }
}
```

`@model weapons:item/ruby_sword`

```json
{
  "parent": "minecraft:item/handheld",
  "textures": {
    "layer0": "minecraft:item/diamond_sword"
  }
}
```

`@model weapons:item/unused`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/stick"
  }
}
```

## Overlay `weld_generated`

`@overlay weld_generated`

### weapons

`@item_model weapons:untextured`

```json
{
  "model": {
    "type": "minecraft:model",
    "model": "weapons:item/untextured"
  }
}
```

`@model weapons:item/untextured`

```json
{
  "parent": "minecraft:item/generated",
  "textures": {
    "layer0": "minecraft:item/paper"
  }
}
```

`@endoverlay`
