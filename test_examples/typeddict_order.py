from typing import TypedDict

class TD1(TypedDict):
    a: int
    b: str

class TD2(TypedDict):
    a: str
    c: int

class TD3(TD2, TD1): ...  # incompatible subclass; order matters

def foo(a: str, b: str, c: int): ...

def td() -> TD3: ...

reveal_type(td()["a"])  # expected str, got int (pyright disagrees)

foo(**td())  # likewise, error expected OK
