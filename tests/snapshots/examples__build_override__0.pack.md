# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
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
  "__smithed__": {
    "override": true,
    "id": "pack.only"
  }
}
```
