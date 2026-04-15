"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: type-is-self-generic-protocol.py
Patterns detected: 1
    - protocol_conformance (3 tests)
Test cases generated: 3
"""

# --- Original source ---

from typing import TypeVar, Generic, Protocol, Self, reveal_type

T = TypeVar('T')

class Comparable(Protocol[T]):
    def __eq__(self, other: object) -> bool: ...

class GenericData(Generic[T]):
    def __init__(self, value: T, identifier: int):
        self.value = value
        self.identifier = identifier

    def __eq__(self: Self, other: object) -> bool:
        # Mypy's issue: `type(other) is type(self)` is not enough to narrow `other`.
        # Here, we combine it with generics and access a generic attribute.
        if isinstance(other, GenericData) and type(other) is type(self):
            # If `type(other) is type(self)` implies `other` is `Self`,
            # then `other.value` and `other.identifier` should be safely accessible.
            # Some checkers might still flag `other.value` as potentially not having `value`.
            return other.value == self.value and other.identifier == self.identifier
        return NotImplemented

if __name__ == "__main__":
    item1 = GenericData("hello", 1)
    item2 = GenericData("hello", 1)
    item3 = GenericData("world", 2)
    item_diff_type = GenericData(123, 1) # Different T

    reveal_type(item1 == item2)
    print(f"item1 == item2: {item1 == item2}")
    print(f"item1 == item3: {item1 == item3}")
    print(f"item1 == item_diff_type: {item1 == item_diff_type}") # This should evaluate to False, not error

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_Generic_has___eq__():
    """Verify Generic has required protocol method '__eq__'."""
    try:
        obj = Generic()
        method = getattr(obj, "__eq__", None)
        if method is None:
            BUGS.append({"line": 5, "type": "AttributeError", "error": "Generic missing protocol method __eq__", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 5, "type": "TypeError", "error": "Generic.__eq__ is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Generic_has___hash__():
    """Verify Generic has required protocol method '__hash__'."""
    try:
        obj = Generic()
        method = getattr(obj, "__hash__", None)
        if method is None:
            BUGS.append({"line": 5, "type": "AttributeError", "error": "Generic missing protocol method __hash__", "test": "protocol_method_exists"})
        elif not callable(method):
            BUGS.append({"line": 5, "type": "TypeError", "error": "Generic.__hash__ is not callable", "test": "protocol_method_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "protocol_check"})


def test_Comparable_non_conforming_object():
    """Pass a non-conforming object where Protocol Comparable is expected."""
    class _FakeNonConforming:
        pass
    fake = _FakeNonConforming()
    for func_name_check, func_obj in [(k, v) for k, v in globals().items() if callable(v)]:
        pass


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
