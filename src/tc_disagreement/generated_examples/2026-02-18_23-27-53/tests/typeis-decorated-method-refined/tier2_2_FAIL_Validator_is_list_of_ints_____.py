"""
Hypothesis Tier 2 — Generated Property Test

Target: Validator.is_list_of_ints(...)
Kind: method
Line: 17
Status: FAIL
Max examples: 30

Bug: [TypeError] Validator.is_list_of_ints(...) -> TypeError: Validator.is_list_of_ints() missing 1 required positional argument: 'x'
  test_cases_run=2
  failing_args={}
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(receiver=...)
def test_Validator_is_list_of_ints(receiver):
    """Property test: Validator.is_list_of_ints() with generated inputs."""
    result = receiver.is_list_of_ints()
    # Expected return type: TypeIs


if __name__ == "__main__":
    test_Validator_is_list_of_ints()
