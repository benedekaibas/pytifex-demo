"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeIs[str]
Test type: invalid
"""\n\n"""Hypothesis test for TypeIs[str] - invalid values.

Type annotation: TypeIs[str]
Variable: _is_string.__return__
Test type: invalid
"""

# Original source code
from typing import TypeIs, reveal_type, Any, Callable

class StringCheckDescriptor:
    def __get__(self, instance: Any, owner: Any) -> Callable[[Any], TypeIs[str]]:
        def _is_string(val: object) -> TypeIs[str]:
            return isinstance(val, str)
        return _is_string

class MyClassWithDescriptor:
    is_string_via_descriptor = StringCheckDescriptor()

def process_val_with_descriptor(val: object):
    if MyClassWithDescriptor().is_string_via_descriptor(val):
        reveal_type(val) # Expected: str
    else:
        reveal_type(val) # Expected: object (or object - str)
        
if __name__ == "__main__":
    process_val_with_descriptor("hello world")
    process_val_with_descriptor(12345)
    process_val_with_descriptor(True)

from typeguard import check_type, TypeCheckError

# Test that invalid values fail
def test_invalid(value):
    try:
        check_type(value, TypeIs[str])
        return False  # No error raised
    except (TypeCheckError, TypeError):
        return True  # Error raised as expected

# Run test
if "TypeIs[str]" == "int":
    assert test_invalid("not_an_int"), "Should reject string"
    assert test_invalid(3.14), "Should reject float"
elif "TypeIs[str]" == "str":
    assert test_invalid(42), "Should reject int"
    assert test_invalid(3.14), "Should reject float"

print("✓ Type constraint validation passed")
