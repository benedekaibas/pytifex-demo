from typing_extensions import TypedDict

class Foo(TypedDict):
    name: str

def _(td: Foo, key: str) -> None:
    reveal_type(td["anything"])
