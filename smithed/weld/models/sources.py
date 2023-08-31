from typing import Annotated, Any, Literal

from pydantic import Field, validator

from .base import BaseModel


class _Source(BaseModel):
    type: str

    @validator("type")
    def fix_type(cls, value: str):
        if value.startswith("smithed:"):
            return value.replace("smithed:", "weld:")
        return value


class ReferenceSource(_Source):
    type: Literal["reference", "weld:reference", "smithed:reference"]
    path: str


class ValueSource(_Source):
    type: Literal["value", "weld:value", "smithed:value"] = "weld:value"
    value: Any


Source = Annotated[ValueSource | ReferenceSource, Field(..., discriminator="type")]
