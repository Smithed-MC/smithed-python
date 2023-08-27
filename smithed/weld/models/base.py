from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    class Config:
        json_encoders = {set: lambda v: list(v)}
