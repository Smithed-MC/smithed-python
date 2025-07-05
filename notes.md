# Weld Resolver

## pack 1
data
|_ minecraft/loot_table/entities/wither.json
|_ minecraft/loot_table/entities/creeper.json
overlay_48_61
|_ data/minecraft/loot_table/entities/wither.json   [48, 61]
overlay_51_64
|_ data/minecraft/loot_table/entities/wither.json   [51, 64]
overlay_62_inf
|_ data/minecraft/loot_table/entities/wither.json   [62, +∞)

## pack 2
data
|_ minecraft/loot_table/entities/wither.json
|_ minecraft/loot_table/entities/creeper.json
overlay_48_62
|_ data/minecraft/loot_table/entities/wither.json   [48, 62]
|_ data/minecraft/loot_table/entities/creeper.json  [48, 62]
overlay_80_inf
|_ data/minecraft/loot_table/entities/creeper.json  [80, +∞)

## ex
```py
pack_1 = [
    ((48, 61), overlay),
    ((51, 64), overlay),
    ((62,), overlay),
]

pack_2 = [
    ((48, 62), overlay),
    ((80,), overlay),
]
```

```py

pack_dict = defaultdict(RangeDict)

# index overlays
for pack in packs:
    for overlay in pack.overlays:
        rng = normalize_range(overlay.supported_format)
        pack_dict[pack][rng] = overlay
        

    
```


### Subpacks
```py
from ranges import RangeDict, Range

{
    tuple(): ["wither", "creeper"],
    (48, 61): ["wither"],
    (51, 64): ["wither"],
    (62,): ["wither"]
}
->
(0, 47): ["../wither"],
(0,): ["../creeper"],
(48, 61): ["../wither"],
(51, 64): ["../wither"],
(62,): ["../wither"],

files_by_namespace = defaultdict(RangeDict)
for pack in packs:
    for overlay in pack.overlays:
        for file in overlay.files():
            files_by_namespace[file.namespace][overlay.supported_formats] = [file]


files = RangeDict()
for pack in packs:
    for overlay in pack.overlays:
        files[overlay.supported_formats] = list(overlay.files())

final_pack = ...
for namespace, range in files_by_namespace.items():
    for supported_formats, files in reversed(range.items()):
        packs = [Pack(file=file) for file in file]
        output = packs.pop(0)
        for pack in packs:
            output.merge(pack)
        
        final_pack.overlays[f"welded_overlay_{supported_formats}"] = output
```

Boot Minecraft -> specific pack format
Game loads datapacks
- for each data pack:
  - choose the pack format (ditch other overlays)  `beet.contrib.bake_overlays`


## Approach 1
For each pack:
- create range dicts for each file to get unique spliced
- collapse them into a singular range dict

for each range dict
- weld the splices?

## Approach 2
For each pack:
- 