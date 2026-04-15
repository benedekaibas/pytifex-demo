"""
Hypothesis Tier 2 — Generated Property Test

Target: MyItem(...)
Kind: constructor
Line: 30
Status: PASS
Max examples: 30

Strategies:
  value: int -> integers(min_value=-1000, max_value=1000)
"""

# --- Original source (full context) ---

from abc import ABC, abstractmethod
from typing import Any, Generic
from typing_extensions import TypeVar, Self, reveal_type

# Forward declarations for cyclic TypeVars
class ConcreteContainer(ABC):
    pass

class ConcreteItem(ABC):
    pass

ContainerT = TypeVar("ContainerT", bound="Container[Any]", default="Container[Any]")
ItemT = TypeVar("ItemT", bound="Item[Any]", default="Item[Any]")


class Container(ABC, Generic[ItemT]):
    @abstractmethod
    def add_item(self, item: ItemT) -> Self: ...
    @abstractmethod
    def get_first_item(self) -> ItemT: ...

class Item(ABC, Generic[ContainerT]):
    @abstractmethod
    def get_parent_container(self) -> ContainerT: ...
    @abstractmethod
    def to_container(self) -> ContainerT: ...


class MyItem(Item["MyContainer"]):
    def __init__(self, value: int) -> None:
        self.value = value
        self._parent: "MyContainer" | None = None

    def set_parent(self, parent: "MyContainer") -> None:
        self._parent = parent

    def get_parent_container(self) -> "MyContainer":
        assert self._parent is not None
        return self._parent

    def to_container(self) -> "MyContainer":
        return self.get_parent_container() # Should return MyContainer

class MyContainer(Container["MyItem"]):
    def __init__(self) -> None:
        self._items: list[MyItem] = []

    def add_item(self, item: "MyItem") -> Self:
        self._items.append(item)
        item.set_parent(self)
        return self

    def get_first_item(self) -> "MyItem":
        return self._items[0]

if __name__ == "__main__":
    my_container = MyContainer()
    item1 = MyItem(1)
    my_container.add_item(item1)

    retrieved_item = my_container.get_first_item()
    reveal_type(retrieved_item) # Expected: MyItem

    parent_from_item = retrieved_item.get_parent_container()
    reveal_type(parent_from_item) # Expected: MyContainer

    container_from_item = item1.to_container()
    reveal_type(container_from_item) # Expected: MyContainer


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(value=...)
def test_MyItem_constructor(value):
    """Property test: MyItem() with generated inputs."""
    instance = MyItem(value)
    assert isinstance(instance, MyItem)


if __name__ == "__main__":
    test_MyItem_constructor()
