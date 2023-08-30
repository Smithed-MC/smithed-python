# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": ""
  },
  "id": "gm4_bat_grenades"
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
      "entries": [
        {
          "type": "loot_table",
          "name": "tcc:items/bat_wing",
          "functions": [
            {
              "function": "set_count",
              "count": {
                "min": 1,
                "max": 2
              }
            }
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "item",
          "name": "minecraft:rabbit_hide",
          "functions": [
            {
              "function": "set_nbt",
              "tag": "{CustomModelData:3420001}"
            },
            {
              "function": "set_name",
              "name": {
                "translate": "%1$s%3427655$s",
                "with": [
                  "Bat Leather",
                  {
                    "translate": "item.gm4.bat_leather"
                  }
                ],
                "italic": false
              }
            },
            {
              "function": "set_lore",
              "lore": [
                {
                  "translate": "%1$s%3427655$s",
                  "with": [
                    "Would make for a very strange,",
                    {
                      "translate": "text.gm4.bat_leather.1"
                    }
                  ],
                  "italic": true,
                  "color": "dark_gray"
                },
                {
                  "translate": "%1$s%3427655$s",
                  "with": [
                    "very tiny jacket",
                    {
                      "translate": "text.gm4.bat_leather.2"
                    }
                  ],
                  "italic": true,
                  "color": "dark_gray"
                }
              ]
            }
          ],
          "weight": 1
        },
        {
          "type": "empty",
          "weight": 5
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "tcc",
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "loot_table",
                  "name": "tcc:items/bat_wing",
                  "functions": [
                    {
                      "function": "set_count",
                      "count": {
                        "min": 1,
                        "max": 2
                      }
                    }
                  ]
                }
              ]
            }
          },
          "type": "smithed:append"
        }
      ]
    },
    {
      "id": "gm4_bat_grenades",
      "rules": [
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "item",
                  "name": "minecraft:gunpowder",
                  "functions": [
                    {
                      "function": "set_count",
                      "count": {
                        "min": 1,
                        "max": 3
                      }
                    }
                  ]
                }
              ]
            }
          },
          "type": "smithed:append"
        },
        {
          "target": "pools",
          "priority": {},
          "source": {
            "value": {
              "rolls": 1,
              "entries": [
                {
                  "type": "item",
                  "name": "minecraft:rabbit_hide",
                  "functions": [
                    {
                      "function": "set_nbt",
                      "tag": "{CustomModelData:3420001}"
                    },
                    {
                      "function": "set_name",
                      "name": {
                        "translate": "%1$s%3427655$s",
                        "with": [
                          "Bat Leather",
                          {
                            "translate": "item.gm4.bat_leather"
                          }
                        ],
                        "italic": false
                      }
                    },
                    {
                      "function": "set_lore",
                      "lore": [
                        {
                          "translate": "%1$s%3427655$s",
                          "with": [
                            "Would make for a very strange,",
                            {
                              "translate": "text.gm4.bat_leather.1"
                            }
                          ],
                          "italic": true,
                          "color": "dark_gray"
                        },
                        {
                          "translate": "%1$s%3427655$s",
                          "with": [
                            "very tiny jacket",
                            {
                              "translate": "text.gm4.bat_leather.2"
                            }
                          ],
                          "italic": true,
                          "color": "dark_gray"
                        }
                      ]
                    }
                  ],
                  "weight": 1
                },
                {
                  "type": "empty",
                  "weight": 5
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