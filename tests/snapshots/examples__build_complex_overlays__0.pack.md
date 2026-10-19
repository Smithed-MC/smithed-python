# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ],
    "description": ""
  },
  "id": "second",
  "overlays": {
    "entries": [
      {
        "formats": [
          48,
          50
        ],
        "directory": "smithed_generated_48_50",
        "min_format": [
          48,
          0
        ],
        "max_format": 50
      },
      {
        "formats": [
          51,
          61
        ],
        "directory": "smithed_generated_51_61",
        "min_format": [
          51,
          0
        ],
        "max_format": 61
      },
      {
        "formats": [
          62,
          2147483647
        ],
        "directory": "smithed_generated_62_2147483647",
        "min_format": [
          62,
          0
        ],
        "max_format": 2147483647
      }
    ]
  }
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
          "name": "minecraft:data"
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
      "id": "pack1",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:data"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    },
    {
      "id": "second",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:second"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    }
  ]
}
```

## Overlay `smithed_generated_48_50`

`@overlay smithed_generated_48_50`

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
          "name": "minecraft:overlay_48_61"
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
      "id": "pack1",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:overlay_48_61"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    },
    {
      "id": "second",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:second"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    }
  ]
}
```

## Overlay `smithed_generated_51_61`

`@overlay smithed_generated_51_61`

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
          "name": "minecraft:overlay_51_64"
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
      "id": "pack1",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:overlay_51_64"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    },
    {
      "id": "second",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:second"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    }
  ]
}
```

## Overlay `smithed_generated_62_2147483647`

`@overlay smithed_generated_62_2147483647`

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
          "name": "minecraft:overlay_62_inf"
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
      "id": "pack1",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:overlay_62_inf"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    },
    {
      "id": "second",
      "override": false,
      "rules": [
        {
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
                  "name": "minecraft:second"
                }
              ]
            }
          },
          "type": "weld:append"
        }
      ]
    }
  ]
}
```

`@endoverlay`

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      75,
      0
    ],
    "max_format": [
      75,
      0
    ],
    "description": ""
  }
}
```
