# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "id": "second",
  "pack": {
    "pack_format": 48,
    "description": "",
    "supported_formats": [
      62,
      64
    ]
  },
  "overlays": {
    "entries": [
      {
        "formats": [
          48,
          61
        ],
        "directory": "examples_complex_overlays_pack1_overlay_48_61"
      },
      {
        "formats": [
          51,
          64
        ],
        "directory": "examples_complex_overlays_pack1_overlay_51_64"
      },
      {
        "formats": [
          62,
          2147483647
        ],
        "directory": "examples_complex_overlays_pack1_overlay_62_inf"
      },
      {
        "formats": [
          61,
          61
        ],
        "directory": "examples_complex_overlays_pack2_overlay"
      },
      {
        "formats": [
          48,
          50
        ],
        "directory": "smithed_generated_48_50"
      },
      {
        "formats": [
          51,
          61
        ],
        "directory": "smithed_generated_51_61"
      },
      {
        "formats": [
          62,
          64
        ],
        "directory": "smithed_generated_62_64"
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
                  "name": "minecraft:data"
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

## Overlay `examples_complex_overlays_pack1_overlay_48_61`

`@overlay examples_complex_overlays_pack1_overlay_48_61`

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
          "name": "minecraft:overlay_48_61"
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
          "path": "pools[0]"
        }
      }
    ]
  }
}
```

## Overlay `examples_complex_overlays_pack1_overlay_51_64`

`@overlay examples_complex_overlays_pack1_overlay_51_64`

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
          "name": "minecraft:overlay_51_64"
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
          "path": "pools[0]"
        }
      }
    ]
  }
}
```

## Overlay `examples_complex_overlays_pack1_overlay_62_inf`

`@overlay examples_complex_overlays_pack1_overlay_62_inf`

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
          "name": "minecraft:overlay_62_inf"
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
          "path": "pools[0]"
        }
      }
    ]
  }
}
```

## Overlay `examples_complex_overlays_pack2_overlay`

`@overlay examples_complex_overlays_pack2_overlay`

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
          "name": "minecraft:second"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "second",
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

## Overlay `smithed_generated_48_50`

`@overlay smithed_generated_48_50`

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
                  "name": "minecraft:overlay_48_61"
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

## Overlay `smithed_generated_51_61`

`@overlay smithed_generated_51_61`

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
                  "name": "minecraft:overlay_51_64"
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

## Overlay `smithed_generated_62_64`

`@overlay smithed_generated_62_64`

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
                  "name": "minecraft:overlay_62_inf"
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
