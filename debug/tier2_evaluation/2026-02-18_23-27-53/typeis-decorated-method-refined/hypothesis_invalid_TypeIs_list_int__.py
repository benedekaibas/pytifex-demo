"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeIs[list[int]]
Test type: invalid
"""\n\n"""Hypothesis test for TypeIs[list[int]] - invalid values.

Type annotation: TypeIs[list[int]]
Variable: is_list_of_ints.__return__
Test type: invalid
"""

# Original source code
from typing import ParamSpec, Callable, TypeVar, reveal_type
from typing_extensions import TypeIs # Changed from typing to typing_extensions

P = ParamSpec('P')
R = TypeVar('R')

def typeis_wrapper(func: Callable[P, TypeIs[R]]) -> Callable[P, TypeIs[R]]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> TypeIs[R]:
        # This wrapper's return annotation TypeIs[R] implies that 'wrapper' itself
        # is a TypeIs function, narrowing its first positional argument.
        # How type checkers handle TypeIs with *args is an ambiguity.
        return func(*args, **kwargs)
    return wrapper

class Validator:
    @typeis_wrapper
    def is_list_of_ints(self, x: object) -> TypeIs[list[int]]:
        # According to PEP 673, TypeIs[list[int]] on this method should narrow 'self'
        # to list[int], not 'x'. However, the function's logic operates on 'x'.
        # This semantic mismatch is a prime candidate for divergence.
        return isinstance(x, list) and all(isinstance(item, int) for item in x)

def check_decorated_typeis(data: object):
    validator_instance = Validator() # Instantiate once
    if validator_instance.is_list_of_ints(data):
        reveal_type(data) # Divergence point: Some may show list[int] (incorrectly narrowed x),
                          # others object (correctly not narrowing x, or decorator failed).
    else:
        reveal_type(data) # Expected: object (or object - list[int])
        
if __name__ == "__main__":
    check_decorated_typeis([1, 2, 3])
    check_decorated_typeis("not a list")
    check_decorated_typeis([1, "a"])

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, TypeIs[list[int]])
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "TypeIs[list[int]]" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "TypeIs[list[int]]" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
