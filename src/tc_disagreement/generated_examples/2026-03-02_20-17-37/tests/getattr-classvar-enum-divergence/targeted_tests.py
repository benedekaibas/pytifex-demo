"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: getattr-classvar-enum-divergence.py
Patterns detected: 1
    - newtype (3 tests)
Test cases generated: 3
"""

# --- Original source ---

import enum
import typing as t
from typing import NewType, ClassVar, Dict, Any, reveal_type # Added reveal_type import

UserID = NewType("UserID", str)

class StatusEnum(float, enum.Enum):
    """An enum with a ClassVar cache of NewType values, accessed via getattr.
    This version aims for divergence by making `getattr`'s return type inference ambiguous
    for some type checkers due to the lack of an explicit runtime ClassVar initialization
    and removal of local variable annotation.
    """

    if t.TYPE_CHECKING:
        # Declare, but do NOT initialize, the ClassVar in the enum body.
        # This is crucial to avoid "Enum members must be left unannotated" errors
        # in strict type checkers like Mypy, which consider an initialized ClassVar
        # an enum member if it's within the enum class body.
        # This declaration makes type checkers aware of the attribute and its type
        # for static analysis.
        _user_status_cache: ClassVar[Dict[UserID, "StatusEnum"]]
    # No 'else' block for runtime, as `_user_status_cache` is dynamically handled
    # via getattr/setattr at runtime.

    ACTIVE = 1.0
    INACTIVE = 0.0
    PENDING = 0.5

    @classmethod
    def get_status_for_user(cls, user_id: UserID) -> "StatusEnum":
        # Removed explicit annotation for `cache`. This forces the type checker
        # to infer the type of `cache` solely from the assignment in the `try`
        # or `except` blocks.
        try:
            # Some type checkers might infer `cache` as Dict[UserID, StatusEnum]
            # due to the ClassVar declaration in `TYPE_CHECKING`.
            # Others might conservatively infer `Any` because `getattr` is a dynamic
            # function and `_user_status_cache` doesn't *exist* at runtime
            # until after the first call (when setattr initializes it).
            cache = getattr(cls, "_user_status_cache")
            reveal_type(cache) # Expected divergence: Dict[UserID, StatusEnum] vs. Any
        except AttributeError:
            print("Cache not initialized, building now...")
            cache = {}
            for item in cls:
                cache[UserID(f"user_{item.name.lower()}")] = item
            setattr(cls, "_user_status_cache", cache)
        
        # If `cache` was inferred as `Any` above by a conservative checker,
        # then `status` will also be `Any`.
        status = cache.get(user_id)
        if status is None:
            raise KeyError(f"No status found for user {user_id}")
        
        # This return statement is the key point of divergence:
        # If `status` is inferred as `Any`, strict type checkers (e.g., mypy)
        # will report an "Incompatible return value type" error because the function
        # is annotated to return "StatusEnum".
        # If `status` is correctly inferred as `StatusEnum`, no error will occur.
        return status

if __name__ == "__main__":
    user_id_1 = UserID("user_active")
    user_id_2 = UserID("user_inactive")
    
    print(f"Status for {user_id_1}: {StatusEnum.get_status_for_user(user_id_1)}")
    print(f"Status for {user_id_2}: {StatusEnum.get_status_for_user(user_id_2)}")
    
    try:
        StatusEnum.get_status_for_user(UserID("non_existent"))
    except KeyError as e:
        print(e)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_UserID_from_string():
    """Create UserID from a plain string."""
    try:
        val = UserID("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_UserID_from_int():
    """Create UserID from an int (wrong base type)."""
    try:
        val = UserID(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_UserID_from_none():
    """Create UserID from None."""
    try:
        val = UserID(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


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
