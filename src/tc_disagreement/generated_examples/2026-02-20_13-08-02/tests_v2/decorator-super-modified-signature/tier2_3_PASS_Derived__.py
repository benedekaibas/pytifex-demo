"""
Hypothesis Tier 2 — Generated Property Test

Target: Derived()
Kind: constructor
Line: 18
Status: PASS
Max examples: 30
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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

def test_Derived_constructor():
    """Test that Derived() can be constructed."""
    instance = Derived()
    assert isinstance(instance, Derived)


if __name__ == "__main__":
    test_Derived_constructor()
