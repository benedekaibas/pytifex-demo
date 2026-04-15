from typing import TypedDict, Required, NotRequired, Literal, TypeGuard


class BaseTD(TypedDict, total=True):
    name: str
    value: int


class ChildTD(BaseTD, total=False):
    optional: str


def process(data: BaseTD) -> None:
    reveal_type(data)


data1: ChildTD = {"name": "test", "value": 42, "optional": "hi"}
process(data1)

if __name__ == "__main__":
    pass
