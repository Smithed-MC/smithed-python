import logging
from typing import Annotated, Any, Iterable, Literal

from beet import ListOption
from jsonpath_ng import parse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, root_validator, validator

logger = logging.getLogger(__name__)


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = {
            set: lambda v: list(v),
        }


class ConditionPackCheck(BaseModel):
    type: Literal["smithed:pack_check"]
    id: str


class ConditionInverted(BaseModel):
    type: Literal["smithed:inverted"]
    condition: "SmithedCondition"


SmithedCondition = ConditionPackCheck | ConditionInverted


class SmithedReferenceSource(BaseModel):
    type: Literal["smithed:reference"]
    path: str


class SmithedValueSource(BaseModel):
    type: Literal["smithed:value"] = "smithed:value"
    value: Any


SmithedSource = SmithedReferenceSource | SmithedValueSource


class SmithedBaseRule(BaseModel):
    target: str
    conditions: list[SmithedCondition] = []

class SmithedAdditiveRule(SmithedBaseRule):
    source: SmithedSource = Field(..., discriminator="type")

class SmithedMergeRule(SmithedAdditiveRule):
    type: Literal["smithed:merge"]

class SmithedAppendRule(SmithedAdditiveRule):
    type: Literal["smithed:append"]

class SmithedPrependRule(SmithedAdditiveRule):
    type: Literal["smithed:prepend"]

class SmithedInsertRule(SmithedAdditiveRule):
    type: Literal["smithed:insert"]
    index: int

class SmithedReplaceRule(SmithedAdditiveRule):
    type: Literal["smithed:replace"]

class SmithedRemoveRule(SmithedBaseRule):
    type: Literal["smithed:remove"]


SmithedRule = Annotated[
    SmithedMergeRule | SmithedAppendRule | SmithedPrependRule | SmithedInsertRule,
    Field(..., discriminator="type"),
]


class SmithedPriority(BaseModel):
    after: set[str] = set()
    before: set[str] = set()

    @validator("*")
    def convert_fields(cls, value: Iterable[str]):
        return set(value)


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    rules: list[SmithedRule]
    priority: SmithedPriority = SmithedPriority()


class SmithedJsonFile(BaseModel, extra="allow"):
    smithed: ListOption[SmithedModel] = Field(
        default_factory=ListOption, alias="__smithed__"
    )

    @root_validator
    def convert_type(cls, values: dict[str, ListOption[SmithedModel]]):
        for model in values["smithed"].entries():
            model.rules = list(cls.convert_rules(model.rules, values))

        return values
    
    @classmethod
    def convert_rules(cls, rules: list[SmithedRule], values: dict[str, Any]):
        for rule in rules:
            match rule.source:
                case SmithedReferenceSource(path=path):
                    try:
                        rule.source = SmithedValueSource(
                            value=parse(path).find(values).pop(0).value
                        )
                    except IndexError:
                        logger.warn(f"Source Reference Path: {path} was not found. Deleting Rule.")
                        continue
            yield rule
