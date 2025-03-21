# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "Smithed's Actionbar Pack",
    "pack_format": 48
  },
  "id": "tacos"
}
```

### minecraft

`@loot_table minecraft:blocks/yellow_shulker_box`

```json
{
  "type": "minecraft:block",
  "pools": [
    {
      "bonus_rolls": 0.0,
      "entries": [
        {
          "type": "minecraft:item",
          "functions": [
            {
              "function": "minecraft:copy_components",
              "include": [
                "minecraft:custom_name",
                "minecraft:container",
                "minecraft:lock",
                "minecraft:container_loot"
              ],
              "source": "block_entity"
            }
          ],
          "name": "minecraft:yellow_shulker_box"
        }
      ],
      "rolls": 1.0
    }
  ],
  "random_sequence": "minecraft:blocks/yellow_shulker_box",
  "__smithed__": []
}
```
