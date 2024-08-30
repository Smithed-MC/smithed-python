# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "Smithed's Actionbar Pack",
    "pack_format": 48
  },
  "id": "tacos"
}
```

### minecraft

`@loot_table minecraft:blocks/yellow_shulker_box`

```json
{
  "type": "minecraft:block",
  "random_sequence": "minecraft:blocks/yellow_shulker_box",
  "pools": [
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "minecraft:item",
          "functions": [
            {
              "function": "minecraft:copy_components",
              "include": [
                "minecraft:custom_name",
                "minecraft:container",
                "minecraft:lock",
                "minecraft:container_loot"
              ],
              "source": "block_entity"
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
