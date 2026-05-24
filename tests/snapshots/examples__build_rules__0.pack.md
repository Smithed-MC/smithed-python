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
  "id": "pack.replace"
}
```

### minecraft

`@loot_table minecraft:entities/enderman`

```json
{
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
              "enchantment": "minecraft:looting",
              "function": "minecraft:enchanted_count_increase"
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
  "random_sequence": "minecraft:entities/enderman",
  "__smithed__": [
    {
      "id": "pack.append",
      "override": false,
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:append"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    },
    {
      "id": "pack.insert",
      "override": false,
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "type": "weld:value",
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
          "type": "weld:insert",
          "index": 1
        }
      ]
    },
    {
      "id": "pack.merge",
      "override": false,
      "rules": [
        {
          "target": "pools[0]",
          "priority": {},
          "source": {
            "type": "weld:value",
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
          },
          "type": "weld:merge"
        }
      ]
    },
    {
      "id": "pack.prepend",
      "override": false,
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:prepend"
                }
              ]
            }
          },
          "type": "weld:prepend"
        }
      ]
    },
    {
      "id": "pack.remove",
      "override": false,
      "rules": [
        {
          "target": "pools[0].entries[0].functions[0]",
          "priority": {},
          "type": "weld:remove"
        }
      ]
    },
    {
      "id": "pack.replace",
      "override": false,
      "rules": [
        {
          "target": "pools[0].entries[0].type",
          "priority": {},
          "source": {
            "type": "weld:value",
            "value": "weld:replace"
          },
          "type": "weld:replace"
        }
      ]
    }
  ]
}
```
