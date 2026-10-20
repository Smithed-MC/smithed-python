# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "",
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ]
  },
  "id": "sandbox_test",
  "overlays": {
    "entries": [
      {
        "directory": "weld_generated",
        "min_format": [
          121,
          0
        ],
        "max_format": [
          121,
          0
        ]
      }
    ]
  }
}
```

### sandbox

`@function sandbox:input`

```mcfunction
say Sandbox input
```

`@loot_table sandbox:input`

```json
{
  "pools": []
}
```

`@weld_script sandbox:main`

```
import beet
import bisect
import bolt_expressions
from collections import ChainMap, Counter, OrderedDict, defaultdict, deque
from copy import copy, deepcopy
from dataclasses import asdict, dataclass, field, fields, replace
import fnmatch
from functools import cache, partial, reduce
import heapq
from itertools import chain, pairwise, product
import json
from math import ceil, sqrt
from random import Random
import re
import string
import textwrap
from typing import Any, Literal, NamedTuple, TypedDict, cast, get_args


# Inspect existing resources; generate output with Bolt syntax below.
input_functions = []
for name, source in ctx.data.functions.items():
    input_functions.append([name, list(source.lines), source.text])

results = {
    "ctx_items": input_functions,
    "ctx_get": ctx.data.functions.get("sandbox:input").lines,
    "ctx_keys": sorted(ctx.data.functions.keys()),
    "ctx_values": len(list(ctx.data.functions.values())),
    "ctx_data": ctx.data.loot_tables["sandbox:input"].data,
    "ctx_format": ctx["scoped"].format("sandbox:{path}generated_{incr}"),
    "beet": beet.Function(["say Local file"]).lines,
    "bolt_expressions": bolt_expressions.type_name({"value": 1}),
    "builtins": sorted(set(range(5)) - set([1, 3])),
}


# Collection helpers and their returned objects.
counts = Counter(["apple", "pear", "apple"])
queue = deque([1])
queue.append(2)
groups = defaultdict(list)
groups["fruit"].append("apple")
results["collections"] = [
    counts.most_common(),
    list(queue),
    groups["fruit"],
    ChainMap({"first": 1}, {"second": 2}).maps,
    list(OrderedDict.fromkeys(["pear", "apple"], 1).items()),
]

original = {"values": [1]}
cloned = deepcopy(original)
cloned["values"].append(2)
results["copy"] = [copy([1, 2]), original, cloned]


# Script-defined records can be converted to ordinary dictionaries or tuples.
@dataclass
class Item:
    name: str
    tags: list[str] = field(default_factory=list)

class Options(TypedDict):
    enabled: bool

Pair = NamedTuple("Pair", [("name", str), ("count", int)])
pair = Pair("apple", 2)
item = replace(Item("apple", ["fruit"]), name="pear")
mode = Literal["catalog", "test"]
results["dataclasses"] = [asdict(item), fields(item)[0].name]
results["typing"] = [
    cast(Any, Options(enabled=True)).get("enabled"),
    pair[0],
    pair[1],
    get_args(mode),
]


# Functional, numeric, and ordering helpers.
calls = []

@cache
def double(value):
    calls.append(value)
    return value * 2

results["functools"] = [
    partial(int, base=16)("ff"),
    reduce(max, [1, 4, 2]),
    double(3),
    double(3),
    len(calls),
]
results["bisect"] = bisect.bisect_left([1, 3, 5], 4)
heap = [3, 1, 2]
heapq.heapify(heap)
heapq.heappush(heap, 0)
results["heapq"] = [heapq.heappop(heap), sorted(heap)]
results["itertools"] = [
    list(chain([1, 2], [3])),
    list(pairwise([1, 2, 3])),
    list(product([1, 2], [3])),
]
results["math"] = [ceil(1.2), sqrt(9)]
results["random"] = Random(7).randrange(100)
results["json"] = json.loads(json.dumps({"enabled": True}))


# Text helpers, including methods on compiled patterns and matches.
pattern = re.compile("item_([a-z]+)")
match = pattern.fullmatch("item_sword")
results["re"] = [match.group(1), match.groups(), pattern.sub("tool", "item_sword")]
results["fnmatch"] = fnmatch.filter(["apple.json", "pear.bolt"], "*.json")
results["string"] = [string.ascii_lowercase[:3], string.digits[:3], string.capwords("hello world")]
results["textwrap"] = [textwrap.dedent("  hello"), textwrap.wrap("hello world", width=6)]


function sandbox:results:
    for name in sorted(results):
        say f"{name}={json.dumps(results[name], sort_keys=True)}"
```

## Overlay `weld_generated`

`@overlay weld_generated`

### sandbox

`@function sandbox:results`

```mcfunction
say beet=["say Local file"]
say bisect=2
say bolt_expressions="dict"
say builtins=[0, 2, 4]
say collections=[[["apple", 2], ["pear", 1]], [1, 2], ["apple"], [{"first": 1}, {"second": 2}], [["pear", 1], ["apple", 1]]]
say copy=[[1, 2], {"values": [1]}, {"values": [1, 2]}]
say ctx_data={"pools": []}
say ctx_format="sandbox:scoped/generated_0"
say ctx_get=["say Sandbox input"]
say ctx_items=[["sandbox:input", ["say Sandbox input"], "say Sandbox input\n"]]
say ctx_keys=["sandbox:input"]
say ctx_values=1
say dataclasses=[{"name": "pear", "tags": ["fruit"]}, "name"]
say fnmatch=["apple.json"]
say functools=[255, 4, 6, 6, 1]
say heapq=[0, [1, 2, 3]]
say itertools=[[1, 2, 3], [[1, 2], [2, 3]], [[1, 3], [2, 3]]]
say json={"enabled": true}
say math=[2, 3.0]
say random=41
say re=["sword", ["sword"], "tool"]
say string=["abc", "012", "Hello World"]
say textwrap=["hello", ["hello", "world"]]
say typing=[true, "apple", 2, ["catalog", "test"]]
```

`@endoverlay`

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      75,
      0
    ],
    "max_format": [
      75,
      0
    ],
    "description": ""
  }
}
```
