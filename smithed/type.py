from typing import Any

JsonType = int | str | float | bool | None | list[Any] | dict[str, Any]
JsonDict = dict[str, "JsonType"]
JsonList = list["JsonType"]
