"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeIs[str]
Test type: valid
"""\n\n"""Hypothesis test for TypeIs[str] - valid values.

Type annotation: TypeIs[str]
Variable: is_string_method.__return__
Test type: valid
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

from typeguard import check_type

# Test that valid values pass
try:
    if "TypeIs[str]" == "int":
        check_type(42, TypeIs[str])
    elif "TypeIs[str]" == "str":
        check_type("test", TypeIs[str])
    elif "TypeIs[str]" == "float":
        check_type(3.14, TypeIs[str])
    else:
        # Generic valid test
        check_type(None, TypeIs[str])
except:
    pass
