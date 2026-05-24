# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
    ],
    "description": ""
  },
  "id": "pack2"
}
```

### other

`@loot_table other:table`

```json
{
  "foo": [
    {
      "minecraft:bar": {
        "taco": "not bell"
      }
    },
    {
      "minecraft:bar": {
        "taco": "not bell"
      }
    },
    {
      "bar": {
        "taco": "not bell"
      }
    }
  ],
  "__smithed__": [
    {
      "id": "pack2",
      "override": false,
      "rules": [
        {
          "target": "foo[0].bar.taco",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": "not bell"
          },
          "type": "weld:replace"
        },
        {
          "target": "foo[1].minecraft:bar.taco",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": "not bell"
          },
          "type": "weld:replace"
        },
        {
          "target": "foo[2].\"minecraft:bar\".taco",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": "not bell"
          },
          "type": "weld:replace"
        }
      ]
    }
  ]
}
```
