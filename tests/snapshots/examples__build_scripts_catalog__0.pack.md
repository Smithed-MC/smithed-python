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
  "id": "bakery",
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

### catalog

`@weld_script catalog:main`

```
from beet import FunctionTag

give_functions = []

for table in sorted(ctx.data.loot_tables):
    namespace, path = table.split(":", 1)
    if path.startswith("items/"):
        entry = f"catalog:give/{namespace}/{path[6:]}"
        give_functions.append(entry)

        function entry:
            loot give @s loot table

function catalog:give_all:
    for entry in give_functions:
        function entry

ctx.data.function_tags["catalog:items"] = FunctionTag({
    "values": give_functions
})
```

### orchard

`@loot_table orchard:items/fruit/apple`

```json
{
  "type": "minecraft:generic",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:apple"
        }
      ]
    }
  ]
}
```

### bakery

`@loot_table bakery:entities/baker`

```json
{
  "type": "minecraft:entity",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:emerald"
        }
      ]
    }
  ]
}
```

`@loot_table bakery:items/pie`

```json
{
  "type": "minecraft:generic",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:pumpkin_pie"
        }
      ]
    }
  ]
}
```

## Overlay `weld_generated`

`@overlay weld_generated`

### catalog

`@function catalog:give/bakery/pie`

```mcfunction
loot give @s loot bakery:items/pie
```

`@function catalog:give/orchard/fruit/apple`

```mcfunction
loot give @s loot orchard:items/fruit/apple
```

`@function catalog:give_all`

```mcfunction
function catalog:give/bakery/pie
function catalog:give/orchard/fruit/apple
```

`@function_tag catalog:items`

```json
{
  "values": [
    "catalog:give/bakery/pie",
    "catalog:give/orchard/fruit/apple"
  ]
}
```

`@endoverlay`

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      75,
      0
    ],
    "max_format": [
      75,
      0
    ],
    "description": ""
  }
}
```
