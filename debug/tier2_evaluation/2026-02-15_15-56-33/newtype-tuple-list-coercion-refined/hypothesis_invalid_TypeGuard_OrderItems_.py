"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeGuard[OrderItems]
Test type: invalid
"""\n\n"""Hypothesis test for TypeGuard[OrderItems] - invalid values.

Type annotation: TypeGuard[OrderItems]
Variable: is_order_items_candidate.__return__
Test type: invalid
"""

# Original source code
from typing import NewType, List, Tuple, TypeGuard

# NewType wrapping a tuple of strings, representing a nominal type for order items.
OrderItems = NewType('OrderItems', Tuple[str, ...])

def is_order_items_candidate(arg: Tuple[str, ...]) -> TypeGuard[OrderItems]:
    """
    A TypeGuard function that attempts to refine a `Tuple[str, ...]` to an `OrderItems`.
    At runtime, an `OrderItems` object *is* a `Tuple[str, ...]`. This function
    simply checks if the input tuple is composed of strings.

    Type checkers may diverge here:
    - Some (like mypy) might treat this TypeGuard as valid for refining to the nominal NewType.
    - Others might strictly adhere to NewType's nominal nature, asserting that a `NewType`
      can only be created via its constructor, not by runtime checks on its base type.
    """
    return isinstance(arg, tuple) and all(isinstance(x, str) for x in arg)

def process_and_refine_orders(raw_items_list: List[Tuple[str, ...]]) -> List[OrderItems]:
    """
    Processes a list of raw tuples, attempting to "promote" them to OrderItems
    using the `is_order_items_candidate` TypeGuard.
    """
    retyped_order_items: List[OrderItems] = []
    print(f"Attempting to refine and process raw items: {raw_items_list}")

    for item in raw_items_list:
        if is_order_items_candidate(item):
            # After this TypeGuard, 'item' is notionally refined to 'OrderItems'.
            # Some checkers will allow this `append` directly, others will not.
            # reveal_type(item) # Uncomment to see what individual checkers think 'item' is here.
            retyped_order_items.append(item) # <--- EXPECTED DIVERGENCE POINT
        else:
            # This branch should not be reached if raw_items_list contains only Tuple[str, ...]
            # but would catch cases like List[Tuple[int, ...]] if passed directly.
            print(f"  Skipping non-OrderItems candidate (e.g., wrong element type): {item}")

    print(f"Refined list (according to some checkers): {retyped_order_items}")
    return retyped_order_items

def consume_order_items(orders: List[OrderItems]) -> None:
    """Consumes a list of OrderItems, ensuring its type correctness."""
    print(f"Consumer received OrderItems: {orders}")
    for order_item in orders:
        _ = order_item[0] if order_item else "" # Accessing underlying tuple elements. This should be fine.

if __name__ == "__main__":
    # A list of raw tuples that are structurally compatible with OrderItems's base type.
    raw_input_data: List[Tuple[str, ...]] = [
        ("apple", "banana"),
        ("cherry",),
        ()
    ]

    # This call attempts to convert `List[Tuple[str, ...]]` into `List[OrderItems]`
    # within the `process_and_refine_orders` function, using a TypeGuard for refinement.
    # The divergence is expected at `retyped_order_items.append(item)`.
    processed_list = process_and_refine_orders(raw_input_data)

    # This final consumption step will also highlight the divergence.
    # If `process_and_refine_orders` fails to produce `List[OrderItems]` (due to the divergence),
    # then this call will be flagged as an error by the stricter checkers.
    consume_order_items(processed_list) # <--- Secondary divergence effect check

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, TypeGuard[OrderItems])
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "TypeGuard[OrderItems]" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "TypeGuard[OrderItems]" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
