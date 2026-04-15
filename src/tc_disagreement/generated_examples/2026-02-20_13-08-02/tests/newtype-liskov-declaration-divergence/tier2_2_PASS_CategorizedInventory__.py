"""
Hypothesis Tier 2 — Generated Property Test

Target: CategorizedInventory()
Kind: constructor
Line: 13
Status: PASS
Max examples: 30

Strategies:
  dict: _empty -> one_of(integers(), text(max_size=20), booleans())
"""

# --- Original source (full context) ---

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


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(dict=...)
def test_CategorizedInventory_constructor(dict):
    """Property test: CategorizedInventory() with generated inputs."""
    instance = CategorizedInventory(dict)
    assert isinstance(instance, CategorizedInventory)


if __name__ == "__main__":
    test_CategorizedInventory_constructor()
