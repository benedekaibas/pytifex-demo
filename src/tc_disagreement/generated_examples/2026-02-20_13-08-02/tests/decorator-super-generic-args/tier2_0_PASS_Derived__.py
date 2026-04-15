"""
Hypothesis Tier 2 — Generated Test

Call: Derived()
Kind: constructor
Line: 26
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

def test_Derived_constructor():
    """Test that Derived() can be constructed."""
    try:
        instance = Derived()
        print(f"OK: {instance}")
    except (TypeError, AttributeError, ValueError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_Derived_constructor()
