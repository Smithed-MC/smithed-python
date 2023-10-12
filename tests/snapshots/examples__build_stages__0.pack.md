# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
    "description": ""
  },
  "id": "pack.early"
}
```

### minecraft

`@loot_table minecraft:entities/wither`

```json
{
  "random_sequence": "minecraft:entities/wither",
  "type": "minecraft:entity",
  "pools": [
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:early"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:pack1"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:pack2"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:late"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "pack.late",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {
            "stage": "late"
          },
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:late"
                }
              ]
            }
          }
        }
      ],
      "priority": {}
    },
    {
      "id": "pack1",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:pack1"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pack2",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {
            "after": [
              "pack1"
            ]
          },
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:pack2"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pack.early",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {
            "stage": "early"
          },
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:early"
                }
              ]
            }
          }
        }
      ],
      "priority": {}
    }
  ]
}
```
