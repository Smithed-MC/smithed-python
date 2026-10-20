# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "",
    "min_format": [
      101,
      0
    ],
    "max_format": [
      101,
      0
    ]
  },
  "id": "sandbox",
  "overlays": {
    "entries": [
      {
        "directory": "weld_generated",
        "min_format": [
          101,
          0
        ],
        "max_format": [
          101,
          0
        ]
      }
    ]
  }
}
```

### sandbox

`@function sandbox:input`

```mcfunction
say Original input
```

`@function sandbox:untouched`

```mcfunction
say Untouched input
```

`@loot_table sandbox:input`

```json
{
  "pools": []
}
```

`@weld_script sandbox:main`

```

for name, source in ctx.data.functions.items():
    lines = list(source.lines)
    text = source.text
table = ctx.data.loot_tables["sandbox:input"].data

function sandbox:input:
    say Regenerated after reading

loot_table sandbox:input {"type": "minecraft:generic", "pools": []}
```

## Overlay `weld_generated`

`@overlay weld_generated`

### sandbox

`@loot_table sandbox:input`

```json
{
  "type": "minecraft:generic",
  "pools": []
}
```

`@function sandbox:input`

```mcfunction
say Regenerated after reading
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
