from typing import overload, Literal


@overload
def process(value: int) -> int: ...
@overload
def process(value: str) -> str: ...
@overload
def process(value: Literal["a", "b"]) -> bool: ...


def process(value):
    return value


result1 = process(42)
result2 = process("hello")
result3 = process("a")

reveal_type(result1)
reveal_type(result2)
reveal_type(result3)

if __name__ == "__main__":
    pass
