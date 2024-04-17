# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
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
      "rules": [
        {
          "type": "replace",
          "target": "foo[0].bar.taco",
          "priority": {},
          "source": {
            "type": "value",
            "value": "not bell"
          }
        },
        {
          "type": "replace",
          "target": "foo[1].minecraft:bar.taco",
          "priority": {},
          "source": {
            "type": "value",
            "value": "not bell"
          }
        },
        {
          "type": "replace",
          "target": "foo[2].\"minecraft:bar\".taco",
          "priority": {},
          "source": {
            "type": "value",
            "value": "not bell"
          }
        }
      ]
    }
  ]
}
```
