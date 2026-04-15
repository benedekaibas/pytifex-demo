"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: reassign-generic-dict-inference.py
Patterns detected: 1
    - newtype (5 tests)
Test cases generated: 5
"""

# --- Original source ---

from typing import TypeVar, Dict, Any, TYPE_CHECKING, NewType, Union

T = TypeVar('T')
UserId = NewType('UserId', int)
ProductId = NewType('ProductId', str)

def create_metadata(key_id: T, description: str) -> Dict[str, Union[T, str]]:
    """Creates a dictionary with generic ID and string description."""
    return {"id": key_id, "desc": description, "type_name": str(type(key_id).__name__)}

if __name__ == "__main__":
    # Initial assignment with int as T
    data_record = create_metadata(1, "system log entry")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, int | str]
        reveal_type(data_record["id"]) # Expected int | str
    assert data_record["id"] == 1
    print(f"Record 1: {data_record}")

    # Reassignment with NewType(UserId) as T.
    # Type checkers must correctly update the type of `data_record` and its elements.
    data_record = create_metadata(UserId(101), "user activity")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, UserId | str] (not int | str)
        reveal_type(data_record["id"]) # Expected UserId | str (not int | str)
    assert data_record["id"] == UserId(101)
    print(f"Record 2: {data_record}")

    # Reassignment with another NewType(ProductId) as T.
    data_record = create_metadata(ProductId("PROD-XYZ"), "product info")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, ProductId | str]
        reveal_type(data_record["id"]) # Expected ProductId | str
    assert data_record["id"] == ProductId("PROD-XYZ")
    print(f"Record 3: {data_record}")

    # Reassignment to a different generic type (e.g., bool)
    data_record = create_metadata(True, "boolean flag")
    if TYPE_CHECKING:
        reveal_type(data_record) # Expected Dict[str, bool | str]
        reveal_type(data_record["id"]) # Expected bool | str
    assert data_record["id"] is True
    print(f"Record 4: {data_record}")

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 11

# --- Test cases ---

def test_UserId_from_int():
    """Create UserId from a plain int."""
    try:
        val = UserId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_UserId_from_string():
    """Create UserId from a string (wrong base type)."""
    try:
        val = UserId("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ProductId_from_string():
    """Create ProductId from a plain string."""
    try:
        val = ProductId("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ProductId_from_int():
    """Create ProductId from an int (wrong base type)."""
    try:
        val = ProductId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 5, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ProductId_from_none():
    """Create ProductId from None."""
    try:
        val = ProductId(None)
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
