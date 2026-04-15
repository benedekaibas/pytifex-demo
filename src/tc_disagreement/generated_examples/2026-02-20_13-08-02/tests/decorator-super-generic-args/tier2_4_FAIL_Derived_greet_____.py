"""
Hypothesis Tier 2 — Generated Property Test

Target: Derived.greet(...)
Kind: method
Line: 20
Status: FAIL
Max examples: 30

Bug: [TypeError] Derived.greet(...) -> TypeError: Derived.greet() missing 1 required positional argument: 'name'
  test_cases_run=2
  failing_args={}
"""

# --- Original source (full context) ---

from typing import Any, TypeVar, Callable, ParamSpec, Concatenate

_R = TypeVar("_R")
_P = ParamSpec("_P")
_Self = TypeVar("_Self")

def trace_method[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """A decorator that logs calls but preserves the signature."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__qualname__} with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Base:
    def greet(self, name: str) -> str:
        return f"Hello, {name} from Base!"

class Derived(Base):
    @trace_method
    def greet(self, name: str) -> str:
        # Some type checkers might incorrectly flag this as missing arguments
        # for super().greet(), despite ParamSpec preserving the signature.
        return super().greet(name)

if __name__ == "__main__":
    d = Derived()
    print(d.greet("World"))


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(receiver=...)
def test_Derived_greet(receiver):
    """Property test: Derived.greet() with generated inputs."""
    result = receiver.greet()
    # Expected return type: R


if __name__ == "__main__":
    test_Derived_greet()
