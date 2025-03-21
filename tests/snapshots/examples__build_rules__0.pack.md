# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
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
  "type": "minecraft:entity",
  "__smithed__": [
    {
      "id": "pack.append",
      "override": false,
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
      "override": false,
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
      "override": false,
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
      ]
    },
    {
      "id": "pack.prepend",
      "override": false,
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
      "override": false,
      "rules": [
        {
          "type": "weld:remove",
          "target": "pools[0].entries[0].functions[0]",
          "priority": {}
        }
      ]
    },
    {
      "id": "pack.replace",
      "override": false,
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
