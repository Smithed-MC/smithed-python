# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 15,
    "description": ""
  },
  "id": "pack.only"
}
```

### minecraft

`@loot_table minecraft:entities/zombie`

```json
{
  "random_sequence": "minecraft:entities/zombie",
  "type": "minecraft:entity",
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
      "override": true,
      "priority": {}
    }
  ]
}
```
