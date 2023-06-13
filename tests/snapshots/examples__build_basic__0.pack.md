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

`@loot_table(strip_final_newline) minecraft:entities/zombie`

```json
{
  "type": "minecraft:entity",
  "pools": [
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:rotten_flesh",
          "functions": [
            {
              "function": "minecraft:set_count",
              "count": {
                "type": "minecraft:uniform",
                "min": 0,
                "max": 2
              },
              "add": false
            },
            {
              "function": "minecraft:looting_enchant",
              "count": {
                "type": "minecraft:uniform",
                "min": 0,
                "max": 1
              }
            }
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
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
          "name": "minecraft:potato",
          "functions": [
            {
              "function": "minecraft:furnace_smelt",
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
              ]
            }
          ]
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:killed_by_player"
        },
        {
          "condition": "minecraft:random_chance_with_looting",
          "chance": 0.025,
          "looting_multiplier": 0.01
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
    }
  ],
  "__smithed__": {
    "rules": [
      {
        "type": "smithed:append",
        "target": "pools",
        "source": {
          "type": "smithed:reference",
          "path": "pools[2]"
        }
      }
    ],
    "priority": {
      "after": [
        "vanilla"
      ]
    }
  }
}
```
