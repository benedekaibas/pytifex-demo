"""
Hypothesis Tier 2 — Generated Property Test

Target: Box(...)
Kind: constructor
Line: 7
Status: PASS
Max examples: 30

Strategies:
  value: TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())
"""

# --- Original source (full context) ---

import typing as t
from typing import Generic, TypeVar, Union, Self, List

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def describe_value(self: Self) -> str:
        # Type checkers might struggle with Self referring to Box[T] and propagating T's type
        # within the match statement for structural pattern matching.
        match self.value:
            case int() as i:
                reveal_type(i) # Expected: int
                return f"Box<{self.value_type_name}> contains an integer: {i}"
            case str() as s:
                reveal_type(s) # Expected: str
                return f"Box<{self.value_type_name}> contains a string: '{s}'"
            case list() if all(isinstance(x, int) for x in self.value): # Runtime check for specific list content
                reveal_type(self.value) # Expected: list[int] (if narrowed correctly)
                return f"Box<{self.value_type_name}> contains a list of integers: {self.value}"
            case _:
                reveal_type(self.value) # Expected: T
                return f"Box<{self.value_type_name}> contains a generic value: {self.value}"
    
    @property
    def value_type_name(self: Self) -> str:
        # Simple property to illustrate Self context
        return type(self.value).__name__

if __name__ == "__main__":
    int_box = Box(123)
    str_box = Box("hello")
    list_int_box = Box([1, 2, 3])
    float_box = Box(3.14)
    mixed_list_box = Box([1, "a", 2.0])

    print(int_box.describe_value())
    print(str_box.describe_value())
    print(list_int_box.describe_value())
    print(float_box.describe_value())
    print(mixed_list_box.describe_value())

    # Demonstrate Self type with a subclass
    class SpecificIntBox(Box[int]):
        def get_value_plus_one(self: Self) -> int:
            # Self here should be SpecificIntBox[int], so self.value is int
            reveal_type(self.value) # Expected: int
            return self.value + 1

    s_int_box = SpecificIntBox(5)
    print(f"Specific box value + 1: {s_int_box.get_value_plus_one()}")


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(value=...)
def test_Box_constructor(value):
    """Property test: Box() with generated inputs."""
    instance = Box(value)
    assert isinstance(instance, Box)


if __name__ == "__main__":
    test_Box_constructor()
