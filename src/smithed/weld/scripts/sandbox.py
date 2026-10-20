"""Permissions for Weld scripts, including Bolt's basic helpers."""

import bisect
import collections
import copy
import dataclasses
import fnmatch
import functools
import heapq
import itertools
import json
import math
import random
import re
import string
import textwrap
import typing

import beet
import bolt_expressions
from bolt import LoopInfo
from bolt.contrib.sandbox import Sandbox, public_attrs


ALLOWED_BUILTINS = {
    "abs",
    "all",
    "any",
    "ascii",
    "bin",
    "bool",
    "callable",
    "chr",
    "dict",
    "divmod",
    "enumerate",
    "filter",
    "float",
    "frozenset",
    "hasattr",
    "hash",
    "hex",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "min",
    "next",
    "object",
    "oct",
    "ord",
    "pow",
    "print",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "slice",
    "sorted",
    "str",
    "sum",
    "tuple",
    "type",
    "zip",
}

ALLOWED_IMPORTS = {
    "beet",
    "bisect",
    "bolt_expressions",
    "collections",
    "copy",
    "dataclasses",
    "fnmatch",
    "functools",
    "heapq",
    "itertools",
    "json",
    "math",
    "random",
    "re",
    "string",
    "textwrap",
    "typing",
}

# Module exports are separate from permission to import the module itself.
ALLOWED_OBJ_ATTRS = {
    dict: {"fromkeys"},
    collections.defaultdict: {"fromkeys"},
    collections.OrderedDict: {"fromkeys"},
    collections.Counter: {"fromkeys"},
    collections.ChainMap: {"fromkeys"},
    beet: public_attrs(beet),
    bolt_expressions: public_attrs(bolt_expressions),
    bisect: public_attrs(bisect),
    heapq: public_attrs(heapq),
    itertools: public_attrs(itertools),
    math: public_attrs(math),
    random: public_attrs(random),
    json: {"loads", "dumps"},
    copy: {"copy", "deepcopy"},
    collections: {"ChainMap", "Counter", "OrderedDict", "defaultdict", "deque"},
    dataclasses: {
        "InitVar",
        "KW_ONLY",
        "MISSING",
        "asdict",
        "astuple",
        "dataclass",
        "field",
        "fields",
        "is_dataclass",
        "replace",
    },
    fnmatch: {"filter", "filterfalse", "fnmatch", "fnmatchcase", "translate"},
    functools: {"cache", "cmp_to_key", "lru_cache", "partial", "reduce", "wraps"},
    re: {
        "ASCII",
        "DOTALL",
        "IGNORECASE",
        "MULTILINE",
        "NOFLAG",
        "UNICODE",
        "VERBOSE",
        "compile",
        "escape",
        "findall",
        "finditer",
        "fullmatch",
        "match",
        "search",
        "split",
        "sub",
        "subn",
    },
    string: {
        "ascii_letters",
        "ascii_lowercase",
        "ascii_uppercase",
        "capwords",
        "digits",
        "hexdigits",
        "octdigits",
        "printable",
        "punctuation",
        "whitespace",
    },
    textwrap: {"dedent", "fill", "indent", "shorten", "wrap"},
    typing: {
        "Annotated",
        "Any",
        "Callable",
        "ClassVar",
        "Collection",
        "Final",
        "Generator",
        "Generic",
        "Iterable",
        "Iterator",
        "Literal",
        "LiteralString",
        "Mapping",
        "MutableMapping",
        "MutableSequence",
        "NamedTuple",
        "Never",
        "NewType",
        "NoReturn",
        "NotRequired",
        "Optional",
        "ParamSpec",
        "Protocol",
        "ReadOnly",
        "Required",
        "Self",
        "Sequence",
        "TYPE_CHECKING",
        "TypeAlias",
        "TypeGuard",
        "TypeIs",
        "TypeVar",
        "TypedDict",
        "Union",
        "cast",
        "final",
        "get_args",
        "get_origin",
        "overload",
        "override",
        "runtime_checkable",
    },
}

# These types expose all public attributes, including methods on helper results.
ALLOWED_TYPES = (
    tuple,
    list,
    dict,
    set,
    frozenset,
    collections.ChainMap,
    collections.Counter,
    collections.OrderedDict,
    collections.defaultdict,
    collections.deque,
    dataclasses.Field,
    functools.partial,
    random.Random,
    re.Match,
    re.Pattern,
    beet.TreeNode,
    beet.TreeData,
    LoopInfo,
    beet.Draft,
    beet.DataPack,
    beet.ResourcePack,
)

ALLOWED_TYPE_ATTRS = {
    allowed_type: public_attrs(allowed_type) for allowed_type in ALLOWED_TYPES
} | {
    str: public_attrs(str)
    - {"maketrans", "translate", "encode", "format", "format_map"},
    collections.ChainMap: public_attrs(collections.ChainMap) | {"maps"},
    beet.NamespaceProxy: {"get", "items", "keys", "match", "values", "walk"},
    beet.TextFileBase: {"text"},
    beet.JsonFileBase: {"data"},
    beet.Function: {"lines"},
    beet.Context: {
        "project_id",
        "project_name",
        "project_description",
        "project_author",
        "project_version",
        "project_root",
        "minecraft_version",
    },
}


def configure_sandbox(sandbox: Sandbox):
    """Apply the Weld permissions before activating Bolt's sandbox."""
    sandbox.allowed_builtins |= ALLOWED_BUILTINS
    sandbox.allowed_imports |= ALLOWED_IMPORTS
    for obj, attrs in ALLOWED_OBJ_ATTRS.items():
        sandbox.allowed_obj_attrs[obj] |= attrs
    for allowed_type, attrs in ALLOWED_TYPE_ATTRS.items():
        sandbox.allowed_type_attrs[allowed_type] |= attrs
    sandbox.activate()
