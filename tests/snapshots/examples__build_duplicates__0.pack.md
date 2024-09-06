# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "Smithed's Actionbar Pack",
    "pack_format": 48
  },
  "description": "A welded pack",
  "id": "tacos"
}
```

`@data_pack pack.png`

![data_pack.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACABAMAAAAxEHz4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJUExURTc5TGOm/0dl/z9F6ZkAAAAJcEhZcwAADsIAAA7CARUoSoAAAAD9SURBVGje7ddhDoMwCIZhrsAVuP8ht8Xo2gq1tECzjPev+R5njItClmXZL4Sf9gH4bQeAbbEA8kUB2CsAwMe8gSEDnYGNPwKHDem8y0BzSH31JsCTUR4kL0A2qvU7R4Az2rU7gOL9oit3gDOoLAKoDWoKAk6D7pkDvT8RohAA9gMyMbpfByRDsV8HWEM1NwDuhnJtATSGfm0BlMbU2gK4jNm1BXAYC+tZgNbOaQOsGUZAbahEO+Bcaa/JFCC6nqYEQoHa2AQURiyAzKv9AQye1QLgDBjOCMDeB0cUgOIHRyCA/AeHMyAY5dPtD0C+JzLG1BryPdEQyLLsPwJ4Abkeykf9h286AAAADmVYSWZNTQAqAAAACAAAAAAAAADSU5MAAAAASUVORK5CYII=)

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

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 34,
    "description": ""
  },
  "description": "A welded pack"
}
```

`@resource_pack pack.png`

![resource_pack.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACABAMAAAAxEHz4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJUExURTc5TGOm/0dl/z9F6ZkAAAAJcEhZcwAADsIAAA7CARUoSoAAAAD9SURBVGje7ddhDoMwCIZhrsAVuP8ht8Xo2gq1tECzjPev+R5njItClmXZL4Sf9gH4bQeAbbEA8kUB2CsAwMe8gSEDnYGNPwKHDem8y0BzSH31JsCTUR4kL0A2qvU7R4Az2rU7gOL9oit3gDOoLAKoDWoKAk6D7pkDvT8RohAA9gMyMbpfByRDsV8HWEM1NwDuhnJtATSGfm0BlMbU2gK4jNm1BXAYC+tZgNbOaQOsGUZAbahEO+Bcaa/JFCC6nqYEQoHa2AQURiyAzKv9AQye1QLgDBjOCMDeB0cUgOIHRyCA/AeHMyAY5dPtD0C+JzLG1BryPdEQyLLsPwJ4Abkeykf9h286AAAADmVYSWZNTQAqAAAACAAAAAAAAADSU5MAAAAASUVORK5CYII=)
