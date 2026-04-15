"""
Hypothesis Tier 2 — Generated Property Test

Target: MyContainer.contains_int(...)
Kind: function
Line: 16
Status: PASS
Max examples: 30

Strategies:
  item: object -> just(<object object at 0x701ce034a180>)
"""

# --- Original source (full context) ---

from typing import TypeVar, Union, reveal_type # Removed ClassVar as it's unused and kept imports minimal
from typing_extensions import TypeIs # Fixed TypeIs import from typing_extensions

T_co = TypeVar('T_co', covariant=True)

# DIVERGENCE POINT:
# Zuban (and some other stricter checkers) will raise an error here:
# "Variance of TypeVar "T_co" incompatible with variance in parent type"
# This is because `list` is an invariant generic type, but `T_co` is declared as covariant.
# Inheriting `list[T_co]` with a covariant `T_co` creates a type-unsafe situation if `MyContainer` were
# to implement methods that violate `list`'s invariance (e.g., `append`).
# Mypy, pyre, and ty often do not flag this at the class definition itself,
# but might only complain if a specific usage violates the variance.
class MyContainer(list[T_co]):
    @classmethod
    def contains_int(cls, item: object) -> TypeIs[int]:
        """Class method to check if an item is an int."""
        return isinstance(item, int)

    @classmethod
    def contains_str(cls, item: object) -> TypeIs[str]:
        """Class method to check if an item is a str."""
        return isinstance(item, str)

def process_item_with_class_method(item: Union[int, str, float]):
    if MyContainer.contains_int(item):
        reveal_type(item) # Expected: int (all checkers agree)
    elif MyContainer.contains_str(item):
        reveal_type(item) # Expected: str (all checkers agree)
    else:
        reveal_type(item) # Expected: float (all checkers agree)

if __name__ == "__main__":
    process_item_with_class_method(1)
    process_item_with_class_method("hello")
    process_item_with_class_method(3.14)


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(item=...)
def test_MyContainer_contains_int(item):
    """Property test: MyContainer.contains_int() with generated inputs."""
    result = MyContainer.contains_int(item)


if __name__ == "__main__":
    test_MyContainer_contains_int()
