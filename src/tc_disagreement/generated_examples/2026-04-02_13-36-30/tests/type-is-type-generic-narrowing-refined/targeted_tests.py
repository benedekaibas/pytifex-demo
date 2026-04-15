"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: type-is-type-generic-narrowing-refined.py
Patterns detected: 1
    - newtype (5 tests)
Test cases generated: 5
"""

# --- Original source ---

from typing import TypeVar, Generic, NewType, reveal_type

UserId = NewType("UserId", int)
DeviceId = NewType("DeviceId", str)

T = TypeVar("T")

class BaseThing(Generic[T]):
    value: T

    def __init__(self, value: T) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        # mypy#20275 involves type(other) is reveal_type(type(self))
        # Here, we test if a generic instance with a NewType type argument
        # can be correctly compared based on type.
        if not (type(other) is type(self)):
            # Some checkers might struggle to see that type(self) includes the generic argument info
            # or that type(other) would match if `other` is also BaseThing[UserId]
            return NotImplemented
        # With reveal_type, mypy might correctly infer type(self) is Type[BaseThing[UserId]]
        # Without it, if `other` is BaseThing[DeviceId], `other.value` is str, not int.
        # This comparison should fail if types are different, but pass if they're the same class and generic param.
        reveal_type(type(self)) # Expect: `Type[BaseThing[UserId]]` when `self` is `BaseThing[UserId]`
        
        # The `type: ignore[attr-defined]` has been removed.
        # This forces type checkers to determine if `other` is correctly narrowed from `object`
        # to a type compatible with `BaseThing[T]` (or `Self`) by the `type(other) is type(self)` check.
        # Some checkers, especially those that correctly infer `type(self)` as `Type[Self]`,
        # might allow `other.value` to be accessed, while others that lose generic information
        # or don't narrow sufficiently will flag an error (e.g., `object` has no `value` attribute).
        return self.value == other.value


if __name__ == "__main__":
    user_thing = BaseThing(UserId(123))
    another_user_thing = BaseThing(UserId(456))
    device_thing = BaseThing(DeviceId("abc"))

    print(f"user_thing == another_user_thing: {user_thing == another_user_thing}")
    print(f"user_thing == device_thing: {user_thing == device_thing}")
    assert user_thing == another_user_thing # Should be True
    assert not (user_thing == device_thing) # Should be True

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_UserId_from_int():
    """Create UserId from a plain int."""
    try:
        val = UserId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_UserId_from_string():
    """Create UserId from a string (wrong base type)."""
    try:
        val = UserId("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_DeviceId_from_string():
    """Create DeviceId from a plain string."""
    try:
        val = DeviceId("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_DeviceId_from_int():
    """Create DeviceId from an int (wrong base type)."""
    try:
        val = DeviceId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_DeviceId_from_none():
    """Create DeviceId from None."""
    try:
        val = DeviceId(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


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
