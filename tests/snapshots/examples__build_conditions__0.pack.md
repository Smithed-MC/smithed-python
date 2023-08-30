# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": ""
  },
  "id": "main"
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
          "name": "minecraft:pass"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:main"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "fail1",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "conditions": [
            {
              "type": "weld:pack_check",
              "id": "non-existing-pack"
            }
          ],
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:fail1"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "pass",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "conditions": [
            {
              "type": "weld:pack_check",
              "id": "main"
            }
          ],
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:pass"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "fail2",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "conditions": [
            {
              "type": "weld:inverted",
              "conditions": [
                {
                  "type": "weld:pack_check",
                  "id": "main"
                }
              ]
            }
          ],
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:fail2"
                }
              ]
            }
          }
        }
      ],
      "priority": {}
    },
    {
      "id": "main",
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:main"
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
