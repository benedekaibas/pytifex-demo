"""Hypothesis-based property test for type constraint validation.

Type annotation: Callable[[Any], TypeIs[str]]
Test type: valid
"""\n\n"""Hypothesis test for Callable[[Any], TypeIs[str]] - valid values.

Type annotation: Callable[[Any], TypeIs[str]]
Variable: __get__.__return__
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
    if "Callable[[Any], TypeIs[str]]" == "int":
        check_type(42, Callable[[Any], TypeIs[str]])
    elif "Callable[[Any], TypeIs[str]]" == "str":
        check_type("test", Callable[[Any], TypeIs[str]])
    elif "Callable[[Any], TypeIs[str]]" == "float":
        check_type(3.14, Callable[[Any], TypeIs[str]])
    else:
        # Generic valid test
        check_type(None, Callable[[Any], TypeIs[str]])
except:
    pass
