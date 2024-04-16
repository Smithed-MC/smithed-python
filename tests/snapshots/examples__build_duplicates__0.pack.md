# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "Smithed's Actionbar Pack",
    "pack_format": 26
  },
  "id": "tacos"
}
```

### minecraft

`@loot_table minecraft:blocks/yellow_shulker_box`

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
              "function": "minecraft:copy_name",
              "source": "block_entity"
            },
            {
              "function": "minecraft:copy_nbt",
              "ops": [
                {
                  "op": "replace",
                  "source": "Lock",
                  "target": "BlockEntityTag.Lock"
                },
                {
                  "op": "replace",
                  "source": "LootTable",
                  "target": "BlockEntityTag.LootTable"
                },
                {
                  "op": "replace",
                  "source": "LootTableSeed",
                  "target": "BlockEntityTag.LootTableSeed"
                }
              ],
              "source": "block_entity"
            },
            {
              "type": "minecraft:shulker_box",
              "entries": [
                {
                  "type": "minecraft:dynamic",
                  "name": "minecraft:contents"
                }
              ],
              "function": "minecraft:set_contents"
            }
          ],
          "name": "minecraft:yellow_shulker_box"
        }
      ],
      "rolls": 1.0,
      "conditions": [
        {
          "condition": "minecraft:inverted",
          "term": {
            "condition": "minecraft:match_tool",
            "predicate": {
              "predicates": {
                "minecraft:custom_data": {
                  "drop_contents": 1
                }
              }
            }
          }
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:dynamic",
          "name": "minecraft:contents"
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:match_tool",
          "predicate": {
            "predicates": {
              "minecraft:custom_data": {
                "drop_contents": 1
              }
            }
          }
        }
      ]
    }
  ],
  "random_sequence": "minecraft:blocks/yellow_shulker_box",
  "type": "minecraft:block",
  "__smithed__": [
    {
      "id": "tcc",
      "rules": [
        {
          "type": "append",
          "target": "pools[0].conditions",
          "priority": {},
          "source": {
            "value": {
              "condition": "minecraft:inverted",
              "term": {
                "condition": "minecraft:match_tool",
                "predicate": {
                  "predicates": {
                    "minecraft:custom_data": {
                      "drop_contents": 1
                    }
                  }
                }
              }
            }
          }
        },
        {
          "type": "append",
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:dynamic",
                  "name": "minecraft:contents"
                }
              ],
              "conditions": [
                {
                  "condition": "minecraft:match_tool",
                  "predicate": {
                    "predicates": {
                      "minecraft:custom_data": {
                        "drop_contents": 1
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      ]
    }
  ]
}
```
