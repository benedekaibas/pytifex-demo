"""Hypothesis Tier 2 test artifact.

Annotation: str
Variable: name
Resolved type: <class 'str'>
Status: PASS
"""

# --- Original source code (full context) ---
from typing import TypeVar, Callable, ParamSpec, Concatenate, Any
from typing_extensions import TypedDict, ReadOnly, NotRequired

# Inspired by pyright#11037 (TypedDict ReadOnly issues) and ParamSpec decorator usage.
# This tests if ParamSpec decorators correctly propagate TypedDict's ReadOnly/NotRequired
# constraints to classmethods they wrap, especially when a non-conforming argument is passed.

P = ParamSpec("P")
R = TypeVar("R")
C = TypeVar("C", bound=type) # Type variable for the class itself in a classmethod

class ItemProps(TypedDict):
    name: str
    price: ReadOnly[float]
    quantity: NotRequired[int]

# Decorator for classmethods that logs arguments.
# Uses ParamSpec to preserve the exact signature of the decorated classmethod.
def log_classmethod_args[C_cls: type, **P_func, R_ret](
    func: Callable[Concatenate[C_cls, P_func], R_ret]
) -> Callable[Concatenate[C_cls, P_func], R_ret]:
    def wrapper(cls: C_cls, *args: P_func.args, **kwargs: P_func.kwargs) -> R_ret:
        print(f"DEBUG: Calling classmethod {cls.__name__}.{func.__name__} with args={args}, kwargs={kwargs}")
        return func(cls, *args, **kwargs)
    return wrapper

class InventoryManager:
    @classmethod
    @log_classmethod_args # Apply the ParamSpec decorator
    def add_item(cls, item_data: ItemProps) -> bool:
        """Adds an item to inventory, prints data."""
        print(f"Adding item: {item_data['name']}")
        # Attempt to modify a ReadOnly field - should be an error.
        # item_data["price"] = 99.99 # Expected error

        # Attempt to modify a NotRequired field - should be fine if it exists.
        if "quantity" in item_data:
            item_data["quantity"] = 100 # No error expected
        return True

if __name__ == "__main__":
    # 1. Valid ItemProps data
    valid_item: ItemProps = {"name": "Laptop", "price": 1200.0}
    InventoryManager.add_item(valid_item) # No error expected

    # 2. Valid ItemProps with optional field
    valid_item_full: ItemProps = {"name": "Mouse", "price": 25.0, "quantity": 50}
    InventoryManager.add_item(valid_item_full) # No error expected

    # 3. Attempt to pass a plain dict (which structurally looks similar but isn't ItemProps)
    # The `price` field in `mutable_price_item` is implicitly mutable (float), not ReadOnly[float].
    # This should be an error, as `ItemProps` (a nominal type with ReadOnly constraints) is expected.
    # The `ParamSpec` decorator should preserve this type constraint.
    mutable_price_item: Any = {"name": "Keyboard", "price": 75.0, "quantity": 30}
    # InventoryManager.add_item(mutable_price_item) # <--- EXPECTED DIVERGENCE: Should be error for type mismatch
    # If a checker allows this, it might be due to loose handling of TypedDict nominality or ReadOnly through ParamSpec.

# --- Hypothesis test ---
from hypothesis import given, settings, strategies as st
from typeguard import check_type, TypeCheckError

# To reproduce: run this file directly
# Annotation under test: str
# check_type(value, str)
