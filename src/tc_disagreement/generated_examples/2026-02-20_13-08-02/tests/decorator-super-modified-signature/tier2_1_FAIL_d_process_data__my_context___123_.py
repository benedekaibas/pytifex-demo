"""
Hypothesis Tier 2 — Generated Test

Call: d.process_data('my-context', 123)
Kind: method
Line: 32
Status: FAIL

Bug: [TypeError] d.process_data('my-context', 123) -> TypeError: Derived.process_data() missing 2 required positional arguments: 'context' and 'data'
"""

# --- Original source (full context) ---

from typing import Any, TypeVar, Callable, ParamSpec, Concatenate

_R = TypeVar("_R")
_P = ParamSpec("_P")
_Self = TypeVar("_Self")

# A decorator that *modifies* the signature by adding a context parameter
def inject_context[**P, R](func: Callable[Concatenate[_Self, P], R]) -> Callable[Concatenate[_Self, str, P], R]:
    def wrapper(self: _Self, context: str, *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Context: {context}")
        return func(self, *args, **kwargs)
    return wrapper

class Base:
    def process_data(self, data: int) -> str:
        return f"Base processed {data}"

class Derived(Base):
    @inject_context
    def process_data(self, context: str, data: int) -> str:
        # The original signature of super().process_data does not expect 'context'.
        # Some type checkers might struggle to understand this signature change
        # and correctly flag the call to super().
        result = super().process_data(data) # Should be error: unexpected argument for super(), or missing 'context' for self.
        return f"Derived processed with context '{context}': {result}"

if __name__ == "__main__":
    d = Derived()
    # Expecting an error here, either at definition or call site,
    # as the decorated method now requires 'context'.
    # Some checkers might not flag the 'super()' call as incorrect.
    print(d.process_data("my-context", 123))


# --- Tier 2 test ---

def test_Derived_process_data():
    """Test that Derived.process_data() runs without type errors."""
    try:
        receiver = Derived()
        result = receiver.process_data()
        # Expected return type: R
        print(f"OK: {result}")
    except (TypeError, AttributeError, ValueError, KeyError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_Derived_process_data()
