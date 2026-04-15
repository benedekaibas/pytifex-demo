"""
Hypothesis Tier 2 — Generated Property Test

Target: Base.greet(...)
Kind: method
Line: 15
Status: PASS
Max examples: 30

Strategies:
  name: str -> text(max_size=30)
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
@given(receiver=..., name=...)
def test_Base_greet(receiver, name):
    """Property test: Base.greet() with generated inputs."""
    result = receiver.greet(name)
    # Expected return type: str


if __name__ == "__main__":
    test_Base_greet()
