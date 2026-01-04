from dataclasses import dataclass
from typing import NamedTuple

from pydantic.v1 import BaseModel
from streamlit.delta_generator import DeltaGenerator


class WebApp(BaseModel):
    class Footer(BaseModel):
        left: str
        right: str

    title: str
    conflicts: str
    intro: str
    warn: str
    fabric: str
    footer: Footer


class Columns(NamedTuple):
    left: DeltaGenerator
    middle: DeltaGenerator
    right: DeltaGenerator
    middle: DeltaGenerator
    right: DeltaGenerator


@dataclass
class WeldSettings:
    output_name: str = "welded-pack"
    description: str = "This pack contains multiple packs welded together"
    make_fabric_mod: bool = False
