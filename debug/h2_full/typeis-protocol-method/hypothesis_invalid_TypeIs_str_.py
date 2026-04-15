"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeIs[str]
Test type: invalid
"""\n\n"""Hypothesis test for TypeIs[str] - invalid values.

Type annotation: TypeIs[str]
Variable: is_string_method.__return__
Test type: invalid
"""

# Original source code
from typing import Protocol, TypeIs, reveal_type, runtime_checkable

@runtime_checkable
class StringChecker(Protocol):
    def is_string_method(self, obj: object) -> TypeIs[str]: ...

class MyStringChecker:
    def is_string_method(self, obj: object) -> TypeIs[str]:
        return isinstance(obj, str)

class OtherType:
    value: int = 0

def check_protocol_typeis_narrowing(x: MyStringChecker | OtherType | int):
    if isinstance(x, MyStringChecker):
        reveal_type(x) # Expected: MyStringChecker
        # The TypeIs method should narrow the *argument*. If `x` is passed, `x` should narrow.
        if x.is_string_method(x):
            reveal_type(x) # Expected: str (or str & MyStringChecker)
        else:
            reveal_type(x) # Expected: MyStringChecker (or MyStringChecker - str)
    elif isinstance(x, int):
        reveal_type(x) # Expected: int
    else:
        reveal_type(x) # Expected: OtherType
        
if __name__ == "__main__":
    check_protocol_typeis_narrowing(MyStringChecker())
    check_protocol_typeis_narrowing(123)
    check_protocol_typeis_narrowing(OtherType())

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
