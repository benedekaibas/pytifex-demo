"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typealiastype-newtype-container.py
Patterns detected: 2
    - newtype (5 tests)
  - main_block_replay (1 tests)
Test cases generated: 6
"""

# --- Original source ---

from typing import TypeAliasType, NewType, List, TypeVar, reveal_type

UserID = NewType('UserID', int)
ItemID = NewType('ItemID', str)

T = TypeVar('T')

# TypeAliasType for a generic list of some ID type
IDList = TypeAliasType('IDList', List[T], type_params=(T,))

def process_user_ids(ids: IDList[UserID]):
    reveal_type(ids) # Expected: List[UserID]
    first_id = ids[0]
    reveal_type(first_id) # Expected: UserID
    
    # This assignment is problematic. Some checkers allow List[int] to be assigned to List[NewType(int)],
    # while others might flag it, testing covariance rules for NewType.
    ids_from_raw_ints: IDList[UserID] = [100, 200] # type: ignore # This line is specifically for disagreement.
    reveal_type(ids_from_raw_ints) # Expected: List[UserID]

def test_newtype_typealiastype():
    my_user_ids: IDList[UserID] = IDList([UserID(1), UserID(2)])
    process_user_ids(my_user_ids)

    my_item_ids: IDList[ItemID] = IDList([ItemID("A1"), ItemID("B2")])
    reveal_type(my_item_ids) # Expected: List[ItemID]
    
if __name__ == "__main__":
    test_newtype_typealiastype()

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_UserID_from_int():
    """Create UserID from a plain int."""
    try:
        val = UserID(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_UserID_from_string():
    """Create UserID from a string (wrong base type)."""
    try:
        val = UserID("not_an_int")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 3, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ItemID_from_string():
    """Create ItemID from a plain string."""
    try:
        val = ItemID("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ItemID_from_int():
    """Create ItemID from an int (wrong base type)."""
    try:
        val = ItemID(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ItemID_from_none():
    """Create ItemID from None."""
    try:
        val = ItemID(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_main_call_test_newtype_typealiastype__():
    """Execute main block call: test_newtype_typealiastype()"""
    import traceback as _tb, sys as _sys
    try:
        test_newtype_typealiastype()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 29
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


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
