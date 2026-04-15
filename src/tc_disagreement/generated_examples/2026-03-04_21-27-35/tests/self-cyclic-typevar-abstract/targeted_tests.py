"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: self-cyclic-typevar-abstract.py
Patterns detected: 1
    - decorator_signature (6 tests)
Test cases generated: 6
"""

# --- Original source ---

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

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_Container_get_first_item_decorated_callable():
    """Verify decorated method Container.get_first_item is callable."""
    try:
        obj = Container()
        method = getattr(obj, "get_first_item", None)
        if method is None:
            BUGS.append({"line": 20, "type": "AttributeError", "error": "Container has no method get_first_item after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 20, "type": "TypeError", "error": "Container.get_first_item is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Container_get_first_item_no_args():
    """Call decorated Container.get_first_item with no extra args."""
    try:
        obj = Container()
        result = obj.get_first_item()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 20, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_Item_get_parent_container_decorated_callable():
    """Verify decorated method Item.get_parent_container is callable."""
    try:
        obj = Item()
        method = getattr(obj, "get_parent_container", None)
        if method is None:
            BUGS.append({"line": 24, "type": "AttributeError", "error": "Item has no method get_parent_container after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 24, "type": "TypeError", "error": "Item.get_parent_container is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Item_get_parent_container_no_args():
    """Call decorated Item.get_parent_container with no extra args."""
    try:
        obj = Item()
        result = obj.get_parent_container()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 24, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_Item_to_container_decorated_callable():
    """Verify decorated method Item.to_container is callable."""
    try:
        obj = Item()
        method = getattr(obj, "to_container", None)
        if method is None:
            BUGS.append({"line": 26, "type": "AttributeError", "error": "Item has no method to_container after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 26, "type": "TypeError", "error": "Item.to_container is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 26, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Item_to_container_no_args():
    """Call decorated Item.to_container with no extra args."""
    try:
        obj = Item()
        result = obj.to_container()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 26, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
