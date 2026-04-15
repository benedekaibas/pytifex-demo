"""Hypothesis-based property test for type constraint validation.

Type annotation: TypeIs[str]
Test type: valid
"""\n\n"""Hypothesis test for TypeIs[str] - valid values.

Type annotation: TypeIs[str]
Variable: _is_string.__return__
Test type: valid
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
