# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": ""
  },
  "id": "tcc"
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
          "name": "minecraft:tacos"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:netherite_upgrade_smithing_template"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "tacos",
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:tacos"
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ]
    },
    {
      "id": "tcc",
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:netherite_upgrade_smithing_template"
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ]
    }
  ]
}
```
