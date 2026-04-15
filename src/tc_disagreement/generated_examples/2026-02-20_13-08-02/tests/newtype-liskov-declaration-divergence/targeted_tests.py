"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: newtype-liskov-declaration-divergence.py
Patterns detected: 2
    - newtype (8 tests)
  - inheritance_override (4 tests)
Test cases generated: 12
"""

# --- Original source ---

from typing import NewType, Union
from collections import UserDict

ProductId = NewType('ProductId', str)
CategoryId = NewType('CategoryId', str)
ItemCount = NewType('ItemCount', int)

class Inventory(UserDict[ProductId, ItemCount]):
    def add_item(self, product_id: ProductId, count: ItemCount) -> None:
        # Fix: Explicitly cast the result of addition back to ItemCount
        self[product_id] = ItemCount(self.get(product_id, ItemCount(0)) + count)

class CategorizedInventory(Inventory):
    # The primary goal is to test divergence on the Liskov violation
    # of broadening a method parameter type in a subclass.
    # Specifically, `__setitem__` on a UserDict.

    def add_item(self, key_or_category: Union[ProductId, CategoryId], count: ItemCount) -> None:
        # This method's parameter `key_or_category` is `Union[ProductId, CategoryId]`.
        # The call `self[key_or_category] = count` will invoke `CategorizedInventory.__setitem__`.
        self[key_or_category] = count

    # This method attempts to broaden the key type parameter:
    # Base `UserDict[ProductId, ItemCount]` implies `__setitem__(key: ProductId, value: ItemCount)`.
    # Here, `key` is declared as `Union[ProductId, CategoryId]`.
    #
    # According to Liskov substitution principle for method parameters (contravariance),
    # a subtype's method parameter can be a *supertype* of the base type's parameter.
    # `Union[ProductId, CategoryId]` IS a supertype of `ProductId`.
    # Therefore, this declaration *should* be allowed by strict Liskov principles.
    #
    # However, type checkers often take a more pragmatic stance, creating divergence.
    # Some might flag the *declaration* as an error, others might allow it.
    # We ensure the `super()` call is "safe" to push the divergence to the *declaration* itself.
    def __setitem__(self, key: Union[ProductId, CategoryId], value: ItemCount) -> None:
        # We need a runtime way to distinguish ProductId from CategoryId if we want
        # to handle them differently before passing to super().__setitem__.
        # Since `isinstance` does not work reliably with NewType at runtime,
        # we'll use a pragmatic string check and explicit casting to ensure
        # the argument to `super().__setitem__` is always `ProductId`.
        # This makes the *call* to super() type-safe, pushing any Liskov
        # violation check to the *method signature's declaration*.
        if isinstance(key, str) and key.startswith("CAT_"):
            # This branch handles a `CategoryId` (identified by runtime value convention)
            # by converting it to a `ProductId` for the super call.
            super().__setitem__(ProductId(key + "_default"), value)
        else:
            # Assume it's a `ProductId` or a `CategoryId` not matching the convention
            # that we'll treat as a `ProductId`. Explicitly cast for `super()`.
            super().__setitem__(ProductId(key), value)


if __name__ == "__main__":
    inv = CategorizedInventory()
    inv.add_item(ProductId("P123"), ItemCount(5))
    inv.add_item(CategoryId("CAT_A"), ItemCount(10)) # This CategoryId value will trigger the 'startswith("CAT_")' branch
    print(inv)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_ProductId_from_string():
    """Create ProductId from a plain string."""
    try:
        val = ProductId("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ProductId_from_int():
    """Create ProductId from an int (wrong base type)."""
    try:
        val = ProductId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ProductId_from_none():
    """Create ProductId from None."""
    try:
        val = ProductId(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_CategoryId_from_string():
    """Create CategoryId from a plain string."""
    try:
        val = CategoryId("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_CategoryId_from_int():
    """Create CategoryId from an int (wrong base type)."""
    try:
        val = CategoryId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_CategoryId_from_none():
    """Create CategoryId from None."""
    try:
        val = CategoryId(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_ItemCount_from_int():
    """Create ItemCount from a plain int."""
    try:
        val = ItemCount(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ItemCount_from_string():
    """Create ItemCount from a string (wrong base type)."""
    try:
        val = ItemCount("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_CategorizedInventory_add_item_via_base_ref():
    """Call CategorizedInventory.add_item through a Inventory reference."""
    try:
        obj: Inventory = CategorizedInventory()
        result = obj.add_item()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "override_via_base"})


def test_CategorizedInventory_add_item_direct():
    """Call CategorizedInventory.add_item directly."""
    try:
        obj = CategorizedInventory()
        result = obj.add_item()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "override_direct"})


def test_CategorizedInventory_isinstance_Inventory():
    """Verify CategorizedInventory is an instance of Inventory."""
    try:
        obj = CategorizedInventory()
        if not isinstance(obj, Inventory):
            BUGS.append({"line": 18, "type": "InheritanceError", "error": "CategorizedInventory is not instance of Inventory", "test": "isinstance_check"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "isinstance_check"})


def test_CategorizedInventory_super_add_item():
    """Verify super().add_item() works from CategorizedInventory."""
    try:
        obj = CategorizedInventory()
        base_method = getattr(super(type(obj), obj), "add_item", None)
        if base_method is not None:
            result = base_method()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 18, "type": type(e).__name__, "error": str(e)[:200], "test": "super_call"})


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
