"""
Hypothesis Tier 2 — Generated Property Test

Target: is_str_pair(...)
Kind: function
Line: 7
Status: PASS
Max examples: 30

Strategies:
  val: Tuple -> tuples(one_of(integers(), text(max_size=10), booleans(), none()), one_of(inte...
"""

# --- Original source (full context) ---

import typing as t
from typing import TypeGuard, TypeVar, Union, Tuple, Any

T = TypeVar("T")
S = TypeVar("S")

def is_str_pair(val: Tuple[Any, Any]) -> TypeGuard[Tuple[str, str]]:
    """TypeGuard to check if a tuple contains two strings."""
    return isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], str) and isinstance(val[1], str)

def is_int_bool_pair(val: Tuple[Any, Any]) -> TypeGuard[Tuple[int, bool]]:
    """TypeGuard to check if a tuple contains an int and a bool."""
    return isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], int) and isinstance(val[1], bool)


def process_item[X, Y](item: Union[Tuple[int, bool], Tuple[str, str], Tuple[X, Y]]) -> str:
    reveal_type(item) # Should be Union[Tuple[int, bool], Tuple[str, str], Tuple[X, Y]]
    match item:
        case (a, b) if is_str_pair(item): # Mypy might not correctly narrow 'a' and 'b' to str
            reveal_type(a) # Expected: str
            reveal_type(b) # Expected: str
            return f"String pair: {a}, {b}"
        case (x, y) if is_int_bool_pair(item): # Mypy might not correctly narrow 'x' and 'y' to int, bool
            reveal_type(x) # Expected: int
            reveal_type(y) # Expected: bool
            return f"Int-bool pair: {x}, {y}"
        case (p, q): # General case for Tuple[X, Y] if not narrowed
            reveal_type(p) # Expected: X
            reveal_type(q) # Expected: Y
            return f"Generic pair: {p} ({type(p).__name__}), {q} ({type(q).__name__})"

if __name__ == "__main__":
    print(process_item((1, True)))
    print(process_item(("hello", "world")))
    print(process_item((3.14, None))) # X=float, Y=None
    
    # Test with a specific generic tuple type, that should hit the generic case
    my_generic_tuple: Tuple[float, int] = (1.5, 2)
    print(process_item(my_generic_tuple))

    # Test with mixed types not caught by guards
    mixed_tuple = (1, "mixed")
    print(process_item(mixed_tuple))


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(val=...)
def test_is_str_pair(val):
    """Property test: is_str_pair() with generated inputs."""
    result = is_str_pair(val)


if __name__ == "__main__":
    test_is_str_pair()
