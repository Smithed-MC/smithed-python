from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field

from .validators import normalize_type
from .base import BaseModel


class _Source(BaseModel): ...


class ReferenceSource(_Source):
    type: Literal["weld:reference", "smithed:reference", "reference"]
    path: str


class ValueSource(_Source):
    type: Literal["weld:value", "smithed:value", "value"]
    value: Any


# Broad source — may be a reference or a concrete value (pre-resolution).
# Use this when parsing raw JSON where references haven't been resolved yet.
type BroadSource = Annotated[
    ValueSource | ReferenceSource,
    BeforeValidator(normalize_type),
    Field(discriminator="type"),
]

# Backward-compat alias — external code (e.g. handler.py) still imports `Source`
type Source = BroadSource
