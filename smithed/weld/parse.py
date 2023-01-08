from tokenstream import Token, TokenStream
from typing import Any

JsonDict = dict[str, Any]



def parse(raw: str):
    stream = TokenStream(raw)
    with stream.syntax(key=r"\w+", separator=r"\.", open=r"\[", close=r"\]", index=r"\[\d+\]"):
        for token in stream.collect():
            match token:
                case Token(type="open"):
                    yield stream.expect("index")
                    stream.expect("close")
                case Token(type=type) if type != "separator":
                    yield token


def get(path: str, obj: JsonDict):
    current = obj
    for token in parse(path):
        match token:
            case Token(type=type, value=str(value)) if type != "separator":
                current = current[value]
    return current

def set(path: str, obj: JsonDict, value: Any):
    current = obj
    for token in parse(path):
        match token:
            case Token(type=type, value=str(value)) if type != "separator":
                if value not in current:
                    current = [None] * (int(value) + 1) if 
                current = current[value]
    return current
