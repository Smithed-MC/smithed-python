# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
    "description": ""
  },
  "id": "pack.replace"
}
```

### minecraft

`@loot_table minecraft:entities/enderman`

```json
{
  "random_sequence": "minecraft:entities/enderman",
  "type": "minecraft:entity",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:prepend"
        }
      ]
    },
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "weld:replace",
          "functions": [
            {
              "count": {
                "type": "minecraft:uniform",
                "max": 1.0,
                "min": 0.0
              },
              "function": "minecraft:looting_enchant"
            }
          ],
          "name": "minecraft:ender_pearl"
        },
        {
          "type": "minecraft:item",
          "name": "minecraft:merge_dict",
          "functions": [
            {
              "function": "merge_list",
              "count": {
                "min": 0.0,
                "max": 1.0
              }
            }
          ]
        }
      ],
      "rolls": 1
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:insert"
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:append"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "pack.append",
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
                  "name": "minecraft:append"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pack.insert",
      "rules": [
        {
          "type": "weld:insert",
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:insert"
                }
              ]
            }
          },
          "index": 1
        }
      ]
    },
    {
      "id": "pack.merge",
      "rules": [
        {
          "type": "weld:merge",
          "target": "pools[0]",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:merge_dict",
                  "functions": [
                    {
                      "function": "merge_list",
                      "count": {
                        "min": 0.0,
                        "max": 1.0
                      }
                    }
                  ]
                }
              ]
            }
          }
        }
      ],
      "priority": {}
    },
    {
      "id": "pack.prepend",
      "rules": [
        {
          "type": "prepend",
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:prepend"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pack.remove",
      "rules": [
        {
          "type": "weld:remove",
          "target": "pools[0].entries[0].functions[0]",
          "priority": {}
        }
      ],
      "priority": {}
    },
    {
      "id": "pack.replace",
      "rules": [
        {
          "type": "weld:replace",
          "target": "pools[0].entries[0].type",
          "priority": {},
          "source": {
            "value": "weld:replace"
          }
        }
      ]
    }
  ]
}
```
