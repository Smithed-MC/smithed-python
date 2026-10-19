# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
    "description": ""
  },
  "id": "pass"
}
```

### minecraft

`@loot_table minecraft:entities/wither`

```json
{
  "type": "minecraft:entity",
  "random_sequence": "minecraft:entities/wither",
  "pools": [
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:main"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:pass"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "fail1",
      "override": false,
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
            "type": "weld:value",
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
      "id": "fail2",
      "override": false,
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
            "type": "weld:value",
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
      ]
    },
    {
      "id": "main",
      "override": false,
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "priority": {},
          "source": {
            "type": "weld:value",
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
    },
    {
      "id": "pass",
      "override": false,
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
            "type": "weld:value",
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
    }
  ]
}
```
