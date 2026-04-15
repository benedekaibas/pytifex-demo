from typing import TypeVar, Generic, Protocol, Self, reveal_type

T = TypeVar('T')

class Comparable(Protocol[T]):
    def __eq__(self, other: object) -> bool: ...

class GenericData(Generic[T]):
    def __init__(self, value: T, identifier: int):
        self.value = value
        self.identifier = identifier

    def __eq__(self: Self, other: object) -> bool:
        # Mypy's issue: `type(other) is type(self)` is not enough to narrow `other`.
        # Here, we combine it with generics and access a generic attribute.
        if isinstance(other, GenericData) and type(other) is type(self):
            # If `type(other) is type(self)` implies `other` is `Self`,
            # then `other.value` and `other.identifier` should be safely accessible.
            # Some checkers might still flag `other.value` as potentially not having `value`.
            return other.value == self.value and other.identifier == self.identifier
        return NotImplemented

if __name__ == "__main__":
    item1 = GenericData("hello", 1)
    item2 = GenericData("hello", 1)
    item3 = GenericData("world", 2)
    item_diff_type = GenericData(123, 1) # Different T

    reveal_type(item1 == item2)
    print(f"item1 == item2: {item1 == item2}")
    print(f"item1 == item3: {item1 == item3}")
    print(f"item1 == item_diff_type: {item1 == item_diff_type}") # This should evaluate to False, not error