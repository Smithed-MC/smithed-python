# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "id": "second",
  "pack": {
    "pack_format": 48,
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "formats": [
          61,
          61
        ],
        "directory": "examples_basic_overlays_first_overlay"
      },
      {
        "formats": [
          61,
          61
        ],
        "directory": "examples_basic_overlays_second_overlay"
      },
      {
        "formats": [
          61,
          61
        ],
        "directory": "smithed_generated_61_61"
      }
    ]
  }
}
```

### minecraft

`@loot_table minecraft:entities/bat`

```json
{
  "random_sequence": "minecraft:entities/bat",
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
  "random_sequence": "minecraft:entities/wither",
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
    },
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
            "type": "weld:value",
            "value": {
              "rolls": 1,
              "bonus_rolls": 0,
              "entries": [
                {
                  "type": "minecraft:item",
                  "name": "minecraft:first_overlay"
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
                  "name": "minecraft:second_overlay"
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
