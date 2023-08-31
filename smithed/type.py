from typing import TypeVar

JsonType = int | str | float | bool | None | list["JsonType"] | dict[str, "JsonType"]
JsonDict = dict[str, "JsonType"]
JsonList = list["JsonType"]

JsonTypeT = TypeVar("JsonTypeT", bound=JsonType)
