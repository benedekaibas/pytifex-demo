"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: callable-union-abc-vs-typing.py
Patterns detected: 2
    - callable_param (3 tests)
  - main_block_replay (3 tests)
Test cases generated: 6
"""

# --- Original source ---

from typing import Callable, Any, Union, reveal_type
import collections.abc

def specific_int_to_str(x: int) -> str:
    return str(x)

def specific_str_to_bool(x: str) -> bool:
    return bool(x)

# The union includes `collections.abc.Callable` (effectively Callable[..., Any])
# and a more specific `typing.Callable` type.
# Disagreement can occur on how this union is materialized after `callable()` check.
def process_callable_types_union(item: Union[collections.abc.Callable, Callable[[int], str], None]):
    if callable(item):
        # How does `collections.abc.Callable` interact with `Callable[[int], str]`?
        # Does the `Callable[..., Any]` aspect absorb the more specific type,
        # or do they remain distinct in the union?
        reveal_type(item) # Expected: Union[collections.abc.Callable, Callable[[int], str]]
                                  # Or simplified to collections.abc.Callable / Callable[..., Any]

        # Call with arbitrary args (should always work if collections.abc.Callable dominates)
        res_any_args = item(1, "extra", True)
        reveal_type(res_any_args) # Expected: Any

        # Call with args matching specific_int_to_str
        res_specific_int = item(10)
        reveal_type(res_specific_int) # Expected: Any or str, depending on materialization.

    else:
        reveal_type(item) # Expected: None

if __name__ == "__main__":
    process_callable_types_union(specific_int_to_str)
    process_callable_types_union(specific_str_to_bool) # This is a collections.abc.Callable
    process_callable_types_union(None)

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 12

# --- Test cases ---

def test_process_callable_types_union_none_callable():
    """Call process_callable_types_union with None for Callable param 'item'."""
    try:
        process_callable_types_union(item=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 13, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_process_callable_types_union_string_callable():
    """Call process_callable_types_union with a string for Callable param 'item'."""
    try:
        process_callable_types_union(item="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 13, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_process_callable_types_union_wrong_arity_callable():
    """Call process_callable_types_union with a zero-arg callable for param 'item'."""
    try:
        process_callable_types_union(item=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 13, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


def test_main_call_process_callable_types_union_specific_in():
    """Execute main block call: process_callable_types_union(specific_int_to_str)"""
    import traceback as _tb, sys as _sys
    try:
        process_callable_types_union(specific_int_to_str)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 33
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_process_callable_types_union_specific_st():
    """Execute main block call: process_callable_types_union(specific_str_to_bool)"""
    import traceback as _tb, sys as _sys
    try:
        process_callable_types_union(specific_str_to_bool)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 34
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_process_callable_types_union_None_():
    """Execute main block call: process_callable_types_union(None)"""
    import traceback as _tb, sys as _sys
    try:
        process_callable_types_union(None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 35
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
