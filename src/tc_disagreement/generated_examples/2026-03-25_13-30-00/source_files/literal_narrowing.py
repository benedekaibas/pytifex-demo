from typing import Literal, reveal_type


def bar(p: Literal["a", "b"]) -> None: ...


# Case 1: positive `in` check: not narrowed
def positive_in(foo: str):
    if foo in ("a", "b"):
        reveal_type(foo)  # Revealed type is "str" (expected "Literal['a', 'b']")
        bar(foo)  # error: Argument 1 to "bar" has incompatible type "str"; expected "Literal['a', 'b']"  [arg-type]


# Case 2: negative `not in` guard with `return`: not narrowed
def negative_not_in_return(foo: str):
    if foo not in ("a", "b"):
        return
    reveal_type(foo)  # Revealed type is "str" (expected "Literal['a', 'b']")
    bar(foo)  # error: [arg-type]


# Case 3: negative `not in` guard with `raise`: not narrowed
def negative_not_in_raise(foo: str):
    if foo not in ("a", "b"):
        raise ValueError(f"unexpected value: {foo}")
    reveal_type(foo)  # Revealed type is "str" (expected "Literal['a', 'b']")
    bar(foo)  # error: [arg-type]
