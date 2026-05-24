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
  "overlays": {
    "entries": [
      {
        "directory": "examples_basic_overlays_first_overlay",
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
        "directory": "examples_basic_overlays_second_overlay",
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
          61,
          61
        ],
        "directory": "smithed_generated_61_61",
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

`@loot_table minecraft:entities/bat`

```json
{
  "type": "minecraft:entity",
  "random_sequence": "minecraft:entities/bat",
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
                  "name": "minecraft:first"
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
                  "name": "minecraft:first"
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

## Overlay `examples_basic_overlays_first_overlay`

`@overlay examples_basic_overlays_first_overlay`

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
          "name": "minecraft:first_overlay"
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

## Overlay `examples_basic_overlays_second_overlay`

`@overlay examples_basic_overlays_second_overlay`

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
          "name": "minecraft:second_overlay"
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

## Overlay `smithed_generated_61_61`

`@overlay smithed_generated_61_61`

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
                  "name": "minecraft:first"
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
