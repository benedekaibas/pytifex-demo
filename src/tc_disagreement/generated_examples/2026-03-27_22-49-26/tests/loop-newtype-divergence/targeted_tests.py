"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: loop-newtype-divergence.py
Patterns detected: 3
    - tuple_length (5 tests)
  - newtype (5 tests)
  - main_block_replay (2 tests)
Test cases generated: 12
"""

# --- Original source ---

from typing import NewType, Tuple, Union, TYPE_CHECKING

UserId = NewType('UserId', int)
ItemId = NewType('ItemId', str)

def process_mixed_data(initial_data: Union[Tuple[UserId, ItemId], Tuple[None, None]]):
    x: UserId | None = None
    y: ItemId | None = None
    data_source: Union[Tuple[UserId, ItemId], Tuple[None, None]] = initial_data

    # The issue here is how `x` and `y` are inferred across loop iterations
    # when reassigned from a potentially changing source `data_source`.
    # `ty` previously marked `x` as Divergent.
    while True:
        x, y = data_source
        if TYPE_CHECKING:
            reveal_type(x) # Expect UserId | None. Some checkers might struggle with the Union.
            reveal_type(y) # Expect ItemId | None.
        
        # Simulate data changing or loop termination
        if x is None:
            break
        data_source = (None, None) # Next iteration will set x, y to None
    
    if TYPE_CHECKING:
        reveal_type(x) # Should be None at loop exit
        reveal_type(y) # Should be None at loop exit


if __name__ == "__main__":
    process_mixed_data((UserId(101), ItemId("item_A")))
    process_mixed_data((None, None))

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_process_mixed_data_empty_tuple():
    """Call process_mixed_data with empty tuple for param 'initial_data'."""
    try:
        process_mixed_data(initial_data=())
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "empty_tuple"})


def test_process_mixed_data_single_element_tuple():
    """Call process_mixed_data with single-element tuple for param 'initial_data'."""
    try:
        process_mixed_data(initial_data=(1,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "single_element_tuple"})


def test_process_mixed_data_none_in_tuple():
    """Call process_mixed_data with None element in tuple for param 'initial_data'."""
    try:
        process_mixed_data(initial_data=(None,))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "none_in_tuple"})


def test_process_mixed_data_wrong_types_in_tuple():
    """Call process_mixed_data with wrong types in tuple for param 'initial_data'."""
    try:
        process_mixed_data(initial_data=(123, 456, 789))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_types_in_tuple"})


def test_process_mixed_data_string_instead_of_tuple():
    """Call process_mixed_data with a string instead of tuple for param 'initial_data'."""
    try:
        process_mixed_data(initial_data="not a tuple")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 6, "type": type(e).__name__, "error": str(e)[:200], "test": "string_instead_of_tuple"})


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


def test_ItemId_from_string():
    """Create ItemId from a plain string."""
    try:
        val = ItemId("test_value")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_from_base"})


def test_ItemId_from_int():
    """Create ItemId from an int (wrong base type)."""
    try:
        val = ItemId(42)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_wrong_base"})


def test_ItemId_from_none():
    """Create ItemId from None."""
    try:
        val = ItemId(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 4, "type": type(e).__name__, "error": str(e)[:200], "test": "newtype_none"})


def test_main_call_process_mixed_data__UserId_101___ItemId_():
    """Execute main block call: process_mixed_data((UserId(101), ItemId('item_A')))"""
    import traceback as _tb, sys as _sys
    try:
        process_mixed_data((UserId(101), ItemId('item_A')))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 31
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_process_mixed_data__None__None__():
    """Execute main block call: process_mixed_data((None, None))"""
    import traceback as _tb, sys as _sys
    try:
        process_mixed_data((None, None))
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 32
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
