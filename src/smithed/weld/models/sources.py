from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field

from .validators import normalize_type

from .base import BaseModel


class _Source(BaseModel): ...


class ReferenceSource(_Source):
    type: Literal["smithed:reference", "weld:reference", "reference"]
    path: str


class ValueSource(_Source):
    type: Literal["smithed:value", "weld:value", "value"]
    value: Any


PureSource = Annotated[ValueSource | ReferenceSource, Field(..., discriminator="type")]
Source = Annotated[PureSource, BeforeValidator(normalize_type)]
