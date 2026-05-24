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
    "description": "",
    "supported_formats": [
      48,
      64
    ]
  },
  "overlays": {
    "entries": [
      {
        "directory": "examples_complex_overlays_pack1_overlay_48_61",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ]
      },
      {
        "directory": "examples_complex_overlays_pack1_overlay_51_64",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ]
      },
      {
        "directory": "examples_complex_overlays_pack1_overlay_62_inf",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ]
      },
      {
        "directory": "examples_complex_overlays_pack2_overlay",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ]
      },
      {
        "formats": [
          48,
          64
        ],
        "directory": "smithed_generated_48_64",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ]
      }
    ]
  },
  "id": "second"
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
  "type": "minecraft:entity",
  "random_sequence": "minecraft:entities/wither",
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

## Overlay `smithed_generated_48_64`

`@overlay smithed_generated_48_64`

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

`@endoverlay`
