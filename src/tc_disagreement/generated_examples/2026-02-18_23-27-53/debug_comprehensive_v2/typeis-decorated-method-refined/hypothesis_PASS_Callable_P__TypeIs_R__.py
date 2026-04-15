"""Hypothesis Tier 2 test artifact.

Annotation: Callable[P, TypeIs[R]]
Variable: typeis_wrapper.__return__
Resolved type: typing.Callable[~P, typing_extensions.TypeIs[~R]]
Status: PASS
"""

# --- Original source code (full context) ---
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

# --- Hypothesis test ---
from hypothesis import given, settings, strategies as st
from typeguard import check_type, TypeCheckError

# To reproduce: run this file directly
# Annotation under test: Callable[P, TypeIs[R]]
# check_type(value, Callable[P, TypeIs[R]])
