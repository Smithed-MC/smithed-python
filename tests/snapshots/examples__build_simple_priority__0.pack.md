# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  },
  "id": "pack3"
}
```

### minecraft

`@loot_table minecraft:entities/zombie`

```json
{
  "pools": [
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "minecraft:item",
          "functions": [
            {
              "add": false,
              "count": {
                "type": "minecraft:uniform",
                "max": 2.0,
                "min": 0.0
              },
              "function": "minecraft:set_count"
            },
            {
              "count": {
                "type": "minecraft:uniform",
                "max": 1.0,
                "min": 0.0
              },
              "function": "minecraft:looting_enchant"
            }
          ],
          "name": "minecraft:rotten_flesh"
        }
      ],
      "rolls": 1.0
    },
    {
      "bonus_rolls": 0.0,
      "conditions": [
        {
          "condition": "minecraft:killed_by_player"
        },
        {
          "chance": 0.025,
          "condition": "minecraft:random_chance_with_looting",
          "looting_multiplier": 0.01
        }
      ],
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:iron_ingot"
        },
        {
          "type": "minecraft:item",
          "name": "minecraft:carrot"
        },
        {
          "type": "minecraft:item",
          "functions": [
            {
              "conditions": [
                {
                  "condition": "minecraft:entity_properties",
                  "entity": "this",
                  "predicate": {
                    "flags": {
                      "is_on_fire": true
                    }
                  }
                }
              ],
              "function": "minecraft:furnace_smelt"
            }
          ],
          "name": "minecraft:potato"
        }
      ],
      "rolls": 1.0
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:diamond"
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:cobblestone"
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:stone"
        }
      ]
    }
  ],
  "type": "minecraft:entity",
  "random_sequence": "minecraft:entities/zombie",
  "__smithed__": [
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
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:diamond"
                }
              ]
            }
          }
        }
      ],
      "priority": {}
    },
    {
      "id": "pack2",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {
            "after": [
              "pack1",
              "pack3"
            ]
          },
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:stone"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pack3",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {
            "after": [
              "pack1",
              "non-existing-pack"
            ]
          },
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:cobblestone"
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
