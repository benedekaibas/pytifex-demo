"""
Hypothesis Tier 2 — Generated Property Test

Target: is_list_of_product_ids(...)
Kind: function
Line: 14
Status: PASS
Max examples: 30

Strategies:
  data: List -> lists(one_of(integers(), text(max_size=10), booleans()), max_size=5)
"""

# --- Original source (full context) ---

import typing as t
from typing import TypeGuard, TypeVar, NewType, List, Union, cast

UserID = NewType("UserID", str)
ProductID = NewType("ProductID", int)

U = TypeVar("U")

def is_list_of_user_ids(data: List[U]) -> TypeGuard[List[UserID]]:
    """Checks if a list contains only UserID (str) values."""
    # Type checkers might incorrectly infer U here, or struggle with NewType comparison.
    return all(isinstance(item, str) for item in data)

def is_list_of_product_ids(data: List[U]) -> TypeGuard[List[ProductID]]:
    """Checks if a list contains only ProductID (int) values."""
    return all(isinstance(item, int) for item in data)


def process_id_list(input_list: List[Union[UserID, ProductID, float, bool]]) -> str:
    reveal_type(input_list) # Expected: List[Union[UserID, ProductID, float, bool]]

    if is_list_of_user_ids(input_list):
        reveal_type(input_list) # Expected: List[UserID]
        # Type checker should know input_list contains only UserID here.
        first_id = input_list[0] if input_list else UserID("N/A")
        reveal_type(first_id) # Expected: UserID
        return f"List contains User IDs: {input_list} (First: {first_id})"
    
    elif is_list_of_product_ids(input_list):
        reveal_type(input_list) # Expected: List[ProductID]
        # Type checker should know input_list contains only ProductID here.
        first_id = input_list[0] if input_list else ProductID(0)
        reveal_type(first_id) # Expected: ProductID
        return f"List contains Product IDs: {input_list} (First: {first_id})"
    
    else:
        # After narrowing, remaining types should be float or bool.
        reveal_type(input_list) # Expected: List[Union[float, bool]]
        return f"List contains mixed or unhandled types: {input_list}"

if __name__ == "__main__":
    user_ids_list: List[Union[UserID, ProductID, float, bool]] = [UserID("user_A"), UserID("user_B")]
    print(process_id_list(user_ids_list))

    product_ids_list: List[Union[UserID, ProductID, float, bool]] = [ProductID(101), ProductID(102)]
    print(process_id_list(product_ids_list))

    mixed_types_list: List[Union[UserID, ProductID, float, bool]] = [UserID("user_C"), 3.14, True]
    print(process_id_list(mixed_types_list))
    
    empty_list: List[Union[UserID, ProductID, float, bool]] = []
    print(process_id_list(empty_list)) # Should hit one of the guards and print its default 'first_id'


# --- Tier 2 property test ---

from hypothesis import given, strategies as st, settings

@settings(max_examples=30, deadline=None)
@given(data=...)
def test_is_list_of_product_ids(data):
    """Property test: is_list_of_product_ids() with generated inputs."""
    result = is_list_of_product_ids(data)


if __name__ == "__main__":
    test_is_list_of_product_ids()
