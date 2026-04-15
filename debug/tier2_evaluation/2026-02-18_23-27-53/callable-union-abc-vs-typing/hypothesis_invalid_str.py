"""Hypothesis-based property test for type constraint validation.

Type annotation: str
Test type: invalid
"""\n\n"""Hypothesis test for str - invalid values.

Type annotation: str
Variable: specific_int_to_str.__return__
Test type: invalid
"""

# Original source code
from typing import Callable, Any, Union, reveal_type
import collections.abc

def specific_int_to_str(x: int) -> str:
    return str(x)

def specific_str_to_bool(x: str) -> bool:
    return bool(x)

# The union includes `collections.abc.Callable` (effectively Callable[..., Any])
# and a more specific `typing.Callable` type.
# Disagreement can occur on how this union is materialized after `callable()` check.
def process_callable_types_union(item: Union[collections.abc.Callable, Callable[[int], str], None]):
    if callable(item):
        # How does `collections.abc.Callable` interact with `Callable[[int], str]`?
        # Does the `Callable[..., Any]` aspect absorb the more specific type,
        # or do they remain distinct in the union?
        reveal_type(item) # Expected: Union[collections.abc.Callable, Callable[[int], str]]
                                  # Or simplified to collections.abc.Callable / Callable[..., Any]

        # Call with arbitrary args (should always work if collections.abc.Callable dominates)
        res_any_args = item(1, "extra", True)
        reveal_type(res_any_args) # Expected: Any

        # Call with args matching specific_int_to_str
        res_specific_int = item(10)
        reveal_type(res_specific_int) # Expected: Any or str, depending on materialization.

    else:
        reveal_type(item) # Expected: None

if __name__ == "__main__":
    process_callable_types_union(specific_int_to_str)
    process_callable_types_union(specific_str_to_bool) # This is a collections.abc.Callable
    process_callable_types_union(None)

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, str)
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "str" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "str" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
