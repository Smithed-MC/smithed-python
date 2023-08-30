"""
This file is super scrappy and needs to be rewritten but I can't be bothered right now.
"""

import logging
from dataclasses import dataclass
from typing import Any, Iterator, NamedTuple

from tokenstream import Token, TokenStream

from smithed.type import JsonDict, JsonList, JsonType

logger = logging.getLogger("weld")


@dataclass
class Filter:
    key: str
    value: Any
    type: str = "filter"


class TraverseResult(NamedTuple):
    parent: JsonDict | JsonList
    current: JsonType
    key: Any


def parse(raw: str, convert_index: bool):
    stream = TokenStream(raw)
    return handle_stream(stream, convert_index)


def handle_stream(stream: TokenStream, convert_index: bool) -> Iterator[Token | Filter]:
    with stream.syntax(
        key=r"[A-Z_a-z]+",
        string=r'"\w*"',
        separator=r"\.",
        bracket=r"\[|\]",
        curly=r"\{|\}",
        number=r"\d+",
        colon=r": *",
    ):
        for token in stream.collect():
            match token:
                case Token(type="key"):
                    yield token

                case Token(type="bracket", value="["):
                    match stream.expect_any("number", ("curly", "{")):
                        case Token(type="number", value=value) as token:
                            if convert_index:
                                yield Filter(key="_index", value=int(value))
                            else:
                                yield token
                        case Token(type="curly"):
                            yield parse_filter(stream)
                            stream.expect(("curly", "}"))
                    stream.expect(("bracket", "]"))

                case Token(type="separator") as token:
                    yield token


def parse_filter(stream: TokenStream):
    match stream.expect_any("key", "string"):
        case Token(type="key", value=value):
            key = value
        case Token(type="string", value=value):
            key = value[1:-1]
        case token:
            raise ValueError(f"Expected key or string. Found {token}")

    stream.expect("colon")
    return Filter(key=key, value=stream.expect_any("string", "number").value)


def traverse(obj: JsonDict, path: str, convert_index: bool = False):
    current = obj
    parent = current
    parser = parse(path, convert_index)
    last_token = None

    for token in parser:
        match token:
            case Token(type="key", value=value):
                if not isinstance(current, dict):
                    raise ValueError
                parent = current
                current = current.setdefault(value, {})
                last_token = token

            case Token(type="number", value=index):
                if not isinstance(current, list):
                    raise ValueError
                elif len(current) <= int(index):
                    raise IndexError
                parent = current
                current = current[int(index)]
                last_token = token

            case Filter(key=key, value=value):
                if not isinstance(current, list):
                    if last_token is None:
                        raise ValueError
                    if not isinstance(parent, dict):
                        raise ValueError
                    current = []
                    parent[last_token.value] = current  # type: ignore

                for item in current:
                    if not isinstance(item, dict):
                        raise ValueError
                    if key in item and item[key] == value:
                        parent = current
                        current = item
                        break
                else:
                    current.append({key: value})
                    parent = current
                    current = current[-1]
                last_token = token

    return TraverseResult(
        parent, current, last_token.value if last_token is not None else None
    )


def get(obj: JsonDict, path: str, convert_index: bool = False):
    return traverse(obj, path, convert_index).current


def append(obj: JsonDict, path: str, value: JsonType):
    parent, current, key = traverse(obj, path, True)
    if isinstance(current, list):
        current.append(value)
    elif not current:
        parent[key] = [value]


def prepend(obj: JsonDict, path: str, value: JsonType):
    parent, current, key = traverse(obj, path, True)
    if isinstance(current, list):
        current.insert(0, value)
    elif not current:
        parent[key] = [value]


def insert(obj: JsonDict, path: str, index: int, value: JsonType):
    parent, current, key = traverse(obj, path, True)
    if isinstance(current, list):
        current.insert(index, value)
    elif not current:
        parent[key] = [value]


def remove(obj: JsonDict, path: str):
    parent, _, key = traverse(obj, path, True)
    if isinstance(parent, list):
        del parent[int(key)]
    else:
        del parent[key]


def merge(obj: JsonDict, path: str, value: JsonType):
    parent, current, key = traverse(obj, path, True)

    def _merge(
        parent: JsonDict | JsonList, original: JsonType, to_merge: JsonType, key: str
    ):
        if isinstance(original, dict) and isinstance(to_merge, dict):
            for new_key, val in to_merge.items():
                if og_val := original.get(new_key, False):
                    parent = original
                    _merge(parent, og_val, val, new_key)
                else:
                    original[new_key] = val

        elif isinstance(original, list) and isinstance(to_merge, list):
            original.extend(to_merge)

        else:
            # logger.warn("Deprecated. Use `smithed:replace` instead.")
            parent[key] = to_merge  # TODO: this might error !!

    _merge(parent, current, value, key)


def replace(obj: JsonDict, path: str, value: JsonType):
    parent, _, key = traverse(obj, path, True)
    parent[key] = value
