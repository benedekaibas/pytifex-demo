"""
Hypothesis Tier 2 — Generated Test

Call: process_mixed_data(list_mixed_float)
Kind: function
Line: 38
Status: PASS
"""

# --- Original source (full context) ---

from typing import TypeGuard, List, Union, Literal, reveal_type

# A custom type guard for a list of mixed types
# MODIFIED: The input type of TypeGuard now includes 'float'
# to match the `data` parameter in `process_mixed_data`.
# This resolves the initial 'arg-type' error and pushes the type-checking
# complexity to the narrowing logic itself, which is a common source of divergence.
def has_only_numbers_or_bools(items: List[Union[int, str, bool, float]]) -> TypeGuard[List[Union[int, bool]]]:
    """Narrows a list to contain only numbers or booleans."""
    return all(isinstance(x, (int, bool)) for x in items)

def process_mixed_data(data: List[Union[int, str, bool, float]]):
    # This scenario tests how TypeGuard interacts with lists containing multiple base types
    # and if it correctly narrows a union type within the list elements.
    # The previous error regarding argument type incompatibility for `has_only_numbers_or_bools(data)`
    # should now be resolved, as the TypeGuard's input type has been broadened.
    if has_only_numbers_or_bools(data):
        for item in data:
            # Type checkers might now disagree on the precise narrowed type of 'item'.
            # Expected: 'int | bool' due to the TypeGuard's return annotation.
            # Some checkers might correctly narrow, while others might retain 'str' or 'float'
            # types, or be overly conservative, leading to divergence.
            reveal_type(item)
            print(f"Number or Bool: {item}")
    else:
        for item in data:
            reveal_type(item) # Expected: int | str | bool | float.
            print(f"Mixed item: {item}")

if __name__ == "__main__":
    list_int_bool: List[Union[int, str, bool, float]] = [1, True, 0, False]
    process_mixed_data(list_int_bool)

    list_mixed_str: List[Union[int, str, bool, float]] = [1, "hello", True, 3.14]
    process_mixed_data(list_mixed_str)

    list_mixed_float: List[Union[int, str, bool, float]] = [1, 2.5, True]
    process_mixed_data(list_mixed_float)

    # Type checkers might now disagree on:
    # The precise narrowed type of `item` inside the `if` block (for `reveal_type(item)`).
    # Some checkers are expected to correctly narrow `item` to `int | bool`,
    # while others might retain `str` or `float` from the original union,
    # or apply the narrowing inconsistently within a generic container.


# --- Tier 2 test ---

def test_process_mixed_data():
    """Test that process_mixed_data() runs without type errors."""
    try:
        result = process_mixed_data(list_mixed_float)
        print(f"OK: {result}")
    except (TypeError, AttributeError, ValueError, KeyError) as e:
        print(f"BUG: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    test_process_mixed_data()
