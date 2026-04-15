"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: match-generic-self.py
Patterns detected: 1
    - decorator_signature (2 tests)
Test cases generated: 2
"""

# --- Original source ---

import typing as t
from typing import Generic, TypeVar, Union, Self, List

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def describe_value(self: Self) -> str:
        # Type checkers might struggle with Self referring to Box[T] and propagating T's type
        # within the match statement for structural pattern matching.
        match self.value:
            case int() as i:
                reveal_type(i) # Expected: int
                return f"Box<{self.value_type_name}> contains an integer: {i}"
            case str() as s:
                reveal_type(s) # Expected: str
                return f"Box<{self.value_type_name}> contains a string: '{s}'"
            case list() if all(isinstance(x, int) for x in self.value): # Runtime check for specific list content
                reveal_type(self.value) # Expected: list[int] (if narrowed correctly)
                return f"Box<{self.value_type_name}> contains a list of integers: {self.value}"
            case _:
                reveal_type(self.value) # Expected: T
                return f"Box<{self.value_type_name}> contains a generic value: {self.value}"
    
    @property
    def value_type_name(self: Self) -> str:
        # Simple property to illustrate Self context
        return type(self.value).__name__

if __name__ == "__main__":
    int_box = Box(123)
    str_box = Box("hello")
    list_int_box = Box([1, 2, 3])
    float_box = Box(3.14)
    mixed_list_box = Box([1, "a", 2.0])

    print(int_box.describe_value())
    print(str_box.describe_value())
    print(list_int_box.describe_value())
    print(float_box.describe_value())
    print(mixed_list_box.describe_value())

    # Demonstrate Self type with a subclass
    class SpecificIntBox(Box[int]):
        def get_value_plus_one(self: Self) -> int:
            # Self here should be SpecificIntBox[int], so self.value is int
            reveal_type(self.value) # Expected: int
            return self.value + 1

    s_int_box = SpecificIntBox(5)
    print(f"Specific box value + 1: {s_int_box.get_value_plus_one()}")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_Box_value_type_name_decorated_callable():
    """Verify decorated method Box.value_type_name is callable."""
    try:
        obj = Box()
        method = getattr(obj, "value_type_name", None)
        if method is None:
            BUGS.append({"line": 28, "type": "AttributeError", "error": "Box has no method value_type_name after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 28, "type": "TypeError", "error": "Box.value_type_name is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Box_value_type_name_no_args():
    """Call decorated Box.value_type_name with no extra args."""
    try:
        obj = Box()
        result = obj.value_type_name()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 28, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


# --- Runner ---
if __name__ == "__main__":
    import sys
    _test_fns = [(name, fn) for name, fn in list(globals().items()) if name.startswith("test_") and callable(fn)]
    print(f"Running {len(_test_fns)} targeted tests...")
    _passed = 0
    _failed = 0
    for _name, _fn in _test_fns:
        try:
            _fn()
            _passed += 1
        except Exception as _e:
            _failed += 1
    print(f"Passed: {_passed}, Failed: {_failed}, Bugs found: {len(BUGS)}")
    for _bug in BUGS:
        print(f"  BUG L{_bug['line']} [{_bug['type']}] {_bug['error']}")
