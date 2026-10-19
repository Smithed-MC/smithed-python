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
  "id": "pack.never2"
}
```

### minecraft

`@loot_table minecraft:entities/zombie`

```json
{
  "type": "minecraft:entity",
  "random_sequence": "minecraft:entities/zombie",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:banana",
          "count": "2 million and a half"
        }
      ]
    }
  ],
  "__smithed__": [
    {
      "id": "pack.only",
      "override": true
    }
  ]
}
```
