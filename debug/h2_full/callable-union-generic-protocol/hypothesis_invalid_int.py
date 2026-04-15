"""Hypothesis-based property test for type constraint validation.

Type annotation: int
Test type: invalid
"""\n\n"""Hypothesis test for int - invalid values.

Type annotation: int
Variable: convert_default.__return__
Test type: invalid
"""

# Original source code
from typing import Protocol, TypeVar, Callable, Any, Union, reveal_type, runtime_checkable

T = TypeVar('T')

@runtime_checkable
class Converter(Protocol[T]):
    def __call__(self, arg: Any) -> T: ...
    def convert_default(self) -> T: ...

class IntConverter:
    def __call__(self, arg: Any) -> int:
        return int(arg)
    def convert_default(self) -> int:
        return 0

def handle_mixed_callable(cb: Callable[..., Any] | Converter[str] | None):
    if callable(cb):
        # Type checkers might disagree on the materialization of this union.
        # Some might simplify to Callable[..., Any], others might keep the union.
        reveal_type(cb) # Expected: Callable[..., Any] | Converter[str]

        # Call with arguments expected by Callable[..., Any]
        result_any = cb(1, "test", kw=True)
        reveal_type(result_any) # Expected: Any (if Callable[..., Any] dominates)

        if isinstance(cb, Converter):
            reveal_type(cb) # Expected: Converter[str]
            converted_str = cb("hello")
            reveal_type(converted_str) # Expected: str
            default_str = cb.convert_default()
            reveal_type(default_str) # Expected: str
        else:
            reveal_type(cb) # Expected: Callable[..., Any] (after excluding Converter)
            result_simple = cb(10)
            reveal_type(result_simple) # Expected: Any
    else:
        reveal_type(cb) # Expected: None

if __name__ == "__main__":
    handle_mixed_callable(IntConverter()) # Should satisfy Callable[..., Any] for call, but not Converter[str]
    handle_mixed_callable(lambda x: str(x)) # Should satisfy Callable[..., Any]
    handle_mixed_callable(None)

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, int)
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "int" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "int" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
