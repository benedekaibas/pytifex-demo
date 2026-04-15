"""
Hypothesis Tier 2 — Generated Property Test

Target: handle_containers(...)
Kind: function
Line: 12
Status: PASS
Max examples: 30

Strategies:
  containers: list -> lists(from_type(__hypothesis_tier2__.BaseContainer[str]), max_size=5)
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
@given(containers=...)
def test_handle_containers(containers):
    """Property test: handle_containers() with generated inputs."""
    result = handle_containers(containers)


if __name__ == "__main__":
    test_handle_containers()
