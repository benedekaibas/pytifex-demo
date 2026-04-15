"""
Targeted Test Suite — Pattern-Based Type Error Detection

Source: typeis-decorated-method-refined.py
Patterns detected: 3
    - decorator_signature (2 tests)
  - callable_param (3 tests)
  - main_block_replay (3 tests)
Test cases generated: 8
"""

# --- Original source ---

from typing import ParamSpec, Callable, TypeVar, reveal_type
from typing_extensions import TypeIs # Changed from typing to typing_extensions

P = ParamSpec('P')
R = TypeVar('R')

def typeis_wrapper(func: Callable[P, TypeIs[R]]) -> Callable[P, TypeIs[R]]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> TypeIs[R]:
        # This wrapper's return annotation TypeIs[R] implies that 'wrapper' itself
        # is a TypeIs function, narrowing its first positional argument.
        # How type checkers handle TypeIs with *args is an ambiguity.
        return func(*args, **kwargs)
    return wrapper

class Validator:
    @typeis_wrapper
    def is_list_of_ints(self, x: object) -> TypeIs[list[int]]:
        # According to PEP 673, TypeIs[list[int]] on this method should narrow 'self'
        # to list[int], not 'x'. However, the function's logic operates on 'x'.
        # This semantic mismatch is a prime candidate for divergence.
        return isinstance(x, list) and all(isinstance(item, int) for item in x)

def check_decorated_typeis(data: object):
    validator_instance = Validator() # Instantiate once
    if validator_instance.is_list_of_ints(data):
        reveal_type(data) # Divergence point: Some may show list[int] (incorrectly narrowed x),
                          # others object (correctly not narrowing x, or decorator failed).
    else:
        reveal_type(data) # Expected: object (or object - list[int])
        
if __name__ == "__main__":
    check_decorated_typeis([1, 2, 3])
    check_decorated_typeis("not a list")
    check_decorated_typeis([1, "a"])

# --- Test infrastructure ---
BUGS = []
_SOURCE_LINE_OFFSET = 13

# --- Test cases ---

def test_Validator_is_list_of_ints_decorated_callable():
    """Verify decorated method Validator.is_list_of_ints is callable."""
    try:
        obj = Validator()
        method = getattr(obj, "is_list_of_ints", None)
        if method is None:
            BUGS.append({"line": 17, "type": "AttributeError", "error": "Validator has no method is_list_of_ints after decoration", "test": "decorated_callable"})
        elif not callable(method):
            BUGS.append({"line": 17, "type": "TypeError", "error": "Validator.is_list_of_ints is not callable after decoration", "test": "decorated_callable"})
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_callable"})


def test_Validator_is_list_of_ints_no_args():
    """Call decorated Validator.is_list_of_ints with no extra args."""
    try:
        obj = Validator()
        result = obj.is_list_of_ints()
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 17, "type": type(e).__name__, "error": str(e)[:200], "test": "decorated_no_args"})


def test_typeis_wrapper_none_callable():
    """Call typeis_wrapper with None for Callable param 'func'."""
    try:
        typeis_wrapper(func=None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "none_callable"})


def test_typeis_wrapper_string_callable():
    """Call typeis_wrapper with a string for Callable param 'func'."""
    try:
        typeis_wrapper(func="not_callable")
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "string_callable"})


def test_typeis_wrapper_wrong_arity_callable():
    """Call typeis_wrapper with a zero-arg callable for param 'func'."""
    try:
        typeis_wrapper(func=lambda: None)
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        BUGS.append({"line": 7, "type": type(e).__name__, "error": str(e)[:200], "test": "wrong_arity_callable"})


def test_main_call_check_decorated_typeis__1__2__3__():
    """Execute main block call: check_decorated_typeis([1, 2, 3])"""
    import traceback as _tb, sys as _sys
    try:
        check_decorated_typeis([1, 2, 3])
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 32
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_check_decorated_typeis__not_a_list__():
    """Execute main block call: check_decorated_typeis('not a list')"""
    import traceback as _tb, sys as _sys
    try:
        check_decorated_typeis('not a list')
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 33
        _root = e
        while getattr(_root, '__cause__', None) or getattr(_root, '__context__', None):
            _root = _root.__cause__ or _root.__context__
        _frames = _tb.extract_tb(_root.__traceback__)
        if _frames:
            _fault_line = _frames[-1].lineno - _SOURCE_LINE_OFFSET
        BUGS.append({"line": _fault_line, "type": type(e).__name__, "error": str(e)[:200], "test": "main_block_call"})


def test_main_call_check_decorated_typeis__1___a___():
    """Execute main block call: check_decorated_typeis([1, 'a'])"""
    import traceback as _tb, sys as _sys
    try:
        check_decorated_typeis([1, 'a'])
    except (TypeError, ValueError, AttributeError, KeyError) as e:
        _fault_line = 34
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
