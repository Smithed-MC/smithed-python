# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
    "description": ""
  },
  "id": "second",
  "overlays": {
    "entries": [
      {
        "formats": [
          61
        ],
        "directory": "overlay"
      }
    ]
  }
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
          "name": "minecraft:first"
        }
      ]
    },
    {
      "rolls": 1,
      "bonus_rolls": 0,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:second"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "first",
      "override": false,
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
                  "name": "minecraft:first"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "second",
      "override": false,
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
                  "name": "minecraft:second"
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

## Overlay `overlay`

`@overlay overlay`

### minecraft

`@loot_table minecraft:entities/wither`

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
          "name": "minecraft:first"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "first",
      "version": 1,
      "override": false,
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "conditions": [],
          "priority": {
            "stage": "standard",
            "default": 0,
            "before": [],
            "after": []
          },
          "source": {
            "type": "weld:value",
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:first"
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id": "second",
      "version": 1,
      "override": false,
      "rules": [
        {
          "type": "weld:append",
          "target": "pools",
          "conditions": [],
          "priority": {
            "stage": "standard",
            "default": 0,
            "before": [],
            "after": []
          },
          "source": {
            "type": "weld:value",
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:second"
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

`@endoverlay`
