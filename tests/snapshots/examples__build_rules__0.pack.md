# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": ""
  },
  "id": "rx:playerdb"
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
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "fake.vanilla:zombie"
        }
      ]
    },
    {
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "rx.playerdb:zombie"
        }
      ]
    },
    {
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "smithed.actionbar:zombie"
        }
      ]
    }
  ],
  "random_sequence": "minecraft:entities/zombie",
  "type": "minecraft:entity",
  "__smithed__": [
    {
      "id": "smithed.actionbar",
      "rules": [
        {
          "target": "pools",
          "priority": {
            "after": [
              "rx:playerdb"
            ]
          },
          "source": {
            "value": {
              "entries": [
                {
                  "type": "minecraft:loot_table",
                  "name": "smithed.actionbar:zombie"
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ]
    },
    {
      "id": "vanilla",
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "entries": [
                {
                  "type": "minecraft:loot_table",
                  "name": "fake.vanilla:zombie"
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ]
    },
    {
      "id": "rx:playerdb",
      "rules": [
        {
          "target": "pools",
          "priority": {
            "after": [
              "vanilla"
            ]
          },
          "source": {
            "value": {
              "entries": [
                {
                  "type": "minecraft:loot_table",
                  "name": "rx.playerdb:zombie"
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ],
      "priority": {}
    }
  ]
}
```
