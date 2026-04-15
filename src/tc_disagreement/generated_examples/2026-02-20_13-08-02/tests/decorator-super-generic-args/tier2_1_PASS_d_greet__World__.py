"""
Hypothesis Tier 2 — Generated Test

Call: d.greet('World')
Kind: method
Line: 27
Status: PASS
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


# --- Tier 2 test ---

def test_Derived_greet():
    """Test that Derived.greet() runs without type errors."""
    try:
        receiver = Derived()
        result = receiver.greet()
        # Expected return type: R
        print(f"OK: {result}")
    except (TypeError, AttributeError, ValueError, KeyError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_Derived_greet()
