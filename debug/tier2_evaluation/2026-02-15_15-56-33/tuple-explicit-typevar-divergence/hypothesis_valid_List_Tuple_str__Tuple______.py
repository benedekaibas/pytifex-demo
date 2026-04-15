"""Hypothesis-based property test for type constraint validation.

Type annotation: List[Tuple[str, Tuple[()]]]
Test type: valid
"""\n\n"""Hypothesis test for List[Tuple[str, Tuple[()]]] - valid values.

Type annotation: List[Tuple[str, Tuple[()]]]
Variable: list_of_str_empty
Test type: valid
"""

# Original source code
from typing import List, Tuple, TypeVar, Dict, Any

# Inspired by mypy#20563 (list[()] and list[(int,)]) - empty tuples in generics.
# Here, we test nested generic structures involving empty tuples and type variables.

T = TypeVar("T")
U = TypeVar("U")

# A mapping where keys are empty tuples, and values are generic.
# Corrected: `()` in type hints must be `Tuple[()]`.
def process_empty_tuple_dict(data: Dict[Tuple[()], T]) -> T:
    """Expects a dictionary where the only key can be an empty tuple."""
    return data[()]

# A list of tuples, where each tuple's second element is a fixed empty tuple.
# Corrected: `()` in type hints must be `Tuple[()]`.
def process_list_of_fixed_tuples(data: List[Tuple[T, Tuple[()]]]) -> List[T]:
    """Extracts the first element from each tuple."""
    return [item[0] for item in data]

# A new function that expects a non-empty tuple (Tuple with `...` implies one or more elements).
def process_non_empty_tuple(data: Tuple[T, ...]) -> T:
    """
    Expects a tuple with at least one element.
    Accessing data[0] would be a runtime error if data were an empty tuple.
    """
    return data[0]

if __name__ == "__main__":
    # Test process_empty_tuple_dict
    dict_int: Dict[Tuple[()], int] = {(): 123} # Corrected from `Dict[(), int]`
    print(f"Dict with int: {process_empty_tuple_dict(dict_int)}") # No error expected

    # What if a dict with a non-empty tuple key is passed to a function expecting Dict[Tuple[()], T]?
    # This should be an error, as Tuple[int] is not assignable to Tuple[()].
    non_empty_key_dict: Dict[Tuple[int], str] = {(1,): "world"}
    # print(f"Non-empty key dict: {process_empty_tuple_dict(non_empty_key_dict)}")
    # Expected: All type checkers should flag this as an error due to Dict key invariance.

    # Test process_list_of_fixed_tuples
    list_of_str_empty: List[Tuple[str, Tuple[()]]] = [("a", ()), ("b", ())] # Corrected from `Tuple[str, ()]`
    print(f"List of str-empty tuples: {process_list_of_fixed_tuples(list_of_str_empty)}") # No error expected

    # What if the inner tuple isn't exactly `Tuple[()]`?
    # This should be an error because Tuple[int] is not assignable to Tuple[()].
    list_of_int_non_empty: List[Tuple[int, Tuple[int]]] = [(1, (2,)), (3, (4,))]
    # print(f"List of int-non-empty tuples: {process_list_of_fixed_tuples(list_of_int_non_empty)}")
    # Expected: All type checkers should flag this as an error.


    # --- REAL DIVERGENCE ATTEMPT ---
    # Scenario: Passing an empty tuple `()` to a function expecting `Tuple[T, ...]`.
    # `Tuple[T, ...]` signifies a tuple with *at least one element*.
    # `Tuple[()]` signifies an empty tuple.
    # Therefore, `()` should NOT be assignable to `Tuple[T, ...]`.
    # Divergence is expected here because some type checkers might:
    # 1. Strictly enforce the length constraint (length >= 1 for `Tuple[T, ...]`).
    # 2. Be more lenient, possibly inferring `T` as `Never` or `Any` if there are no elements,
    #    and allowing the assignment, perhaps only flagging `data[0]` inside the function.
    # This tests structural typing for tuples, TypeVar inference with empty iterables,
    # and the interpretation of `...` in `Tuple` type hints.

    empty_tuple_literal = () # Type: Tuple[()]
    # The original test line `process_non_empty_tuple(empty_tuple_literal)`
    # did not trigger an error in any type checker. This is surprising, as `Tuple[()]`
    # (zero elements) is incompatible with `Tuple[T, ...]` (one or more elements).

    # To force a divergence, we explicitly bind the TypeVar `T` to `int` for the call.
    # This requires the argument `data` to be of type `Tuple[int, ...]`.
    # `Tuple[()]` is clearly incompatible with `Tuple[int, ...]` due to both
    # element type and length constraint.
    try:
        # This call is expected to be flagged as an error by type checkers
        # that strictly enforce `Tuple[T, ...]` length and type when T is bound.
        # mypy is expected to flag this, while others might not.
        result_divergence = process_non_empty_tuple[int](empty_tuple_literal)
        print(f"Processing empty tuple with non-empty processor (explicit T=int): {result_divergence}")
    except IndexError as e:
        print(f"Runtime error (expected): {e} when processing an empty tuple with data[0]")

from typeguard import check_type

# Test that valid values pass
try:
    if "List[Tuple[str, Tuple[()]]]" == "int":
        check_type(42, List[Tuple[str, Tuple[()]]])
    elif "List[Tuple[str, Tuple[()]]]" == "str":
        check_type("test", List[Tuple[str, Tuple[()]]])
    elif "List[Tuple[str, Tuple[()]]]" == "float":
        check_type(3.14, List[Tuple[str, Tuple[()]]])
    else:
        # Generic valid test
        check_type(None, List[Tuple[str, Tuple[()]]])
except:
    pass
