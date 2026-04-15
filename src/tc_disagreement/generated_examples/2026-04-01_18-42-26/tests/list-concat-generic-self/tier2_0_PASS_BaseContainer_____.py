"""
Hypothesis Tier 2 — Generated Property Test

Target: BaseContainer(...)
Kind: constructor
Line: 6
Status: PASS
Max examples: 30

Strategies:
  data: TypeVar (shared) -> one_of(integers(), text(max_size=10), booleans())
"""

# --- Original source (full context) ---

from typing import TypeVar, Generic, Self, reveal_type

T = TypeVar('T')

class BaseContainer(Generic[T]):
    def __init__(self, data: T):
        self.data = data

class SpecializedContainer(BaseContainer[T]):
    pass

def handle_containers(containers: list[BaseContainer[str]]) -> None:
    print(f"Handling {len(containers)} generic containers.")

if __name__ == "__main__":
    base_list: list[BaseContainer[str]] = [BaseContainer("hello")]
    specialized_list: list[SpecializedContainer[str]] = [SpecializedContainer("world")]

    # Concatenation of a list of generic base class instances
    # with a list of generic subclass instances, type annotated.
    # This tests variance for Generic types with list concatenation.
    combined_list: list[BaseContainer[str]] = base_list + specialized_list
    reveal_type(combined_list)

    handle_containers(combined_list)


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(data=...)
def test_BaseContainer_constructor(data):
    """Property test: BaseContainer() with generated inputs."""
    instance = BaseContainer(data)
    assert isinstance(instance, BaseContainer)


if __name__ == "__main__":
    test_BaseContainer_constructor()
